#version 450

in vec3 pos;
in vec4 col;

out vec4 color;

uniform mat4 VP;

void main() {
	color = col;
	gl_Position = VP * vec4(pos.xyz, 1.0);
}
