// Alchemy AO / Scalable Ambient Obscurance
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/brdf.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform mat4 invVP;

#ifdef _CPostprocess
	uniform vec3 PPComp12;
#endif

in vec2 texCoord;
in vec3 viewRay;
out vec3 fragColor;

void main() {
	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	if (depth == 1.0) { fragColor = vec3(0.0); return; }

	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	float metallic;
	uint matid;
	unpackFloatInt16(g0.a, metallic, matid);

	vec3 basecol = textureLod(gbuffer1, texCoord, 0.0).rgb;
	vec3 albedo = surfaceAlbedo(basecol, metallic);
	float roughness = textureLod(gbuffer0, texCoord, 0.0).b;

	vec3 indirectLight = vec3(0.0);
	float weightSum = 0.0;


	vec3 vray = normalize(viewRay);
	vec3 currentPos = getPosNoEye(eyeLook, vray, depth, cameraProj);
	// vec3 currentPos = getPos2NoEye(eye, invVP, depth, texCoord);
	float currentDistance = length(currentPos);
	#ifdef _CPostprocess
		float currentDistanceA = currentDistance * PPComp12.z * (1.0 / PPComp12.y);
	#else
		float currentDistanceA = currentDistance * ssaoScale * (1.0 / ssaoRadius);
	#endif
	float currentDistanceB = currentDistance * 0.0005;
	ivec2 px = ivec2(texCoord * screenSize);
	float phi = (3 * px.x ^ px.y + px.x * px.y) * 10;

	fragColor = vec3(0.0);
	const int samples = 8;
	const float samplesInv = PI2 * (1.0 / samples);

	for (int i = 0; i < samples; ++i) {
		float theta = samplesInv * (i + 0.5) + phi;
		vec2 k = vec2(cos(theta), sin(theta)) / currentDistanceA;
		vec2 offsetTC = texCoord + k;

		float sampleDepth = textureLod(gbufferD, offsetTC, 0.0).r * 2.0 - 1.0;
		vec3 samplePos = getPos2NoEye(eye, invVP, sampleDepth, offsetTC);
		vec3 toSample = samplePos - currentPos;
		float dist2 = dot(toSample, toSample);

		vec3 sampleNormal;
		vec2 sampleEnc = textureLod(gbuffer0, offsetTC, 0.0).rg;
		sampleNormal.z = 1.0 - abs(sampleEnc.x) - abs(sampleEnc.y);
		sampleNormal.xy = sampleNormal.z >= 0.0 ? sampleEnc.xy : octahedronWrap(sampleEnc.xy);
		sampleNormal = normalize(sampleNormal);

		vec3 sampleAlbedo = textureLod(gbuffer1, offsetTC, 0.0).rgb;

		// Visibility and weighting
		float nDotL = max(dot(n, normalize(toSample)), 0.0);
		float visibility = max(dot(sampleNormal, -normalize(toSample)), 0.0);
		float attenuation = 1.0 / (dist2 + 0.015);

		float weight = nDotL * visibility * attenuation;
		indirectLight += sampleAlbedo * weight;
		weightSum += weight;
	}

	if (weightSum > 0.0) {
		indirectLight /= weightSum;
	}

	#ifdef _CPostprocess
		indirectLight *= PPComp12.x * 0.3;
	#else
		indirectLight *= ssaoStrength * 0.3;
	#endif

	float roughnessFactor = 1.0 - roughness;
	indirectLight *= roughnessFactor;

	fragColor = indirectLight; // simple luminance
}
