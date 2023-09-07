#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#ifdef _Clusters
#include "std/clusters.glsl"
#endif
#ifdef _Irr
#include "std/shirr.glsl"
#endif
#ifdef _VoxelAOvar
#include "std/conetrace.glsl"
#endif
#ifdef _SSS
#include "std/sss.glsl"
#endif
#ifdef _SSRS
#include "std/ssrs.glsl"
#endif

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
#ifdef _gbuffer2
	uniform sampler2D gbuffer2;
#endif
#ifdef _EmissionShaded
	uniform sampler2D gbufferEmission;
#endif

#ifdef _VoxelAOvar
uniform sampler3D voxels;
#endif
#ifdef _VoxelGITemporal
uniform sampler3D voxelsLast;
uniform float voxelBlend;
#endif
#ifdef _VoxelGICam
uniform vec3 eyeSnap;
#endif

uniform float envmapStrength;
#ifdef _Irr
uniform vec4 shirr[7];
#endif
#ifdef _Brdf
uniform sampler2D senvmapBrdf;
#endif
#ifdef _Rad
uniform sampler2D senvmapRadiance;
uniform int envmapNumMipmaps;
#endif
#ifdef _EnvCol
uniform vec3 backgroundCol;
#endif

#ifdef _SSAO
uniform sampler2D ssaotex;
#endif

#ifdef _SSS
uniform vec2 lightPlane;
#endif

#ifdef _SSRS
//!uniform mat4 VP;
uniform mat4 invVP;
#endif

#ifdef _LightIES
//!uniform sampler2D texIES;
#endif

#ifdef _SMSizeUniform
//!uniform vec2 smSizeUniform;
#endif

#ifdef _LTC
//!uniform vec3 lightArea0;
//!uniform vec3 lightArea1;
//!uniform vec3 lightArea2;
//!uniform vec3 lightArea3;
//!uniform sampler2D sltcMat;
//!uniform sampler2D sltcMag;
#ifdef _ShadowMap
	#ifdef _SinglePoint
	//!uniform sampler2DShadow shadowMapSpot[1];
	//!uniform mat4 LWVPSpot[1];
	#endif
	#ifdef _Clusters
	//!uniform sampler2DShadow shadowMapSpot[4];
	//!uniform mat4 LWVPSpotArray[4];
	#endif
#endif
#endif

uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;

#ifdef _Clusters
uniform vec4 lightsArray[maxLights * 3];
	#ifdef _Spot
	uniform vec4 lightsArraySpot[maxLights * 2];
	#endif
uniform sampler2D clustersData;
uniform vec2 cameraPlane;
#endif

#ifdef _ShadowMap
#ifdef _SinglePoint
	#ifdef _Spot
	//!uniform sampler2DShadow shadowMapSpot[1];
	//!uniform mat4 LWVPSpot[1];
	#else
	//!uniform samplerCubeShadow shadowMapPoint[1];
	//!uniform vec2 lightProj;
	#endif
#endif
#ifdef _Clusters
	#ifdef _ShadowMapAtlas
		#ifdef _SingleAtlas
		uniform sampler2DShadow shadowMapAtlas;
		#endif
	#endif
	#ifdef _ShadowMapAtlas
		#ifndef _SingleAtlas
		//!uniform sampler2DShadow shadowMapAtlasPoint;
		#endif
		//!uniform vec4 pointLightDataArray[4];
	#else
		//!uniform samplerCubeShadow shadowMapPoint[4];
	#endif
	//!uniform vec2 lightProj;
	#ifdef _Spot
		#ifdef _ShadowMapAtlas
		#ifndef _SingleAtlas
		//!uniform sampler2DShadow shadowMapAtlasSpot;
		#endif
		#else
		//!uniform sampler2DShadow shadowMapSpot[4];
		#endif
	//!uniform mat4 LWVPSpotArray[4];
	#endif
#endif
#endif

#ifdef _Sun
uniform vec3 sunDir;
uniform vec3 sunCol;
	#ifdef _ShadowMap
	#ifdef _ShadowMapAtlas
	#ifndef _SingleAtlas
	uniform sampler2DShadow shadowMapAtlasSun;
	#endif
	#else
	uniform sampler2DShadow shadowMap;
	#endif
	uniform float shadowsBias;
	#ifdef _CSM
	//!uniform vec4 casData[shadowmapCascades * 4 + 4];
	#else
	uniform mat4 LWVP;
	#endif
	#endif // _ShadowMap
#endif

#ifdef _SinglePoint // Fast path for single light
uniform vec3 pointPos;
uniform vec3 pointCol;
	#ifdef _ShadowMap
	uniform float pointBias;
	#endif
	#ifdef _Spot
	uniform vec3 spotDir;
	uniform vec3 spotRight;
	uniform vec4 spotData;
	#endif
#endif

#ifdef _LightClouds
uniform sampler2D texClouds;
uniform float time;
#endif

#include "std/light.glsl"

in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

void main() {
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0); // Normal.xy, roughness, metallic/matid

	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	float roughness = g0.b;
	float metallic;
	uint matid;
	unpackFloatInt16(g0.a, metallic, matid);

	vec4 g1 = textureLod(gbuffer1, texCoord, 0.0); // Basecolor.rgb, spec/occ
	vec2 occspec = unpackFloat2(g1.a);
	vec3 albedo = surfaceAlbedo(g1.rgb, metallic); // g1.rgb - basecolor
	vec3 f0 = surfaceF0(g1.rgb, metallic);

	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	vec3 p = getPos(eye, eyeLook, normalize(viewRay), depth, cameraProj);
	vec3 v = normalize(eye - p);
	float dotNV = max(dot(n, v), 0.0);

#ifdef _gbuffer2
	vec4 g2 = textureLod(gbuffer2, texCoord, 0.0);
#endif

#ifdef _MicroShadowing
	occspec.x = mix(1.0, occspec.x, dotNV); // AO Fresnel
#endif

#ifdef _Brdf
	vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(vec2(dotNV, 1.0 - roughness) * 256.0), 0).xy;
#endif

	// Envmap
#ifdef _Irr

	vec3 envl = shIrradiance(n, shirr);

	#ifdef _gbuffer2
		if (g2.b < 0.5) {
			envl = envl;
		} else {
			envl = vec3(0.0);
		}
	#endif

	#ifdef _EnvTex
		envl /= PI;
	#endif
#else
	vec3 envl = vec3(0.0);
#endif

#ifdef _Rad
	vec3 reflectionWorld = reflect(-v, n);
	float lod = getMipFromRoughness(roughness, envmapNumMipmaps);
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
#endif

#ifdef _EnvLDR
	envl.rgb = pow(envl.rgb, vec3(2.2));
	#ifdef _Rad
		prefilteredColor = pow(prefilteredColor, vec3(2.2));
	#endif
#endif

	envl.rgb *= albedo;

#ifdef _Brdf
	envl.rgb *= 1.0 - (f0 * envBRDF.x + envBRDF.y); //LV: We should take refracted light into account
#endif

#ifdef _Rad // Indirect specular
	envl.rgb += prefilteredColor * (f0 * envBRDF.x + envBRDF.y); //LV: Removed "1.5 * occspec.y". Specular should be weighted only by FV LUT
#else
	#ifdef _EnvCol
	envl.rgb += backgroundCol * (f0 * envBRDF.x + envBRDF.y); //LV: Eh, what's the point of weighting it only by F0?
	#endif
#endif

	envl.rgb *= envmapStrength * occspec.x;

#ifdef _VoxelAOvar

	#ifdef _VoxelGICam
	vec3 voxpos = (p - eyeSnap) / voxelgiHalfExtents;
	#else
	vec3 voxpos = p / voxelgiHalfExtents;
	#endif

	#ifndef _VoxelAONoTrace
	#ifdef _VoxelGITemporal
	envl.rgb *= 1.0 - (traceAO(voxpos, n, voxels) * voxelBlend +
					   traceAO(voxpos, n, voxelsLast) * (1.0 - voxelBlend));
	#else
	envl.rgb *= 1.0 - traceAO(voxpos, n, voxels);
	#endif
	#endif

#endif

	fragColor.rgb = envl;

#ifdef _SSAO
	// #ifdef _RTGI
	// fragColor.rgb *= textureLod(ssaotex, texCoord, 0.0).rgb;
	// #else
	fragColor.rgb *= textureLod(ssaotex, texCoord, 0.0).r;
	// #endif
#endif

#ifdef _EmissionShadeless
	if (matid == 1) { // pure emissive material, color stored in basecol
		fragColor.rgb += g1.rgb;
		fragColor.a = 1.0; // Mark as opaque
		return;
	}
#endif
#ifdef _EmissionShaded
	#ifdef _EmissionShadeless
	else {
	#endif
		vec3 emission = textureLod(gbufferEmission, texCoord, 0.0).rgb;
		fragColor.rgb += emission;
	#ifdef _EmissionShadeless
	}
	#endif
#endif

	// Show voxels
	// vec3 origin = vec3(texCoord * 2.0 - 1.0, 0.99);
	// vec3 direction = vec3(0.0, 0.0, -1.0);
	// vec4 color = vec4(0.0f);
	// for(uint step = 0; step < 400 && color.a < 0.99f; ++step) {
	// 	vec3 point = origin + 0.005 * step * direction;
	// 	color += (1.0f - color.a) * textureLod(voxels, point * 0.5 + 0.5, 0);
	// }
	// fragColor.rgb += color.rgb;

	// Show SSAO
	// fragColor.rgb = texture(ssaotex, texCoord).rrr;

#ifdef _Sun
	vec3 sh = normalize(v + sunDir);
	float sdotNH = max(0.0, dot(n, sh));
	float sdotVH = max(0.0, dot(v, sh));
	float sdotNL = max(0.0, dot(n, sunDir));
	float svisibility = 1.0;
	vec3 sdirect = lambertDiffuseBRDF(albedo, sdotNL) +
	               specularBRDF(f0, roughness, sdotNL, sdotNH, dotNV, sdotVH) * occspec.y;

	#ifdef _ShadowMap
		#ifdef _CSM
			svisibility = shadowTestCascade(
				#ifdef _ShadowMapAtlas
					#ifndef _SingleAtlas
					shadowMapAtlasSun
					#else
					shadowMapAtlas
					#endif
				#else
				shadowMap
				#endif
				, eye, p + n * shadowsBias * 10, shadowsBias
			);
		#else
			vec4 lPos = LWVP * vec4(p + n * shadowsBias * 100, 1.0);
			if (lPos.w > 0.0) svisibility = shadowTest(
				#ifdef _ShadowMapAtlas
					#ifndef _SingleAtlas
					shadowMapAtlasSun
					#else
					shadowMapAtlas
					#endif
				#else
				shadowMap
				#endif
				, lPos.xyz / lPos.w, shadowsBias
			);
		#endif
	#endif

	#ifdef _VoxelAOvar
	#ifdef _VoxelShadow
	svisibility *= 1.0 - traceShadow(voxels, voxpos, sunDir);
	#endif
	#endif

	#ifdef _SSRS
	// vec2 coords = getProjectedCoord(hitCoord);
	// vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	// float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);
	svisibility *= traceShadowSS(sunDir, p, gbufferD, invVP, eye);
	#endif

	#ifdef _LightClouds
	svisibility *= textureLod(texClouds, vec2(p.xy / 100.0 + time / 80.0), 0.0).r * dot(n, vec3(0,0,1));
	#endif

	#ifdef _MicroShadowing
	// See https://advances.realtimerendering.com/other/2016/naughty_dog/NaughtyDog_TechArt_Final.pdf
	svisibility *= clamp(sdotNL + 2.0 * occspec.x * occspec.x - 1.0, 0.0, 1.0);
	#endif

	fragColor.rgb += sdirect * svisibility * sunCol;

//	#ifdef _Hair // Aniso
// 	if (matid == 2) {
// 		const float shinyParallel = roughness;
// 		const float shinyPerpendicular = 0.1;
// 		const vec3 v = vec3(0.99146, 0.11664, 0.05832);
// 		vec3 T = abs(dot(n, v)) > 0.99999 ? cross(n, vec3(0.0, 1.0, 0.0)) : cross(n, v);
// 		fragColor.rgb = orenNayarDiffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH) + wardSpecular(n, h, dotNL, dotNV, dotNH, T, shinyParallel, shinyPerpendicular) * spec;
// 	}
//	#endif

	#ifdef _SSS
	if (matid == 2) {
		#ifdef _CSM
		int casi, casindex;
		mat4 LWVP = getCascadeMat(distance(eye, p), casi, casindex);
		#endif
		fragColor.rgb += fragColor.rgb * SSSSTransmittance(
			LWVP, p, n, sunDir, lightPlane.y,
			#ifdef _ShadowMapAtlas
				#ifndef _SingleAtlas
				shadowMapAtlasSun
				#else
				shadowMapAtlas
				#endif
			#else
			shadowMap
			#endif
		);
	}
	#endif

#endif // _Sun

#ifdef _SinglePoint

	fragColor.rgb += sampleLight(
		p, n, v, dotNV, pointPos, pointCol, albedo, roughness, occspec.y, f0
		#ifdef _ShadowMap
			, 0, pointBias, true
		#endif
		#ifdef _Spot
		, true, spotData.x, spotData.y, spotDir, spotData.zw, spotRight
		#endif
		#ifdef _VoxelAOvar
		#ifdef _VoxelShadow
		, voxels, voxpos
		#endif
		#endif
		#ifdef _MicroShadowing
		, occspec.x
		#endif
		#ifdef _SSRS
		, gbufferD, invVP, eye
		#endif
	);

	#ifdef _Spot
	#ifdef _SSS
	if (matid == 2) fragColor.rgb += fragColor.rgb * SSSSTransmittance(LWVPSpot0, p, n, normalize(pointPos - p), lightPlane.y, shadowMapSpot[0]);
	#endif
	#endif

#endif

#ifdef _Clusters
	float viewz = linearize(depth * 0.5 + 0.5, cameraProj);
	int clusterI = getClusterI(texCoord, viewz, cameraPlane);
	int numLights = int(texelFetch(clustersData, ivec2(clusterI, 0), 0).r * 255);

	#ifdef HLSL
	viewz += textureLod(clustersData, vec2(0.0), 0.0).r * 1e-9; // TODO: krafix bug, needs to generate sampler
	#endif

	#ifdef _Spot
	int numSpots = int(texelFetch(clustersData, ivec2(clusterI, 1 + maxLightsCluster), 0).r * 255);
	int numPoints = numLights - numSpots;
	#endif

	for (int i = 0; i < min(numLights, maxLightsCluster); i++) {
		int li = int(texelFetch(clustersData, ivec2(clusterI, i + 1), 0).r * 255);
		fragColor.rgb += sampleLight(
			p,
			n,
			v,
			dotNV,
			lightsArray[li * 3].xyz, // lp
			lightsArray[li * 3 + 1].xyz, // lightCol
			albedo,
			roughness,
			occspec.y,
			f0
			#ifdef _ShadowMap
				// light index, shadow bias, cast_shadows
				, li, lightsArray[li * 3 + 2].x, lightsArray[li * 3 + 2].z != 0.0
			#endif
			#ifdef _Spot
			, lightsArray[li * 3 + 2].y != 0.0
			, lightsArray[li * 3 + 2].y // spot size (cutoff)
			, lightsArraySpot[li * 2].w // spot blend (exponent)
			, lightsArraySpot[li * 2].xyz // spotDir
			, vec2(lightsArray[li * 3].w, lightsArray[li * 3 + 1].w) // scale
			, lightsArraySpot[li * 2 + 1].xyz // right
			#endif
			#ifdef _VoxelAOvar
			#ifdef _VoxelShadow
			, voxels, voxpos
			#endif
			#endif
			#ifdef _MicroShadowing
			, occspec.x
			#endif
			#ifdef _SSRS
			, gbufferD, invVP, eye
			#endif
		);
	}
#endif // _Clusters

	fragColor.a = 1.0; // Mark as opaque
}
