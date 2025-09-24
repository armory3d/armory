#ifndef _SSRS_GLSL_
#define _SSRS_GLSL_

#include "std/gbuffer.glsl"

uniform mat4 VP;
const int   ssrsBinarySteps = 7;  // refinement steps
const float ssrsJitter = 0.125;      // per-pixel randomization scale

// Projects world position to screen space
vec2 getProjectedCoord(vec3 hitCoord) {
    vec4 projectedCoord = VP * vec4(hitCoord, 1.0);
    projectedCoord.xy /= projectedCoord.w;
    projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
#if defined(HLSL) || defined(METAL)
    projectedCoord.y = 1.0 - projectedCoord.y;
#endif
    return projectedCoord.xy;
}

// Compute delta depth (positive means ray behind geometry)
float getDeltaDepth(vec3 hitCoord, sampler2D gbufferD, mat4 invVP, vec3 eye) {
    vec2 texCoord = getProjectedCoord(hitCoord);
    if (texCoord.x < 0.0 || texCoord.x > 1.0 ||
        texCoord.y < 0.0 || texCoord.y > 1.0) return 1e9; // offscreen

    float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
    vec3 wpos = getPos2(invVP, depth, texCoord);

    float d1 = length(eye - wpos);
    float d2 = length(eye - hitCoord);
    return d1 - d2;
}

// Binary search refinement around last step
vec3 refineHit(vec3 prev, vec3 curr, sampler2D gbufferD, mat4 invVP, vec3 eye) {
    vec3 a = prev, b = curr;
    for (int i = 0; i < ssrsBinarySteps; i++) {
        vec3 mid = 0.5 * (a + b);
        float delta = getDeltaDepth(mid, gbufferD, invVP, eye);
        if (delta > 0.0) {
            b = mid; // behind
        } else {
            a = mid; // in front
        }
    }
    return 0.5 * (a + b);
}

// Radical inverse with base 2 (bit-reversal)
float radicalInverse_VdC(uint bits) {
    bits = (bits << 16u) | (bits >> 16u);
    bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
    bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
    bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
    bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
    return float(bits) * 2.3283064365386963e-10; // / 2^32
}

// Hammersley sequence in 2D
vec2 hammersley2D(uint i, uint N) {
    return vec2(float(i) / float(N), radicalInverse_VdC(i));
}

// Raytrace screen-space shadow
float trace(vec3 dir, vec3 hitCoord, sampler2D gbufferD, mat4 invVP, vec3 eye, vec2 rand) {
	vec3 start = hitCoord + normalize(dir) * rand.x * ssrsRayStep;
	vec3 stepDir = normalize(dir) * ssrsRayStep;

    vec3 prev = start;
    for (int i = 0; i < ssrsMaxSteps; i++) {
        vec3 curr = prev + stepDir;
        float delta = getDeltaDepth(curr, gbufferD, invVP, eye);

        if (delta > -ssrsThickness && delta < ssrsThickness) {
            // Refine intersection
            vec3 hit = refineHit(prev, curr, gbufferD, invVP, eye);
            // Found occluder → shadowed
            return 0.0;
        }

        prev = curr;
    }

    return 1.0; // no hit → unshadowed
}

float traceShadowSS(vec3 dir, vec3 hitCoord, sampler2D gbufferD, sampler2D gbuffer0, mat4 invVP, vec3 eye, vec2 rand, vec2 texCoord) {
    float shadowSum = 0.0;

    for (uint i = 0u; i < uint(ssrsSamples); i++) {
		vec2 sampleRand = hammersley2D(uint(i), uint(ssrsSamples));
		shadowSum += trace(dir, hitCoord, gbufferD, invVP, eye, sampleRand);
	}

    shadowSum /= float(ssrsSamples);
    return shadowSum;
}

#endif
