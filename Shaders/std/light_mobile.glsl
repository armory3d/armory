#ifndef _LIGHT_MOBILE_GLSL_
#define _LIGHT_MOBILE_GLSL_

#include "compiled.inc"
#include "std/brdf.glsl"
#ifdef _ShadowMap
#include "std/shadows.glsl"
#endif

#ifdef _ShadowMap
	#ifdef _ShadowMapCube
	uniform vec2 lightProj;
	// uniform samplerCubeShadow shadowMap0; //arm_dev
	uniform samplerCube shadowMap0;
	#else
	// uniform sampler2DShadow shadowMap0; //arm_dev
	uniform sampler2D shadowMap0;
	uniform mat4 LWVP0;
	#endif
	#ifdef _Spot
	uniform sampler2D shadowMapSpot0;
	uniform mat4 LWVPSpot0;
	#endif
#endif

vec3 sampleLight(const vec3 p, const vec3 n, const vec3 v, const float dotNV, const vec3 lp, const vec3 lightCol,
	const vec3 albedo, const float rough, const float spec, const vec3 f0
	#ifdef _ShadowMap
		, float bias
	#endif
	#ifdef _Spot
		, bool isSpot, float spotA, float spotB, vec3 spotDir
	#endif
	) {
	vec3 ld = lp - p;
	vec3 l = normalize(ld);
	vec3 h = normalize(v + l);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);
	float dotNL = dot(n, l);

	vec3 direct = albedo * max(dotNL, 0.0) +
				  specularBRDF(f0, rough, dotNL, dotNH, dotNV, dotVH) * spec;

	direct *= lightCol;
	direct *= attenuate(distance(p, lp));

	#ifdef _Spot
	if (isSpot) {
		float spotEffect = dot(spotDir, l); // lightDir
		// x - cutoff, y - cutoff - exponent
		if (spotEffect < spotA) {
			direct *= smoothstep(spotB, spotA, spotEffect);
		}
		#ifdef _ShadowMap
		vec4 lPos = LWVPSpot0 * vec4(p + n * bias * 10, 1.0);
		if (lPos.w > 0.0) {
			direct *= shadowTest(shadowMapSpot0, lPos.xyz / lPos.w, bias, shadowmapSize);
		}
		#endif
		return direct;
	}
	#endif

	#ifdef _ShadowMap
		#ifdef _ShadowMapCube
		direct *= PCFCube(shadowMap0, ld, -l, bias, lightProj, n);
		#else
		vec4 lPos = LWVP0 * vec4(p + n * bias * 10, 1.0);
		if (lPos.w > 0.0) {
			vec2 smSize = shadowmapSize;
			direct *= shadowTest(shadowMap0, lPos.xyz / lPos.w, bias, smSize);
		}
		#endif
	#endif

	return direct;
}

#endif
