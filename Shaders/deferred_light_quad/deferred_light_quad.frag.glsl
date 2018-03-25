#version 450

#include "compiled.glsl"
#include "std/brdf.glsl"
#include "std/math.glsl"
#ifdef _VoxelGIDirect
	#include "std/conetrace.glsl"
#endif
#ifndef _NoShadows
	#include "std/shadows.glsl"
#endif
#ifdef _SSS
#include "std/sss.glsl"
#endif
#ifdef _SSRS
#include "std/ssrs.glsl"
#endif
#include "std/gbuffer.glsl"

#ifdef _VoxelGIDirect
	uniform sampler3D voxels;
#endif
#ifdef _VoxelGICam
	uniform vec3 eyeSnap;
#endif

// uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

#ifdef _SSS
vec2 lightPlane;
#endif

#ifndef _NoShadows
	#ifdef _SoftShadows
		uniform sampler2D svisibility;
	#else
		uniform sampler2D shadowMap;
		#ifdef _CSM
		//!uniform vec4 casData[shadowmapCascades * 4 + 4];
		#else
		uniform mat4 LWVP;
		#endif
	#endif
#endif
#ifdef _LampClouds
	uniform sampler2D texClouds;
	uniform float time;
#endif

uniform vec3 lightColor;
uniform vec3 l; // lightDir
uniform int lightShadow;
uniform float shadowsBias;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 cameraProj;
#ifdef _SSRS
	//!uniform mat4 VP;
	uniform mat4 invVP;
#endif

#ifdef _LampColTex
	uniform sampler2D texlampcolor;
#endif

in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

void main() {
	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, occlusion
	vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, 
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0; // 0 - 1 => -1 - 1
	// TODO: store_depth
	// TODO: Firefox throws feedback loop detected error, read depth from gbuffer0
	float depth = (1.0 - g0.a) * 2.0 - 1.0;

	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	vec3 p = getPos(eye, eyeLook, viewRay, depth, cameraProj);
	vec2 metrough = unpackFloat(g0.b);
	
	vec3 v = normalize(eye - p);
	float dotNV = dot(n, v);
	
	vec3 albedo = surfaceAlbedo(g1.rgb, metrough.x); // g1.rgb - basecolor
	vec3 f0 = surfaceF0(g1.rgb, metrough.x);
	float dotNL = dot(n, l);

	float visibility = 1.0;
#ifndef _NoShadows

	#ifdef _SoftShadows

	visibility = texture(svisibility, texCoord).r;

	#else

	if (lightShadow == 1) {
		#ifdef _CSM
		visibility = shadowTestCascade(shadowMap, eye, p + n * shadowsBias * 10, shadowsBias, shadowmapSize * vec2(shadowmapCascades, 1.0));
		#else
		vec4 lPos = LWVP * vec4(p + n * shadowsBias * 100, 1.0);
		if (lPos.w > 0.0) visibility = shadowTest(shadowMap, lPos.xyz / lPos.w, shadowsBias, shadowmapSize);
		#endif
	}
	#endif
#endif

#ifdef _VoxelGIShadow // #else
	#ifdef _VoxelGICam
	vec3 voxpos = (p - eyeSnap) / voxelgiHalfExtents;
	#else
	vec3 voxpos = p / voxelgiHalfExtents;
	#endif
	if (dotNL > 0.0) visibility = max(0, 1.0 - traceShadow(voxels, voxpos, l, 0.1, 10.0, n));
#endif

	// Per-light
	// vec3 l = lightDir; // lightType == 0 // Sun
	vec3 h = normalize(v + l);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);

#ifdef _Hair // Aniso
	if (floor(g1.a) == 2) {
		const float shinyParallel = metrough.y;
		const float shinyPerpendicular = 0.1;
		const vec3 v = vec3(0.99146, 0.11664, 0.05832);
		vec3 T = abs(dot(n, v)) > 0.99999 ? cross(n, vec3(0.0, 1.0, 0.0)) : cross(n, v);
		fragColor.rgb = orenNayarDiffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH) + wardSpecular(n, h, dotNL, dotNV, dotNH, T, shinyParallel, shinyPerpendicular);
	}
	else fragColor.rgb = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#else
#ifdef _OrenNayar
	float facdif = min((1.0 - metrough.x) * 3.0, 1.0);
	float facspec = min(metrough.x * 3.0, 1.0);
	fragColor.rgb = orenNayarDiffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH) * facdif + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH) * facspec;
#else
	fragColor.rgb = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#endif
#endif

	fragColor.rgb *= lightColor;

#ifdef _LampColTex
	// fragColor.rgb *= texture(texlampcolor, envMapEquirect(l)).rgb;
	fragColor.rgb *= pow(texture(texlampcolor, l.xy).rgb, vec3(2.2));
#endif
	
#ifdef _SSS
	if (floor(g1.a) == 2) {
		#ifdef _CSM
		int casi, casindex;
		mat4 LWVP = getCascadeMat(distance(eye, p), casi, casindex);
		#endif
		fragColor.rgb += fragColor.rgb * SSSSTransmittance(LWVP, p, n, l, lightPlane.y, shadowMap);
	}
#endif

#ifdef _SSRS
	float tvis = traceShadowSS(-l, p, gbuffer0, invVP, eye);
	// vec2 coords = getProjectedCoord(hitCoord);
	// vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	// float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);
	// tvis *= screenEdgeFactor;
	visibility *= tvis;
#endif

#ifdef _LampClouds
	visibility *= texture(texClouds, vec2(p.xy / 100.0 + time / 80.0)).r * dot(n, vec3(0,0,1));
#endif

	fragColor.rgb *= visibility;

#ifdef _VoxelGIRefract
	#ifdef _VoxelGICam
	vec3 voxposr = (p - eyeSnap) / voxelgiHalfExtents;
	#else
	vec3 voxposr = p / voxelgiHalfExtents;
	#endif
	fragColor.rgb = mix(traceRefraction(voxels, voxposr, n, -v, metrough.y), fragColor.rgb, g1.a);
#endif
}
