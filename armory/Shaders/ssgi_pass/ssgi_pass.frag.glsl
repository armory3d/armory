// Projection-Artifact-Free SSGI
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/brdf.glsl"
#include "std/math.glsl"
#ifdef _Clusters
#include "std/clusters.glsl"
#endif
#ifdef _ShadowMap
#include "std/shadows.glsl"
#endif
#ifdef _LTC
#include "std/ltc.glsl"
#endif
#ifdef _LightIES
#include "std/ies.glsl"
#endif
#ifdef _Spot
#include "std/light_common.glsl"
#endif

uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D gbufferD;
#ifdef _EmissionShaded
uniform sampler2D gbufferEmission;
#endif
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform mat4 invVP;

#ifdef _SMSizeUniform
//!uniform vec2 smSizeUniform;
#endif

#ifdef _Clusters
uniform vec4 lightsArray[maxLights * 3];
	#ifdef _Spot
	uniform vec4 lightsArraySpot[maxLights * 2];
	#endif
uniform sampler2D clustersData;
uniform vec2 cameraPlane;
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

#ifdef _CPostprocess
    uniform vec3 PPComp12;
#endif

#ifdef _ShadowMap
	#ifdef _SinglePoint
		#ifdef _Spot
			#ifndef _LTC
				uniform sampler2DShadow shadowMapSpot[1];
				uniform sampler2D shadowMapSpotTransparent[1];
				uniform mat4 LWVPSpot[1];
			#endif
		#else
			uniform samplerCubeShadow shadowMapPoint[1];
			uniform samplerCube shadowMapPointTransparent[1];
			uniform vec2 lightProj;
		#endif
	#endif
	#ifdef _Clusters
		#ifdef _SingleAtlas
		uniform sampler2DShadow shadowMapAtlas;
		uniform sampler2D shadowMapAtlasTransparent;
		#endif
		uniform vec2 lightProj;
		#ifdef _ShadowMapAtlas
		#ifndef _SingleAtlas
		uniform sampler2DShadow shadowMapAtlasPoint;
		uniform sampler2D shadowMapAtlasPointTransparent;
		#endif
		//!uniform vec4 pointLightDataArray[maxLightsCluster * 6];
		#else
		uniform samplerCubeShadow shadowMapPoint[4];
		uniform samplerCube shadowMapPointTransparent[4];
		#endif
		#ifdef _Spot
			#ifdef _ShadowMapAtlas
			#ifndef _SingleAtlas
			uniform sampler2DShadow shadowMapAtlasSpot;
			uniform sampler2D shadowMapAtlasSpotTransparent;
			#endif
			#else
			uniform sampler2DShadow shadowMapSpot[4];
			uniform sampler2D shadowMapSpotTransparent[4];
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
		uniform sampler2D shadowMapSpotTransparent[1];
		uniform mat4 LWVPSpot[1];
	#endif
	#ifdef _Clusters
		uniform sampler2DShadow shadowMapSpot[maxLightsCluster];
		uniform sampler2D shadowMapSpotTransparent[maxLightsCluster];
		uniform mat4 LWVPSpotArray[maxLightsCluster];
	#endif
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
	uniform sampler2D shadowMapAtlasSunTransparent;
	#endif
	#else
	uniform sampler2DShadow shadowMap;
	uniform sampler2D shadowMapTransparent;
	#endif
	uniform float shadowsBias;
	#ifdef _CSM
	//!uniform vec4 casData[shadowmapCascades * 4 + 4];
	#else
	uniform mat4 LWVP;
	#endif
	#endif // _ShadowMap
#endif

vec3 sampleLight(const vec3 p, const vec3 n, const vec3 lp, const vec3 lightCol
	#ifdef _ShadowMap
		, int index, float bias, bool receiveShadow, bool transparent
	#endif
	#ifdef _Spot
		, const bool isSpot, const float spotSize, float spotBlend, vec3 spotDir, vec2 scale, vec3 right
	#endif
	) {

	vec3 ld = lp - p;
	vec3 l = normalize(ld);

	vec3 visibility = lightCol;
	visibility *= attenuate(distance(p, lp));

	#ifdef _LTC
	#ifdef _ShadowMap
		if (receiveShadow) {
			#ifdef _SinglePoint
			vec4 lPos = LWVPSpotArray[0] * vec4(p + n * bias * 10, 1.0);
			visibility *= shadowTest(shadowMapSpot[0], shadowMapSpotTransparent[0], lPos.xyz / lPos.w, bias, transparent);
			#endif
			#ifdef _Clusters
			vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
			if (index == 0) visibility *= shadowTest(shadowMapSpot[0], shadowMapSpotTransparent[0], lPos.xyz / lPos.w, bias, transparent);
			else if (index == 1) visibility *= shadowTest(shadowMapSpot[1], shadowMapSpotTransparent[1], lPos.xyz / lPos.w, bias, transparent);
			else if (index == 2) visibility *= shadowTest(shadowMapSpot[2], shadowMapSpotTransparent[2], lPos.xyz / lPos.w, bias, transparent);
			else if (index == 3) visibility *= shadowTest(shadowMapSpot[3], shadowMapSpotTransparent[3], lPos.xyz / lPos.w, bias, transparent);
			#endif
		}
	#endif
	return visibility;
	#endif

	#ifdef _Spot
	if (isSpot) {
		visibility *= spotlightMask(l, spotDir, right, scale, spotSize, spotBlend);

		#ifdef _ShadowMap
			if (receiveShadow) {
				#ifdef _SinglePoint
				vec4 lPos = LWVPSpot[0] * vec4(p + n * bias * 10, 1.0);
				visibility *= shadowTest(shadowMapSpot[0], shadowMapSpotTransparent[0], lPos.xyz / lPos.w, bias, transparent);
				#endif
				#ifdef _Clusters
					vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
					#ifdef _ShadowMapAtlas
						visibility *= shadowTest(
							#ifndef _SingleAtlas
							shadowMapAtlasSpot, shadowMapAtlasSpotTransparent
							#else
							shadowMapAtlas, shadowMapAtlasTransparent
							#endif
							, lPos.xyz / lPos.w, bias, transparent
						);
					#else
							 if (index == 0) visibility *= shadowTest(shadowMapSpot[0], shadowMapSpotTransparent[0], lPos.xyz / lPos.w, bias, transparent);
						else if (index == 1) visibility *= shadowTest(shadowMapSpot[1], shadowMapSpotTransparent[1], lPos.xyz / lPos.w, bias, transparent);
						else if (index == 2) visibility *= shadowTest(shadowMapSpot[2], shadowMapSpotTransparent[2], lPos.xyz / lPos.w, bias, transparent);
						else if (index == 3) visibility *= shadowTest(shadowMapSpot[3], shadowMapSpotTransparent[3], lPos.xyz / lPos.w, bias, transparent);
					#endif
				#endif
			}
		#endif
		return visibility;
	}
	#endif

	#ifdef _LightIES
	visibility *= iesAttenuation(-l);
	#endif

	#ifdef _ShadowMap
		if (receiveShadow) {
			#ifdef _SinglePoint
			#ifndef _Spot
			visibility *= PCFCube(shadowMapPoint[0], shadowMapPointTransparent[0], ld, -l, bias, lightProj, n, transparent);
			#endif
			#endif
			#ifdef _Clusters
				#ifdef _ShadowMapAtlas
				visibility *= PCFFakeCube(
					#ifndef _SingleAtlas
					shadowMapAtlasPoint, shadowMapAtlasPointTransparent
					#else
					shadowMapAtlas, shadowMapAtlasTransparent
					#endif
					, ld, -l, bias, lightProj, n, index, transparent
				);
				#else
					 if (index == 0) visibility *= PCFCube(shadowMapPoint[0], shadowMapPointTransparent[0], ld, -l, bias, lightProj, n, transparent);
				else if (index == 1) visibility *= PCFCube(shadowMapPoint[1], shadowMapPointTransparent[1], ld, -l, bias, lightProj, n, transparent);
				else if (index == 2) visibility *= PCFCube(shadowMapPoint[2], shadowMapPointTransparent[2], ld, -l, bias, lightProj, n, transparent);
				else if (index == 3) visibility *= PCFCube(shadowMapPoint[3], shadowMapPointTransparent[3], ld, -l, bias, lightProj, n, transparent);
				#endif
			#endif
		}
	#endif

	return visibility;
}


in vec2 texCoord;
in vec3 viewRay;
out vec3 fragColor;

vec3 getBaseColor(vec2 uv) {
    return textureLod(gbuffer1, uv, 0.0).rgb;
}

vec3 getWorldPos(vec2 uv, float depth) {
    vec4 pos = invVP * vec4(uv * 2.0 - 1.0, depth, 1.0);
    return pos.xyz / pos.w;
}

vec3 getVisibility(vec3 p, vec3 n, float depth, vec2 uv) {
		vec3 visibility = vec3(0.0);
#ifdef _Sun
	#ifdef _ShadowMap
		#ifdef _CSM
			visibility = shadowTestCascade(
				#ifdef _ShadowMapAtlas
					#ifndef _SingleAtlas
					shadowMapAtlasSun, shadowMapAtlasSunTransparent
					#else
					shadowMapAtlas, shadowMapAtlasTransparent
					#endif
				#else
				shadowMap, shadowMapTransparent
				#endif
				, eye, p + n * shadowsBias * 10, shadowsBias, false
			);
		#else
			vec4 lPos = LWVP * vec4(p + n * shadowsBias * 100, 1.0);
			if (lPos.w > 0.0) {
				visibility = shadowTest(
					#ifdef _ShadowMapAtlas
						#ifndef _SingleAtlas
						shadowMapAtlasSun, shadowMapAtlasSunTransparent
						#else
						shadowMapAtlas, shadowMapAtlasTransparent
						#endif
					#else
					shadowMap, shadowMapTransparent
					#endif
					, lPos.xyz / lPos.w, shadowsBias, false
				);
			}
		#endif
	#endif
#endif // _Sun

#ifdef _SinglePoint
	visibility += sampleLight(
		p, n, pointPos, pointCol
		#ifdef _ShadowMap
			, 0, pointBias, true, false
		#endif
		#ifdef _Spot
		, true, spotData.x, spotData.y, spotDir, spotData.zw, spotRight
		#endif
	);
#endif

#ifdef _Clusters
	float viewz = linearize(depth * 0.5 + 0.5, cameraProj);
	int clusterI = getClusterI(uv, viewz, cameraPlane);
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
		visibility += sampleLight(
			p,
			n,
			lightsArray[li * 3].xyz, // lp
			lightsArray[li * 3 + 1].xyz // lightCol
			#ifdef _ShadowMap
				// light index, shadow bias, cast_shadows
				, li, lightsArray[li * 3 + 2].x, lightsArray[li * 3 + 2].z != 0.0, false
			#endif
			#ifdef _Spot
			, lightsArray[li * 3 + 2].y != 0.0
			, lightsArray[li * 3 + 2].y // spot size (cutoff)
			, lightsArraySpot[li * 2].w // spot blend (exponent)
			, lightsArraySpot[li * 2].xyz // spotDir
			, vec2(lightsArray[li * 3].w, lightsArray[li * 3 + 1].w) // scale
			, lightsArraySpot[li * 2 + 1].xyz // right
			#endif
		);
	}
#endif // _Clusters
	return visibility;
}

float depthDiff(vec3 a, vec3 b) {
    return abs(a.z - b.z);
}

float normalSimilarity(vec3 a, vec3 b) {
    return max(0.0, dot(a, b));
}

float distanceWeight(float d, float maxD) {
    return 1.0 - smoothstep(0.0, maxD, d);
}

const float GOLDEN_ANGLE = 2.39996323;
const float DEPTH_TOLERANCE = 0.1;
const float NORMAL_TOLERANCE = 0.5;

void main() {
    float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
    if (depth == 1.0) {
        fragColor = vec3(0.0);
        return;
    }

    vec3 basecol = textureLod(gbuffer1, texCoord, 0.0).rgb;
    // Decode normal
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
    vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);

	float metallic;
	uint matid;
	unpackFloatInt16(g0.a, metallic, matid);

    vec3 currentPos = getWorldPos(texCoord, depth);

	vec3 gi = vec3(0.0);
    float totalWeight = 0.0;

    float radius = ssaoRadius;
    float stepSize = radius / float(ssgiSamples);
    float angle = fract(sin(dot(texCoord, vec2(12.9898, 78.233))) * 43758.5453);

    for (int i = 0; i < ssgiSamples; i++) {
        float r = float(i) * stepSize;
        float a = float(i) * GOLDEN_ANGLE + angle;

        vec2 offset = vec2(cos(a), sin(a)) * r / screenSize;
        vec2 sampleUV = clamp(texCoord + offset, vec2(0.0), vec2(1.0));

		if (any(lessThan(sampleUV, vec2(0.0)))) continue;
		if (any(greaterThan(sampleUV, vec2(1.0)))) continue;

		vec4 sampleG0 = textureLod(gbuffer0, sampleUV, 0.0);
		vec2 sampleEnc = sampleG0.rg;
		vec3 sampleN;
		sampleN.z = 1.0 - abs(sampleEnc.x) - abs(sampleEnc.y);
		sampleN.xy = sampleN.z >= 0.0 ? sampleEnc.xy : octahedronWrap(sampleEnc.xy);
		sampleN = normalize(sampleN);
		float sampleDepth = textureLod(gbufferD, sampleUV, 0.0).r * 2.0 - 1.0;
		vec3 samplePos = getWorldPos(sampleUV, sampleDepth);

		if (depthDiff(currentPos, samplePos) > DEPTH_TOLERANCE)
            continue;

        if (normalSimilarity(n, sampleN) < NORMAL_TOLERANCE)
            continue;

		float dist = length(samplePos - currentPos);
        float weight = distanceWeight(dist, radius) * normalSimilarity(n, sampleN);

		vec3 sampleColor = textureLod(gbuffer1, sampleUV, 0.0).rgb * getVisibility(samplePos, sampleN, sampleDepth, sampleUV);

		#ifdef _EmissionShadeless
			if (matid == 1) { // pure emissive material, color stored in basecol
				sampleColor += textureLod(gbuffer1, sampleUV, 0.0).rgb;
			}
		#endif
		#ifdef _EmissionShaded
			#ifdef _EmissionShadeless
			else {
			#endif
				vec3 sampleEmission = textureLod(gbufferEmission, sampleUV, 0.0).rgb;
				sampleColor += sampleEmission; // Emission should be added directly
			#ifdef _EmissionShadeless
			}
			#endif
		#endif

		gi += sampleColor * weight;
		totalWeight += weight;
	}

	if (totalWeight > 0.0) {
		gi /= totalWeight;
		#ifdef _CPostprocess
			gi *= PPComp12.x;
		#else
			gi *= ssaoStrength ;
		#endif
	}
	else gi = vec3(0.0);
    // Final output
    fragColor = gi / (1.0 + gi);
}
