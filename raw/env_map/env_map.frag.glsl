#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415926
#define TwoPI (2.0 * PI)

uniform sampler2D envmap;
// uniform sampler2D tex;

in vec3 normal;
// in vec2 texCoord;

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
	// gl_FragColor = texture(envmap, envMapEquirect(n));
	gl_FragColor = vec4(pow(texture(envmap, envMapEquirect(n)).rgb, vec3(2.2)), 1.0);
}
