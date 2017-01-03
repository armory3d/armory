#version 450
#define _EnvCol
#define _SSAO
#define _SMAA

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/brdf.glsl"
#include "../std/math.glsl"
// #ifdef _PolyLight
#include "../std/ltc.glsl"
// #endif
// ...
#ifndef _NoShadows
	#ifdef _PCSS
	#include "../std/shadows_pcss.glsl"
	// PCSS()
	#else
	#include "../std/shadows.glsl"
	// PCF()
	#endif
#endif
#include "../std/gbuffer.glsl"
// octahedronWrap()
// unpackFloat()

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

#ifndef _NoShadows
	//!uniform sampler2D shadowMap;
	#ifdef _PCSS
	//!uniform sampler2D snoise;
	//!uniform float lampSizeUV;
	#endif
#endif

#ifdef _VoxelGI
	uniform sampler2D ssaotex;
	uniform sampler2D senvmapBrdf;
	//!uniform sampler3D voxels;
#endif

#ifdef _PolyLight
	//!uniform sampler2D sltcMat;
	//!uniform sampler2D sltcMag;
#endif

uniform mat4 invVP;
uniform mat4 LWVP;
uniform vec3 lightPos;
uniform vec3 lightDir;
uniform int lightType;
// uniform int lightIndex;
uniform vec3 lightColor;
uniform float shadowsBias;
uniform float spotlightCutoff;
uniform float spotlightExponent;
#ifdef _PolyLight
uniform vec3 lampArea0;
uniform vec3 lampArea1;
uniform vec3 lampArea2;
uniform vec3 lampArea3;
#endif
uniform vec3 eye;
// uniform vec3 eyeLook;
// uniform vec2 screenSize;

#ifdef _LampColTex
uniform sampler2D texlampcolor;
#endif

// in vec2 texCoord;
in vec4 wvpposition;
// in vec3 viewRay;
out vec4 fragColor;

// Separable SSS Transmittance Function, ref to sss_pass
#ifdef _SSS
vec3 SSSSTransmittance(float translucency, float sssWidth, vec3 worldPosition, vec3 worldNormal, vec3 lightDir) {
	float scale = 8.25 * (1.0 - translucency) / sssWidth;
	vec4 shrinkedPos = vec4(worldPosition - 0.005 * worldNormal, 1.0);
	vec4 shadowPosition = LWVP * shrinkedPos;
	float d1 = texture(shadowMap, shadowPosition.xy / shadowPosition.w).r; // 'd1' has a range of 0..1
	float d2 = shadowPosition.z; // 'd2' has a range of 0..'lightFarPlane'
	const float lightFarPlane = 120 / 3.5;
	d1 *= lightFarPlane; // So we scale 'd1' accordingly:
	float d = scale * abs(d1 - d2);

	float dd = -d * d;
	vec3 profile = vec3(0.233, 0.455, 0.649) * exp(dd / 0.0064) +
				   vec3(0.1,   0.336, 0.344) * exp(dd / 0.0484) +
				   vec3(0.118, 0.198, 0.0)   * exp(dd / 0.187) +
				   vec3(0.113, 0.007, 0.007) * exp(dd / 0.567) +
				   vec3(0.358, 0.004, 0.0)   * exp(dd / 1.99) +
				   vec3(0.078, 0.0,   0.0)   * exp(dd / 7.41);
	return profile * clamp(0.3 + dot(lightDir, -worldNormal), 0.0, 1.0);
}
#endif

#ifndef _NoShadows
float shadowTest(vec4 lPos) {
	lPos.xyz /= lPos.w;
	lPos.xy = lPos.xy * 0.5 + 0.5;
	
	#ifdef _Clampstc
	// Filtering out of bounds, remove
	// const vec2 border = vec2(1.0 / shadowmapSize[0], 1.0 / shadowmapSize[1]) * 2.0;
	// lPos.xy = clamp(lPos.xy, border[0], 1.0 - border[1]);
	if (lPos.x < 0.0) return 1.0;
	if (lPos.y < 0.0) return 1.0;
	if (lPos.x > 1.0) return 1.0;
	if (lPos.y > 1.0) return 1.0;
	#endif

	#ifdef _PCSS
	return PCSS(lPos.xy, lPos.z - shadowsBias);
	#else
	return PCF(lPos.xy, lPos.z - shadowsBias);
	#endif
}
#endif

void main() {
	vec2 screenPosition = wvpposition.xy / wvpposition.w;
	vec2 texCoord = screenPosition * 0.5 + 0.5;
	// texCoord += vec2(0.5 / screenSize); // Half pixel offset

	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, mask
	vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, occlusion
	// 0 - 1 => -1 - 1
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// TODO: Can not read and test depth buffer at once, fetch depth from g0
	float depth = (1.0 - g0.a) * 2.0 - 1.0;

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
	
	// Per-light
	vec3 l;
	if (lightType == 0) { // Sun
		l = lightDir;
	}
	else { // Point, spot
		l = normalize(lightPos - p);
	}
	
	vec3 h = normalize(v + l);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);
	float dotNL = dot(n, l);
	// float dotLV = dot(l, v);
	// float dotLH = dot(l, h);
	
	float visibility = 1.0;
#ifndef _NoShadows
	vec4 lampPos = LWVP * vec4(p, 1.0);
	if (lampPos.w > 0.0) {
		visibility = shadowTest(lampPos);
	}
#endif
	
	// Direct
	vec3 direct;

#ifdef _PolyLight
	if (lightType == 3) { // Area
		float theta = acos(dotNV);
		vec2 tuv = vec2(metrough.y, theta / (0.5 * PI));
		tuv = tuv * LUT_SCALE + LUT_BIAS;
		// vec4 t = texture(sltcMat, tuv);
		vec4 t = clamp(texture(sltcMat, tuv), 0.0, 1.0);
		mat3 invM = mat3(
			vec3(1.0, 0.0, t.y),
			vec3(0.0, t.z, 0.0),
			vec3(t.w, 0.0, t.x));

		vec3 ltcspec = ltcEvaluate(n, v, dotNV, p, invM, lampArea0, lampArea1, lampArea2, lampArea3, true); 
		ltcspec *= texture(sltcMag, tuv).a;
		
		vec3 ltcdiff = ltcEvaluate(n, v, dotNV, p, mat3(1.0), lampArea0, lampArea1, lampArea2, lampArea3, true);
		direct = ltcdiff * albedo + ltcspec;
		direct = clamp(direct, 0.0, 10.0);
	}
	else {
#endif

#ifdef _OrenNayar
	direct = orenNayarDiffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#else
	direct = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, metrough.y, dotNL, dotNH, dotNV, dotVH);
#endif

		if (lightType == 2) { // Spot
			float spotEffect = dot(lightDir, l);
			if (spotEffect < spotlightCutoff) {
				float spotEffect = smoothstep(spotlightCutoff - spotlightExponent, spotlightCutoff, spotEffect);
				direct *= spotEffect;
			}
		}

#ifdef _PolyLight
	}
#endif
	
	// Aniso spec
	// #ifdef _Aniso
	// float shinyParallel = metrough.y;
	// float shinyPerpendicular = 0.08;
	// vec3 fiberDirection = vec3(0.0, 1.0, 8.0);
	// vec3 direct = diffuseBRDF(albedo, metrough.y, dotNV, dotNL, dotVH, dotLV) + wardSpecular(n, h, dotNL, dotNV, dotNH, fiberDirection, shinyParallel, shinyPerpendicular);
	// #endif

	direct *= lightColor;

#ifdef _LampColTex
	// direct *= texture(texlampcolor, envMapEquirect(l)).rgb;
	direct *= pow(texture(texlampcolor, l.xy).rgb, vec3(2.2));	
#endif
	
#ifdef _SSS
	float mask = g0.a;
	if (mask == 2.0) {
		direct *= SSSSTransmittance(1.0, 0.005, p, n, l);
	}
#endif

	// Direct
	fragColor = vec4(vec3(direct * visibility), 1.0);

	// Voxels test..
#ifdef _VoxelGI
	vec4 g1a = texture(gbuffer1, texCoord); // Basecolor.rgb, occlusion
	vec3 albedoa = surfaceAlbedo(g1a.rgb, metrough.x); // g1a.rgb - basecolor

	vec3 tangent = normalize(cross(n, vec3(0.0, 1.0, 0.0)));
	if (length(tangent) == 0.0) {
		tangent = normalize(cross(n, vec3(0.0, 0.0, 1.0)));
	}
	vec3 bitangent = normalize(cross(n, tangent));
	mat3 tanToWorld = inverse(transpose(mat3(tangent, bitangent, n)));

	float diffOcclusion = 0.0;
	vec3 indirectDiffusea = coneTraceIndirect(p, tanToWorld, n, diffOcclusion).rgb * 4.0;
	indirectDiffusea *= albedoa;
	diffOcclusion = min(1.0, 1.5 * diffOcclusion);

	vec3 reflectWorld = reflect(-v, n);
	float specularOcclusion;
	float lodOffset = 0.0;//getMipFromRoughness(roughness, numMips);
	vec3 indirectSpecular = coneTrace(p, reflectWorld, n, 0.07 + lodOffset, specularOcclusion).rgb;

	if (metrough.y > 0.0) { // Temp..
		float dotNVa = max(dot(n, v), 0.0);
		vec3 f0a = surfaceF0(g1a.rgb, metrough.x);
		vec2 envBRDFa = texture(senvmapBrdf, vec2(metrough.y, 1.0 - dotNVa)).xy;
		indirectSpecular *= (f0a * envBRDFa.x + envBRDFa.y);
	}

	vec3 indirect1 = indirectDiffusea * diffOcclusion + indirectSpecular;
	indirect1 *= texture(ssaotex, texCoord).r;
	fragColor.rgb += indirect1;
#endif
}
