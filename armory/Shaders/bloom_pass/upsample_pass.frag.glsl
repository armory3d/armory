#version 450

#include "compiled.inc" // bloomStrength
#include "std/resample.glsl"

uniform sampler2D tex;
uniform vec2 screenSizeInv;
uniform int currentMipLevel;
uniform float sampleScale;

#ifdef _CPostprocess
	uniform vec3 PPComp11;
#endif

in vec2 texCoord;

out vec4 fragColor;

void main() {
	#ifdef _BloomQualityHigh
		fragColor.rgb = upsample_tent_filter_3x3(tex, texCoord, screenSizeInv, sampleScale);
	#else
		#ifdef _BloomQualityMedium
			fragColor.rgb = upsample_dual_filter(tex, texCoord, screenSizeInv, sampleScale);
		#else // _BloomQualityLow
			fragColor.rgb = upsample_4tap_bilinear(tex, texCoord, screenSizeInv, sampleScale);
		#endif
	#endif

	if (currentMipLevel == 0) {
		#ifdef _CPostprocess
			fragColor.rgb *= PPComp11.x;
		#else
			fragColor.rgb *= bloomStrength;
		#endif
	}

	fragColor.a = 1.0;
}
