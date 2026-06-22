#ifndef _SSRS_GLSL_
#define _SSRS_GLSL_

#include "std/gbuffer.glsl"

uniform mat4 VP;

vec2 getProjectedCoord(vec3 hitCoord) {
	vec4 projectedCoord = VP * vec4(hitCoord, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	#if defined(HLSL) || defined(METAL)
	projectedCoord.y = 1.0 - projectedCoord.y;
	#endif
	return projectedCoord.xy;
}

float getDeltaDepth(vec3 hitCoord, sampler2D gbufferD, mat4 invVP, vec3 eye) {
	vec2 texCoord = getProjectedCoord(hitCoord);
	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	vec3 wpos = getPos2(invVP, depth, texCoord);
	float d1 = length(eye - wpos);
	float d2 = length(eye - hitCoord);
	return d1 - d2;
}

float traceShadowSS(vec3 dir, vec3 hitCoord, sampler2D gbufferD, mat4 invVP, vec3 eye) {
	dir *= ssrsRayStep;
	for (int i = 0; i < 4; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord, gbufferD, invVP, eye) > 0.0) return 1.0;
	}
	return 0.0;
}

#endif
