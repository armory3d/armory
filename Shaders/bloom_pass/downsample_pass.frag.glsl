#version 450

#include "compiled.inc" // bloomKnee, bloomThreshold
#include "std/resample.glsl"

uniform sampler2D tex;
uniform vec2 screenSizeInv;
uniform int currentMipLevel;

#ifdef _CPostprocess
	uniform vec3 PPComp11;
#endif

in vec2 texCoord;

out vec4 fragColor;

const float epsilon = 6.2e-5; // see https://github.com/keijiro/KinoBloom/issues/15

void main() {
	#ifdef _BloomQualityHigh
		fragColor.rgb = downsample_13_tap(tex, texCoord, screenSizeInv);
	#else
		#ifdef _BloomQualityMedium
			fragColor.rgb = downsample_dual_filter(tex, texCoord, screenSizeInv);
		#else // _BloomQualityLow
			fragColor.rgb = downsample_box_filter(tex, texCoord, screenSizeInv);
		#endif
	#endif

	if (currentMipLevel == 0) {
		#ifdef _CPostprocess
			const float threshold = PPComp11.x;
			const float knee = PPComp11.y;
		#else
			const float threshold = bloomThreshold;
			const float knee = bloomKnee;
		#endif

		// https://catlikecoding.com/unity/tutorials/advanced-rendering/bloom/#3.2
		float brightness = max(fragColor.r, max(fragColor.g, fragColor.b));
		float softeningCurve = brightness - threshold + knee;
		softeningCurve = clamp(softeningCurve, 0.0, 2.0 * knee); // "connect" to hard knee curve
		softeningCurve = softeningCurve * softeningCurve / (4 * knee + epsilon);

		float contributionFactor = max(softeningCurve, brightness - threshold);
		contributionFactor /= max(epsilon, brightness);

		fragColor.rgb *= contributionFactor;
	}

	fragColor.a = 1.0;
}
