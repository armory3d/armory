#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

uniform sampler2D senvmapRadiance;
uniform sampler2D senvmapIrradiance;
uniform int envmapNumMipmaps;
uniform float envmapStrength;
uniform sampler2D senvmapBrdf;

#ifdef _Probe1
uniform sampler2D senvmapRadiance_1;
uniform sampler2D senvmapIrradiance_1;
// uniform int envmapNumMipmaps_1;
// uniform float envmapStrength_1;
#endif
#ifdef _Probe2
uniform sampler2D senvmapRadiance_2;
uniform sampler2D senvmapIrradiance_2;
#endif
#ifdef _Probe3
uniform sampler2D senvmapRadiance_3;
uniform sampler2D senvmapIrradiance_3;
#endif
#ifdef _Probe4
uniform sampler2D senvmapRadiance_4;
uniform sampler2D senvmapIrradiance_4;
#endif

// uniform sampler2D giblur; // Path-traced

uniform sampler2D ssaotex;
uniform sampler2D shadowMap;

const float PI = 3.1415926535;
const float TwoPI = (2.0 * PI);
const vec2 shadowMapSize = vec2(2048, 2048);

// #ifdef _LTC
// uniform sampler2D sltcMat;
// uniform sampler2D sltcMag;
// #endif

// uniform mat4 invVP;
uniform mat4 LMVP;
uniform vec3 light;
uniform vec3 lightColor;
uniform float lightStrength;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform float time;



// LTC
// const float roughness = 0.25;
const vec3 dcolor = vec3(1.0, 1.0, 1.0);
// const vec3 scolor = vec3(1.0, 1.0, 1.0);
// const float intensity = 4.0; // 0-10
// const float width = 4.0;
// const float height = 4.0;
const vec2 resolution = vec2(800.0, 600.0);
// const int sampleCount = 0;
// const int NUM_SAMPLES = 8;
const float LUT_SIZE  = 64.0;
const float LUT_SCALE = (LUT_SIZE - 1.0)/LUT_SIZE;
const float LUT_BIAS  = 0.5/LUT_SIZE;
// vec2 mys[NUM_SAMPLES];		
vec3 L0 = vec3(0.0);
vec3 L1 = vec3(0.0);
vec3 L2 = vec3(0.0);
vec3 L3 = vec3(0.0);
vec3 L4 = vec3(0.0);



in vec2 texCoord;
in vec3 viewRay;

// Separable SSS Transmittance Function, ref to sss_pass
vec3 SSSSTransmittance(float translucency, float sssWidth, vec3 worldPosition, vec3 worldNormal, vec3 lightDir) {
	float scale = 8.25 * (1.0 - translucency) / sssWidth;
    vec4 shrinkedPos = vec4(worldPosition - 0.005 * worldNormal, 1.0);
    vec4 shadowPosition = LMVP * shrinkedPos;
    float d1 = texture(shadowMap, shadowPosition.xy / shadowPosition.w).r; // 'd1' has a range of 0..1
    float d2 = shadowPosition.z; // 'd2' has a range of 0..'lightFarPlane'
    const float lightFarPlane = 120 / 3.5;
	d1 *= lightFarPlane; // So we scale 'd1' accordingly:
    float d = scale * abs(d1 - d2);

    float dd = -d * d;
    vec3 profile = vec3(0.233, 0.455, 0.649) * exp(dd / 0.0064) +
                     vec3(0.1,   0.336, 0.344) * exp(dd / 0.0484) +
                     vec3(0.118, 0.198, 0.0)   * exp(dd / 0.187)  +
                     vec3(0.113, 0.007, 0.007) * exp(dd / 0.567)  +
                     vec3(0.358, 0.004, 0.0)   * exp(dd / 1.99)   +
                     vec3(0.078, 0.0,   0.0)   * exp(dd / 7.41);
    return profile * clamp(0.3 + dot(lightDir, -worldNormal), 0.0, 1.0);
}

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / TwoPI, phi / PI);
}

float getMipLevelFromRoughness(float roughness) {
	// First mipmap level = roughness 0, last = roughness = 1
	// baseColor texture already counted
	return roughness * envmapNumMipmaps;
}

vec3 surfaceAlbedo(vec3 baseColor, float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(vec3 baseColor, float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
}

vec3 f_schlick(vec3 f0, float vh) {
	return f0 + (1.0-f0)*exp2((-5.55473 * vh - 6.98316)*vh);
}

float v_smithschlick(float nl, float nv, float a) {
	return 1.0 / ( (nl*(1.0-a)+a) * (nv*(1.0-a)+a) );
}

float d_ggx(float nh, float a) {
	float a2 = a*a;
	float denom = pow(nh*nh * (a2-1.0) + 1.0, 2.0);
	return a2 * (1.0 / 3.1415926535) / denom;
}

vec3 specularBRDF(vec3 f0, float roughness, float nl, float nh, float nv, float vh, float lh) {
	float a = roughness * roughness;
	return d_ggx(nh, a) * clamp(v_smithschlick(nl, nv, a), 0.0, 1.0) * f_schlick(f0, vh) / 4.0;
	//return vec3(LightingFuncGGX_OPT3(nl, lh, nh, roughness, f0[0]));
}

vec3 lambert(vec3 albedo, float nl) {
	return albedo * max(0.0, nl);
}

vec3 diffuseBRDF(vec3 albedo, float roughness, float nv, float nl, float vh, float lv) {
	return lambert(albedo, nl);
}

float texture2DCompare(vec2 uv, float compare){
    float depth = texture(shadowMap, uv).r * 2.0 - 1.0;
    return step(compare, depth);
}

float texture2DShadowLerp(vec2 size, vec2 uv, float compare){
    vec2 texelSize = vec2(1.0) / size;
    vec2 f = fract(uv * size + 0.5);
    vec2 centroidUV = floor(uv * size + 0.5) / size;

    float lb = texture2DCompare(centroidUV + texelSize * vec2(0.0, 0.0), compare);
    float lt = texture2DCompare(centroidUV + texelSize * vec2(0.0, 1.0), compare);
    float rb = texture2DCompare(centroidUV + texelSize * vec2(1.0, 0.0), compare);
    float rt = texture2DCompare(centroidUV + texelSize * vec2(1.0, 1.0), compare);
    float a = mix(lb, lt, f.y);
    float b = mix(rb, rt, f.y);
    float c = mix(a, b, f.x);
    return c;
}

float PCF(vec2 uv, float compare) {
    float result = 0.0;
    // for (int x = -1; x <= 1; x++){
        // for(int y = -1; y <= 1; y++){
            // vec2 off = vec2(x, y) / shadowMapSize;
            // result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			
			vec2 off = vec2(-1, -1) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(-1, 0) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(-1, 1) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(0, -1) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(0, 0) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(0, 1) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(1, -1) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(1, 0) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
			off = vec2(1, 1) / shadowMapSize;
            result += texture2DShadowLerp(shadowMapSize, uv + off, compare);
        // }
    // }
    return result / 9.0;
}


#define _PCSS
#ifdef _PCSS
    // Based on ThreeJS PCSS example
    const float LIGHT_WORLD_SIZE = 0.45;
    const float LIGHT_FRUSTUM_WIDTH = 7.75;
    const float LIGHT_SIZE_UV = (LIGHT_WORLD_SIZE / LIGHT_FRUSTUM_WIDTH);
    const float NEAR_PLANE = 3.5;
    const int NUM_SAMPLES = 17;
    const int NUM_RINGS = 11;
    // vec2 poissonDisk[NUM_SAMPLES];
    vec2 poissonDisk0;
    vec2 poissonDisk1;
    vec2 poissonDisk2;
    vec2 poissonDisk3;
    vec2 poissonDisk4;
    vec2 poissonDisk5;
    vec2 poissonDisk6;
    vec2 poissonDisk7;
    vec2 poissonDisk8;
    vec2 poissonDisk9;
    vec2 poissonDisk10;
    vec2 poissonDisk11;
    vec2 poissonDisk12;
    vec2 poissonDisk13;
    vec2 poissonDisk14;
    vec2 poissonDisk15;
    vec2 poissonDisk16;

    float rand(vec2 co) {
        return fract(sin(dot(co.xy ,vec2(12.9898, 78.233))) * 43758.5453);
    }

    void initPoissonSamples(const in vec2 randomSeed) {
        const float ANGLE_STEP = TwoPI * float(NUM_RINGS) / float(NUM_SAMPLES);
        const float INV_NUM_SAMPLES = 1.0 / float(NUM_SAMPLES);

        float angle = rand(randomSeed) * TwoPI;
        float radius = INV_NUM_SAMPLES;
        float radiusStep = radius;

        // for (int i = 0; i < NUM_SAMPLES; i++) {
            poissonDisk0 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk1 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk2 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk3 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk4 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk5 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk6 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk7 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk8 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk9 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk10 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk11 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk12 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk13 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk14 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk15 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
            poissonDisk16 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
            radius += radiusStep; angle += ANGLE_STEP;
        // }
    }

    float penumbraSize(const in float zReceiver, const in float zBlocker) { // Parallel plane estimation
        return (zReceiver - zBlocker) / zBlocker;
    }

    float findBlocker(const in vec2 uv, const in float zReceiver) {
        // This uses similar triangles to compute what area of the shadow map we should search
        float searchRadius = LIGHT_SIZE_UV * (zReceiver - NEAR_PLANE) / zReceiver;
        float blockerDepthSum = 0.0;
        int numBlockers = 0;

        // for (int i = 0; i < NUM_SAMPLES; i++) {
            float shadowMapDepth = texture(shadowMap, uv + poissonDisk0 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk1 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk2 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk3 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk4 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk5 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk6 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk7 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk8 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk9 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk10 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk11 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk12 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk13 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk14 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk15 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
            shadowMapDepth = texture(shadowMap, uv + poissonDisk16 * searchRadius).r * 2.0 - 1.0;
            if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
        // }

        if (numBlockers == 0) return -1.0;
        return blockerDepthSum / float(numBlockers);
    }

    float PCF_Filter(vec2 uv, float zReceiver, float filterRadius) {
        float sum = 0.0;
        // for (int i = 0; i < NUM_SAMPLES; i++) {
            float depth = texture(shadowMap, uv + poissonDisk0 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk1 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk2 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk3 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk4 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk5 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk6 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk7 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk8 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk9 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk10 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk11 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk12 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk13 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk14 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk15 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + poissonDisk16 * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
        // }
        // for (int i = 0; i < NUM_SAMPLES; i++) {
            depth = texture(shadowMap, uv + -poissonDisk0.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk1.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk2.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk3.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk4.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk5.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk6.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk7.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk8.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk9.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk10.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk11.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk12.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk13.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk14.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk15.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
            depth = texture(shadowMap, uv + -poissonDisk16.yx * filterRadius).r * 2.0 - 1.0;
            if (zReceiver <= depth) sum += 1.0;
        // }
        return sum / (2.0 * float(NUM_SAMPLES));
    }

    float PCSS(vec2 uv, float zReceiver) {
        initPoissonSamples(uv);
        
        // Blocker search
        float avgBlockerDepth = findBlocker(uv, zReceiver);

        // There are no occluders so early out (this saves filtering)
        if (avgBlockerDepth == -1.0) return 1.0;

        // Penumbra size
        float penumbraRatio = penumbraSize(zReceiver, avgBlockerDepth);
        float filterRadius = penumbraRatio * LIGHT_SIZE_UV * NEAR_PLANE / zReceiver;

        // Filtering
        return PCF_Filter(uv, zReceiver, filterRadius);
    }
#endif



float shadowTest(vec4 lPos) {
	vec4 lPosH = lPos / lPos.w;
	lPosH.x = (lPosH.x + 1.0) / 2.0;
    lPosH.y = (lPosH.y + 1.0) / 2.0;
	
	const float bias = 0.001; // Persp
	// const float bias = 0.01; // Ortho
    
#ifdef _PCSS
    return PCSS(lPosH.xy, lPosH.z - bias);
#else
	// return PCF(lPosH.xy, lPosH.z - bias);
#endif
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec3 getPos(float depth) {	
    // vec4 pos = vec4(coord * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    // vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
    // pos = invVP * pos;
    // pos.xyz /= pos.w;
    // return pos.xyz;
	
	vec3 vray = normalize(viewRay);
	const float znear = 0.1;
	const float zfar = 1000.0;
	const float projectionA = zfar / (zfar - znear);
	const float projectionB = (-zfar * znear) / (zfar - znear);
	// float linearDepth = projectionB / (depth - projectionA);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}

vec2 unpackFloat(float f) {
	float index = floor(f) / 1000.0;
	float alpha = fract(f);
	return vec2(index, alpha);
}





// Linearly Transformed Cosines
// https://eheitzresearch.wordpress.com/415-2/
vec3 mul(mat3 m, vec3 v) {
    return m * v;
}
mat3 mul(mat3 m1, mat3 m2) {
    return m1 * m2;
}
mat3 transpose2(mat3 v) {
    mat3 tmp;
    tmp[0] = vec3(v[0].x, v[1].x, v[2].x);
    tmp[1] = vec3(v[0].y, v[1].y, v[2].y);
    tmp[2] = vec3(v[0].z, v[1].z, v[2].z);

    return tmp;
}
float IntegrateEdge(vec3 v1, vec3 v2) {
    float cosTheta = dot(v1, v2);
    cosTheta = clamp(cosTheta, -0.9999, 0.9999);
    float theta = acos(cosTheta);    
    float res = cross(v1, v2).z * theta / sin(theta);
    return res;
}
int ClipQuadToHorizon(/*inout vec3 L[5], out int n*/) {
    // detect clipping config
    int config = 0;
    if (L0.z > 0.0) config += 1;
    if (L1.z > 0.0) config += 2;
    if (L2.z > 0.0) config += 4;
    if (L3.z > 0.0) config += 8;

    // clip
    int n = 0;
    if (config == 0) {
        // clip all
    }
    else if (config == 1) { // V1 clip V2 V3 V4
        n = 3;
        L1 = -L1.z * L0 + L0.z * L1;
        L2 = -L3.z * L0 + L0.z * L3;
    }
    else if (config == 2) { // V2 clip V1 V3 V4
        n = 3;
        L0 = -L0.z * L1 + L1.z * L0;
        L2 = -L2.z * L1 + L1.z * L2;
    }
    else if (config == 3) { // V1 V2 clip V3 V4
        n = 4;
        L2 = -L2.z * L1 + L1.z * L2;
        L3 = -L3.z * L0 + L0.z * L3;
    }
    else if (config == 4) { // V3 clip V1 V2 V4
        n = 3;
        L0 = -L3.z * L2 + L2.z * L3;
        L1 = -L1.z * L2 + L2.z * L1;
    }
    else if (config == 5) { // V1 V3 clip V2 V4) impossible
        n = 0;
    }
    else if (config == 6) { // V2 V3 clip V1 V4
        n = 4;
        L0 = -L0.z * L1 + L1.z * L0;
        L3 = -L3.z * L2 + L2.z * L3;
    }
    else if (config == 7) { // V1 V2 V3 clip V4
        n = 5;
        L4 = -L3.z * L0 + L0.z * L3;
        L3 = -L3.z * L2 + L2.z * L3;
    }
    else if (config == 8) { // V4 clip V1 V2 V3
        n = 3;
        L0 = -L0.z * L3 + L3.z * L0;
        L1 = -L2.z * L3 + L3.z * L2;
        L2 =  L3;
    }
    else if (config == 9) { // V1 V4 clip V2 V3
        n = 4;
        L1 = -L1.z * L0 + L0.z * L1;
        L2 = -L2.z * L3 + L3.z * L2;
    }
    else if (config == 10) { // V2 V4 clip V1 V3) impossible
        n = 0;
    }
    else if (config == 11) { // V1 V2 V4 clip V3
        n = 5;
        L4 = L3;
        L3 = -L2.z * L3 + L3.z * L2;
        L2 = -L2.z * L1 + L1.z * L2;
    }
    else if (config == 12) { // V3 V4 clip V1 V2
        n = 4;
        L1 = -L1.z * L2 + L2.z * L1;
        L0 = -L0.z * L3 + L3.z * L0;
    }
    else if (config == 13) { // V1 V3 V4 clip V2
        n = 5;
        L4 = L3;
        L3 = L2;
        L2 = -L1.z * L2 + L2.z * L1;
        L1 = -L1.z * L0 + L0.z * L1;
    }
    else if (config == 14) { // V2 V3 V4 clip V1
        n = 5;
        L4 = -L0.z * L3 + L3.z * L0;
        L0 = -L0.z * L1 + L1.z * L0;
    }
    else if (config == 15) { // V1 V2 V3 V4
        n = 4;
    }
    
    if (n == 3)
        L3 = L0;
    if (n == 4)
        L4 = L0;
	return n;
}
vec3 LTC_Evaluate(vec3 N, vec3 V, vec3 P, mat3 Minv, vec3 points0, vec3 points1, vec3 points2, vec3 points3, bool twoSided) {
    // construct orthonormal basis around N
    vec3 T1, T2;
    T1 = normalize(V - N*dot(V, N));
    T2 = cross(N, T1);

    // rotate area light in (T1, T2, R) basis
    Minv = mul(Minv, transpose2(mat3(T1, T2, N)));

    // polygon (allocate 5 vertices for clipping)
    // vec3 L[5];
    L0 = mul(Minv, points0 - P);
    L1 = mul(Minv, points1 - P);
    L2 = mul(Minv, points2 - P);
    L3 = mul(Minv, points3 - P);

    int n = ClipQuadToHorizon(/*L, n*/);
    
    if (n == 0) {
        return vec3(0, 0, 0);
	}

    // project onto sphere
    L0 = normalize(L0);
    L1 = normalize(L1);
    L2 = normalize(L2);
    L3 = normalize(L3);
    L4 = normalize(L4);

    // integrate
    float sum = 0.0;

    sum += IntegrateEdge(L0, L1);
    sum += IntegrateEdge(L1, L2);
    sum += IntegrateEdge(L2, L3);
	
	if (n >= 4) {
        sum += IntegrateEdge(L3, L4);
	}
    if (n == 5) {
        sum += IntegrateEdge(L4, L0);
	}

    sum = twoSided ? abs(sum) : max(0.0, -sum);

    vec3 Lo_i = vec3(sum, sum, sum);

    return Lo_i;
}

#ifdef _Aniso
float wardSpecular(vec3 N, vec3 H, float dotNL, float dotNV, float dotNH, vec3 fiberDirection, float shinyParallel, float shinyPerpendicular) {
	if(dotNL < 0.0 || dotNV < 0.0) {
		return 0.0;
	}
	// fiberDirection - parse from rotation
	// shinyParallel - roughness
	// shinyPerpendicular - anisotropy
	
	vec3 fiberParallel = normalize(fiberDirection);
  	vec3 fiberPerpendicular = normalize(cross(N, fiberDirection));
	float dotXH = dot(fiberParallel, H);
	float dotYH = dot(fiberPerpendicular, H);
	float coeff = sqrt(dotNL/dotNV) / (4.0 * PI * shinyParallel * shinyPerpendicular); 
	float theta = (pow(dotXH/shinyParallel, 2.0) + pow(dotYH/shinyPerpendicular, 2.0)) / (1.0 + dotNH);
	return clamp(coeff * exp(-2.0 * theta), 0.0, 1.0);
}
#endif

void main() {
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// float depth = 1.0 - g0.a;
	// if (depth == 0.0) discard;
	if (depth == 1.0) discard;
	
	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, occlusion, mask
	vec4 g1 = texture(gbuffer1, texCoord); // Base color.rgb, roughn/met
	float ao = texture(ssaotex, texCoord).r;

	vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);

	vec3 p = getPos(depth);
	vec3 baseColor = g1.rgb;
	vec2 roughmet = unpackFloat(g1.a);
	float roughness = roughmet.x;
	float metalness = roughmet.y;
	
    vec3 lightDir = light - p.xyz;
    vec3 eyeDir = eye - p.xyz;
	vec3 l = normalize(lightDir);
	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);

	float dotNL = max(dot(n, l), 0.0);
	float dotNV = max(dot(n, v), 0.0);
	float dotNH = max(dot(n, h), 0.0);
	float dotVH = max(dot(v, h), 0.0);
	float dotLV = max(dot(l, v), 0.0);
	float dotLH = max(dot(l, h), 0.0);
	
	vec3 albedo = surfaceAlbedo(baseColor, metalness);
	vec3 f0 = surfaceF0(baseColor, metalness);
	
	vec4 lPos = LMVP * vec4(vec3(p), 1.0);
	float visibility = 1.0;
	if (lPos.w > 0.0) {
		visibility = shadowTest(lPos);
		// visibility = 1.0;
	}
	
    
	// Direct
	vec3 direct = diffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH, dotLV) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH, dotLH);
    // Aniso spec
    // float shinyParallel = roughness;
    // float shinyPerpendicular = 0.08;
    // vec3 fiberDirection = vec3(0.0, 1.0, 8.0);
	// vec3 direct = diffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH, dotLV) + wardSpecular(n, h, dotNL, dotNV, dotNH, fiberDirection, shinyParallel, shinyPerpendicular);
	direct = direct * lightColor * lightStrength;
	
	// SSS only masked objects
// #ifdef _SSS
    float mask = g0.a;
	if (mask == 2.0) {
		direct.rgb = direct.rgb * SSSSTransmittance(1.0, 0.005, p, n, lightDir);
	}
// #endif


	// Indirect
#ifdef _Probe1
    float probeFactor = mask;
    float probeID = floor(probeFactor);
    float probeFract = fract(probeFactor);
    
    vec3 indirectDiffuse;
    vec3 prefilteredColor;
    vec2 envCoord = envMapEquirect(n);
    
    float lod = getMipLevelFromRoughness(roughness);
    vec3 reflectionWorld = reflect(-v, n); 
    vec2 envCoordRefl = envMapEquirect(reflectionWorld);
    
    // Global probe only
    if (probeID == 0.0) {
        indirectDiffuse = texture(senvmapIrradiance, envCoord).rgb;
        prefilteredColor = textureLod(senvmapRadiance, envCoordRefl, lod).rgb;
    }
    // fract 0 = local probe, 1 = global probe 
    else if (probeID == 1.0) {
        indirectDiffuse = texture(senvmapIrradiance_1, envCoord).rgb * (1.0 - probeFract);
        prefilteredColor = textureLod(senvmapRadiance_1, envCoordRefl, lod).rgb * (1.0 - probeFract);
        if (probeFract > 0.0) {
            indirectDiffuse += texture(senvmapIrradiance, envCoord).rgb * (probeFract);
            prefilteredColor += textureLod(senvmapRadiance, envCoordRefl, lod).rgb * (probeFract);
        }
    }
#ifdef _Probe2
    else if (probeID == 2.0) {
        indirectDiffuse = texture(senvmapIrradiance_2, envCoord).rgb * (1.0 - probeFract);
        prefilteredColor = textureLod(senvmapRadiance_2, envCoordRefl, lod).rgb * (1.0 - probeFract);
        if (probeFract > 0.0) {
            indirectDiffuse += texture(senvmapIrradiance, envCoord).rgb * (probeFract);
            prefilteredColor += textureLod(senvmapRadiance, envCoordRefl, lod).rgb * (probeFract);
        }
    }
#endif
#ifdef _Probe3
    else if (probeID == 3.0) {
        indirectDiffuse = texture(senvmapIrradiance_3, envCoord).rgb * (1.0 - probeFract);
        prefilteredColor = textureLod(senvmapRadiance_3, envCoordRefl, lod).rgb * (1.0 - probeFract);
        if (probeFract > 0.0) {
            indirectDiffuse += texture(senvmapIrradiance, envCoord).rgb * (probeFract);
            prefilteredColor += textureLod(senvmapRadiance, envCoordRefl, lod).rgb * (probeFract);
        }
    }
#endif
#ifdef _Probe4
    else if (probeID == 4.0) {
        indirectDiffuse = texture(senvmapIrradiance_4, envCoord).rgb * (1.0 - probeFract);
        prefilteredColor = textureLod(senvmapRadiance_4, envCoordRefl, lod).rgb * (1.0 - probeFract);
        if (probeFract > 0.0) {
            indirectDiffuse += texture(senvmapIrradiance, envCoord).rgb * (probeFract);
            prefilteredColor += textureLod(senvmapRadiance, envCoordRefl, lod).rgb * (probeFract);
        }
    }
#endif
#else // No probes   
	vec3 indirectDiffuse = texture(senvmapIrradiance, envMapEquirect(n)).rgb;
    
    vec3 reflectionWorld = reflect(-v, n); 
	float lod = getMipLevelFromRoughness(roughness);
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
#endif


#ifdef _LDR
	indirectDiffuse = pow(indirectDiffuse, vec3(2.2));
    prefilteredColor = pow(prefilteredColor, vec3(2.2));
#endif
    indirectDiffuse = pow(indirectDiffuse, vec3(1.0/2.2));////
    prefilteredColor = pow(prefilteredColor, vec3(1.0/2.2));////
	indirectDiffuse *= albedo;
	
	
	vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
	vec3 indirectSpecular = prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
	vec3 indirect = indirectDiffuse + indirectSpecular;
	indirect = indirect * lightColor * lightStrength * envmapStrength;
	float occlusion = g0.b;
    
    vec4 outColor = vec4(vec3(direct * visibility + indirect * ao * occlusion), 1.0);



    // Path-traced
    // vec4 nois = texture(giblur, texCoord);
    // nois.rgb = pow(nois.rgb, vec3(1.0 / 2.2));
    // indirect = nois.rgb;
    // vec4 outColor = vec4(vec3(direct * visibility + indirect * 3.0 * ao * occlusion), 1.0);
	
	
	// LTC
	// float sinval = (sin(time) * 0.5 + 0.5);
	// vec4 outColor = vec4(1.0);
	// float rectSizeX = 4.000 + sin(time) * 4.0;
	// float rectSizeY = 1.2;// + sin(time * 2.0);
	// vec3 ex = vec3(1, 0, 0)*rectSizeX;
	// vec3 ey = vec3(0, 0, 1)*rectSizeY;
	// vec3 p1 = light - ex + ey;
	// vec3 p2 = light + ex + ey;
	// vec3 p3 = light + ex - ey;
	// vec3 p4 = light - ex - ey;
	// float theta = acos(dotNV);
	// vec2 tuv = vec2(roughness, theta/(0.5*PI));
	// tuv = tuv*LUT_SCALE + LUT_BIAS;

	// vec4 t = texture(sltcMat, tuv);		
	// mat3 Minv = mat3(
	// 	vec3(  1, t.y, 0),
	// 	vec3(  0, 0,   t.z),
	// 	vec3(t.w, 0,   t.x)
	// );
	
	// vec3 ltcspec = LTC_Evaluate(n, v, p, Minv, p1, p2, p3, p4, true); 
	
	// ltcspec *= vec3(1.0, 1.0 - sinval, 1.0 - sinval);
	
	// ltcspec *= texture(sltcMag, tuv).a;
	// vec3 ltcdiff = LTC_Evaluate(n, v, p, mat3(1), p1, p2, p3, p4, true);
	
	// ltcdiff *= vec3(1.0, 1.0 - sinval, 1.0 - sinval);
	
	// vec3 ltccol = ltcspec + ltcdiff * albedo;
	// ltccol /= 2.0*PI;
	// outColor.rgb = ltccol * 5.0 * visibility + (indirect / 14.0 * ao * (rectSizeX / 6.0) );
	// // outColor.rgb = ltccol * visibility + (indirect / 2.0 * ao);
	
	
	
	// outColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
	gl_FragColor = vec4(outColor.rgb, outColor.a);
}
