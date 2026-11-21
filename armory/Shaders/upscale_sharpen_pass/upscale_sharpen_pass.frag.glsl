#version 450

// Contrast adaptive sharpening of the upscaled image, written to the framebuffer

#include "compiled.inc"

uniform sampler2D tex;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	ivec2 size = textureSize(tex, 0);
	ivec2 p = clamp(ivec2(texCoord * vec2(size)), ivec2(0), size - 1);
	vec3 c = texelFetch(tex, p, 0).rgb;

	if (upscaleSharpness <= 0.0) {
		fragColor = vec4(c, 1.0);
		return;
	}

	ivec2 sMax = size - 1;
	vec3 n = texelFetch(tex, clamp(p + ivec2(0, 1), ivec2(0), sMax), 0).rgb;
	vec3 s = texelFetch(tex, clamp(p - ivec2(0, 1), ivec2(0), sMax), 0).rgb;
	vec3 e = texelFetch(tex, clamp(p + ivec2(1, 0), ivec2(0), sMax), 0).rgb;
	vec3 w = texelFetch(tex, clamp(p - ivec2(1, 0), ivec2(0), sMax), 0).rgb;

	vec3 mn = min(c, min(min(n, s), min(e, w)));
	vec3 mx = max(c, max(max(n, s), max(e, w)));

	// Less sharpening where the local contrast is already high, avoids halos
	vec3 amp = sqrt(clamp(min(mn, 1.0 - mx) / max(mx, vec3(1e-4)), 0.0, 1.0));
	vec3 wt = amp * (-1.0 / mix(8.0, 5.0, upscaleSharpness));

	vec3 result = (c + (n + s + e + w) * wt) / (1.0 + 4.0 * wt);
	fragColor = vec4(clamp(result, 0.0, 1.0), 1.0);
}
