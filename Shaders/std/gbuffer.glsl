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

vec3 getPos2(const mat4 invVP, const float depth, const vec2 coord) {
	// vec4 pos = vec4(coord * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
	vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
	pos = invVP * pos;
	pos.xyz /= pos.w;
	return pos.xyz;
}

vec3 getPos2NoEye(const vec3 eye, const mat4 invVP, const float depth, const vec2 coord) {
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

vec2 unpackFloat(float f) {
	return vec2(floor(f) / 100.0, fract(f));
}
