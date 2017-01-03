#version 450
#define _EnvCol
#define _SSAO
#define _SMAA
in vec3 pos;
in vec3 nor;
out vec3 wposition;
out vec3 eyeDir;
out vec3 wnormal;
uniform mat4 W;
uniform mat4 N;
uniform mat4 WVP;
uniform vec3 eye;
void main() {
	vec4 spos = vec4(pos, 1.0);
	wnormal = normalize(mat3(N) * nor);
	wposition = vec4(W * spos).xyz;
	eyeDir = eye - wposition;
	gl_Position = WVP * spos;
}
