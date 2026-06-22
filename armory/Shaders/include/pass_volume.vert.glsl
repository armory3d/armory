#version 450

uniform mat4 VWVP;

in vec3 pos;

out vec4 wvpposition;

void main() {
	wvpposition = VWVP * vec4(pos, 1.0);
	gl_Position = wvpposition;
}
