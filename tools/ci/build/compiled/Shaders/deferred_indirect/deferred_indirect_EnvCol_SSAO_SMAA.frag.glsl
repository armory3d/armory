#version 450
#define _EnvCol
#define _SSAO
#define _SMAA

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/gbuffer.glsl"
// octahedronWrap()
// unpackFloat()
#include "../std/math.glsl"
// envMapEquirect()
#include "../std/brdf.glsl"
#include "../std/shirr.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

//!uniform float shirr[27];
uniform float envmapStrength;
#ifdef _Rad
	uniform sampler2D senvmapRadiance;
	uniform sampler2D senvmapBrdf;
	uniform int envmapNumMipmaps;
#endif

#ifdef _SSAO
	uniform sampler2D ssaotex;
#endif

#ifdef _Rad
	uniform vec3 eye;
	uniform vec3 eyeLook;
#endif

in vec2 texCoord;
#ifdef _Rad
	in vec3 viewRay;
#endif
out vec4 fragColor;

void main() {
	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, mask
	
	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	vec2 metrough = unpackFloat(g0.b);

#ifdef _Rad
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	vec3 p = getPos(eye, eyeLook, viewRay, depth);
	vec3 v = normalize(eye - p.xyz);
#endif

	// Indirect
	vec3 indirect = shIrradiance(n, 2.2) / PI;
#ifdef _Rad
	vec3 reflectionWorld = reflect(-v, n);
	float lod = getMipFromRoughness(metrough.y, envmapNumMipmaps);
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
#endif

#ifdef _EnvLDR
	indirect = pow(indirect, vec3(2.2));
	#ifdef _Rad
		prefilteredColor = pow(prefilteredColor, vec3(2.2));
	#endif
#endif

	vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, occlusion
	vec3 albedo = surfaceAlbedo(g1.rgb, metrough.x); // g1.rgb - basecolor
	indirect *= albedo;
	
#ifdef _Rad
	// Indirect specular
	float dotNV = max(dot(n, v), 0.0);
	
	vec3 f0 = surfaceF0(g1.rgb, metrough.x);

	vec2 envBRDF = texture(senvmapBrdf, vec2(metrough.y, 1.0 - dotNV)).xy;
	indirect += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
#endif

	indirect = indirect * envmapStrength;// * lightColor;
	indirect = indirect * g1.a; // Occlusion

#ifdef _SSAO
	indirect *= texture(ssaotex, texCoord).r; // SSAO
#endif
	
	fragColor.rgb = indirect;
}
