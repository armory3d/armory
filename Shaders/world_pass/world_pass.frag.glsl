#version 450

#include "compiled.glsl"
#ifdef _EnvTex
#include "std/math.glsl"
#endif

#ifdef _EnvCol
	uniform vec3 backgroundCol;
#endif
#ifdef _EnvSky
	uniform vec3 A;
	uniform vec3 B;
	uniform vec3 C;
	uniform vec3 D;
	uniform vec3 E;
	uniform vec3 F;
	uniform vec3 G;
	uniform vec3 H;
	uniform vec3 I;
	uniform vec3 Z;
	uniform vec3 sunDirection;
#endif
#ifdef _EnvClouds
	uniform sampler2D snoise;
	uniform float time;
	// uniform vec3 eye;
	const float difference = cloudsUpper - cloudsLower;
	const float steps = 25.0;
#endif
#ifdef _EnvTex
	uniform sampler2D envmap;
#endif
#ifdef _EnvImg // Static background
	uniform vec2 screenSize;
	uniform sampler2D envmap;
#endif

#ifdef _EnvStr
uniform float envmapStrength;
#endif

// in vec2 texCoord;
in vec3 normal;
out vec4 fragColor;

#ifdef _EnvSky
vec3 hosekWilkie(float cos_theta, float gamma, float cos_gamma) {
	vec3 chi = (1 + cos_gamma * cos_gamma) / pow(1 + H * H - 2 * cos_gamma * H, vec3(1.5));
	return (1 + A * exp(B / (cos_theta + 0.01))) * (C + D * exp(E * gamma) + F * (cos_gamma * cos_gamma) + G * chi + I * sqrt(cos_theta));
}
#endif

#ifdef _EnvClouds
// float hash(vec3 p) {
	// p = fract(p * vec3(0.16532, 0.17369, 0.15787));
	// p += dot(p.xyz, p.zyx + 19.19);
	// return fract(p.x * p.y * p.z);
// }
float noise(vec3 x) {
	vec3 p = floor(x);
	vec3 f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	vec2 uv = (p.xy + vec2(37.0, 17.0) * p.z) + f.xy;
	vec2 rg = texture(snoise, (uv + 0.5) / 256.0).yx;
	return mix(rg.x, rg.y, f.z);
}
float fbm(vec3 p) {
	p *= 0.0005 * cloudsSize;
	float f = 0.5 * noise(p); p = p * 3.0; p.y += time * cloudsWind.x;
	f += 0.25 * noise(p); p = p * 2.0; p.y += time * cloudsWind.y;
	f += 0.125 * noise(p); p = p * 3.0;
	f += 0.0625 * noise(p); p = p * 3.0;
	f += 0.03125 * noise(p); p = p * 3.0;
	f += 0.015625 * noise(p);
	return f;
}
float map(vec3 p) {
	return fbm(p) - cloudsDensity * 0.6;
}
// Weather by David Hoskins, https://www.shadertoy.com/view/4dsXWn
// Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
vec3 traceP;
vec2 doCloudTrace(vec3 add, vec2 shadeSum) {
	float h = map(traceP);
	vec2 shade = vec2(traceP.z / difference, max(-h, 0.0));
	traceP += add;
	return shadeSum + shade * (1.0 - shadeSum.y);
}
vec2 traceCloud(vec3 pos, vec3 dir) {
	float beg = ((cloudsLower - pos.z) / dir.z);
	float end = ((cloudsUpper - pos.z) / dir.z);
	traceP = vec3(pos.x + dir.x * beg, pos.y + dir.y * beg, 0.0);
	// beg += hash(traceP) * 150.0; // Noisy
	vec3 add = dir * ((end - beg) / steps);

	vec2 shadeSum = vec2(0.0);
	for (int i = 0; i < steps; i++) {
		shadeSum = doCloudTrace(add, shadeSum);
		if (shadeSum.y >= 1.0) return shadeSum;
	}
	return shadeSum;
}
// GPU PRO 7 - Real-time Volumetric Cloudscapes
// https://www.guerrilla-games.com/read/the-real-time-volumetric-cloudscapes-of-horizon-zero-dawn
vec3 cloudsColor(vec3 R, vec3 pos, vec3 dir) {
	vec2 traced = traceCloud(pos, dir);
	float d = traced.x / 200.0 * traced.y + traced.x / 1500.0 * cloudsSecondary;
	const float g = cloudsEccentricity;
#ifdef _EnvSky
	float cosAngle = dot(sunDirection, dir);
#else // Predefined sun direction
	float cosAngle = dot(vec3(0.0, -1.0, 0.0), dir);
#endif
	float E = 2.0 * exp(-d * cloudsPrecipitation) * (1.0 - exp(-2.0 * d)) * (0.25 * PI) * ((1.0 - g * g) / pow(1.0 + g * g - 2.0 * g * cosAngle, 3.0 / 2.0));
	return mix(vec3(R), vec3(E * 24.0), d * 12.0);
}
#endif

void main() {

#ifdef _EnvCol
	fragColor.rgb = backgroundCol;
#ifdef _EnvTransp
	return;
#endif
#ifdef _EnvClouds
	vec3 n = normalize(normal);
#endif
#endif

#ifndef _EnvSky // Prevent case when sky radiance is enabled
#ifdef _EnvTex
	vec3 n = normalize(normal);
	fragColor.rgb = texture(envmap, envMapEquirect(n)).rgb * envmapStrength;
	#ifdef _EnvLDR
	fragColor.rgb = pow(fragColor.rgb, vec3(2.2));
	#endif
#endif
#endif

#ifdef _EnvImg // Static background
	// Will have to get rid of gl_FragCoord, pass tc from VS
	vec2 texco = gl_FragCoord.xy / screenSize;
	fragColor.rgb = texture(envmap, vec2(texco.x, 1.0 - texco.y)).rgb * envmapStrength;
#endif

#ifdef _EnvSky
	vec3 n = normalize(normal);
	float phi = acos(n.z);
	float theta = atan(-n.y, n.x) + PI;
	
	float cos_theta = clamp(n.z, 0.0, 1.0);
	float cos_gamma = dot(n, sunDirection);
	float gamma_val = acos(cos_gamma);

	fragColor.rgb = Z * hosekWilkie(cos_theta, gamma_val, cos_gamma) * envmapStrength;
#endif

#ifdef _EnvClouds
	// cloudsColor(fragColor.rgb, eye, n)
	vec3 clouds = cloudsColor(fragColor.rgb, vec3(0.0), n);
	if (n.z > 0.0) fragColor.rgb = mix(fragColor.rgb, clouds, n.z * 5.0 * envmapStrength);
#endif

#ifdef _LDR
	fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / 2.2));
#endif
}
