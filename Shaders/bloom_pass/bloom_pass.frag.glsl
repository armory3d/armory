#version 450

#include "compiled.inc"

uniform sampler2D tex;

#ifdef _CPostprocess
uniform vec3 PPComp10;
#endif

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec3 col = textureLod(tex, texCoord, 0.0).rgb;
	float brightness = dot(col, vec3(0.2126, 0.7152, 0.0722));
	#ifdef _CPostprocess
		if (brightness > PPComp10.z) {
			fragColor.rgb = col;
		}
		else {
			fragColor.rgb = vec3(0.0);
		}
	#else
		if (brightness > bloomThreshold) {
			fragColor.rgb = col;
		}
		else {
			fragColor.rgb = vec3(0.0);
		}
	#endif
}
