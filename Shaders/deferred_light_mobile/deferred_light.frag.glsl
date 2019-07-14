#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/math.glsl"
#include "std/light_mobile.glsl"
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
//!uniform vec4 shirr[7];
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

uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;

#ifdef _Clusters
uniform vec4 lightsArray[maxLights * 2];
	#ifdef _Spot
	uniform vec4 lightsArraySpot[maxLights];
	#endif
uniform sampler2D clustersData;
uniform vec2 cameraPlane;
#endif

#ifdef _ShadowMap
#ifdef _SinglePoint
	#ifdef _Spot
	//!uniform sampler2DShadow shadowMapSpot[1];
	//!uniform mat4 LWVPSpot0;
	#else
	//!uniform samplerCubeShadow shadowMapPoint[1];
	//!uniform vec2 lightProj;
	#endif
#endif
#ifdef _Clusters
	//!uniform samplerCubeShadow shadowMapPoint[4];
	//!uniform vec2 lightProj;
	#ifdef _Spot
	//!uniform sampler2DShadow shadowMapSpot[4];
	//!uniform mat4 LWVPSpot0;
	//!uniform mat4 LWVPSpot1;
	//!uniform mat4 LWVPSpot2;
	//!uniform mat4 LWVPSpot3;
	#endif
#endif
#endif

#ifdef _Sun
uniform vec3 sunDir;
uniform vec3 sunCol;
	#ifdef _ShadowMap
	uniform sampler2DShadow shadowMap;
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
	uniform vec2 spotData;
	#endif
#endif

in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

void main() {
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0); // Normal.xy, metallic/roughness, depth
	
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
	vec2 envBRDF = textureLod(senvmapBrdf, vec2(roughness, 1.0 - dotNV), 0.0).xy;
#endif

	// Envmap
#ifdef _Irr
	vec3 envl = shIrradiance(n);
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
	float sdotNH = dot(n, sh);
	float sdotVH = dot(v, sh);
	float sdotNL = dot(n, sunDir);
	float svisibility = 1.0;
	vec3 sdirect = lambertDiffuseBRDF(albedo, sdotNL) +
				   specularBRDF(f0, roughness, sdotNL, sdotNH, dotNV, sdotVH) * occspec.y;

	#ifdef _ShadowMap
		#ifdef _CSM
		svisibility = shadowTestCascade(shadowMap, eye, p + n * shadowsBias * 10, shadowsBias, shadowmapSize * vec2(shadowmapCascades, 1.0));
		#else
		vec4 lPos = LWVP * vec4(p + n * shadowsBias * 100, 1.0);
		if (lPos.w > 0.0) svisibility = shadowTest(shadowMap, lPos.xyz / lPos.w, shadowsBias, shadowmapSize);
		#endif
	#endif

	fragColor.rgb += sdirect * svisibility * sunCol;
#endif

#ifdef _SinglePoint
	fragColor.rgb += sampleLight(
		p, n, v, dotNV, pointPos, pointCol, albedo, roughness, occspec.y, f0
		#ifdef _ShadowMap
			, 0, pointBias
		#endif
		#ifdef _Spot
		, true, spotData.x, spotData.y, spotDir
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
			lightsArray[li * 2].xyz, // lp
			lightsArray[li * 2 + 1].xyz, // lightCol
			albedo,
			roughness,
			occspec.y,
			f0
			#ifdef _ShadowMap
				, li, lightsArray[li * 2].w // bias
			#endif
			#ifdef _Spot
			, li > numPoints - 1
			, lightsArray[li * 2 + 1].w // cutoff
			, lightsArraySpot[li].w // cutoff - exponent
			, lightsArraySpot[li].xyz // spotDir
			#endif
		);
	}
#endif // _Clusters
}
