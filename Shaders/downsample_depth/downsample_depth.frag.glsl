#version 450

#include "compiled.inc"

uniform sampler2D texdepth;

in vec2 texCoord;

void main() {
	float d = textureLod(texdepth, texCoord, 0.0).r;
	// Select max depth from 2x2 area..
	gl_FragDepth = d;
}
