// Temporal accumulation of the SSR voxel fallback (_SSRVoxelFallback).
// The TAA jitter moves the reflected rays every frame: pixels at the edge
// of a hit flip between SSR and the voxel cones, and the reflected image
// (the previous lit frame, not anti-aliased) shimmers. Blend the result
// (color, confidence) into a reprojected history, clamped to the current
// neighborhood so moving reflections do not ghost.

#version 450

#include "compiled.inc"

uniform sampler2D tex;  // Current SSR result: color, confidence
uniform sampler2D hist; // Accumulated result of the previous frame
uniform sampler2D gbufferD;
#ifdef _Veloc
uniform sampler2D sveloc;
#else
uniform mat4 invVP;
uniform mat4 prevVP;
#endif

in vec2 texCoord;
out vec4 fragColor;

// Weight of the current frame
const float currentWeight = 0.1;

vec2 getPrevUV(const vec2 uv) {
	#ifdef _Veloc
	// Same convention as the TAA and SSGI passes
	vec2 velocity = -textureLod(sveloc, uv, 0.0).rg;
	#ifdef _InvY
	velocity.y = -velocity.y;
	#endif
	return uv + velocity;
	#else
	// Camera-only reprojection of the reflecting surface
	float depth = textureLod(gbufferD, uv, 0.0).r * 2.0 - 1.0;
	vec4 wpos = invVP * vec4(uv * 2.0 - 1.0, depth, 1.0);
	wpos /= wpos.w;
	vec4 prevPos = prevVP * vec4(wpos.xyz, 1.0);
	vec2 prevUV = (prevPos.xy / prevPos.w) * 0.5 + 0.5;
	#ifdef _InvY
	prevUV.y = 1.0 - prevUV.y;
	#endif
	return prevUV;
	#endif
}

void main() {
	vec4 current = textureLod(tex, texCoord, 0.0);

	// Neighborhood of the current result, the history is clamped to it
	vec2 texel = 1.0 / vec2(textureSize(tex, 0));
	vec4 nmin = current;
	vec4 nmax = current;
	for (int j = -1; j <= 1; j++) {
		for (int i = -1; i <= 1; i++) {
			vec4 s = textureLod(tex, texCoord + vec2(i, j) * texel, 0.0);
			nmin = min(nmin, s);
			nmax = max(nmax, s);
		}
	}

	vec2 prevUV = getPrevUV(texCoord);
	if (prevUV.x < 0.0 || prevUV.x > 1.0 || prevUV.y < 0.0 || prevUV.y > 1.0) {
		fragColor = current;
		return;
	}
	vec4 history = textureLod(hist, prevUV, 0.0);
	// The history starts uninitialized, a NaN would stick forever
	if (any(isnan(history)) || any(isinf(history))) history = current;
	history = clamp(history, nmin, nmax);

	fragColor = mix(history, current, currentWeight);
}
