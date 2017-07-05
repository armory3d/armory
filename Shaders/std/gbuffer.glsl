#ifndef _GBUFFER_GLSL_
#define _GBUFFER_GLSL_

#include "../compiled.glsl"

vec2 octahedronWrap(const vec2 v) {
	return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec3 getNor(const vec2 enc) {
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);
	return n;
}

vec3 getPosView(const vec3 viewRay, const float depth) {	
	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
	const float projectionB = (-cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
	float linearDepth = projectionB / (projectionA - depth);
	return viewRay * linearDepth;
}

vec3 getPos(const vec3 eye, const vec3 eyeLook, const vec3 viewRay, const float depth) {	
	vec3 vray = normalize(viewRay);
	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
	const float projectionB = (-cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}

vec3 getPosNoEye(const vec3 eyeLook, const vec3 viewRay, const float depth) {	
	vec3 vray = normalize(viewRay);
	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
	const float projectionB = -(cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = vray * (linearDepth / viewZDist);
	return wposition;
}

#ifdef _InvY
vec3 getPos2(const mat4 invVP, const float depth, vec2 coord) {
	coord.y = 1.0 - coord.y;
#else
vec3 getPos2(const mat4 invVP, const float depth, const vec2 coord) {
#endif
	vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
	pos = invVP * pos;
	pos.xyz /= pos.w;
	return pos.xyz;
}

#ifdef _InvY
vec3 getPosView2(const mat4 invP, const float depth, vec2 coord) {
	coord.y = 1.0 - coord.y;
#else
vec3 getPosView2(const mat4 invP, const float depth, const vec2 coord) {
#endif
	vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
	pos = invP * pos;
	pos.xyz /= pos.w;
	return pos.xyz;
}

#ifdef _InvY
vec3 getPos2NoEye(const vec3 eye, const mat4 invVP, const float depth, vec2 coord) {
	coord.y = 1.0 - coord.y;
#else
vec3 getPos2NoEye(const vec3 eye, const mat4 invVP, const float depth, const vec2 coord) {
#endif
	vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
	pos = invVP * pos;
	pos.xyz /= pos.w;
	return pos.xyz - eye;
}

float packFloat(const float f1, const float f2) {
	float index = floor(f1 * 100.0); // Temporary
	float alpha = clamp(f2, 0.0, 1.0 - 0.001);
	return index + alpha;
}

vec2 unpackFloat(const float f) {
	return vec2(floor(f) / 100.0, fract(f));
}

vec4 encodeRGBM(const vec3 rgb) {
	const float maxRange = 6.0;
	float maxRGB = max(rgb.x, max(rgb.g, rgb.b));
	float m = maxRGB / maxRange;
	m = ceil(m * 255.0) / 255.0;
	return vec4(rgb / (m * maxRange), m);
}

vec3 decodeRGBM(const vec4 rgbm) {
	const float maxRange = 6.0;
    return rgbm.rgb * rgbm.a * maxRange;
}

#endif
