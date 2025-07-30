#version 450

#include "compiled.inc"

#ifdef _CPostprocess
uniform vec3 PPComp8;
#endif

uniform sampler2D tex;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	#ifdef _CPostprocess
		fragColor.a = 0.01 * PPComp8.z;
	#else
		fragColor.a = 0.01 * autoExposureSpeed;
	#endif

	fragColor.rgb = textureLod(tex, vec2(0.5, 0.5), 0.0).rgb +
					textureLod(tex, vec2(0.2, 0.2), 0.0).rgb +
					textureLod(tex, vec2(0.8, 0.2), 0.0).rgb +
					textureLod(tex, vec2(0.2, 0.8), 0.0).rgb +
					textureLod(tex, vec2(0.8, 0.8), 0.0).rgb;
	fragColor.rgb /= 5.0;
}
