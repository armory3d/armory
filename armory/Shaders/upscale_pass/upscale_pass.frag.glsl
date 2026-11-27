#version 450

// Temporal upscaler (TAAU). Reconstructs a display resolution image from
// jittered lower resolution frames: every frame adds its samples at their
// sub-pixel positions to a display resolution history, which is reprojected
// with the velocity buffer and clipped to the current neighbourhood to reject
// stale data.

#include "compiled.inc"

uniform sampler2D tex;    // Current frame, render resolution
uniform sampler2D tex2;   // History, display resolution (alpha = history length)
uniform sampler2D sveloc; // Velocity, render resolution
uniform vec2 jitter;      // Projection jitter of the current frame, in render pixels

in vec2 texCoord;
out vec4 fragColor;

const float maxHistory = 32.0;

vec3 rgb2ycocg(const vec3 c) {
	return vec3(0.25 * c.r + 0.5 * c.g + 0.25 * c.b, 0.5 * c.r - 0.5 * c.b, -0.25 * c.r + 0.5 * c.g - 0.25 * c.b);
}

vec3 ycocg2rgb(const vec3 c) {
	return vec3(c.x + c.y - c.z, c.x + c.z, c.x - c.y - c.z);
}

// 5 tap Catmull-Rom history filter, keeps the history sharp while resampling
vec3 sampleHistory(const vec2 uv, const vec2 size) {
	vec2 samplePos = uv * size;
	vec2 texPos1 = floor(samplePos - 0.5) + 0.5;
	vec2 f = samplePos - texPos1;
	vec2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f));
	vec2 w1 = 1.0 + f * f * (-2.5 + 1.5 * f);
	vec2 w2 = f * (0.5 + f * (2.0 - 1.5 * f));
	vec2 w3 = f * f * (-0.5 + 0.5 * f);
	vec2 w12 = w1 + w2;
	vec2 tc0 = (texPos1 - 1.0) / size;
	vec2 tc3 = (texPos1 + 2.0) / size;
	vec2 tc12 = (texPos1 + w2 / w12) / size;

	vec3 result = textureLod(tex2, vec2(tc12.x, tc0.y), 0.0).rgb * (w12.x * w0.y);
	result += textureLod(tex2, vec2(tc0.x, tc12.y), 0.0).rgb * (w0.x * w12.y);
	result += textureLod(tex2, vec2(tc12.x, tc12.y), 0.0).rgb * (w12.x * w12.y);
	result += textureLod(tex2, vec2(tc3.x, tc12.y), 0.0).rgb * (w3.x * w12.y);
	result += textureLod(tex2, vec2(tc12.x, tc3.y), 0.0).rgb * (w12.x * w3.y);
	float wsum = w12.x * w0.y + w0.x * w12.y + w12.x * w12.y + w3.x * w12.y + w12.x * w3.y;
	return max(result / wsum, vec3(0.0));
}

// Clip the history towards the neighbourhood mean instead of clamping per channel
vec3 clipAABB(const vec3 boxMin, const vec3 boxMax, const vec3 mean, const vec3 h) {
	vec3 center = clamp(mean, boxMin, boxMax);
	vec3 extents = max(0.5 * (boxMax - boxMin), vec3(1e-5));
	vec3 v = h - center;
	vec3 a = abs(v / extents);
	float m = max(a.x, max(a.y, a.z));
	return m > 1.0 ? center + v / m : h;
}

void main() {
	vec2 inSize = vec2(textureSize(tex, 0));
	vec2 outSize = vec2(textureSize(tex2, 0));
	ivec2 inMax = ivec2(inSize) - 1;

	// The scene is shifted by the jitter, find where this display pixel lands in the current frame
	vec2 jitterUV = jitter / inSize;
	#ifdef _InvY
	jitterUV.y = -jitterUV.y;
	#endif
	vec2 inPos = (texCoord + jitterUV) * inSize;
	ivec2 center = ivec2(floor(inPos));

	vec3 colors[9];
	vec2 offsets[9];
	vec3 m1 = vec3(0.0);
	vec3 m2 = vec3(0.0);
	vec3 boxMin = vec3(1e10);
	vec3 boxMax = vec3(-1e10);
	vec2 velocity = vec2(0.0);

	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			int i = (y + 1) * 3 + (x + 1);
			ivec2 p = clamp(center + ivec2(x, y), ivec2(0), inMax);
			vec3 c = rgb2ycocg(max(texelFetch(tex, p, 0).rgb, vec3(0.0)));
			colors[i] = c;
			offsets[i] = vec2(center + ivec2(x, y)) + 0.5 - inPos; // In render pixels

			m1 += c;
			m2 += c * c;
			boxMin = min(boxMin, c);
			boxMax = max(boxMax, c);

			// Dilate velocity so that edges of moving objects reproject with them
			vec2 v = texelFetch(sveloc, p, 0).rg;
			if (dot(v, v) > dot(velocity, velocity)) velocity = v;
		}
	}

	#ifdef _InvY
	velocity.y = -velocity.y;
	#endif
	vec2 prevUV = texCoord - velocity;

	float historyLen = textureLod(tex2, prevUV, 0.0).a * maxHistory;
	if (any(lessThan(prevUV, vec2(0.0))) || any(greaterThan(prevUV, vec2(1.0)))) {
		historyLen = 0.0;
	}

	// Reconstruction kernel (Gaussian fit of Blackman-Harris) sized in display pixels so that
	// the accumulated image stays sharp. Without history it widens to render pixels to fill the gaps.
	vec2 upscale = outSize / inSize;
	vec2 kernelScale = mix(vec2(1.0), upscale, clamp(historyLen / 4.0, 0.0, 1.0));
	vec3 colorSum = vec3(0.0);
	float weightSum = 0.0;
	float weightMax = 0.0;
	for (int i = 0; i < 9; i++) {
		vec2 d = offsets[i] * kernelScale;
		float w = exp(-2.29 * dot(d, d));
		colorSum += colors[i] * w;
		weightSum += w;
		weightMax = max(weightMax, w);
	}
	vec3 current = colorSum / max(weightSum, 1e-5);

	vec3 history = rgb2ycocg(sampleHistory(prevUV, outSize));

	// Variance clipping, tightened by the min/max box
	vec3 mean = m1 / 9.0;
	vec3 sigma = sqrt(max(m2 / 9.0 - mean * mean, vec3(0.0)));
	const float gamma = 1.25;
	vec3 vMin = max(boxMin, mean - gamma * sigma);
	vec3 vMax = min(boxMax, mean + gamma * sigma);
	vec3 clipped = clipAABB(vMin, vMax, mean, history);

	// Shorten the history where it got rejected (disocclusion, lighting change)
	float rejection = clamp(distance(history, clipped) * 8.0, 0.0, 1.0);
	historyLen = mix(historyLen, min(historyLen, 4.0), rejection);

	// Moving content keeps less history to avoid smearing
	float velocityPx = length(velocity * outSize);
	float maxLen = mix(maxHistory, 8.0, clamp(velocityPx / 16.0, 0.0, 1.0));

	// A sample landing close to this display pixel counts more than a distant one
	float newLen = min(historyLen + weightMax, maxLen);
	float blend = clamp(weightMax / max(newLen, 1e-4), 0.0, 1.0);

	vec3 result = ycocg2rgb(mix(clipped, current, blend));
	fragColor = vec4(max(result, vec3(0.0)), newLen / maxHistory);
}
