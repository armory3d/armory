#version 450

#include "compiled.inc" // bloomKnee, bloomThreshold
#include "std/resample.glsl"

uniform sampler2D tex;
uniform vec2 screenSizeInv;
uniform int currentMipLevel;

#ifdef _CPostprocess
	uniform vec4 BloomThresholdData; // Only filled with data if currentMipLevel == 0
#endif

in vec2 texCoord;

out vec4 fragColor;

const float epsilon = 6.2e-5; // see https://github.com/keijiro/KinoBloom/issues/15

#ifdef _BloomAntiFlicker
	const bool antiFlicker = true;
#else
	const bool antiFlicker = false;
#endif

void main() {
	if (antiFlicker && currentMipLevel == 0) {
		#ifdef _BloomQualityHigh
			fragColor.rgb = downsample_13_tap_anti_flicker(tex, texCoord, screenSizeInv);
		#else
			#ifdef _BloomQualityMedium
				fragColor.rgb = downsample_dual_filter_anti_flicker(tex, texCoord, screenSizeInv);
			#else // _BloomQualityLow
				fragColor.rgb = downsample_box_filter_anti_flicker(tex, texCoord, screenSizeInv);
			#endif
		#endif
	}
	else {
		#ifdef _BloomQualityHigh
			fragColor.rgb = downsample_13_tap(tex, texCoord, screenSizeInv);
		#else
			#ifdef _BloomQualityMedium
				fragColor.rgb = downsample_dual_filter(tex, texCoord, screenSizeInv);
			#else // _BloomQualityLow
				fragColor.rgb = downsample_box_filter(tex, texCoord, screenSizeInv);
			#endif
		#endif
	}

	if (currentMipLevel == 0) {
		// https://catlikecoding.com/unity/tutorials/advanced-rendering/bloom/#3.2
		// https://catlikecoding.com/unity/tutorials/advanced-rendering/bloom/#3.4

		float brightness = max(fragColor.r, max(fragColor.g, fragColor.b));

		#ifdef _CPostprocess
			// Only apply precalculation optimization if _CPostprocess, otherwise
			// the compiler is able to do the same optimization for the constant
			// values from compiled.inc without the need to pass a uniform
			float softeningCurve = brightness - BloomThresholdData.y;
			softeningCurve = clamp(softeningCurve, 0.0, BloomThresholdData.z); // "connect" to hard knee curve
			softeningCurve = softeningCurve * softeningCurve * BloomThresholdData.w;

			float contributionFactor = max(softeningCurve, brightness - BloomThresholdData.x);
		#else
			float softeningCurve = brightness - bloomThreshold + bloomKnee;
			softeningCurve = clamp(softeningCurve, 0.0, 2.0 * bloomKnee);
			softeningCurve = softeningCurve * softeningCurve / (4 * bloomKnee + epsilon);

			float contributionFactor = max(softeningCurve, brightness - bloomThreshold);
		#endif

		contributionFactor /= max(epsilon, brightness);

		fragColor.rgb *= contributionFactor;
	}

	fragColor.a = 1.0;
}
