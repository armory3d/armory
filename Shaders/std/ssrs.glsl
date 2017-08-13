#include "../std/gbuffer.glsl"

uniform mat4 VP;

vec2 getProjectedCoord(vec3 hitCoord) {
	vec4 projectedCoord = VP * vec4(hitCoord, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	#ifdef _InvY
	projectedCoord.y = 1.0 - projectedCoord.y;
	#endif
	return projectedCoord.xy;
}

float getDeltaDepth(vec3 hitCoord, sampler2D gbuffer0, mat4 invVP, vec3 eye) {
	vec2 texCoord = getProjectedCoord(hitCoord);
	// #ifdef _InvY // D3D
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// #else
	// TODO: store_depth
	vec4 g0 = texture(gbuffer0, texCoord);
	float depth = (1.0 - g0.a) * 2.0 - 1.0;
	// #endif
	vec3 wpos = getPos2(invVP, depth, texCoord);
	float d1 = length(eye - wpos);
	float d2 = length(eye - hitCoord);
	return d1 - d2;
}

float traceShadowSS(vec3 dir, vec3 hitCoord, sampler2D gbuffer0, mat4 invVP, vec3 eye) {
	dir *= ssrsRayStep;
	// for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord, gbuffer0, invVP, eye) > 0.0) return 0.6;
		hitCoord += dir;
		if (getDeltaDepth(hitCoord, gbuffer0, invVP, eye) > 0.0) return 0.7;
		hitCoord += dir;
		if (getDeltaDepth(hitCoord, gbuffer0, invVP, eye) > 0.0) return 0.8;
		hitCoord += dir;
		if (getDeltaDepth(hitCoord, gbuffer0, invVP, eye) > 0.0) return 0.9;
	//}
	return 1.0;
}
