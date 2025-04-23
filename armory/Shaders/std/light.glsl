#ifndef _LIGHT_GLSL_
#define _LIGHT_GLSL_

#include "compiled.inc"
#include "std/brdf.glsl"
#include "std/math.glsl"
#ifdef _ShadowMap
#include "std/shadows.glsl"
#endif
#ifdef _VoxelShadow
#include "std/conetrace.glsl"
#endif
#ifdef _gbuffer2
uniform sampler2D gbuffer2;
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
				#ifdef _ShadowMapTransparent
				uniform sampler2D shadowMapSpotTransparent[1];
				#endif
				uniform mat4 LWVPSpot[1];
			#endif
		#else
			uniform samplerCubeShadow shadowMapPoint[1];
			#ifdef _ShadowMapTransparent
			uniform samplerCube shadowMapPointTransparent[1];
			#endif
			uniform vec2 lightProj;
		#endif
	#endif
	#ifdef _Clusters
		#ifdef _SingleAtlas
		//!uniform sampler2DShadow shadowMapAtlas;
		#ifdef _ShadowMapTransparent
		//!uniform sampler2D shadowMapAtlasTransparent;
		#endif
		#endif
		uniform vec2 lightProj;
		#ifdef _ShadowMapAtlas
		#ifndef _SingleAtlas
		uniform sampler2DShadow shadowMapAtlasPoint;
		#ifdef _ShadowMapTransparent
		uniform sampler2D shadowMapAtlasPointTransparent;
		#endif
		#endif
		#else
		uniform samplerCubeShadow shadowMapPoint[4];
		#ifdef _ShadowMapTransparent
		uniform samplerCube shadowMapPointTransparent[4];
		#endif
		#endif
		#ifdef _Spot
			#ifdef _ShadowMapAtlas
			#ifndef _SingleAtlas
			uniform sampler2DShadow shadowMapAtlasSpot;
			#ifdef _ShadowMapTransparent
			uniform sampler2D shadowMapAtlasSpotTransparent;
			#endif
			#endif
			#else
			uniform sampler2DShadow shadowMapSpot[4];
			#ifdef _ShadowMapTransparent
			uniform sampler2D shadowMapSpotTransparent[4];
			#endif
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
		#ifdef _ShadowMapTransparent
		uniform sampler2D shadowMapSpotTransparent[1];
		#endif
		uniform mat4 LWVPSpot[1];
	#endif
	#ifdef _Clusters
		uniform sampler2DShadow shadowMapSpot[maxLightsCluster];
		#ifdef _ShadowMapTransparent
		uniform sampler2D shadowMapSpotTransparent[maxLightsCluster];
		#endif
		uniform mat4 LWVPSpotArray[maxLightsCluster];
	#endif
#endif
#endif
#endif

vec3 sampleLight(const vec3 p, const vec3 n, const vec3 v, const float dotNV, const vec3 lp, const vec3 lightCol,
	const vec3 albedo, const float rough, const float spec, const vec3 f0
	#ifdef _ShadowMap
		, int index, float bias, bool receiveShadow, bool transparent
	#endif
	#ifdef _Spot
		, const bool isSpot, const float spotSize, float spotBlend, vec3 spotDir, vec2 scale, vec3 right
	#endif
	#ifdef _VoxelShadow
		, sampler3D voxels, sampler3D voxelsSDF, float clipmaps[10 * voxelgiClipmapCount]
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

	#ifdef _LTC
	float theta = acos(dotNV);
	vec2 tuv = vec2(rough, theta / (0.5 * PI));
	tuv = tuv * LUT_SCALE + LUT_BIAS;
	vec4 t = textureLod(sltcMat, tuv, 0.0);
	mat3 invM = mat3(
		vec3(1.0, 0.0, t.y),
		vec3(0.0, t.z, 0.0),
		vec3(t.w, 0.0, t.x));
	float ltcspec = ltcEvaluate(n, v, dotNV, p, invM, lightArea0, lightArea1, lightArea2, lightArea3);
	ltcspec *= textureLod(sltcMag, tuv, 0.0).a;
	float ltcdiff = ltcEvaluate(n, v, dotNV, p, mat3(1.0), lightArea0, lightArea1, lightArea2, lightArea3);
	vec3 direct = albedo * ltcdiff + ltcspec * spec * 0.05;
	#else
	vec3 direct = lambertDiffuseBRDF(albedo, dotNL) +
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

	#ifdef _VoxelShadow
	vec4 g2 = -textureLod(gbuffer2, gl_FragCoord.xy, 0.0);
	direct *= (1.0 - traceShadow(p, n, voxels, voxelsSDF, l, clipmaps, gl_FragCoord.xy, g2.rg).r) * voxelgiShad;
	#endif

	#ifdef _LTC
	#ifdef _ShadowMap
		if (receiveShadow) {
			#ifdef _SinglePoint
			vec4 lPos = LWVPSpotArray[0] * vec4(p + n * bias * 10, 1.0);
			direct *= shadowTest(shadowMapSpot[0],
						#ifdef _ShadowMapTransparent
							shadowMapSpotTransparent[0],
						#endif
							lPos.xyz / lPos.w, bias, transparent);
			#endif
			#ifdef _Clusters
			vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
			if (index == 0) direct *= shadowTest(shadowMapSpot[0],
				#ifdef _ShadowMapTransparent
					shadowMapSpotTransparent[0],
				#endif
					lPos.xyz / lPos.w, bias, transparent);
			else if (index == 1) direct *= shadowTest(shadowMapSpot[1],
				#ifdef _ShadowMapTransparent
					shadowMapSpotTransparent[1],
				#endif
					, lPos.xyz / lPos.w, bias, transparent);
			else if (index == 2) direct *= shadowTest(shadowMapSpot[2],
				#ifdef _ShadowMapTransparent
					shadowMapSpotTransparent[2],
				#endif
					lPos.xyz / lPos.w, bias, transparent);
			else if (index == 3) direct *= shadowTest(shadowMapSpot[3],
				#ifdef _ShadowMapTransparent
					shadowMapSpotTransparent[3],
				#endif
					lPos.xyz / lPos.w, bias, transparent);
			#endif
		}
	#endif
	return direct;
	#endif

	#ifdef _Spot
	if (isSpot) {
		direct *= spotlightMask(l, spotDir, right, scale, spotSize, spotBlend);

		#ifdef _ShadowMap
			if (receiveShadow) {
				#ifdef _SinglePoint
				vec4 lPos = LWVPSpot[0] * vec4(p + n * bias * 10, 1.0);
				direct *= shadowTest(shadowMapSpot[0],
							#ifdef _ShadowMapTransparent
									 shadowMapSpotTransparent[0],
							#endif
									lPos.xyz / lPos.w, bias, transparent);
				#endif
				#ifdef _Clusters
					vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
					#ifdef _ShadowMapAtlas
						direct *= shadowTest(
							#ifndef _SingleAtlas
							#ifdef _ShadowMapTransparent
							shadowMapAtlasSpot, shadowMapAtlasSpotTransparent
							#else
							shadowMapAtlasSpot
							#endif
							#else
							#ifdef _ShadowMapTransparent
							shadowMapAtlas, shadowMapAtlasTransparent
							#else
							shadowMapAtlas
							#endif
							#endif
							, lPos.xyz / lPos.w, bias, transparent
						);
					#else
							 if (index == 0) direct *= shadowTest(shadowMapSpot[0],
								 #ifdef _ShadowMapTransparent
									shadowMapSpotTransparent[0],
								 #endif
									lPos.xyz / lPos.w, bias, transparent);
						else if (index == 1) direct *= shadowTest(shadowMapSpot[1],
								#ifdef _ShadowMapTransparent
									shadowMapSpotTransparent[1],
								#endif
									lPos.xyz / lPos.w, bias, transparent);
						else if (index == 2) direct *= shadowTest(shadowMapSpot[2],
								#ifdef _ShadowMapTransparent
									shadowMapSpotTransparent[2],
								#endif
									lPos.xyz / lPos.w, bias, transparent);
						else if (index == 3) direct *= shadowTest(shadowMapSpot[3],
								#ifdef _ShadowMapTransparent
									shadowMapSpotTransparent[3],
								#endif
									lPos.xyz / lPos.w, bias, transparent);
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
			direct *= PCFCube(shadowMapPoint[0],
						#ifdef _ShadowMapTransparent
							shadowMapPointTransparent[0],
						#endif
							ld, -l, bias, lightProj, n, transparent);
			#endif
			#endif
			#ifdef _Clusters
				#ifdef _ShadowMapAtlas
				direct *= PCFFakeCube(
					#ifndef _SingleAtlas
					#ifdef _ShadowMapTransparent
					shadowMapAtlasPoint, shadowMapAtlasPointTransparent
					#else
					shadowMapAtlasPoint
					#endif
					#else
					#ifdef _ShadowMapTransparent
					shadowMapAtlas, shadowMapAtlasTransparent
					#else
					shadowMapAtlas
					#endif
					#endif
					, ld, -l, bias, lightProj, n, index, transparent
				);
				#else
					 if (index == 0) direct *= PCFCube(shadowMapPoint[0],
							#ifdef _ShadowMapTransparent
								shadowMapPointTransparent[0],
							#endif
								ld, -l, bias, lightProj, n, transparent);
				else if (index == 1) direct *= PCFCube(shadowMapPoint[1],
							#ifdef _ShadowMapTransparent
								shadowMapPointTransparent[1],
							#endif
								ld, -l, bias, lightProj, n, transparent);
				else if (index == 2) direct *= PCFCube(shadowMapPoint[2],
							#ifdef _ShadowMapTransparent
								shadowMapPointTransparent[2],
							#endif
								ld, -l, bias, lightProj, n, transparent);
				else if (index == 3) direct *= PCFCube(shadowMapPoint[3],
							#ifdef _ShadowMapTransparent
								shadowMapPointTransparent[3],
							#endif
								ld, -l, bias, lightProj, n, transparent);
				#endif
			#endif
		}
	#endif

	return direct;
}

#endif
