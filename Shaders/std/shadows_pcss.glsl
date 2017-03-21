// Based on ThreeJS and nvidia pcss
#include "../compiled.glsl"

uniform sampler2D shadowMap;
uniform samplerCube shadowMapCube;
uniform sampler2D snoise;
uniform float lampSizeUV;

const int NUM_SAMPLES = 17;
const float radiusStep = 1.0 / float(NUM_SAMPLES);
const float angleStep = PI2 * float(pcssRings) / float(NUM_SAMPLES);
const float lampNear = 0.5;

vec2 poissonDisk0; vec2 poissonDisk1; vec2 poissonDisk2;
vec2 poissonDisk3; vec2 poissonDisk4; vec2 poissonDisk5;
vec2 poissonDisk6; vec2 poissonDisk7; vec2 poissonDisk8;
vec2 poissonDisk9; vec2 poissonDisk10; vec2 poissonDisk11;
vec2 poissonDisk12; vec2 poissonDisk13; vec2 poissonDisk14;
vec2 poissonDisk15; vec2 poissonDisk16;

void initPoissonSamples(const vec2 randomSeed) {
	float angle = texture(snoise, randomSeed).r * 1000.0;
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

float findBlocker(const vec2 uv, const float zReceiver) {
	// This uses similar triangles to compute what area of the shadow map we should search
	float searchRadius = lampSizeUV * (zReceiver - lampNear) / zReceiver;
	float blockerDepthSum = 0.0;
	int numBlockers = 0;
	// for (int i = 0; i < NUM_SAMPLES; i++) {
		float shadowMapDepth = texture(shadowMap, uv + poissonDisk0 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk1 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk2 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk3 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk4 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk5 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk6 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk7 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk8 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk9 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk10 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk11 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk12 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk13 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk14 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk15 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
		shadowMapDepth = texture(shadowMap, uv + poissonDisk16 * searchRadius).r;
		if (shadowMapDepth < zReceiver) { blockerDepthSum += shadowMapDepth; numBlockers++; }
	// }
	if (numBlockers == 0) return -1.0;
	return blockerDepthSum / float(numBlockers);
}

float filterPCF(const vec2 uv, const float zReceiver, const float filterRadius) {
	float sum = 0.0;
	// for (int i = 0; i < NUM_SAMPLES; i++) {
		float depth = texture(shadowMap, uv + poissonDisk0 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk1 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk2 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk3 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk4 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk5 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk6 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk7 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk8 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk9 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk10 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk11 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk12 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk13 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk14 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk15 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + poissonDisk16 * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
	// }
	// for (int i = 0; i < NUM_SAMPLES; i++) {
		depth = texture(shadowMap, uv + -poissonDisk0.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk1.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk2.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk3.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk4.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk5.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk6.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk7.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk8.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk9.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk10.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk11.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk12.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk13.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk14.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk15.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
		depth = texture(shadowMap, uv + -poissonDisk16.yx * filterRadius).r;
		if (zReceiver <= depth) sum += 1.0;
	// }
	return sum / (2.0 * float(NUM_SAMPLES));
}

float PCSS(const vec2 uv, const float zReceiver) {
	initPoissonSamples(uv);
	float avgBlockerDepth = findBlocker(uv, zReceiver);
	if (avgBlockerDepth == -1.0) return 1.0;
	float penumbraRatio = (zReceiver - avgBlockerDepth) / avgBlockerDepth;
	float filterRadius = penumbraRatio * lampSizeUV * lampNear / zReceiver;
	return filterPCF(uv, zReceiver, filterRadius);
}

// No soft shadows for cube yet..
float lpToDepth(vec3 lp, const vec2 lightPlane) {
	float d = lightPlane.y - lightPlane.x;
	lp = abs(lp);
	float zcomp = max(lp.x, max(lp.y, lp.z));
	zcomp = (lightPlane.y + lightPlane.x) / (d) - (2.0 * lightPlane.y * lightPlane.x) / (d) / zcomp;
	return zcomp * 0.5 + 0.5;
}

float PCFCube(const vec3 lp, const vec3 ml, const float bias, const vec2 lightPlane) {
	// return float(texture(shadowMapCube, ml).r + bias > lpToDepth(lp));

	const float s = 0.001; // TODO: incorrect...
	float compare = lpToDepth(lp, lightPlane) - bias;
	float result = step(compare, texture(shadowMapCube, ml).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, -s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, s, -s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, -s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, -s, -s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, s, -s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, -s, -s)).r);
	result /= 9.0;
	return result;
}