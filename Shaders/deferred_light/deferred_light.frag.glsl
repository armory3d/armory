#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/brdf.glsl"
#include "../std/math.glsl"
// #ifdef _VoxelGI
	// #include "../std/conetrace.glsl"
// #endif
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
#include "../std/gbuffer.glsl"

// #ifdef _VoxelGI
	//-!uniform sampler3D voxels;
// #endif

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
	//!uniform sampler2D sdftex;
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
	uniform mat4 VP;
#endif

#ifdef _LampColTex
	uniform sampler2D texlampcolor;
#endif

in vec4 wvpposition;
out vec4 fragColor;

#ifndef _NoShadows
float shadowTest(const vec3 lPos) {
	
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
float shadowTestCube(const vec3 lp, const vec3 l) {
	return PCFCube(lp, -l, shadowsBias, lightPlane);
}
#endif

#ifdef _SSRS
vec2 getProjectedCoord(vec3 hitCoord) {
	vec4 projectedCoord = VP * vec4(hitCoord, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	return projectedCoord.xy;
}
float getDeltaDepth(vec3 hitCoord) {
	vec2 texCoord = getProjectedCoord(hitCoord);
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// TODO: store_depth
	vec4 g0 = texture(gbuffer0, texCoord);
	float depth = (1.0 - g0.a) * 2.0 - 1.0;
	vec3 wpos = getPos2(invVP, depth, texCoord);
	float d1 = length(eye - wpos);
	float d2 = length(eye - hitCoord);
	return d1 - d2;
}
float traceShadow(vec3 dir, vec3 hitCoord) {
	dir *= ssrsRayStep;
	// for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return 0.0;
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return 0.0;
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return 0.0;
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return 0.0;
	//}
	return 1.0;
}
#endif

void main() {
	vec2 texCoord = wvpposition.xy / wvpposition.w;
	texCoord = texCoord * 0.5 + 0.5;

	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, occlusion
	vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, 
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0; // 0 - 1 => -1 - 1
	// TODO: store_depth
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
	
	vec3 lp = lightPos - p;
	vec3 l = normalize(lp);

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

#ifdef _DFRS

	const float distmax = 40.0;
	const float eps = 0.02;
	const int maxSteps = 30;
	float dist = 0.1;

	// float test = mapsdf2(p);
	// if (test < 0.1) {
		// fragColor = vec4(1.0, 0.0, 0.0, 1.0);
		// return;
	// }

	float lastd = distmax;
	for (int i = 0; i < maxSteps; i++) {
		vec3 rd = l * dist;
		float d = sdBox(p + rd, vec3(1.0));

		// Going out of volume box
		// if (d > 0.0 && lastd < d) {
		// 	break;
		// }
		// lastd = d;

		if (d <= 0.0) { // In volume
			d = mapsdf(p, rd);

			if (d < eps) {
				visibility = 0.0;
				break;
			}
		}
		else { // To volume
			// d += mapsdf(p, rd);

			vec3 sampleBorder = clamp(p + rd, vec3(-1.0), vec3(1.0)); 
			float phi = mapsdf2(sampleBorder, rd);
			float dd = 0.1;
			float grad_x = mapsdf2(sampleBorder + vec3(dd, 0, 0), rd) - phi;
			float grad_y = mapsdf2(sampleBorder + vec3(0, dd, 0), rd) - phi;
			vec3 grad = vec3(grad_x, grad_y, 1.0);
			vec3 endpoint = sampleBorder - normalize(grad) * phi;
			d = distance(endpoint, p + rd);

			// float dd = 0.1;
			// vec3 p0 = clamp(p, vec3(-1.0), vec3(1.0));
			// vec3 p1 = clamp(p, vec3(-0.99), vec3(0.99));
			// float r0 = mapsdf2(p0, rd);
			// float r1 = mapsdf2(p1, rd);
			// float h0 = 0.5 + (r0 * r0 - r1 * r1) / (2.0 * dd * dd);
			// float ri = sqrt(abs(r0 * r0 - h0 * h0 * dd * dd));
			// vec3 p2 = p0 + (p1 - p0) * h0;
			// vec3 p3 = p2 + vec3(p1.z - p0.z, p1.y - p0.y, p1.x - p0.x) * ri;
			// d = length((p + rd) - p3);
		}
		
		const float k = 2.0;
		visibility = min(visibility, (k * d / dist));
		dist += d;
		
		if (dist > distmax) {
			break;
		}
	}
#endif

	// Per-light
#ifndef _NoLampFalloff
	visibility *= attenuate(distance(p, lightPos));
#endif
	if (lightType == 2) { // Spot
		float spotEffect = dot(lightDir, l);
		// x - cutoff, y - cutoff - exponent
		if (spotEffect < spotlightData.x) {
			visibility *= smoothstep(spotlightData.y, spotlightData.x, spotEffect);
		}
	}
	
	vec3 h = normalize(v + l);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);
	float dotNL = dot(n, l);
	// float dotLV = dot(l, v);
	// float dotLH = dot(l, h);
	
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
		fragColor.rgb = albedo * ltcdiff + ltcspec;
	}
	else {
#endif

#ifdef _Cycles
	// Diff/glossy
	float facdif = min((1.0 - metrough.x) * 3.0, 1.0);
	float facspec = min(metrough.x * 3.0, 1.0);
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
	float tvis = traceShadow(-l, p);
	// vec2 coords = getProjectedCoord(hitCoord);
	// vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	// float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);
	// tvis *= screenEdgeFactor;
	visibility *= tvis;
#endif

// #ifdef _VoxelGI
	// if (dotNL > 0.0) visibility *= traceShadowCone(p / voxelgiResolution.x, l, distance(p, lightPos) / voxelgiResolution.x, n);
// #endif

	fragColor.rgb *= visibility;
}
