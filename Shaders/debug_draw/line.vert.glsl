#version 450

in vec3 pos;
in vec3 col;

uniform mat4 ViewProjection;
out vec3 color;

void main() {
	color = col;
	gl_Position = ViewProjection * vec4(pos, 1.0);
}
