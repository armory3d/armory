#ifndef _LIGHT_GLSL_
#define _LIGHT_GLSL_

#include "compiled.inc"
#include "std/brdf.glsl"
#include "std/math.glsl"
#ifdef _ShadowMap
#include "std/shadows.glsl"
#endif
#ifdef _LTC
#include "std/ltc.glsl"
#endif
#ifdef _LightIES
#include "std/ies.glsl"
#endif
#ifdef _SSRS
#include "std/ssrs.glsl"
#endif
#ifdef _Spot
#include "std/light_common.glsl"
#endif

#ifdef _ShadowMap
	#ifdef _SinglePoint
		#ifdef _Spot
			#ifndef _LTC
				uniform sampler2DShadow shadowMapSpot[1];
				uniform mat4 LWVPSpot[1];
			#endif
		#else
			uniform samplerCubeShadow shadowMapPoint[1];
			uniform vec2 lightProj;
		#endif
	#endif
	#ifdef _Clusters
		#ifdef _SingleAtlas
		//!uniform sampler2DShadow shadowMapAtlas;
		#endif
		uniform vec2 lightProj;
		#ifdef _ShadowMapAtlas
		#ifndef _SingleAtlas
		uniform sampler2DShadow shadowMapAtlasPoint;
		#endif
		#else
		uniform samplerCubeShadow shadowMapPoint[4];
		#endif
		#ifdef _Spot
			#ifdef _ShadowMapAtlas
			#ifndef _SingleAtlas
			uniform sampler2DShadow shadowMapAtlasSpot;
			#endif
			#else
			uniform sampler2DShadow shadowMapSpot[4];
			#endif
			uniform mat4 LWVPSpotArray[maxLightsCluster];
		#endif
	#endif
#endif

#ifdef _LTC
uniform vec3 lightArea0;
uniform vec3 lightArea1;
uniform vec3 lightArea2;
uniform vec3 lightArea3;
uniform sampler2D sltcMat;
uniform sampler2D sltcMag;
#ifdef _ShadowMap
#ifndef _Spot
	#ifdef _SinglePoint
		uniform sampler2DShadow shadowMapSpot[1];
		uniform mat4 LWVPSpot[1];
	#endif
	#ifdef _Clusters
		uniform sampler2DShadow shadowMapSpot[maxLightsCluster];
		uniform mat4 LWVPSpotArray[maxLightsCluster];
	#endif
	#endif
#endif
#endif

vec3 sampleLight(const vec3 p, const vec3 n, const vec3 v, const float dotNV, const vec3 lp, const vec3 lightCol,
	const vec3 albedo, const float rough, const float spec, const vec3 f0
	#ifdef _ShadowMap
		, int index, float bias, bool receiveShadow
	#endif
	#ifdef _Spot
		, bool isSpot, float spotSize, float spotBlend, vec3 spotDir, vec2 scale, vec3 right
	#endif
	#ifdef _VoxelShadow
		, vec2 texCoord
	#endif
	#ifdef _MicroShadowing
		, float occ
	#endif
	#ifdef _SSRS
		, sampler2D gbufferD, mat4 invVP, vec3 eye
	#endif
	) {
	vec3 ld = lp - p;
	vec3 l = normalize(ld);
	vec3 h = normalize(v + l);
	float dotNH = max(0.0, dot(n, h));
	float dotVH = max(0.0, dot(v, h));
	float dotNL = max(0.0, dot(n, l));
	
	bool isArea = false;
	#ifdef _LTC
		#ifdef _Spot
			if (!isSpot && spotBlend < -0.5) isArea = true;
		#else
			isArea = true;
		#endif
	#endif

	vec3 direct;
	#ifdef _LTC
	if (isArea) {
		const float PI = 3.1415926535;
		float theta = acos(dotNV);
		vec2 tuv = vec2(rough, theta / (0.5 * PI));
		tuv = tuv * LUT_SCALE + LUT_BIAS;
		vec4 t = textureLod(sltcMat, tuv, 0.0);
		mat3 invM = mat3(
			vec3(1.0, 0.0, t.y),
			vec3(0.0, t.z, 0.0),
			vec3(t.w, 0.0, t.x));

		#if defined(_Clusters) && defined(_Spot)
		vec3 up = cross(spotDir, right);
		vec3 p0 = lp - right * scale.x + up * scale.y;
		vec3 p1 = lp + right * scale.x + up * scale.y;
		vec3 p2 = lp + right * scale.x - up * scale.y;
		vec3 p3 = lp - right * scale.x - up * scale.y;
		#else
		vec3 p0 = lightArea0;
		vec3 p1 = lightArea1;
		vec3 p2 = lightArea2;
		vec3 p3 = lightArea3;
		#endif

		float ltcspec = ltcEvaluate(n, v, dotNV, p, invM, p0, p1, p2, p3) / PI;
		ltcspec *= textureLod(sltcMag, tuv, 0.0).a;
		float ltcdiff = ltcEvaluate(n, v, dotNV, p, mat3(1.0), p0, p1, p2, p3) / PI;
		direct = albedo * ltcdiff + ltcspec * spec * 0.05;
	}
	else {
		direct = lambertDiffuseBRDF(albedo, dotNL) +
				 specularBRDF(f0, rough, dotNL, dotNH, dotNV, dotVH) * spec;
	}
	#else
	direct = lambertDiffuseBRDF(albedo, dotNL) +
				  specularBRDF(f0, rough, dotNL, dotNH, dotNV, dotVH) * spec;
	#endif
	direct *= attenuate(distance(p, lp));
	direct *= lightCol;

	#ifdef _MicroShadowing
	direct *= clamp(dotNL + 2.0 * occ * occ - 1.0, 0.0, 1.0);
	#endif

	#ifdef _SSRS
	direct *= traceShadowSS(l, p, gbufferD, invVP, eye);
	#endif

	#ifdef _LTC
	if (isArea) {
		#ifdef _ShadowMap
			if (receiveShadow) {
				#ifdef _SinglePoint
				vec4 lPos = LWVPSpot[0] * vec4(p + n * bias * 10, 1.0);
				direct *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
				#endif
				#ifdef _Clusters
				vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
				#ifdef _ShadowMapAtlas
					direct *= shadowTest(
						#ifndef _SingleAtlas
						shadowMapAtlasSpot
						#else
						shadowMapAtlas
						#endif
						, lPos.xyz / lPos.w, bias
					);
				#else
						 if (index == 0) direct *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
					else if (index == 1) direct *= shadowTest(shadowMapSpot[1], lPos.xyz / lPos.w, bias);
					else if (index == 2) direct *= shadowTest(shadowMapSpot[2], lPos.xyz / lPos.w, bias);
					else if (index == 3) direct *= shadowTest(shadowMapSpot[3], lPos.xyz / lPos.w, bias);
				#endif
				#endif
			}
		#endif
		return direct;
	}
	#endif

	#ifdef _Spot
	if (isSpot) {
		direct *= spotlightMask(l, spotDir, right, scale, spotSize, spotBlend);

		#ifdef _ShadowMap
			if (receiveShadow) {
				#ifdef _SinglePoint
				vec4 lPos = LWVPSpot[0] * vec4(p + n * bias * 10, 1.0);
				direct *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
				#endif
				#ifdef _Clusters
					vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
					#ifdef _ShadowMapAtlas
						direct *= shadowTest(
							#ifndef _SingleAtlas
							shadowMapAtlasSpot
							#else
							shadowMapAtlas
							#endif
							, lPos.xyz / lPos.w, bias
						);
					#else
							 if (index == 0) direct *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
						else if (index == 1) direct *= shadowTest(shadowMapSpot[1], lPos.xyz / lPos.w, bias);
						else if (index == 2) direct *= shadowTest(shadowMapSpot[2], lPos.xyz / lPos.w, bias);
						else if (index == 3) direct *= shadowTest(shadowMapSpot[3], lPos.xyz / lPos.w, bias);
					#endif
				#endif
			}
		#endif
		return direct;
	}
	#endif

	#ifdef _LightIES
	direct *= iesAttenuation(-l);
	#endif

	#ifdef _ShadowMap
		if (receiveShadow) {
			#ifdef _SinglePoint
			#ifndef _Spot
			direct *= PCFCube(shadowMapPoint[0], ld, -l, bias, lightProj, n);
			#endif
			#endif
			#ifdef _Clusters
				#ifdef _ShadowMapAtlas
				direct *= PCFFakeCube(
					#ifndef _SingleAtlas
					shadowMapAtlasPoint
					#else
					shadowMapAtlas
					#endif
					, ld, -l, bias, lightProj, n, index
				);
				#else
					 if (index == 0) direct *= PCFCube(shadowMapPoint[0], ld, -l, bias, lightProj, n);
				else if (index == 1) direct *= PCFCube(shadowMapPoint[1], ld, -l, bias, lightProj, n);
				else if (index == 2) direct *= PCFCube(shadowMapPoint[2], ld, -l, bias, lightProj, n);
				else if (index == 3) direct *= PCFCube(shadowMapPoint[3], ld, -l, bias, lightProj, n);
				#endif
			#endif
		}
	#endif

	return direct;
}

#endif
