#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/brdf.glsl"
#ifdef _PolyLight
#include "../std/ltc.glsl"
#endif
#ifdef _Rad
#include "../std/math.glsl"
#endif
#ifndef _NoShadows
	#ifdef _PCSS
	#include "../std/shadows_pcss.glsl"
	// PCSS()
	#else
	#include "../std/shadows.glsl"
	// PCF()
	#endif
#endif
#include "../std/shirr.glsl"
// shIrradiance()
//!uniform float shirr[27];

#ifdef _PolyLight
	//!uniform sampler2D sltcMat;
	//!uniform sampler2D sltcMag;
#endif

#ifdef _BaseTex
	uniform sampler2D sbase;
#endif
#ifndef _NoShadows
	//!uniform sampler2D shadowMap;
	#ifdef _PCSS
	//!uniform sampler2D snoise;
	//!uniform float lampSizeUV;
	#endif
#endif
#ifdef _Rad
	uniform sampler2D senvmapRadiance;
	uniform sampler2D senvmapBrdf;
	uniform int envmapNumMipmaps;
#endif
#ifdef _NorTex
	uniform sampler2D snormal;
#endif
#ifdef _NorStr
	uniform float normalStrength;
#endif
#ifdef _OccTex
	uniform sampler2D socclusion;
#else
	uniform float occlusion;
#endif
#ifdef _RoughTex
uniform sampler2D srough;
#else
	uniform float roughness;
#endif
#ifdef _RoughStr
	uniform float roughnessStrength;
#endif
#ifdef _MetTex
	uniform sampler2D smetal;
#else
	uniform float metalness;
#endif

uniform float envmapStrength;
uniform bool receiveShadow;
uniform vec3 lightPos;
uniform vec3 lightDir;
uniform int lightType;
uniform vec3 lightColor;
uniform float lightStrength;
uniform float spotlightCutoff;
uniform float spotlightExponent;
uniform float shadowsBias;
uniform vec3 eye;
#ifdef _PolyLight
uniform vec3 lampArea0;
uniform vec3 lampArea1;
uniform vec3 lampArea2;
uniform vec3 lampArea3;
#endif

#ifdef _VoxelGI
	uniform sampler2D ssaotex;
	uniform sampler2D senvmapBrdf;
	//!uniform sampler3D voxels;
#endif

in vec3 position;
#ifdef _Tex
	in vec2 texCoord;
#endif
#ifdef _Tex1
	in vec2 texCoord1;
#endif
#ifndef _NoShadows
	in vec4 lampPos;
#endif
in vec4 matColor;
in vec3 eyeDir;
#ifdef _NorTex
	in mat3 TBN;
#else
	in vec3 normal;
#endif
out vec4 fragColor;

#ifndef _NoShadows
float shadowTest(vec4 lPos) {
	lPos.xyz /= lPos.w;
	lPos.xy = lPos.xy * 0.5 + 0.5;
	#ifdef _PCSS
	return PCSS(lPos.xy, lPos.z - shadowsBias);
	#else
	return PCF(lPos.xy, lPos.z - shadowsBias);
	#endif
	// return VSM(lPos.xy, lPos.z);
	// float distanceFromLight = texture(shadowMap, lPos.xy).r * 2.0 - 1.0;
	// return float(distanceFromLight > lPos.z - shadowsBias);
}
#endif

// #ifdef _Toon
// float stepmix(float edge0, float edge1, float E, float x) {
// 	float T = clamp(0.5 * (x - edge0 + E) / E, 0.0, 1.0);
// 	return mix(edge0, edge1, T);
// }
// #endif

void main() {
	
#ifdef _NorTex	
	#ifdef _NorTex1
	vec3 n = texture(snormal, texCoord1).rgb * 2.0 - 1.0;
	#else
	vec3 n = texture(snormal, texCoord).rgb * 2.0 - 1.0;
	#endif

	n = normalize(TBN * normalize(n));
	
	// vec3 normal = texture(snormal, texCoord).rgb * 2.0 - 1.0;
	// vec3 nn = normalize(normal);
	// vec3 dp1 = dFdx(position);
	// vec3 dp2 = dFdy(position);
	// vec2 duv1 = dFdx(texCoord);
	// vec2 duv2 = dFdy(texCoord);
	// vec3 dp2perp = cross(dp2, nn);
	// vec3 dp1perp = cross(nn, dp1);
	// vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
	// vec3 B = dp2perp * duv1.y + dp1perp * duv2.y; 
	// float invmax = inversesqrt(max(dot(T,T), dot(B,B)));
	// mat3 TBN = mat3(T * invmax, B * invmax, nn);
	// vec3 n = (TBN * nn);
#else
	vec3 n = normalize(normal);
#endif
#ifdef _NorStr
	n *= normalStrength;
#endif

	// Move out
	vec3 l;
	if (lightType == 0) { // Sun
		l = lightDir;
	}
	else { // Point, spot
		l = normalize(lightPos - position.xyz);
	}
	
	float visibility = 1.0;
#ifndef _NoShadows
	if (receiveShadow) {
		if (lampPos.w > 0.0) {
			visibility = shadowTest(lampPos);
		}
	}
#endif

	vec3 baseColor = matColor.rgb;

#ifdef _BaseTex
	#ifdef _BaseTex1
	vec4 texel = texture(sbase, texCoord1);
	#else
	vec4 texel = texture(sbase, texCoord);
	#endif

#ifdef _AlphaTest
	if (texel.a < 0.4)
		discard;
#endif

	texel.rgb = pow(texel.rgb, vec3(2.2));
	baseColor *= texel.rgb;
#endif

	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);

	float dotNL = dot(n, l);
	float dotNV = dot(n, v);
	float dotNH = dot(n, h);
	float dotVH = dot(v, h);

#ifdef _MetTex
	#ifdef _MetTex1
	float metalness = texture(smetal, texCoord1).r;
	#else
	float metalness = texture(smetal, texCoord).r;
	#endif
#endif

	vec3 albedo = surfaceAlbedo(baseColor, metalness);
	vec3 f0 = surfaceF0(baseColor, metalness);

#ifdef _RoughTex
	#ifdef _RoughTex1
	float roughness = texture(srough, texCoord1).r;
	#else
	float roughness = texture(srough, texCoord).r;
	#endif
#endif
#ifdef _RoughStr
	roughness *= roughnessStrength;
#endif


// #ifdef _Toon
// 	vec3 v = normalize(eyeDir);
// 	vec3 h = normalize(v + l);
	
// 	const vec3 ambientMaterial = baseColor * vec3(0.35, 0.35, 0.35) + vec3(0.15);
// 	const vec3 diffuseMaterial = baseColor;
// 	const vec3 specularMaterial = vec3(0.45, 0.35, 0.35);
// 	const float shininess = 0.5;
	
// 	float df = max(0.0, dotNL);
// 	float sf = max(0.0, dot(n, h));
//     sf = pow(sf, shininess);
	
// 	const float A = 0.1;
//     const float B = 0.3;
//     const float C = 0.6;
//     const float D = 1.0;
//     float E = fwidth(df);
// 	bool f = false;
// 	if (df > A - E) if (df < A + E) {
// 		f = true;
// 		df = stepmix(A, B, E, df);
// 	}
	
// 	/*else*/if (!f) if (df > B - E) if(df < B + E) {
// 		f = true;
// 		df = stepmix(B, C, E, df);
// 	}
	
// 	/*else*/if (!f) if (df > C - E) if (df < C + E) {
// 		f = true;
// 		df = stepmix(C, D, E, df);
// 	}
// 	/*else*/if (!f) if (df < A) {
// 		df = 0.0;
// 	}
// 	else if (df < B) {
// 		df = B;
// 	}
// 	else if (df < C) {
// 		df = C;
// 	}
// 	else df = D;
	
// 	E = fwidth(sf);
//     if (sf > 0.5 - E && sf < 0.5 + E) {
//         sf = smoothstep(0.5 - E, 0.5 + E, sf);
//     }
//     else {
//         sf = step(0.5, sf);
//     }
	
// 	fragColor.rgb = ambientMaterial + (df * diffuseMaterial + sf * specularMaterial) * visibility;
//     float edgeDetection = (dot(v, n) < 0.1) ? 0.0 : 1.0;
// 	fragColor.rgb *= edgeDetection;
	
// 	// const int levels = 4;
// 	// const float scaleFactor = 1.0 / levels;
	
// 	// float diffuse = max(0, dotNL);
// 	// const float material_kd = 0.8;
// 	// const float material_ks = 0.3;
// 	// vec3 diffuseColor = vec3(0.40, 0.60, 0.70);
// 	// diffuseColor = diffuseColor * material_kd * floor(diffuse * levels) * scaleFactor;
// 	// float specular = 0.0;
// 	// if(dotNL > 0.0) {
// 	// 	specular = material_ks * pow( max(0, dot( h, n)), shininess);
// 	// }
// 	// // Limit specular
// 	// float specMask = (pow(dot(h, n), shininess) > 0.4) ? 1.0 : 0.0;
	
// 	// float edgeDetection = (dot(v, n) > 0.3) ? 1.0 : 0.0;
// 	// fragColor.rgb = edgeDetection * ((diffuseColor + specular * specMask) * visibility + ambientMaterial);
// #endif



	// Direct
	vec3 direct;

#ifdef _PolyLight
	if (lightType == 3) { // Area
		float theta = acos(dotNV);
		vec2 tuv = vec2(roughness, theta / (0.5 * PI));
		tuv = tuv * LUT_SCALE + LUT_BIAS;
		// vec4 t = texture(sltcMat, tuv);
		vec4 t = clamp(texture(sltcMat, tuv), 0.0, 1.0);
		mat3 invM = mat3(
			vec3(1.0, 0.0, t.y),
			vec3(0.0, t.z, 0.0),
			vec3(t.w, 0.0, t.x));

		vec3 ltcspec = ltcEvaluate(n, v, dotNV, position, invM, lampArea0, lampArea1, lampArea2, lampArea3, false); 
		ltcspec *= texture(sltcMag, tuv).a;
		
		vec3 ltcdiff = ltcEvaluate(n, v, dotNV, position, mat3(1.0), lampArea0, lampArea1, lampArea2, lampArea3, false);
		direct = ltcdiff * albedo + ltcspec;
	}
	else {
#endif

	// Direct
#ifdef _OrenNayar
	direct = orenNayarDiffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);
#else
	direct = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);
#endif

	if (lightType == 2) { // Spot
		float spotEffect = dot(lightDir, l);
		if (spotEffect < spotlightCutoff) {
			spotEffect = smoothstep(spotlightCutoff - spotlightExponent, spotlightCutoff, spotEffect);
			direct *= spotEffect;
		}
	}

#ifdef _PolyLight
	}
#endif
	
	direct = direct * lightColor * lightStrength;


#ifdef _VoxelGI
	vec3 tangent = normalize(cross(n, vec3(0.0, 1.0, 0.0)));
	if (length(tangent) == 0.0) {
		tangent = normalize(cross(n, vec3(0.0, 0.0, 1.0)));
	}
	vec3 bitangent = normalize(cross(n, tangent));
	mat3 tanToWorld = inverse(transpose(mat3(tangent, bitangent, n)));

	float diffOcclusion = 0.0;
	vec3 indirectDiffuse = indirectLight(tanToWorld, n, diffOcclusion).rgb * 4.0;
	indirectDiffuse *= albedo;
	diffOcclusion = min(1.0, 1.5 * diffOcclusion);

	vec3 reflectWorld = reflect(-v, n);
	float specularOcclusion;
	float lodOffset = 0.0;//getMipFromRoughness(roughness, numMips);
	vec3 indirectSpecular = coneTrace(reflectWorld, n, 0.07 + lodOffset, specularOcclusion).rgb;
	if (roughness > 0.0) { // Temp..
		vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
		indirectSpecular *= (f0 * envBRDF.x + envBRDF.y);
	}

	vec3 indirect = indirectDiffuse * diffOcclusion + indirectSpecular;

#else

	// Indirect
	vec3 indirectDiffuse = shIrradiance(n, 2.2) / PI;	
#ifdef _EnvLDR
	indirectDiffuse = pow(indirectDiffuse, vec3(2.2));
#endif
	indirectDiffuse *= albedo;
	vec3 indirect = indirectDiffuse;
	
#ifdef _Rad
	vec3 reflectionWorld = reflect(-v, n); 
	float lod = getMipFromRoughness(roughness, envmapNumMipmaps);
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
	#ifdef _EnvLDR
		prefilteredColor = pow(prefilteredColor, vec3(2.2));
	#endif
	vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
	vec3 indirectSpecular = prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
	indirect += indirectSpecular;
#endif
	indirect = indirect * envmapStrength;// * lightColor * lightStrength;

#endif	

	fragColor = vec4(vec3(direct * visibility + indirect), 1.0);

#ifdef _OccTex
	#ifdef _OccTex1
	float occ = texture(socclusion, texCoord1).r;
	#else
	float occ = texture(socclusion, texCoord).r;
	#endif
	fragColor.rgb *= occ;
#else
	fragColor.rgb *= occlusion; 
#endif

#ifdef _LDR
	fragColor = vec4(pow(fragColor.rgb, vec3(1.0 / 2.2)), fragColor.a);
#endif
}
