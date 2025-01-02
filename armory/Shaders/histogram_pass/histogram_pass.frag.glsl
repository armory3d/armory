#version 450

#include "compiled.inc"

uniform sampler2D tex;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	fragColor.a = 0.01 * autoExposureSpeed;
	fragColor.rgb = textureLod(tex, vec2(0.5, 0.5), 0.0).rgb +
					textureLod(tex, vec2(0.2, 0.2), 0.0).rgb +
					textureLod(tex, vec2(0.8, 0.2), 0.0).rgb +
					textureLod(tex, vec2(0.2, 0.8), 0.0).rgb +
					textureLod(tex, vec2(0.8, 0.8), 0.0).rgb;
	fragColor.rgb /= 5.0;
}
