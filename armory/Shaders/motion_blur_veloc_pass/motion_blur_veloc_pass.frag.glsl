// Per-Object Motion Blur
// http://john-chapman-graphics.blogspot.com/2013/01/per-object-motion-blur.html
#version 450

#include "compiled.inc"

uniform sampler2D sveloc;
uniform sampler2D tex;
// uniform vec2 texStep;
uniform float frameScale;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec2 velocity = textureLod(sveloc, texCoord, 0.0).rg * motionBlurIntensity * frameScale;

	#ifdef _InvY
	velocity.y = -velocity.y;
	#endif

	fragColor.rgb = textureLod(tex, texCoord, 0.0).rgb;

	// float speed = length(velocity / texStep);
	// const int MAX_SAMPLES = 8;
	// int samples = clamp(int(speed), 1, MAX_SAMPLES);
	const int samples = 8;
	for (int i = 0; i < samples; ++i) {
		vec2 offset = velocity * (float(i) / float(samples - 1) - 0.5);
		fragColor.rgb += textureLod(tex, texCoord + offset, 0.0).rgb;
	}
	fragColor.rgb /= float(samples + 1);
}
