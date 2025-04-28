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
#include "std/constants.glsl"

uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D gbufferD;
#ifdef _EmissionShaded
uniform sampler2D gbufferEmission;
#endif
uniform sampler2D sveloc;
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform mat4 invVP;

in vec2 texCoord;
in vec3 viewRay;
out vec3 fragColor;

float metallic;
uint matid;

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
				uniform mat4 LWVPSpot[1];
			#endif
		#else
			uniform samplerCubeShadow shadowMapPoint[1];
			uniform vec2 lightProj;
		#endif
	#endif
	#ifdef _Clusters
		#ifdef _SingleAtlas
		uniform sampler2DShadow shadowMapAtlas;
		#endif
		uniform vec2 lightProj;
		#ifdef _ShadowMapAtlas
		#ifndef _SingleAtlas
		uniform sampler2DShadow shadowMapAtlasPoint;
		#endif
		//!uniform vec4 pointLightDataArray[maxLightsCluster * 6];
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

vec3 sampleLight(const vec3 p, const vec3 n, const vec3 lp, const vec3 lightCol
	#ifdef _ShadowMap
		, int index, float bias, bool receiveShadow
	#endif
	#ifdef _Spot
		, const bool isSpot, const float spotSize, float spotBlend, vec3 spotDir, vec2 scale, vec3 right
	#endif
	) {

	vec3 ld = lp - p;
	vec3 l = normalize(ld);

	vec3 direct = lightCol;
	direct *= attenuate(distance(p, lp));
	float visibility = 1.0;

	#ifdef _LTC
	#ifdef _ShadowMap
		if (receiveShadow) {
			#ifdef _SinglePoint
			vec4 lPos = LWVPSpotArray[0] * vec4(p + n * bias * 10, 1.0);
			visibility *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
			#endif
			#ifdef _Clusters
			vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
			if (index == 0) visibility *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
			else if (index == 1) visibility *= shadowTest(shadowMapSpot[1], lPos.xyz / lPos.w, bias);
			else if (index == 2) visibility *= shadowTest(shadowMapSpot[2], lPos.xyz / lPos.w, bias);
			else if (index == 3) visibility *= shadowTest(shadowMapSpot[3], lPos.xyz / lPos.w, bias);
			#endif
		}
	#endif
	return visibility * direct;
	#endif

	#ifdef _Spot
	if (isSpot) {
		visibility *= spotlightMask(l, spotDir, right, scale, spotSize, spotBlend);

		#ifdef _ShadowMap
			if (receiveShadow) {
				#ifdef _SinglePoint
				vec4 lPos = LWVPSpot[0] * vec4(p + n * bias * 10, 1.0);
				visibility *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
				#endif
				#ifdef _Clusters
					vec4 lPos = LWVPSpotArray[index] * vec4(p + n * bias * 10, 1.0);
					#ifdef _ShadowMapAtlas
						visibility *= shadowTest(
							#ifndef _SingleAtlas
							shadowMapAtlasSpot
							#else
							shadowMapAtlas
							#endif
							, lPos.xyz / lPos.w, bias
						);
					#else
							 if (index == 0) visibility *= shadowTest(shadowMapSpot[0], lPos.xyz / lPos.w, bias);
						else if (index == 1) visibility *= shadowTest(shadowMapSpot[1], lPos.xyz / lPos.w, bias);
						else if (index == 2) visibility *= shadowTest(shadowMapSpot[2], lPos.xyz / lPos.w, bias);
						else if (index == 3) visibility *= shadowTest(shadowMapSpot[3], lPos.xyz / lPos.w, bias);
					#endif
				#endif
			}
		#endif
		return visibility * direct;
	}
	#endif

	#ifdef _LightIES
	visibility *= iesAttenuation(-l);
	#endif

	#ifdef _ShadowMap
		if (receiveShadow) {
			#ifdef _SinglePoint
			#ifndef _Spot
			visibility *= PCFCube(shadowMapPoint[0], ld, -l, bias, lightProj, n);
			#endif
			#endif
			#ifdef _Clusters
				#ifdef _ShadowMapAtlas
				visibility *= PCFFakeCube(
					#ifndef _SingleAtlas
					shadowMapAtlasPoint
					#else
					shadowMapAtlas
					#endif
					, ld, -l, bias, lightProj, n, index
				);
				#else
					 if (index == 0) visibility *= PCFCube(shadowMapPoint[0], ld, -l, bias, lightProj, n);
				else if (index == 1) visibility *= PCFCube(shadowMapPoint[1], ld, -l, bias, lightProj, n);
				else if (index == 2) visibility *= PCFCube(shadowMapPoint[2], ld, -l, bias, lightProj, n);
				else if (index == 3) visibility *= PCFCube(shadowMapPoint[3], ld, -l, bias, lightProj, n);
				#endif
			#endif
		}
	#endif

	return visibility * direct;
}

vec3 getLight(vec3 p, vec3 n, float depth, vec2 uv) {
		vec3 direct = vec3(0.0);
		float visibility = 1.0;
#ifdef _Sun
	#ifdef _ShadowMap
		#ifdef _CSM
			visibility = shadowTestCascade(
				#ifdef _ShadowMapAtlas
					#ifndef _SingleAtlas
					_ShadowMapAtlasSun
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
			if (lPos.w > 0.0) {
				visibility = shadowTest(
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
			}
		#endif
	#endif
	direct += sunCol * visibility;
#endif

#ifdef _SinglePoint
	direct += sampleLight(
		p, n, pointPos, pointCol
		#ifdef _ShadowMap
			, 0, pointBias, true
		#endif
		#ifdef _Spot
		, true, spotData.x, spotData.y, spotDir, spotData.zw, spotRight
		#endif
	);
#endif

#ifdef _Clusters
	float viewz = linearize(depth, cameraProj);
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
		direct += sampleLight(
			p,
			n,
			lightsArray[li * 3].xyz, // lp
			lightsArray[li * 3 + 1].xyz // lightCol
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
		);
	}
#endif // _Clusters

	return direct;
}

vec3 getWorldPos(vec2 uv, float depth) {
    vec4 pos = invVP * vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    return pos.xyz / pos.w;
}

vec3 getNormal(vec2 uv) {
    vec4 g0 = textureLod(gbuffer0, uv, 0.0);
    vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    return normalize(n);
}

vec3 calculateIndirectLight(vec2 uv, vec3 pos, vec3 normal, float depth) {
    // Simplified visibility - replace with your full visibility function if needed
    vec3 sampleColor = textureLod(gbuffer1, uv, 0.0).rgb * getLight(pos, normal, depth, uv);

	#ifdef _EmissionShadeless
		if (matid == 1) { // pure emissive material, color stored in basecol
			sampleColor += textureLod(gbuffer1, uv, 0.0).rgb;
		}
	#endif
	#ifdef _EmissionShaded
		#ifdef _EmissionShadeless
		else {
		#endif
			vec3 sampleEmission = textureLod(gbufferEmission, uv, 0.0).rgb;
			sampleColor += sampleEmission; // Emission should be added directly
		#ifdef _EmissionShadeless
		}
		#endif
	#endif

	return sampleColor;
}

// Improved sampling parameters
const float GOLDEN_ANGLE = 2.39996323;
const float MAX_DEPTH_DIFFERENCE = 0.9; // More conservative depth threshold
const float SAMPLE_BIAS = 0.01; // Small offset to avoid self-occlusion

void main() {
    float depth = textureLod(gbufferD, texCoord, 0.0).r;
    if (depth >= 1.0) {
        fragColor = vec3(0.0);
        return;
    }

	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0); // Normal.xy, roughness, metallic/matid
	unpackFloatInt16(g0.a, metallic, matid);

	vec2 velocity = -textureLod(sveloc, texCoord, 0.0).rg;

	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

    vec3 pos = getWorldPos(texCoord, depth);
    vec3 normal = getNormal(texCoord);
    vec3 centerColor = textureLod(gbuffer1, texCoord, 0.0).rgb;

    float radius = ssaoRadius;

    vec3 gi = vec3(0.0);
    float totalWeight = 0.0;
    float angle = fract(sin(dot(texCoord, vec2(12.9898, 78.233))) * 100.0);

	for (int i = 0; i < ssgiSamples; i++) {
		// Use quasi-random sequence for better coverage
		float r = sqrt((float(i) + 0.5) / float(ssgiSamples)) * radius;
		float a = (float(i) * GOLDEN_ANGLE) + angle;

		vec2 offset = vec2(cos(a), sin(a)) * r * radius;
		vec2 sampleUV = clamp(texCoord + offset * (BayerMatrix8[int(gl_FragCoord.x + velocity.x) % 8][int(gl_FragCoord.y + velocity.y) % 8] - 0.5) / screenSize, vec2(0.001), vec2(0.999));

		float sampleDepth = textureLod(gbufferD, sampleUV, 0.0).r;
		if (sampleDepth >= 1.0) continue;

		vec3 samplePos = getWorldPos(sampleUV, sampleDepth);
		vec3 sampleNormal = getNormal(sampleUV);

		// Apply small bias to sample position to avoid self-occlusion
		samplePos += sampleNormal * SAMPLE_BIAS;

		vec3 dir = pos - samplePos;
		float dist = length(dir);

		if (abs(pos.z - samplePos.z) > MAX_DEPTH_DIFFERENCE) continue;;

		vec3 sampleColor = calculateIndirectLight(sampleUV, samplePos, sampleNormal, sampleDepth);
		float weight = 1.0 / (1.0 + dist * dist * 2.0) * max(dot(sampleNormal, n), 0.0);

		gi += sampleColor * weight;
		totalWeight += weight;
	}

    // Normalize and apply intensity
    if (totalWeight > 0.0) {
        gi /= totalWeight;
        #ifdef _CPostprocess
            gi *= PPComp12.x;
        #else
            gi *= ssaoStrength;
        #endif
    }

	#ifdef _EmissionShadeless
		if (matid == 1) { // pure emissive material, color stored in basecol
			gi += textureLod(gbuffer1, texCoord, 0.0).rgb;
		}
	#endif
	#ifdef _EmissionShaded
		#ifdef _EmissionShadeless
		else {
		#endif
			gi += textureLod(gbufferEmission, texCoord, 0.0).rgb;
		#ifdef _EmissionShadeless
		}
		#endif
	#endif
	fragColor = gi / (gi + vec3(1.0)); // Reinhard tone mapping
}
