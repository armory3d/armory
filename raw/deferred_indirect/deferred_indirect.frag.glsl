#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

#ifdef _Probes
	uniform float shirr[27 * 20]; // Maximum of 20 SH sets
#else
	uniform float shirr[27];
#endif
uniform float envmapStrength;
#ifdef _Rad
	uniform sampler2D senvmapRadiance;
	uniform sampler2D senvmapBrdf;
	uniform int envmapNumMipmaps;
#endif

// uniform sampler2D giblur; // Path-traced

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

#ifdef _Rad
float getMipLevelFromRoughness(float roughness) {
	// First mipmap level = roughness 0, last = roughness = 1
	// baseColor texture already counted
	return roughness * envmapNumMipmaps;
}
#endif

vec3 surfaceAlbedo(vec3 baseColor, float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(vec3 baseColor, float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
}

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / PI2, phi / PI);
}

vec2 octahedronWrap(vec2 v) {
	return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

#ifdef _Rad
vec3 getPos(float depth) {	
	vec3 vray = normalize(viewRay);
	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
	const float projectionB = (-cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}
#endif

vec2 unpackFloat(float f) {
	return vec2(floor(f) / 1000.0, fract(f));
}

#ifdef _Probes
vec3 shIrradiance(vec3 nor, float scale, int probe) {
#else
vec3 shIrradiance(vec3 nor, float scale) {
#endif
	const float c1 = 0.429043;
	const float c2 = 0.511664;
	const float c3 = 0.743125;
	const float c4 = 0.886227;
	const float c5 = 0.247708;
	vec3 cl00, cl1m1, cl10, cl11, cl2m2, cl2m1, cl20, cl21, cl22;
#ifdef _Probes
	if (probe == 0) {
#endif
		cl00 = vec3(shirr[0], shirr[1], shirr[2]);
		cl1m1 = vec3(shirr[3], shirr[4], shirr[5]);
		cl10 = vec3(shirr[6], shirr[7], shirr[8]);
		cl11 = vec3(shirr[9], shirr[10], shirr[11]);
		cl2m2 = vec3(shirr[12], shirr[13], shirr[14]);
		cl2m1 = vec3(shirr[15], shirr[16], shirr[17]);
		cl20 = vec3(shirr[18], shirr[19], shirr[20]);
		cl21 = vec3(shirr[21], shirr[22], shirr[23]);
		cl22 = vec3(shirr[24], shirr[25], shirr[26]);
#ifdef _Probes
	}
	else if (probe == 1) {
		cl00 = vec3(shirr[27 + 0], shirr[27 + 1], shirr[27 + 2]);
		cl1m1 = vec3(shirr[27 + 3], shirr[27 + 4], shirr[27 + 5]);
		cl10 = vec3(shirr[27 + 6], shirr[27 + 7], shirr[27 + 8]);
		cl11 = vec3(shirr[27 + 9], shirr[27 + 10], shirr[27 + 11]);
		cl2m2 = vec3(shirr[27 + 12], shirr[27 + 13], shirr[27 + 14]);
		cl2m1 = vec3(shirr[27 + 15], shirr[27 + 16], shirr[27 + 17]);
		cl20 = vec3(shirr[27 + 18], shirr[27 + 19], shirr[27 + 20]);
		cl21 = vec3(shirr[27 + 21], shirr[27 + 22], shirr[27 + 23]);
		cl22 = vec3(shirr[27 + 24], shirr[27 + 25], shirr[27 + 26]);
	}
#endif
	return (
		c1 * cl22 * (nor.x * nor.x - (-nor.z) * (-nor.z)) +
		c3 * cl20 * nor.y * nor.y +
		c4 * cl00 -
		c5 * cl20 +
		2.0 * c1 * cl2m2 * nor.x * (-nor.z) +
		2.0 * c1 * cl21  * nor.x * nor.y +
		2.0 * c1 * cl2m1 * (-nor.z) * nor.y +
		2.0 * c2 * cl11  * nor.x +
		2.0 * c2 * cl1m1 * (-nor.z) +
		2.0 * c2 * cl10  * nor.y
	) * scale;
}

void main() {
	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, roughness/metallic, mask
	
	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	vec2 roughmet = unpackFloat(g0.b);

#ifdef _Rad
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	vec3 p = getPos(depth);
	vec3 v = normalize(eye - p.xyz);
#endif
	
	// Indirect
#ifdef _Probes
	float probeFactor = mask;
	float probeID = floor(probeFactor);
	float probeFract = fract(probeFactor);
	vec3 indirect;
	#ifdef _Rad
		float lod = getMipLevelFromRoughness(roughmet.x);
		vec3 reflectionWorld = reflect(-v, n); 
		vec2 envCoordRefl = envMapEquirect(reflectionWorld);
		vec3 prefilteredColor = textureLod(senvmapRadiance, envCoordRefl, lod).rgb;
	#endif
	
	// Global probe only
	if (probeID == 0.0) {
		indirect = shIrradiance(n, 2.2, 0) / PI;
	}
	// fract 0 = local probe, 1 = global probe 
	else if (probeID == 1.0) {
		indirect = (shIrradiance(n, 2.2, 1) / PI) * (1.0 - probeFract);
		//prefilteredColor /= 4.0;
		if (probeFract > 0.0) {
			indirect += (shIrradiance(n, 2.2, 0) / PI) * (probeFract);
		}
	}
#else // No probes   
		// vec3 indirect = texture(shirr, envMapEquirect(n)).rgb;
	vec3 indirect = shIrradiance(n, 2.2) / PI;
	#ifdef _Rad
		vec3 reflectionWorld = reflect(-v, n);
		float lod = getMipLevelFromRoughness(roughmet.x);
		vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
	#endif
#endif

#ifdef _EnvLDR
	indirect = pow(indirect, vec3(2.2));
	#ifdef _Rad
		prefilteredColor = pow(prefilteredColor, vec3(2.2));
	#endif
#endif

	vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, occlusion
	vec3 albedo = surfaceAlbedo(g1.rgb, roughmet.y); // g1.rgb - basecolor
	indirect *= albedo;
	
#ifdef _Rad
	// Indirect specular
	float dotNV = max(dot(n, v), 0.0);
	
	vec3 f0 = surfaceF0(g1.rgb, roughmet.y);

	vec2 envBRDF = texture(senvmapBrdf, vec2(roughmet.x, 1.0 - dotNV)).xy;
	indirect += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);;
#endif

	indirect = indirect * envmapStrength;// * lightColor * lightStrength;
	indirect = indirect * g1.a; // Occlusion

#ifdef _SSAO
	indirect *= texture(ssaotex, texCoord).r; // SSAO
#endif
	
	gl_FragColor.rgb = indirect;
}
