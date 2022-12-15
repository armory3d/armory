// Weighted blended OIT by McGuire and Bavoil
#version 450

#include "compiled.inc"

uniform vec2 texSize;
uniform sampler2D accum;
uniform sampler2D revealage;
in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec4 Accum = texelFetch(accum, ivec2(texCoord * texSize), 0);
	float reveal = 1.0 - Accum.a;
	// Save the blending and color texture fetch cost

	if (reveal == 0.0) {
		discard;
	}

	float f = texelFetch(revealage, ivec2(texCoord * texSize), 0).r;
	fragColor = vec4(Accum.rgb / clamp(f, 0.0001, 5000), reveal);
}
