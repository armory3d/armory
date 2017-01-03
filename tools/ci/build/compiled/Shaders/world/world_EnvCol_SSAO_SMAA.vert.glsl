#version 450
#define _EnvCol
#define _SSAO
#define _SMAA

#ifdef GL_ES
precision highp float;
#endif

in vec3 pos;
in vec3 nor;

out vec3 normal;

uniform mat4 SMVP;

void main() {
	normal = nor;
	vec4 position = SMVP * vec4(pos, 1.0);
	gl_Position = vec4(position);
}
