#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/brdf.glsl"
#include "../std/math.glsl"
#ifdef _LampIES
#include "../std/ies.glsl"
#endif
#ifdef _VoxelGIDirect
	#include "../std/conetrace.glsl"
#endif
#ifdef _PolyLight
	#include "../std/ltc.glsl"
#endif
#ifndef _NoShadows
	#ifdef _PCSS
	#include "../std/shadows_pcss.glsl"
	#else
	#include "../std/shadows.glsl"
	#endif
#endif
#ifdef _DFRS
#include "../std/sdf.glsl"
#endif
#ifdef _SSS
#include "../std/sss.glsl"
#endif
#ifdef _SSRS
#include "../std/ssrs.glsl"
#endif
#include "../std/gbuffer.glsl"

#ifdef _VoxelGIDirect
	//!uniform sampler3D voxels;
#endif
#ifdef _VoxelGICam
	uniform vec3 eyeSnap;
#endif

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

// TODO: separate shaders
#ifndef _NoShadows
	//!uniform sampler2D shadowMap;
	//!uniform samplerCube shadowMapCube;
	#ifdef _PCSS
	//!uniform sampler2D snoise;
	//!uniform float lampSizeUV;
	#endif
#endif
#ifdef _DFRS
	//!uniform sampler3D sdftex;
#endif
#ifdef _LampIES
	//!uniform sampler2D texIES;
#endif

uniform mat4 invVP;
uniform mat4 LWVP;
uniform vec3 lightColor;
uniform vec3 lightDir;
uniform vec3 lightPos;
uniform vec2 lightPlane;
uniform int lightType;
uniform int lightShadow;
uniform float shadowsBias;
uniform vec2 spotlightData;
#ifdef _PolyLight
	uniform vec3 lampArea0;
	uniform vec3 lampArea1;
	uniform vec3 lampArea2;
	uniform vec3 lampArea3;
	uniform sampler2D sltcMat;
	uniform sampler2D sltcMag;
#endif
uniform vec3 eye;
#ifdef _SSRS
	//!uniform mat4 VP;
#endif

#ifdef _LampColTex
	uniform sampler2D texlampcolor;
#endif

in vec4 wvpposition;
out vec4 fragColor;

#ifndef _NoShadows
float shadowTest(const vec3 lPos) {
	
	// Out of bounds
	if (lPos.x < 0.0 || lPos.y < 0.0 || lPos.x > 1.0 || lPos.y > 1.0) return 1.0;

	#ifdef _PCSS
	return PCSS(lPos.xy, lPos.z - shadowsBias);
	#else
	return PCF(lPos.xy, lPos.z - shadowsBias);
	#endif
}
float shadowTestCube(const vec3 lp, const vec3 l) {
	return PCFCube(lp, -l, shadowsBias, lightPlane);
}
#endif

void main() {
	vec2 texCoord = wvpposition.xy / wvpposition.w;
	texCoord = texCoord * 0.5 + 0.5;
	#ifdef _InvY
	texCoord.y = 1.0 - texCoord.y;
	#endif

	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, occlusion
	vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, 
	// #ifdef _InvY // D3D
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0; // 0 - 1 => -1 - 1
	// #else
	// TODO: store_depth
	float depth = (1.0 - g0.a) * 2.0 - 1.0;
	// #endif

	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	vec3 p = getPos2(invVP, depth, texCoord);
	vec2 metrough = unpackFloat(g0.b);
	
	vec3 v = normalize(eye - p);
	float dotNV = dot(n, v);
	
	vec3 albedo = surfaceAlbedo(g1.rgb, metrough.x); // g1.rgb - basecolor
	vec3 f0 = surfaceF0(g1.rgb, metrough.x);
	
	vec3 lp = lightPos - p;
	vec3 l = normalize(lp);
	vec3 h = normalize(v + l);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);
	float dotNL = dot(n, l);

	float visibility = 1.0;
#ifndef _NoShadows
	// TODO: merge..
	if (lightShadow == 1) {
		vec4 lampPos = LWVP * vec4(p, 1.0);
		if (lampPos.w > 0.0) visibility = shadowTest(lampPos.xyz / lampPos.w);
	}
	else if (lightShadow == 2) { // Cube
		visibility = shadowTestCube(lp, l);
	}
#endif
	
#ifdef _VoxelGIShadow // #else
	#ifdef _VoxelGICam
	vec3 voxpos = (p - eyeSnap) / voxelgiHalfExtents;
	#else
	vec3 voxpos = p / voxelgiHalfExtents;
	#endif
	if (dotNL > 0.0) visibility = max(0, 1.0 - traceShadow(voxpos, l, 0.1, length(lp)));
#endif


#ifdef _DFRS
	visibility = dfrs(p, l, lightPos);
#endif

	visibility *= attenuate(distance(p, lightPos));

#ifdef _LampIES
	visibility *= iesAttenuation(-l);
#endif
	if (lightType == 2) { // Spot
		float spotEffect = dot(lightDir, l);
		// x - cutoff, y - cutoff - exponent
		if (spotEffect < spotlightData.x) {
			visibility *= smoothstep(spotlightData.y, spotlightData.x, spotEffect);
		}
	}

#ifdef _OrenNayar
	float facdif = min((1.0 - metrough.x) * 3.0, 1.0);
	float facspec = min(metrough.x * 3.0, 1.0);
#endif

#ifdef _PolyLight
	if (lightType == 3) { // Area
		float theta = acos(dotNV);
		vec2 tuv = vec2(metrough.y, theta / (0.5 * PI));
		tuv = tuv * LUT_SCALE + LUT_BIAS;
		vec4 t = texture(sltcMat, tuv);
		mat3 invM = mat3(
			vec3(1.0, 0.0, t.y),
			vec3(0.0, t.z, 0.0),
			vec3(t.w, 0.0, t.x));

		float ltcspec = ltcEvaluate(n, v, dotNV, p, invM, lampArea0, lampArea1, lampArea2, lampArea3);
		ltcspec *= texture(sltcMag, tuv).a;
		float ltcdiff = ltcEvaluate(n, v, dotNV, p, mat3(1.0), lampArea0, lampArea1, lampArea2, lampArea3);
	#ifdef _OrenNayar
		fragColor.rgb = albedo * ltcdiff * facdif + ltcspec * facspec;
	#else
		fragColor.rgb = albedo * ltcdiff + ltcspec;
	#endif
	}
	else {
#endif

#ifdef _OrenNayar
	// Diff/glossy
	float rough = pow(metrough.y, 0.5);
	fragColor.rgb = orenNayarDiffuseBRDF(albedo, rough, dotNV, dotNL, dotVH) * max(1.0 - metrough.y, 0.88) * facdif + specularBRDF(f0, rough, dotNL, dotNH, dotNV, dotVH) * 3.5 * facspec;
	// Metallic
	// fragColor.rgb = orenNayarDiffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#else
	fragColor.rgb = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#endif

#ifdef _PolyLight
	}
#endif
	
	// Aniso spec
	// #ifdef _Aniso
	// float shinyParallel = metrough.y;
	// float shinyPerpendicular = 0.08;
	// vec3 fiberDirection = vec3(0.0, 1.0, 8.0);
	// fragColor.rgb = diffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH, dotLV) + wardSpecular(n, h, dotNL, dotNV, dotNH, fiberDirection, shinyParallel, shinyPerpendicular);
	// #endif

	fragColor.rgb *= lightColor;

#ifdef _LampColTex
	// fragColor.rgb *= texture(texlampcolor, envMapEquirect(l)).rgb;
	fragColor.rgb *= pow(texture(texlampcolor, l.xy).rgb, vec3(2.2));
#endif
	
#ifdef _SSS
	if (floor(g1.a) == 2) {
		if (lightShadow == 1) fragColor.rgb += fragColor.rgb * SSSSTransmittance(1.0, 0.005, p, n, l, shadowMap, LWVP);
		else fragColor.rgb += fragColor.rgb * SSSSTransmittanceCube(1.0, 0.005, p, n, l, shadowMapCube, LWVP);
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

	fragColor.rgb *= visibility;

#ifdef _VoxelGIRefract
	#ifdef _VoxelGICam
	vec3 voxposr = (p - eyeSnap) / voxelgiHalfExtents;
	#else
	vec3 voxposr = p / voxelgiHalfExtents;
	#endif
	fragColor.rgb = mix(traceRefraction(voxposr, n, -v, metrough.y), fragColor.rgb, g1.a);
#endif
}
