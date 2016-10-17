
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

float rand(vec2 co) { // Unreliable
	return fract(sin(dot(co.xy, vec2(12.9898,78.233))) * 43758.5453);
}
