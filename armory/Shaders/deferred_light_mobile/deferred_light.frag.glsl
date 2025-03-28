#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/math.glsl"
#ifdef _Clusters
#include "std/clusters.glsl"
#endif
#ifdef _Irr
#include "std/shirr.glsl"
#endif

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

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

#ifdef _SMSizeUniform
//!uniform vec2 smSizeUniform;
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
uniform float pointBias;
	#ifdef _Spot
	uniform vec3 spotDir;
	uniform vec3 spotRight;
	uniform vec4 spotData;
	#endif
#endif

#include "std/light_mobile.glsl"

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

#ifdef _Brdf
	vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(vec2(dotNV, 1.0 - roughness) * 256.0), 0).xy;
#endif

	// Envmap
#ifdef _Irr
	vec3 envl = shIrradiance(n, shirr);
	#ifdef _EnvTex
	envl /= PI;
	#endif
#else
	vec3 envl = vec3(1.0);
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

#ifdef _Rad // Indirect specular
	envl.rgb += prefilteredColor * (f0 * envBRDF.x + envBRDF.y) * 1.5 * occspec.y;
#else
	#ifdef _EnvCol
	envl.rgb += backgroundCol * surfaceF0(g1.rgb, metallic); // f0
	#endif
#endif

	envl.rgb *= envmapStrength * occspec.x;
	fragColor.rgb = envl;

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

	fragColor.rgb += sdirect * svisibility * sunCol;
#endif

#ifdef _SinglePoint
	fragColor.rgb += sampleLight(
		p, n, v, dotNV, pointPos, pointCol, albedo, roughness, occspec.y, f0
		#ifdef _ShadowMap
			, 0, pointBias, true
		#endif
		#ifdef _Spot
		, true, spotData.x, spotData.y, spotDir, spotData.zw, spotRight  // TODO: Test!
		#endif
	);
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
			, lightsArraySpot[li].w // spot blend (exponent)
			, lightsArraySpot[li].xyz // spotDir
			, vec2(lightsArray[li * 3].w, lightsArray[li * 3 + 1].w) // scale
			, lightsArraySpot[li * 2 + 1].xyz // right
			#endif
		);
	}
#endif // _Clusters
}
