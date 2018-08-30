#version 450

#include "compiled.inc"

uniform sampler2D tex;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec4 col = texture(tex, texCoord);
	fragColor.rgb = vec4(col.r * 10.0, col.g * 10.0, 0.0);
}
