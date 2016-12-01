#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/brdf.glsl"
// ...
#include "../std/math.glsl"
// envMapEquirect()
#include "../std/shirr.glsl"
// shIrradiance()
//!uniform float shirr[27];
#ifndef _NoShadows
	#ifdef _PCSS
	#include "../std/shadows_pcss.glsl"
	// PCSS()
	#else
	#include "../std/shadows.glsl"
	// PCF()
	#endif
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
	uniform float shadowsBias;
	// uniform bool receiveShadow; // TODO: pass uniform from exporter
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
uniform vec3 lightPos;
uniform vec3 lightDir;
uniform int lightType;
uniform vec3 lightColor;
uniform float lightStrength;
uniform float spotlightCutoff;
uniform float spotlightExponent;
uniform vec3 eye;

in vec4 wvpposition;
in vec3 position;
#ifdef _Tex
	in vec2 texCoord;
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
out vec4[2] fragColor;

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

void main() {
	
#ifdef _NorTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
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
	float dotNL = max(dot(n, l), 0.0);

	float visibility = 1.0;
#ifndef _NoShadows
	// if (receiveShadow) {
		if (lampPos.w > 0.0) {
			visibility = shadowTest(lampPos);
		}
	// }
#endif

	vec3 baseColor = matColor.rgb;
#ifdef _BaseTex
	vec4 texel = texture(sbase, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2));
	baseColor *= texel.rgb;
#endif

	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);

	float dotNV = max(dot(n, v), 0.0);
	float dotNH = max(dot(n, h), 0.0);
	float dotVH = max(dot(v, h), 0.0);
	float dotLV = max(dot(l, v), 0.0);
	float dotLH = max(dot(l, h), 0.0);

#ifdef _MetTex
	float metalness = texture(smetal, texCoord).r;
#endif
	vec3 albedo = surfaceAlbedo(baseColor, metalness);
	vec3 f0 = surfaceF0(baseColor, metalness);

#ifdef _RoughTex
	float roughness = texture(srough, texCoord).r;
#endif
#ifdef _RoughStr
	roughness *= roughnessStrength;
#endif

#ifdef _OccTex
	float occlusion = texture(socclusion, texCoord).r;
#endif

	// Direct
#ifdef _OrenNayar
	vec3 direct = orenNayarDiffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);
#else
	vec3 direct = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);
#endif

	if (lightType == 2) { // Spot
		float spotEffect = dot(lightDir, l);
		if (spotEffect < spotlightCutoff) {
			spotEffect = smoothstep(spotlightCutoff - spotlightExponent, spotlightCutoff, spotEffect);
			direct *= spotEffect;
		}
	}
	
	direct = direct * lightColor * lightStrength;

	// Indirect
	vec3 indirectDiffuse = shIrradiance(n, 2.2) / PI;	
#ifdef _EnvLDR
	indirectDiffuse = pow(indirectDiffuse, vec3(2.2));
#endif
	indirectDiffuse *= albedo;
	vec3 indirect = indirectDiffuse;
	
#ifdef _Rad
	vec3 reflectionWorld = reflect(-v, n); 
	float lod = getMipFromRoughness(roughness, envmapNumMipmaps);// + 1.0;
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
	#ifdef _EnvLDR
		prefilteredColor = pow(prefilteredColor, vec3(2.2));
	#endif
	vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
	vec3 indirectSpecular = prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
	indirect += indirectSpecular;
#endif
	indirect = indirect * envmapStrength;// * lightColor * lightStrength;


	vec4 premultipliedReflect = vec4(vec3(direct * visibility + indirect * occlusion), matColor.a);
#ifdef _BaseTex
		premultipliedReflect.a *= texel.a; // Base color alpha
#endif
	// vec4 premultipliedReflect = vec4(1.0, 0.0, 0.0, 0.01);
	// vec4 premultipliedReflect = baseColor;
	
	float fragZ = wvpposition.z / wvpposition.w;
	float a = min(1.0, premultipliedReflect.a) * 8.0 + 0.01;
	float b = -fragZ * 0.95 + 1.0;
	float w = clamp(a * a * a * 1e8 * b * b * b, 1e-2, 3e2);
	// accum = premultipliedReflect * w;
	// revealage = premultipliedReflect.a;
	// RT0 = vec4(C * w, a)
	// RT1 = vec4(vec3(a * w), 1)
	fragColor[0] = vec4(premultipliedReflect.rgb * w, premultipliedReflect.a);
	fragColor[1] = vec4(premultipliedReflect.a * w, 0.0, 0.0, 1.0);
}
