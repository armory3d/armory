#version 450

#ifdef GL_ES
precision mediump float;
#endif

in vec4 color;

out vec4 outColor;

void main() {
    outColor = color;
}
