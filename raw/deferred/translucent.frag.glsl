#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

#ifdef _NMTex
#define _AMTex
#endif

#ifdef _AMTex
	uniform sampler2D salbedo;
#endif
#ifdef _NMTex
	uniform sampler2D snormal;
#endif
#ifdef _OMTex
	uniform sampler2D som;
#endif
#ifdef _RMTex
	uniform sampler2D srm;
#else
	uniform float roughness;
#endif
#ifdef _MMTex
	uniform sampler2D smm;
#else
	uniform float metalness;
#endif
uniform float mask;

uniform sampler2D senvmapRadiance;
uniform sampler2D senvmapIrradiance;
uniform sampler2D senvmapBrdf;
uniform float envmapStrength;
uniform int envmapNumMipmaps;
uniform vec3 light;
uniform vec3 lightColor;
uniform float lightStrength;
uniform vec3 eye;

in vec4 mvpposition;
in vec3 position;
#ifdef _Tex
	in vec2 texCoord;
#endif
in vec4 lPos;
in vec4 matColor;
#ifdef _NMTex
	in mat3 TBN;
#else
	in vec3 normal;
#endif
out vec4[2] outColor;

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / PI2, phi / PI);
}

float getMipLevelFromRoughness(float roughness) {
	// First mipmap level = roughness 0, last = roughness = 1
	return roughness * envmapNumMipmaps;
}

vec3 surfaceAlbedo(vec3 baseColor, float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(vec3 baseColor, float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
}

vec3 f_schlick(vec3 f0, float vh) {
	return f0 + (1.0-f0)*exp2((-5.55473 * vh - 6.98316)*vh);
}

float v_smithschlick(float nl, float nv, float a) {
	return 1.0 / ( (nl*(1.0-a)+a) * (nv*(1.0-a)+a) );
}

float d_ggx(float nh, float a) {
	float a2 = a*a;
	float denom = pow(nh*nh * (a2-1.0) + 1.0, 2.0);
	return a2 * (1.0 / 3.1415926535) / denom;
}

vec3 specularBRDF(vec3 f0, float roughness, float nl, float nh, float nv, float vh, float lh) {
	float a = roughness * roughness;
	return d_ggx(nh, a) * clamp(v_smithschlick(nl, nv, a), 0.0, 1.0) * f_schlick(f0, vh) / 4.0;
	//return vec3(LightingFuncGGX_OPT3(nl, lh, nh, roughness, f0[0]));
}

vec3 lambert(vec3 albedo, float nl) {
	return albedo * max(0.0, nl);
}

vec3 diffuseBRDF(vec3 albedo, float roughness, float nv, float nl, float vh, float lv) {
	return lambert(albedo, nl);
}


void main() {
	
#ifdef _NMTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
#else
	vec3 n = normalize(normal);
#endif

	vec4 baseColor = matColor;
#ifdef _AMTex
	vec4 texel = texture(salbedo, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2));
	baseColor *= texel;
#endif

#ifdef _MMTex
	float metalness = texture(smm, texCoord).r;
#endif

#ifdef _RMTex
	float roughness = texture(srm, texCoord).r;
#endif
		
#ifdef _OMTex
	float occlusion = texture(som, texCoord).r;
#else
	float occlusion = 1.0; 
#endif


	vec3 lightDir = light - position.xyz;
    vec3 eyeDir = eye - position.xyz;
	vec3 l = normalize(lightDir);
	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);

	float dotNL = max(dot(n, l), 0.0);
	float dotNV = max(dot(n, v), 0.0);
	float dotNH = max(dot(n, h), 0.0);
	float dotVH = max(dot(v, h), 0.0);
	float dotLV = max(dot(l, v), 0.0);
	float dotLH = max(dot(l, h), 0.0);
	
	vec3 albedo = surfaceAlbedo(baseColor.rgb, metalness);
	vec3 f0 = surfaceF0(baseColor.rgb, metalness);
	
	// Direct
	vec3 direct = diffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH, dotLV) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH, dotLH);
	direct = direct * lightColor * lightStrength;

	// Indirect
	vec3 indirectDiffuse = texture(senvmapIrradiance, envMapEquirect(n)).rgb;
	// indirectDiffuse = pow(indirectDiffuse, vec3(2.2));
	indirectDiffuse *= albedo;
	
	vec3 reflectionWorld = reflect(-v, n); 
	float lod = getMipLevelFromRoughness(roughness);// + 1.0;
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
	// prefilteredColor = pow(prefilteredColor, vec3(2.2));
	
	vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
	vec3 indirectSpecular = prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
	vec3 indirect = indirectDiffuse + indirectSpecular;
	indirect = indirect * lightColor * lightStrength * envmapStrength;

	vec4 premultipliedReflect = vec4(vec3(direct + indirect * occlusion), baseColor.a);

	// vec4 premultipliedReflect = vec4(1.0, 0.0, 0.0, 0.01);
	// vec4 premultipliedReflect = baseColor;
	float fragZ = mvpposition.z / mvpposition.w;
	float a = min(1.0, premultipliedReflect.a) * 8.0 + 0.01;
    float b = -fragZ * 0.95 + 1.0;
	float w = clamp(a * a * a * 1e8 * b * b * b, 1e-2, 3e2);
    // accum = premultipliedReflect * w;
    // revealage = premultipliedReflect.a;
	// RT0 = vec4(C*w, a)
	// RT1 = vec4(vec3(a*w), 1)
	outColor[0] = vec4(premultipliedReflect.rgb * w, premultipliedReflect.a);
	outColor[1] = vec4(vec3(premultipliedReflect.a * w), 1.0);
}
