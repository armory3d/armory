#version 450
#define _EnvCol
#define _SSAO
#define _SMAA
in vec3 pos;
in vec3 nor;
uniform mat4 LWVP;
void main() {
	vec4 spos = vec4(pos, 1.0);
	gl_Position = LWVP * spos;
}
