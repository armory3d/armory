#version 450

#include "compiled.inc"

uniform sampler2D texdepth;
uniform vec2 screenSizeInv;

in vec2 texCoord;

out float fragColor;

void main() {
	float d0 = textureLod(texdepth, texCoord, 0.0).r;
	float d1 = textureLod(texdepth, texCoord + vec2(screenSizeInv.x, 0.0), 0.0).r;
	float d2 = textureLod(texdepth, texCoord + vec2(0.0, screenSizeInv.y), 0.0).r;
	float d3 = textureLod(texdepth, texCoord + vec2(screenSizeInv.x, screenSizeInv.y), 0.0).r;
	fragColor = max(max(d0, d1), max(d2, d3));
}
