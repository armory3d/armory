#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415926
#define TwoPI (2.0 * PI)

#ifdef _Hosek
uniform vec3 A;
uniform vec3 B;
uniform vec3 C;
uniform vec3 D;
uniform vec3 E;
uniform vec3 F;
uniform vec3 G;
uniform vec3 H;
uniform vec3 I;
uniform vec3 Z;
uniform vec3 sunDirection;
#endif

uniform sampler2D envmap;
// uniform sampler2D tex;
uniform float envmapStrength;

in vec3 normal;
// in vec2 texCoord;

#ifdef _Hosek
vec3 hosekWilkie(float cos_theta, float gamma, float cos_gamma) {
	vec3 chi = (1 + cos_gamma * cos_gamma) / pow(1 + H * H - 2 * cos_gamma * H, vec3(1.5));
    return (1 + A * exp(B / (cos_theta + 0.01))) * (C + D * exp(E * gamma) + F * (cos_gamma * cos_gamma) + G * chi + I * sqrt(cos_theta));
}
#endif

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / TwoPI, phi / PI);
}

void main() {
	// if (texture(tex, texCoord).a == 0.0) {
		// discard;
	// }
	
	vec3 n = normalize(normal);
	gl_FragColor = texture(envmap, envMapEquirect(n)) * 3.0;// envmapStrength;

#ifdef _Hosek
    vec3 sunDir = vec3(sunDirection.x, -sunDirection.y, sunDirection.z);	
	float phi = acos(n.z);
	float theta = atan(-n.y, n.x) + PI;
	
	float cos_theta = clamp(n.z, 0, 1);
	float cos_gamma = dot(n, sunDir);
	float gamma_val = acos(cos_gamma);

	vec3 R = Z * hosekWilkie(cos_theta, gamma_val, cos_gamma);
	// R = pow(R, vec3(1.0 / 2.2));
    gl_FragColor = vec4(R, 1.0);
#endif
}
