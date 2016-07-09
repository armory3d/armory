#version 450

#ifdef GL_ES
precision mediump float;
#endif

const float PI = 3.1415926;
const float TwoPI = (2.0 * PI);

#ifdef _EnvCol
	uniform vec3 backgroundCol;
#endif
#ifdef _EnvSky
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
#ifdef _EnvTex
	uniform sampler2D envmap;
#endif
uniform sampler2D gbufferD;
uniform float envmapStrength;

in vec2 texCoord;
in vec3 normal;

#ifdef _EnvSky
vec3 hosekWilkie(float cos_theta, float gamma, float cos_gamma) {
	vec3 chi = (1 + cos_gamma * cos_gamma) / pow(1 + H * H - 2 * cos_gamma * H, vec3(1.5));
    return (1 + A * exp(B / (cos_theta + 0.01))) * (C + D * exp(E * gamma) + F * (cos_gamma * cos_gamma) + G * chi + I * sqrt(cos_theta));
}
#endif

#ifdef _EnvTex
vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / TwoPI, phi / PI);
}
#endif

void main() {
	if (texture(gbufferD, texCoord).r/* * 2.0 - 1.0*/ != 1.0) {
		discard;
	}

#ifdef _EnvCol
	gl_FragColor = vec4(backgroundCol, 1.0);
	return;
#else
	vec3 n = normalize(normal);
#endif

#ifdef _EnvTex
	gl_FragColor = texture(envmap, envMapEquirect(n)) * envmapStrength;
	return;
#endif

#ifdef _EnvSky
    vec3 sunDir = vec3(sunDirection.x, -sunDirection.y, sunDirection.z);	
	float phi = acos(n.z);
	float theta = atan(-n.y, n.x) + PI;
	
	float cos_theta = clamp(n.z, 0, 1);
	float cos_gamma = dot(n, sunDir);
	float gamma_val = acos(cos_gamma);

	vec3 R = Z * hosekWilkie(cos_theta, gamma_val, cos_gamma) * envmapStrength;
	R = pow(R, vec3(2.2));
    gl_FragColor = vec4(R, 1.0);
    return;
#endif
}
