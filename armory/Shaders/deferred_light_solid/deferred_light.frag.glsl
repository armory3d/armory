#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbuffer1;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	fragColor.rgb = textureLod(gbuffer1, texCoord, 0.0).rgb; // Basecolor.rgb
}
