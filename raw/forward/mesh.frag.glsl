#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

#ifdef _BaseTex
	uniform sampler2D sbase;
#endif
#ifndef _NoShadows
	uniform sampler2D shadowMap;
	#ifdef _PCSS
	uniform sampler2D snoise;
	uniform float lampSizeUV;
	uniform float lampNear;
	#endif
#endif
uniform float shirr[27];
#ifdef _Rad
	uniform sampler2D senvmapRadiance;
	uniform sampler2D senvmapBrdf;
	uniform int envmapNumMipmaps;
#endif
// uniform sampler2D sltcMat;
// uniform sampler2D sltcMag;
#ifdef _NorTex
	uniform sampler2D snormal;
#endif
#ifdef _NorStr
	uniform float normalStrength;
#endif
#ifdef _OccTex
	uniform sampler2D socclusion;
#else
	uniform float occlusion;
#endif
#ifdef _RoughTex
uniform sampler2D srough;
#else
	uniform float roughness;
#endif
#ifdef _RoughStr
	uniform float roughnessStrength;
#endif
#ifdef _MetTex
	uniform sampler2D smetal;
#else
	uniform float metalness;
#endif
// #ifdef _HeightTex
	// uniform sampler2D sheight;
	// uniform float heightStrength;
// #endif

uniform float envmapStrength;
uniform bool receiveShadow;
uniform vec3 lightPos;
uniform vec3 lightDir;
uniform int lightType;
uniform vec3 lightColor;
uniform float lightStrength;
uniform float spotlightCutoff;
uniform float spotlightExponent;
uniform float shadowsBias;
uniform vec3 eye;

#ifdef _VoxelGI
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

// LTC
// uniform vec3 light;
// //// const float roughness = 0.25;
// const vec3  dcolor = vec3(1.0, 1.0, 1.0);
// const vec3  scolor = vec3(1.0, 1.0, 1.0);
// const float intensity = 4.0; // 0-10
// const float width = 4.0;
// const float height = 4.0;
// const vec2  resolution = vec2(800.0, 600.0);
// const int   sampleCount = 0;
// const int   NUM_SAMPLES = 8;
// const float LUT_SIZE  = 64.0;
// const float LUT_SCALE = (LUT_SIZE - 1.0)/LUT_SIZE;
// const float LUT_BIAS  = 0.5/LUT_SIZE;
// //// vec2 mys[NUM_SAMPLES];		
// vec3 L0 = vec3(0.0);
// vec3 L1 = vec3(0.0);
// vec3 L2 = vec3(0.0);
// vec3 L3 = vec3(0.0);
// vec3 L4 = vec3(0.0);

in vec3 position;
#ifdef _Tex
	in vec2 texCoord;
#endif
in vec4 lPos;
in vec4 matColor;
in vec3 eyeDir;
#ifdef _NorTex
	in mat3 TBN;
#else
	in vec3 normal;
#endif
out vec4 fragColor;

#ifndef _NoShadows
#ifndef _PCSS
// float linstep(float low, float high, float v) {
//     return clamp((v - low) / (high - low), 0.0, 1.0);
// }
// float VSM(vec2 uv, float compare) {
//     vec2 moments = texture(shadowMap, uv).xy;
//     float p = smoothstep(compare - 0.02, compare, moments.x);
//     float variance = max(moments.y - moments.x * moments.x, -0.001);
//     float d = compare - moments.x;
//     float p_max = linstep(0.2, 1.0, variance / (variance + d * d));
//     return clamp(max(p, p_max), 0.0, 1.0);
// }
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
			// vec2 off = vec2(x, y) / shadowmapSize;
			// result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			
			vec2 off = vec2(-1, -1) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(-1, 0) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(-1, 1) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(0, -1) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(0, 0) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(0, 1) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(1, -1) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(1, 0) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			off = vec2(1, 1) / shadowmapSize;
			result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
		// }
	// }
	return result / 9.0;
}
#else // _PCSS
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
	vec4 lPosH = lPos / lPos.w;
	lPosH.x = (lPosH.x + 1.0) / 2.0;
	lPosH.y = (lPosH.y + 1.0) / 2.0;
	#ifdef _PCSS
	return PCSS(lPosH.xy, lPosH.z - shadowsBias);
	#else
	return PCF(lPosH.xy, lPosH.z - shadowsBias);
	#endif
	// return VSM(lPosH.xy, lPosH.z);
	// float distanceFromLight = texture(shadowMap, lPosH.xy).r * 2.0 - 1.0;
	// return float(distanceFromLight > lPosH.z - shadowsBias);
}
#endif

vec3 shIrradiance(vec3 nor, float scale) {
	const float c1 = 0.429043;
	const float c2 = 0.511664;
	const float c3 = 0.743125;
	const float c4 = 0.886227;
	const float c5 = 0.247708;
	vec3 cl00, cl1m1, cl10, cl11, cl2m2, cl2m1, cl20, cl21, cl22;
	cl00 = vec3(shirr[0], shirr[1], shirr[2]);
	cl1m1 = vec3(shirr[3], shirr[4], shirr[5]);
	cl10 = vec3(shirr[6], shirr[7], shirr[8]);
	cl11 = vec3(shirr[9], shirr[10], shirr[11]);
	cl2m2 = vec3(shirr[12], shirr[13], shirr[14]);
	cl2m1 = vec3(shirr[15], shirr[16], shirr[17]);
	cl20 = vec3(shirr[18], shirr[19], shirr[20]);
	cl21 = vec3(shirr[21], shirr[22], shirr[23]);
	cl22 = vec3(shirr[24], shirr[25], shirr[26]);
	return (
		c1 * cl22 * (nor.y * nor.y - (-nor.z) * (-nor.z)) +
		c3 * cl20 * nor.x * nor.x +
		c4 * cl00 -
		c5 * cl20 +
		2.0 * c1 * cl2m2 * nor.y * (-nor.z) +
		2.0 * c1 * cl21  * nor.y * nor.x +
		2.0 * c1 * cl2m1 * (-nor.z) * nor.x +
		2.0 * c2 * cl11  * nor.y +
		2.0 * c2 * cl1m1 * (-nor.z) +
		2.0 * c2 * cl10  * nor.x
	) * scale;
}

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / PI2, phi / PI);
}


vec2 LightingFuncGGX_FV(float dotLH, float roughness) {
	float alpha = roughness*roughness;

	// F
	float F_a, F_b;
	float dotLH5 = pow(1.0 - dotLH, 5.0);
	F_a = 1.0;
	F_b = dotLH5;

	// V
	float vis;
	float k = alpha / 2.0;
	float k2 = k * k;
	float invK2 = 1.0 - k2;
	//vis = rcp(dotLH * dotLH * invK2 + k2);
	vis = inversesqrt(dotLH * dotLH * invK2 + k2);

	return vec2(F_a * vis, F_b * vis);
}

float LightingFuncGGX_D(float dotNH, float roughness) {
	float alpha = roughness * roughness;
	float alphaSqr = alpha * alpha;
	float pi = 3.14159;
	float denom = dotNH * dotNH * (alphaSqr - 1.0) + 1.0;

	float D = alphaSqr / (pi * denom * denom);
	return D;
}

// John Hable - Optimizing GGX Shaders
// http://www.filmicworlds.com/2014/04/21/optimizing-ggx-shaders-with-dotlh/
float LightingFuncGGX_OPT3(float dotNL, float dotLH, float dotNH, float roughness, float F0) {
	// vec3 H = normalize(V + L);
	// float dotNL = clamp(dot(N, L), 0.0, 1.0);
	// float dotLH = clamp(dot(L, H), 0.0, 1.0);
	// float dotNH = clamp(dot(N, H), 0.0, 1.0);

	float D = LightingFuncGGX_D(dotNH, roughness);
	vec2 FV_helper = LightingFuncGGX_FV(dotLH, roughness);
	float FV = F0 * FV_helper.x + (1.0 - F0) * FV_helper.y;
	float specular = dotNL * D * FV;

	return specular;
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

vec3 specularBRDF(vec3 f0, float roughness, float nl, float nh, float nv, float vh) {
	float a = roughness * roughness;
	return d_ggx(nh, a) * clamp(v_smithschlick(nl, nv, a), 0.0, 1.0) * f_schlick(f0, vh) / 4.0;
	//return vec3(LightingFuncGGX_OPT3(nl, lh, nh, roughness, f0[0]));
}

#ifdef _OrenNayar
vec3 orenNayarDiffuseBRDF(vec3 albedo, float roughness, float nv, float nl, float vh) {
	float a = roughness * roughness;
	float s = a;
	float s2 = s * s;
	float vl = 2.0 * vh * vh - 1.0; // Double angle identity
	float Cosri = vl - nv * nl;
	float C1 = 1.0 - 0.5 * s2 / (s2 + 0.33);
	float test = 1.0;
	if (Cosri >= 0.0) test = (1.0 / (max(nl, nv)));
	float C2 = 0.45 * s2 / (s2 + 0.09) * Cosri * test;
	return albedo * max(0.0, nl) * (C1 + C2) * (1.0 + roughness * 0.5);
}
#else
vec3 lambertDiffuseBRDF(vec3 albedo, float nl) {
	return albedo * max(0.0, nl);
}
#endif

vec3 surfaceAlbedo(vec3 baseColor, float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(vec3 baseColor, float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
}

#ifdef _Rad
float getMipLevelFromRoughness(float roughness) {
	// First mipmap level = roughness 0, last = roughness = 1
	return roughness * envmapNumMipmaps;
}
#endif


// Linearly Transformed Cosines
/*
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
int ClipQuadToHorizon() { //inout vec3 L[5], out int n) {
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

	int n = ClipQuadToHorizon(); //L, n);
	
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
}*/

#ifdef _Toon
float stepmix(float edge0, float edge1, float E, float x) {
	float T = clamp(0.5 * (x - edge0 + E) / E, 0.0, 1.0);
	return mix(edge0, edge1, T);
}
#endif

#ifdef _VoxelGI
vec4 sampleVoxels(vec3 worldPosition, float lod) {
	vec3 offset = vec3(1.0 / voxelDimensions, 1.0 / voxelDimensions, 0);
	vec3 texco = worldPosition / (voxelGridWorldSize * 0.5);
	texco = texco * 0.5 + 0.5 + offset;
	return textureLod(voxels, texco, lod);
}
// See https://github.com/Cigg/Voxel-Cone-Tracing
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
	
#ifdef _NorTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
	
	// vec3 nn = normalize(normal);
	// vec3 dp1 = dFdx( position );
	// vec3 dp2 = dFdy( position );
	// vec2 duv1 = dFdx( texCoord );
	// vec2 duv2 = dFdy( texCoord );
	// vec3 dp2perp = cross( dp2, nn );
	// vec3 dp1perp = cross( nn, dp1 );
	// vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
	// vec3 B = dp2perp * duv1.y + dp1perp * duv2.y; 
	// float invmax = inversesqrt( max( dot(T,T), dot(B,B) ) );
	// mat3 TBN = mat3(T * invmax, B * invmax, nn);
	// vec3 n = normalize(TBN * nn);
#else
	vec3 n = normalize(normal);
#endif
#ifdef _NorStr
	n *= normalStrength;
#endif

	// Move out
	vec3 l;
	if (lightType == 0) { // Sun
		l = lightDir;
	}
	else { // Point, spot
		l = normalize(lightPos - position.xyz);
	}
	float dotNL = dot(n, l);
	
	float visibility = 1.0;
#ifndef _NoShadows
	if (receiveShadow) {
		if (lPos.w > 0.0) {
			visibility = shadowTest(lPos);
		}
	}
#endif

	vec3 baseColor = matColor.rgb;
#ifdef _BaseTex
	vec4 texel = texture(sbase, texCoord);
#ifdef _AlphaTest
	if (texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2));
	baseColor *= texel.rgb;
#endif

	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);

	float dotNV = dot(n, v);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);
	float dotLV = dot(l, v);
	float dotLH = dot(l, h);

#ifdef _MetTex
	float metalness = texture(smetal, texCoord).r;
#endif
	vec3 albedo = surfaceAlbedo(baseColor, metalness);
	vec3 f0 = surfaceF0(baseColor, metalness);

#ifdef _RoughTex
	float roughness = texture(srough, texCoord).r;
#endif
#ifdef _RoughStr
	roughness *= roughnessStrength;
#endif



// #ifdef _Toon
// 	vec3 v = normalize(eyeDir);
// 	vec3 h = normalize(v + l);
	
// 	const vec3 ambientMaterial = baseColor * vec3(0.35, 0.35, 0.35) + vec3(0.15);
// 	const vec3 diffuseMaterial = baseColor;
// 	const vec3 specularMaterial = vec3(0.45, 0.35, 0.35);
// 	const float shininess = 0.5;
	
// 	float df = max(0.0, dotNL);
// 	float sf = max(0.0, dot(n, h));
//     sf = pow(sf, shininess);
	
// 	const float A = 0.1;
//     const float B = 0.3;
//     const float C = 0.6;
//     const float D = 1.0;
//     float E = fwidth(df);
// 	bool f = false;
// 	if (df > A - E) if (df < A + E) {
// 		f = true;
// 		df = stepmix(A, B, E, df);
// 	}
	
// 	/*else*/if (!f) if (df > B - E) if(df < B + E) {
// 		f = true;
// 		df = stepmix(B, C, E, df);
// 	}
	
// 	/*else*/if (!f) if (df > C - E) if (df < C + E) {
// 		f = true;
// 		df = stepmix(C, D, E, df);
// 	}
// 	/*else*/if (!f) if (df < A) {
// 		df = 0.0;
// 	}
// 	else if (df < B) {
// 		df = B;
// 	}
// 	else if (df < C) {
// 		df = C;
// 	}
// 	else df = D;
	
// 	E = fwidth(sf);
//     if (sf > 0.5 - E && sf < 0.5 + E) {
//         sf = smoothstep(0.5 - E, 0.5 + E, sf);
//     }
//     else {
//         sf = step(0.5, sf);
//     }
	
// 	fragColor.rgb = ambientMaterial + (df * diffuseMaterial + sf * specularMaterial) * visibility;
//     float edgeDetection = (dot(v, n) < 0.1) ? 0.0 : 1.0;
// 	fragColor.rgb *= edgeDetection;
	
// 	// const int levels = 4;
// 	// const float scaleFactor = 1.0 / levels;
	
// 	// float diffuse = max(0, dotNL);
// 	// const float material_kd = 0.8;
// 	// const float material_ks = 0.3;
// 	// vec3 diffuseColor = vec3(0.40, 0.60, 0.70);
// 	// diffuseColor = diffuseColor * material_kd * floor(diffuse * levels) * scaleFactor;
// 	// float specular = 0.0;
// 	// if(dotNL > 0.0) {
// 	// 	specular = material_ks * pow( max(0, dot( h, n)), shininess);
// 	// }
// 	// // Limit specular
// 	// float specMask = (pow(dot(h, n), shininess) > 0.4) ? 1.0 : 0.0;
	
// 	// float edgeDetection = (dot(v, n) > 0.3) ? 1.0 : 0.0;
// 	// fragColor.rgb = edgeDetection * ((diffuseColor + specular * specMask) * visibility + ambientMaterial);
// #endif


	// LTC
	// const float rectSizeX = 2.5;
	// const float rectSizeY = 1.2;
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
	
	// vec3 ltcspec = LTC_Evaluate(n, v, position, Minv, p1, p2, p3, p4, true);
	// ltcspec *= texture(sltcMag, tuv).a;
	// vec3 ltcdiff = LTC_Evaluate(n, v, position, mat3(1), p1, p2, p3, p4, true); 
	// vec3 ltccol = ltcspec + ltcdiff * albedo;
	// ltccol /= 2.0*PI;


	// Direct
#ifdef _OrenNayar
	vec3 direct = orenNayarDiffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);
#else
	vec3 direct = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);
#endif

	if (lightType == 2) { // Spot
		float spotEffect = dot(lightDir, l);
		if (spotEffect < spotlightCutoff) {
			spotEffect = smoothstep(spotlightCutoff - spotlightExponent, spotlightCutoff, spotEffect);
			direct *= spotEffect;
		}
	}
	
	direct = direct * lightColor * lightStrength;
	



#ifdef _VoxelGI
	vec3 tangent = normalize(cross(n, vec3(0.0, 1.0, 0.0)));
	if (length(tangent) == 0.0) {
		tangent = normalize(cross(n, vec3(0.0, 0.0, 1.0)));
	}
	vec3 bitangent = normalize(cross(n, tangent));
	mat3 tanToWorld = inverse(transpose(mat3(tangent, bitangent, n)));

	float diffOcclusion = 0.0;
	vec3 indirectDiffuse = indirectLight(tanToWorld, n, diffOcclusion).rgb * 4.0;
	indirectDiffuse *= albedo;
	diffOcclusion = min(1.0, 1.5 * diffOcclusion);

	vec3 reflectWorld = reflect(-v, n);
	float specularOcclusion;
	float lodOffset = 0.0;//getMipLevelFromRoughness(roughness);
	vec3 indirectSpecular = coneTrace(reflectWorld, n, 0.07 + lodOffset, specularOcclusion).rgb;
	if (roughness > 0.0) { // Temp..
		vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
		indirectSpecular *= (f0 * envBRDF.x + envBRDF.y);
	}

	vec3 indirect = indirectDiffuse * diffOcclusion + indirectSpecular;

#else

	// Indirect
	vec3 indirectDiffuse = shIrradiance(n, 2.2) / PI;	
#ifdef _EnvLDR
	indirectDiffuse = pow(indirectDiffuse, vec3(2.2));
#endif
	indirectDiffuse *= albedo;
	vec3 indirect = indirectDiffuse;
	
#ifdef _Rad
	vec3 reflectionWorld = reflect(-v, n); 
	float lod = getMipLevelFromRoughness(roughness);// + 1.0;
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
	#ifdef _EnvLDR
		prefilteredColor = pow(prefilteredColor, vec3(2.2));
	#endif
	vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
	vec3 indirectSpecular = prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
	indirect += indirectSpecular;
#endif
	indirect = indirect * envmapStrength;// * lightColor * lightStrength;

#endif	

	fragColor = vec4(vec3(direct * visibility + indirect), 1.0);


#ifdef _OccTex
	vec3 occ = texture(socclusion, texCoord).rgb;
	fragColor.rgb *= occ;
#else
	fragColor.rgb *= occlusion; 
#endif
	

	// LTC
	// fragColor.rgb = ltccol * 10.0 * visibility + indirect / 14.0;


#ifdef _LDR
	// gl_FragColor = vec4(pow(fragColor.rgb, vec3(1.0 / 2.2)), fragColor.a);
	fragColor = vec4(pow(fragColor.rgb, vec3(1.0 / 2.2)), fragColor.a);
// #else
	// gl_FragColor = vec4(fragColor.rgb, fragColor.a);
	//fragColor = vec4(fragColor.rgb, fragColor.a);
#endif
}
