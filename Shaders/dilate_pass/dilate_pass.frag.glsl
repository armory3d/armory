#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D shadowMap;

in vec2 texCoord;
out float fragColor;

uniform vec2 step;

void main() {
	fragColor = 1.0;
	const vec2 smStep = 1.0 / shadowmapSize;
	for (int i = -20 * penumbraScale; i < 20 * penumbraScale; i++) fragColor = min(fragColor, texture(shadowMap, texCoord.xy + step * smStep * i).r);
}
