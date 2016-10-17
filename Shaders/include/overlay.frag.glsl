#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define _NoShadows
#define _LDR

#include "../compiled.glsl"
#include "../std/brdf.glsl"
// ...
#ifdef _Rad
#include "../std/math.glsl"
// envMapEquirect()
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

#ifdef _BaseTex
	uniform sampler2D sbase;
#endif
#ifndef _NoShadows
	//!uniform sampler2D shadowMap;
	#ifdef _PCSS
	//!uniform sampler2D snoise;
	//!uniform float lampSizeUV;
	//!uniform float lampNear;
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
#ifdef _MetTex
	uniform sampler2D smetal;
#else
	uniform float metalness;
#endif

uniform float envmapStrength;
uniform bool receiveShadow;
uniform vec3 lightDir;
uniform vec3 lightColor;
uniform float lightStrength;

in vec3 position;
#ifdef _Tex
	in vec2 texCoord;
#endif
in vec4 lampPos;
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
}
#endif

void main() {
	
#ifdef _NorTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
#else
	vec3 n = normalize(normal);
#endif

	vec3 l = normalize(lightDir);
	float dotNL = max(dot(n, l), 0.0);
	
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
	vec4 texel = texture(sbase, texCoord);
#ifdef _AlphaTest
	if (texel.a < 0.4)
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

	// Direct
	vec3 direct = diffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH, dotLV) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH, dotLH);	
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
	indirect = indirect * envmapStrength // * lightColor * lightStrength;
	fragColor = vec4(vec3(direct * visibility + indirect), 1.0);
	
#ifdef _OccTex
	vec3 occ = texture(socclusion, texCoord).rgb;
	fragColor.rgb *= occ;
#else
	fragColor.rgb *= occlusion; 
#endif

#ifdef _LDR
	fragColor.rgb = vec3(pow(fragColor.rgb, vec3(1.0 / 2.2)));
#endif
}
