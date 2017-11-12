#version 450

#ifdef GL_ES
precision mediump float;
#endif

in vec3 color;
out vec4 fragColor;

void main() {
	fragColor = vec4(color, 1.0);
}
