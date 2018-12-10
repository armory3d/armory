#ifndef _LIGHT_MOBILE_GLSL_
#define _LIGHT_MOBILE_GLSL_

#include "compiled.inc"
#include "std/brdf.glsl"
#ifdef _ShadowMap
#include "std/shadows.glsl"
#endif

#ifdef _ShadowMap
	uniform vec2 lightProj;
	// uniform samplerCubeShadow shadowMap0; //arm_dev
	uniform samplerCube shadowMap0;
	uniform samplerCube shadowMap1;
	uniform samplerCube shadowMap2;
	uniform samplerCube shadowMap3;
	#ifdef _Spot
	uniform sampler2D shadowMapSpot0;
	uniform sampler2D shadowMapSpot1;
	uniform sampler2D shadowMapSpot2;
	uniform sampler2D shadowMapSpot3;
	uniform mat4 LWVPSpot0;
	uniform mat4 LWVPSpot1;
	uniform mat4 LWVPSpot2;
	uniform mat4 LWVPSpot3;
	#endif
#endif

vec3 sampleLight(const vec3 p, const vec3 n, const vec3 v, const float dotNV, const vec3 lp, const vec3 lightCol,
	const vec3 albedo, const float rough, const float spec, const vec3 f0
	#ifdef _ShadowMap
		, int index, float bias
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
	if (index == 0) direct *= PCFCube(shadowMap0, ld, -l, bias, lightProj, n);
	else if (index == 1) direct *= PCFCube(shadowMap1, ld, -l, bias, lightProj, n);
	else if (index == 2) direct *= PCFCube(shadowMap2, ld, -l, bias, lightProj, n);
	else if (index == 3) direct *= PCFCube(shadowMap3, ld, -l, bias, lightProj, n);
	#endif

	return direct;
}

#endif
