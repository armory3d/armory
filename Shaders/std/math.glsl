
#ifndef _MATH_GLSL_
#define _MATH_GLSL_

float hash(const vec2 p) {
	float h = dot(p, vec2(127.1, 311.7));
	return fract(sin(h) * 43758.5453123);
}

vec2 envMapEquirect(const vec3 normal) {
	const float PI = 3.1415926535;
	const float PI2 = PI * 2.0;
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / PI2, phi / PI);
}

float rand(const vec2 co) { // Unreliable
	return fract(sin(dot(co.xy, vec2(12.9898,78.233))) * 43758.5453);
}

vec2 rand2(const vec2 coord) {
	const float width = 1100;
	const float height = 500;
	float noiseX = ((fract(1.0 - coord.s * (width / 2.0)) * 0.25) + (fract(coord.t * (height / 2.0)) * 0.75)) * 2.0 - 1.0;
	float noiseY = ((fract(1.0 - coord.s * (width / 2.0)) * 0.75) + (fract(coord.t * (height / 2.0)) * 0.25)) * 2.0 - 1.0;	
	return vec2(noiseX, noiseY);
}

float linearize(const float depth) {
	return -cameraPlane.y * cameraPlane.x / (depth * (cameraPlane.y - cameraPlane.x) - cameraPlane.y);
}

float attenuate(const float dist) {
// float attenuate(float dist, float constant, float linear, float quadratic) {
	return 1.0 / (dist * dist);
	// 1.0 / (constant * 1.0)
	// 1.0 / (lienar * dist)
	// 1.0 / (quadratic * dist * dist);
}

bool isInsideCube(const vec3 p) {
	return abs(p.x) < 1 && abs(p.y) < 1 && abs(p.z) < 1;
}

#endif
