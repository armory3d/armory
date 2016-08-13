#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

uniform sampler2D tex;

in vec2 texCoord;
out vec4 outColor;

void main() {
	vec4 col = texture(tex, texCoord);
	outColor = vec4(col.r * 10.0, col.g * 10.0, 0.0, 1.0);
}
