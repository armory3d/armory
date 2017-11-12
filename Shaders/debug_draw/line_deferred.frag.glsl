#version 450

#ifdef GL_ES
precision mediump float;
#endif

in vec3 color;
out vec4[2] fragColor;

void main() {
	fragColor[0] = vec4(1.0, 1.0, 0.0, 1.0 - gl_FragCoord.z);
	fragColor[1] = vec4(color, 1.0);
}
