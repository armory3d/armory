#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

// #ifdef _Probes
	// uniform float shirr[27 * 20]; // Maximum of 20 SH sets
// #else
	// uniform float shirr[27];
// #endif
// uniform float envmapStrength;
// #ifdef _Rad
	// uniform sampler2D senvmapRadiance;
	// uniform sampler2D senvmapBrdf;
	// uniform int envmapNumMipmaps;
// #endif

// uniform sampler2D giblur; // Path-traced

// #ifdef _SSAO
	// uniform sampler2D ssaotex;
// #endif
#ifndef _NoShadows
	uniform sampler2D shadowMap;
	#ifdef _PCSS
	uniform sampler2D snoise;
	uniform float lampSizeUV; // 0.55
	uniform float lampNear; // 0.5
	#endif
#endif

#ifdef _VoxelGI
	uniform sampler2D ssaotex;
	uniform sampler2D senvmapBrdf;
	uniform sampler3D voxels;
	const float voxelGridWorldSize = 150.0;
	const int voxelDimensions = 512;
	const float maxDist = 30.0;
	const float alphaTreshold = 0.95;
	const int numCones = 6;
	vec3 coneDirections[6] = vec3[](
		vec3(0, 1, 0),
		vec3(0, 0.5, 0.866025),
		vec3(0.823639, 0.5, 0.267617),
		vec3(0.509037, 0.5, -0.700629),
		vec3(-0.509037, 0.5, -0.700629),
		vec3(-0.823639, 0.5, 0.267617));
	float coneWeights[6] = float[](0.25, 0.15, 0.15, 0.15, 0.15, 0.15);
#endif

// #ifdef _LTC
	// uniform sampler2D sltcMat;
	// uniform sampler2D sltcMag;
	// uniform float time;
	// const float roughness = 0.25;
	// const vec3 dcolor = vec3(1.0, 1.0, 1.0);
	// const vec3 scolor = vec3(1.0, 1.0, 1.0);
	// const float intensity = 4.0; // 0-10
	// const float width = 4.0;
	// const float height = 4.0;
	// const int sampleCount = 0;
	// const int NUM_SAMPLES = 8;
	// const float LUT_SIZE  = 64.0;
	// const float LUT_SCALE = (LUT_SIZE - 1.0)/LUT_SIZE;
	// const float LUT_BIAS  = 0.5/LUT_SIZE;
	// vec2 mys[NUM_SAMPLES];		
	// vec3 L0 = vec3(0.0);
	// vec3 L1 = vec3(0.0);
	// vec3 L2 = vec3(0.0);
	// vec3 L3 = vec3(0.0);
	// vec3 L4 = vec3(0.0);
// #endif

uniform mat4 invVP;
uniform mat4 LWVP;
uniform vec3 lightPos;
uniform vec3 lightDir;
uniform int lightType;
// uniform int lightIndex;
uniform vec3 lightColor;
uniform float lightStrength;
uniform float shadowsBias;
uniform float spotlightCutoff;
uniform float spotlightExponent;
uniform vec3 eye;
// uniform vec3 eyeLook;
// uniform vec2 screenSize;

// in vec2 texCoord;
in vec4 wvpposition;
// in vec3 viewRay;
out vec4 fragColor;

// Separable SSS Transmittance Function, ref to sss_pass
#ifdef _SSS
vec3 SSSSTransmittance(float translucency, float sssWidth, vec3 worldPosition, vec3 worldNormal, vec3 lightDir) {
	float scale = 8.25 * (1.0 - translucency) / sssWidth;
	vec4 shrinkedPos = vec4(worldPosition - 0.005 * worldNormal, 1.0);
	vec4 shadowPosition = LWVP * shrinkedPos;
	float d1 = texture(shadowMap, shadowPosition.xy / shadowPosition.w).r; // 'd1' has a range of 0..1
	float d2 = shadowPosition.z; // 'd2' has a range of 0..'lightFarPlane'
	const float lightFarPlane = 120 / 3.5;
	d1 *= lightFarPlane; // So we scale 'd1' accordingly:
	float d = scale * abs(d1 - d2);

	float dd = -d * d;
	vec3 profile = vec3(0.233, 0.455, 0.649) * exp(dd / 0.0064) +
				   vec3(0.1,   0.336, 0.344) * exp(dd / 0.0484) +
				   vec3(0.118, 0.198, 0.0)   * exp(dd / 0.187) +
				   vec3(0.113, 0.007, 0.007) * exp(dd / 0.567) +
				   vec3(0.358, 0.004, 0.0)   * exp(dd / 1.99) +
				   vec3(0.078, 0.0,   0.0)   * exp(dd / 7.41);
	return profile * clamp(0.3 + dot(lightDir, -worldNormal), 0.0, 1.0);
}
#endif

// #ifdef _Rad
// float getMipLevelFromRoughness(float roughness) {
// 	// First mipmap level = roughness 0, last = roughness = 1
// 	// baseColor texture already counted
// 	return roughness * envmapNumMipmaps;
// }
// #endif

vec3 surfaceAlbedo(vec3 baseColor, float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(vec3 baseColor, float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
}

vec3 f_schlick(vec3 f0, float vh) {
	return f0 + (1.0 - f0) * exp2((-5.55473 * vh - 6.98316) * vh);
}

float v_smithschlick(float nl, float nv, float a) {
	return 1.0 / ((nl * (1.0 - a) + a) * (nv * (1.0 - a) + a) );
}

float d_ggx(float nh, float a) {
	float a2 = a * a;
	float denom = pow(nh * nh * (a2 - 1.0) + 1.0, 2.0);
	return a2 * (1.0 / 3.1415926535) / denom;
}

vec3 specularBRDF(vec3 f0, float roughness, float nl, float nh, float nv, float vh) {
	float a = roughness * roughness;
	return d_ggx(nh, a) * clamp(v_smithschlick(nl, nv, a), 0.0, 1.0) * f_schlick(f0, vh) / 4.0;
}
// Gotanda 2012, Beyond a Simple Physically Based Blinn-Phong Model in Real-Time
// http://research.tri-ace.com/Data/s2012_beyond_CourseNotes.pdf
vec3 orenNayarDiffuseBRDF(vec3 albedo, float roughness, float nv, float nl, float vh) {
	float a = roughness * roughness;
	float s = a;
	float s2 = s * s;
	float vl = 2.0 * vh * vh - 1.0;	// Double angle identity
	float Cosri = vl - nv * nl;
	float C1 = 1.0 - 0.5 * s2 / (s2 + 0.33);
	float test = 1.0;
	if (Cosri >= 0.0) test = (1.0 / (max(nl, nv)));
	float C2 = 0.45 * s2 / (s2 + 0.09) * Cosri * test;
	return albedo * max(0.0, nl) * (C1 + C2) * (1.0 + roughness * 0.5);
}
vec3 lambertDiffuseBRDF(vec3 albedo, float nl) {
	return albedo * max(0.0, nl);
}

#ifndef _NoShadows
#ifndef _PCSS
float texture2DCompare(vec2 uv, float compare){
	float depth = texture(shadowMap, uv).r;// * 2.0 - 1.0; // - mult compare instead
	return step(compare, depth);
}
float texture2DShadowLerp(vec2 uv, float compare){
	const vec2 texelSize = vec2(1.0) / shadowmapSize;
	vec2 f = fract(uv * shadowmapSize + 0.5);
	vec2 centroidUV = floor(uv * shadowmapSize + 0.5) / shadowmapSize;
	float lb = texture2DCompare(centroidUV, compare);
	float lt = texture2DCompare(centroidUV + texelSize * vec2(0.0, 1.0), compare);
	float rb = texture2DCompare(centroidUV + texelSize * vec2(1.0, 0.0), compare);
	float rt = texture2DCompare(centroidUV + texelSize, compare);
	float a = mix(lb, lt, f.y);
	float b = mix(rb, rt, f.y);
	float c = mix(a, b, f.x);
	return c;
}
float PCF(vec2 uv, float compare) {
	// float result = 0.0;
	// for (int x = -1; x <= 1; x++){
		// for(int y = -1; y <= 1; y++){
			// vec2 off = vec2(x, y) / shadowmapSize;
			// result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			compare = compare * 0.5 + 0.5;
			float result = texture2DShadowLerp(uv + (vec2(-1.0, -1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(-1.0, 0.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(-1.0, 1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(0.0, -1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv, compare);
			result += texture2DShadowLerp(uv + (vec2(0.0, 1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(1.0, -1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(1.0, 0.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(1.0, 1.0) / shadowmapSize), compare);
		// }
	// }
	return result / 9.0;
}
#else // _PCSS
	// Based on ThreeJS and nvidia pcss
	// const int pcssRings = 11;
	const int NUM_SAMPLES = 17;
	const float radiusStep = 1.0 / float(NUM_SAMPLES);
	const float angleStep = PI2 * float(pcssRings) / float(NUM_SAMPLES);
	vec2 poissonDisk0; vec2 poissonDisk1; vec2 poissonDisk2;
	vec2 poissonDisk3; vec2 poissonDisk4; vec2 poissonDisk5;
	vec2 poissonDisk6; vec2 poissonDisk7; vec2 poissonDisk8;
	vec2 poissonDisk9; vec2 poissonDisk10; vec2 poissonDisk11;
	vec2 poissonDisk12; vec2 poissonDisk13; vec2 poissonDisk14;
	vec2 poissonDisk15; vec2 poissonDisk16;
	void initPoissonSamples(const in vec2 randomSeed) {
		float angle = texture(snoise, randomSeed).r * PI2;
		float radius = radiusStep;
		// for (int i = 0; i < NUM_SAMPLES; i++) {
			poissonDisk0 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk1 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk2 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk3 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk4 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk5 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk6 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk7 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk8 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk9 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk10 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk11 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk12 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk13 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk14 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk15 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
			poissonDisk16 = vec2(cos(angle), sin(angle)) * pow(radius, 0.75);
			radius += radiusStep; angle += angleStep;
		// }
	}
	float findBlocker(const in vec2 uv, const in float zReceiver) {
		// This uses similar triangles to compute what area of the shadow map we should search
		float searchRadius = lampSizeUV * (zReceiver - lampNear) / zReceiver;
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
	float filterPCF(vec2 uv, float zReceiver, float filterRadius) {
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
		float avgBlockerDepth = findBlocker(uv, zReceiver);
		if (avgBlockerDepth == -1.0) return 1.0;
		float penumbraRatio = (zReceiver - avgBlockerDepth) / avgBlockerDepth;
		float filterRadius = penumbraRatio * lampSizeUV * lampNear / zReceiver;
		return filterPCF(uv, zReceiver, filterRadius);
	}
#endif
float shadowTest(vec4 lPos) {
	lPos.xyz /= lPos.w;
	lPos.xy = lPos.xy * 0.5 + 0.5;
	#ifdef _PCSS
	return PCSS(lPos.xy, lPos.z - shadowsBias);
	#else
	return PCF(lPos.xy, lPos.z - shadowsBias);
	#endif
}
#endif

// vec2 envMapEquirect(vec3 normal) {
// 	float phi = acos(normal.z);
// 	float theta = atan(-normal.y, normal.x) + PI;
// 	return vec2(theta / PI2, phi / PI);
// }

vec2 octahedronWrap(vec2 v) {
	return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

// vec3 getPos(float depth) {
// 	vec3 vray = normalize(viewRay);
// 	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
// 	const float projectionB = (-cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
// 	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
// 	float viewZDist = dot(eyeLook, vray);
// 	vec3 wposition = eye + vray * (linearDepth / viewZDist);
// 	return wposition;
// }
vec3 getPos(float depth, vec2 coord) {
    vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
    pos = invVP * pos;
    pos.xyz /= pos.w;
    return pos.xyz;// - eye;
}

vec2 unpackFloat(float f) {
	return vec2(floor(f) / 1000.0, fract(f));
}

// Linearly Transformed Cosines
// https://eheitzresearch.wordpress.com/415-2/
// vec3 mul(mat3 m, vec3 v) {
// 	return m * v;
// }
// mat3 mul(mat3 m1, mat3 m2) {
// 	return m1 * m2;
// }
// mat3 transpose2(mat3 v) {
// 	mat3 tmp;
// 	tmp[0] = vec3(v[0].x, v[1].x, v[2].x);
// 	tmp[1] = vec3(v[0].y, v[1].y, v[2].y);
// 	tmp[2] = vec3(v[0].z, v[1].z, v[2].z);

// 	return tmp;
// }
// float IntegrateEdge(vec3 v1, vec3 v2) {
// 	float cosTheta = dot(v1, v2);
// 	cosTheta = clamp(cosTheta, -0.9999, 0.9999);
// 	float theta = acos(cosTheta);    
// 	float res = cross(v1, v2).z * theta / sin(theta);
// 	return res;
// }
// int ClipQuadToHorizon(/*inout vec3 L[5], out int n*/) {
// 	// detect clipping config
// 	int config = 0;
// 	if (L0.z > 0.0) config += 1;
// 	if (L1.z > 0.0) config += 2;
// 	if (L2.z > 0.0) config += 4;
// 	if (L3.z > 0.0) config += 8;

// 	// clip
// 	int n = 0;
// 	if (config == 0) {
// 		// clip all
// 	}
// 	else if (config == 1) { // V1 clip V2 V3 V4
// 		n = 3;
// 		L1 = -L1.z * L0 + L0.z * L1;
// 		L2 = -L3.z * L0 + L0.z * L3;
// 	}
// 	else if (config == 2) { // V2 clip V1 V3 V4
// 		n = 3;
// 		L0 = -L0.z * L1 + L1.z * L0;
// 		L2 = -L2.z * L1 + L1.z * L2;
// 	}
// 	else if (config == 3) { // V1 V2 clip V3 V4
// 		n = 4;
// 		L2 = -L2.z * L1 + L1.z * L2;
// 		L3 = -L3.z * L0 + L0.z * L3;
// 	}
// 	else if (config == 4) { // V3 clip V1 V2 V4
// 		n = 3;
// 		L0 = -L3.z * L2 + L2.z * L3;
// 		L1 = -L1.z * L2 + L2.z * L1;
// 	}
// 	else if (config == 5) { // V1 V3 clip V2 V4) impossible
// 		n = 0;
// 	}
// 	else if (config == 6) { // V2 V3 clip V1 V4
// 		n = 4;
// 		L0 = -L0.z * L1 + L1.z * L0;
// 		L3 = -L3.z * L2 + L2.z * L3;
// 	}
// 	else if (config == 7) { // V1 V2 V3 clip V4
// 		n = 5;
// 		L4 = -L3.z * L0 + L0.z * L3;
// 		L3 = -L3.z * L2 + L2.z * L3;
// 	}
// 	else if (config == 8) { // V4 clip V1 V2 V3
// 		n = 3;
// 		L0 = -L0.z * L3 + L3.z * L0;
// 		L1 = -L2.z * L3 + L3.z * L2;
// 		L2 =  L3;
// 	}
// 	else if (config == 9) { // V1 V4 clip V2 V3
// 		n = 4;
// 		L1 = -L1.z * L0 + L0.z * L1;
// 		L2 = -L2.z * L3 + L3.z * L2;
// 	}
// 	else if (config == 10) { // V2 V4 clip V1 V3) impossible
// 		n = 0;
// 	}
// 	else if (config == 11) { // V1 V2 V4 clip V3
// 		n = 5;
// 		L4 = L3;
// 		L3 = -L2.z * L3 + L3.z * L2;
// 		L2 = -L2.z * L1 + L1.z * L2;
// 	}
// 	else if (config == 12) { // V3 V4 clip V1 V2
// 		n = 4;
// 		L1 = -L1.z * L2 + L2.z * L1;
// 		L0 = -L0.z * L3 + L3.z * L0;
// 	}
// 	else if (config == 13) { // V1 V3 V4 clip V2
// 		n = 5;
// 		L4 = L3;
// 		L3 = L2;
// 		L2 = -L1.z * L2 + L2.z * L1;
// 		L1 = -L1.z * L0 + L0.z * L1;
// 	}
// 	else if (config == 14) { // V2 V3 V4 clip V1
// 		n = 5;
// 		L4 = -L0.z * L3 + L3.z * L0;
// 		L0 = -L0.z * L1 + L1.z * L0;
// 	}
// 	else if (config == 15) { // V1 V2 V3 V4
// 		n = 4;
// 	}
	
// 	if (n == 3)
// 		L3 = L0;
// 	if (n == 4)
// 		L4 = L0;
// 	return n;
// }
// vec3 LTC_Evaluate(vec3 N, vec3 V, vec3 P, mat3 Minv, vec3 points0, vec3 points1, vec3 points2, vec3 points3, bool twoSided) {
// 	// construct orthonormal basis around N
// 	vec3 T1, T2;
// 	T1 = normalize(V - N*dot(V, N));
// 	T2 = cross(N, T1);

// 	// rotate area light in (T1, T2, R) basis
// 	Minv = mul(Minv, transpose2(mat3(T1, T2, N)));

// 	// polygon (allocate 5 vertices for clipping)
// 	// vec3 L[5];
// 	L0 = mul(Minv, points0 - P);
// 	L1 = mul(Minv, points1 - P);
// 	L2 = mul(Minv, points2 - P);
// 	L3 = mul(Minv, points3 - P);

// 	int n = ClipQuadToHorizon(/*L, n*/);
	
// 	if (n == 0) {
// 		return vec3(0, 0, 0);
// 	}

// 	// project onto sphere
// 	L0 = normalize(L0);
// 	L1 = normalize(L1);
// 	L2 = normalize(L2);
// 	L3 = normalize(L3);
// 	L4 = normalize(L4);

// 	// integrate
// 	float sum = 0.0;

// 	sum += IntegrateEdge(L0, L1);
// 	sum += IntegrateEdge(L1, L2);
// 	sum += IntegrateEdge(L2, L3);
	
// 	if (n >= 4) {
// 		sum += IntegrateEdge(L3, L4);
// 	}
// 	if (n == 5) {
// 		sum += IntegrateEdge(L4, L0);
// 	}

// 	sum = twoSided ? abs(sum) : max(0.0, -sum);

// 	vec3 Lo_i = vec3(sum, sum, sum);

// 	return Lo_i;
// }

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

// #ifdef _Probes
// vec3 shIrradiance(vec3 nor, float scale, int probe) {
// #else
// vec3 shIrradiance(vec3 nor, float scale) {
// #endif
// 	const float c1 = 0.429043;
// 	const float c2 = 0.511664;
// 	const float c3 = 0.743125;
// 	const float c4 = 0.886227;
// 	const float c5 = 0.247708;
// 	vec3 cl00, cl1m1, cl10, cl11, cl2m2, cl2m1, cl20, cl21, cl22;
// #ifdef _Probes
// 	if (probe == 0) {
// #endif
// 		cl00 = vec3(shirr[0], shirr[1], shirr[2]);
// 		cl1m1 = vec3(shirr[3], shirr[4], shirr[5]);
// 		cl10 = vec3(shirr[6], shirr[7], shirr[8]);
// 		cl11 = vec3(shirr[9], shirr[10], shirr[11]);
// 		cl2m2 = vec3(shirr[12], shirr[13], shirr[14]);
// 		cl2m1 = vec3(shirr[15], shirr[16], shirr[17]);
// 		cl20 = vec3(shirr[18], shirr[19], shirr[20]);
// 		cl21 = vec3(shirr[21], shirr[22], shirr[23]);
// 		cl22 = vec3(shirr[24], shirr[25], shirr[26]);
// #ifdef _Probes
// 	}
// 	else if (probe == 1) {
// 		cl00 = vec3(shirr[27 + 0], shirr[27 + 1], shirr[27 + 2]);
// 		cl1m1 = vec3(shirr[27 + 3], shirr[27 + 4], shirr[27 + 5]);
// 		cl10 = vec3(shirr[27 + 6], shirr[27 + 7], shirr[27 + 8]);
// 		cl11 = vec3(shirr[27 + 9], shirr[27 + 10], shirr[27 + 11]);
// 		cl2m2 = vec3(shirr[27 + 12], shirr[27 + 13], shirr[27 + 14]);
// 		cl2m1 = vec3(shirr[27 + 15], shirr[27 + 16], shirr[27 + 17]);
// 		cl20 = vec3(shirr[27 + 18], shirr[27 + 19], shirr[27 + 20]);
// 		cl21 = vec3(shirr[27 + 21], shirr[27 + 22], shirr[27 + 23]);
// 		cl22 = vec3(shirr[27 + 24], shirr[27 + 25], shirr[27 + 26]);
// 	}
// #endif
// 	return (
// 		c1 * cl22 * (nor.y * nor.y - (-nor.z) * (-nor.z)) +
//		c3 * cl20 * nor.x * nor.x +
//		c4 * cl00 -
//		c5 * cl20 +
//		2.0 * c1 * cl2m2 * nor.y * (-nor.z) +
//		2.0 * c1 * cl21  * nor.y * nor.x +
//		2.0 * c1 * cl2m1 * (-nor.z) * nor.x +
//		2.0 * c2 * cl11  * nor.y +
//		2.0 * c2 * cl1m1 * (-nor.z) +
//		2.0 * c2 * cl10  * nor.x
// 	) * scale;
// }

#ifdef _VoxelGI
vec4 sampleVoxels(vec3 worldPosition, float lod) {
	vec3 offset = vec3(1.0 / voxelDimensions, 1.0 / voxelDimensions, 0);
	vec3 texco = worldPosition / (voxelGridWorldSize * 0.5);
	texco = texco * 0.5 + 0.5 + offset;
	return textureLod(voxels, texco, lod);
}
vec4 coneTrace(vec3 posWorld, vec3 direction, vec3 norWorld, float tanHalfAngle, out float occlusion) {
	const float voxelWorldSize = voxelGridWorldSize / voxelDimensions;
	float dist = voxelWorldSize; // Start one voxel away to avoid self occlusion
	vec3 startPos = posWorld + norWorld * voxelWorldSize;

	vec3 color = vec3(0.0);
	float alpha = 0.0;
	occlusion = 0.0;
	while (dist < maxDist && alpha < alphaTreshold) {
		// Smallest sample diameter possible is the voxel size
		float diameter = max(voxelWorldSize, 2.0 * tanHalfAngle * dist);
		float lodLevel = log2(diameter / voxelWorldSize);
		vec4 voxelColor = sampleVoxels(startPos + dist * direction, lodLevel);
		// Front-to-back compositing
		float a = (1.0 - alpha);
		color += a * voxelColor.rgb;
		alpha += a * voxelColor.a;
		occlusion += (a * voxelColor.a) / (1.0 + 0.03 * diameter);
		dist += diameter * 0.5; // * 2.0
	}
	return vec4(color, alpha);
}
vec4 indirectLight(vec3 posWorld, mat3 tanToWorld, vec3 norWorld, out float occlusion) {
	vec4 color = vec4(0);
	occlusion = 0.0;

	for (int i = 0; i < numCones; i++) {
		float coneOcclusion;
		const float tanangle = tan(30):
		color += coneWeights[i] * coneTrace(posWorld, tanToWorld * coneDirections[i], norWorld, tanangle, coneOcclusion);
		occlusion += coneWeights[i] * coneOcclusion;
	}
	occlusion = 1.0 - occlusion;
	return color;
}
#endif

void main() {
	vec2 screenPosition = wvpposition.xy / wvpposition.w;
	vec2 texCoord = screenPosition * 0.5 + 0.5;
	// texCoord += vec2(0.5 / screenSize); // Half pixel offset

	// 0 - 1 => -1 - 1
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, mask
	vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, occlusion

	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	vec3 p = getPos(depth, texCoord);
	// vec3 p = getPos(depth);
	vec2 metrough = unpackFloat(g0.b);
	
	vec3 v = normalize(eye - p.xyz);
	float dotNV = dot(n, v);
	
	vec3 albedo = surfaceAlbedo(g1.rgb, metrough.x); // g1.rgb - basecolor
	vec3 f0 = surfaceF0(g1.rgb, metrough.x);
	
	// Per-light
	vec3 l;
	if (lightType == 0) { // Sun
		l = lightDir;
	}
	else { // Point, spot
		l = normalize(lightPos - p.xyz);
	}
	
	vec3 h = normalize(v + l);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);
	float dotNL = dot(n, l);
	// float dotLV = dot(l, v);
	// float dotLH = dot(l, h);
	
	float visibility = 1.0;
#ifndef _NoShadows
	vec4 lampPos = LWVP * vec4(p, 1.0);
	if (lampPos.w > 0.0) {
		visibility = shadowTest(lampPos);
	}
#endif
	
	// Direct
#ifdef _OrenNayar
	vec3 direct = orenNayarDiffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#else
	vec3 direct = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#endif

	if (lightType == 2) { // Spot
		float spotEffect = dot(lightDir, l);
		if (spotEffect < spotlightCutoff) {
			float spotEffect = smoothstep(spotlightCutoff - spotlightExponent, spotlightCutoff, spotEffect);
			direct *= spotEffect;
		}
	}
	
	// Aniso spec
	// float shinyParallel = metrough.y;
	// float shinyPerpendicular = 0.08;
	// vec3 fiberDirection = vec3(0.0, 1.0, 8.0);
	// vec3 direct = diffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH, dotLV) + wardSpecular(n, h, dotNL, dotNV, dotNH, fiberDirection, shinyParallel, shinyPerpendicular);
	direct = direct * lightColor * lightStrength;
	
	
#ifdef _SSS
	float mask = g0.a;
	if (mask == 2.0) {
		direct *= SSSSTransmittance(1.0, 0.005, p, n, l);
	}
#endif

	// Direct
	fragColor = vec4(vec3(direct * visibility), 1.0);

	// Voxels test..
#ifdef _VoxelGI
	vec4 g1a = texture(gbuffer1, texCoord); // Basecolor.rgb, occlusion
	vec3 albedoa = surfaceAlbedo(g1a.rgb, metrough.x); // g1a.rgb - basecolor

	vec3 tangent = normalize(cross(n, vec3(0.0, 1.0, 0.0)));
	if (length(tangent) == 0.0) {
		tangent = normalize(cross(n, vec3(0.0, 0.0, 1.0)));
	}
	vec3 bitangent = normalize(cross(n, tangent));
	mat3 tanToWorld = inverse(transpose(mat3(tangent, bitangent, n)));

	float diffOcclusion = 0.0;
	vec3 indirectDiffusea = indirectLight(p, tanToWorld, n, diffOcclusion).rgb * 4.0;
	indirectDiffusea *= albedoa;
	diffOcclusion = min(1.0, 1.5 * diffOcclusion);

	vec3 reflectWorld = reflect(-v, n);
	float specularOcclusion;
	float lodOffset = 0.0;//getMipLevelFromRoughness(roughness);
	vec3 indirectSpecular = coneTrace(p, reflectWorld, n, 0.07 + lodOffset, specularOcclusion).rgb;

	if (metrough.y > 0.0) { // Temp..
		float dotNVa = max(dot(n, v), 0.0);
		vec3 f0a = surfaceF0(g1a.rgb, metrough.x);
		vec2 envBRDFa = texture(senvmapBrdf, vec2(metrough.y, 1.0 - dotNVa)).xy;
		indirectSpecular *= (f0a * envBRDFa.x + envBRDFa.y);
	}

	vec3 indirect1 = indirectDiffusea * diffOcclusion + indirectSpecular;
	indirect1 *= texture(ssaotex, texCoord).r;
	fragColor.rgb += indirect1;
#endif

	
	// LTC
	// float sinval = (sin(time) * 0.5 + 0.5);
	// vec4 fragColor = vec4(1.0);
	// float rectSizeX = 4.000 + sin(time) * 4.0;
	// float rectSizeY = 1.2;// + sin(time * 2.0);
	// vec3 ex = vec3(1, 0, 0)*rectSizeX;
	// vec3 ey = vec3(0, 0, 1)*rectSizeY;
	// vec3 p1 = lightPos - ex + ey;
	// vec3 p2 = lightPos + ex + ey;
	// vec3 p3 = lightPos + ex - ey;
	// vec3 p4 = lightPos - ex - ey;
	// float theta = acos(dotNV);
	// vec2 tuv = vec2(metrough.y, theta/(0.5*PI));
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
	// fragColor.rgb = ltccol * 5.0 * visibility + (indirect / 14.0 * ao * (rectSizeX / 6.0) );
	// // fragColor.rgb = ltccol * visibility + (indirect / 2.0 * ao);
	
	// fragColor = vec4(pow(fragColor.rgb, vec3(1.0 / 2.2)), fragColor.a);
	// outputColor = vec4(fragColor.rgb, fragColor.a);
	//gl_FragColor = vec4(fragColor.rgb, fragColor.a);    
}
