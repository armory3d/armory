// Alchemy AO / Scalable Ambient Obscurance
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform mat4 invVP;

#ifdef _CPostprocess
uniform vec3 PPComp11;
uniform vec3 PPComp12;
#endif

in vec2 texCoord;
in vec3 viewRay;
out float fragColor;

void main() {
	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	if (depth == 1.0) { fragColor = 1.0; return; }

	vec2 enc = textureLod(gbuffer0, texCoord, 0.0).rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 vray = normalize(viewRay);
	vec3 currentPos = getPosNoEye(eyeLook, vray, depth, cameraProj);
	// vec3 currentPos = getPos2NoEye(eye, invVP, depth, texCoord);
	float currentDistance = length(currentPos);
	#ifdef _CPostprocess
		float currentDistanceA = currentDistance * PPComp12.y * (1.0 / PPComp11.z);
	#else
		float currentDistanceA = currentDistance * ssaoScale * (1.0 / ssaoRadius);
	#endif
	float currentDistanceB = currentDistance * 0.0005;
	ivec2 px = ivec2(texCoord * screenSize);
	float phi = (3 * px.x ^ px.y + px.x * px.y) * 10;

	fragColor = 0;
	const int samples = 8;
	const float samplesInv = PI2 * (1.0 / samples);
	for (int i = 0; i < samples; ++i) {
		float theta = samplesInv * (i + 0.5) + phi;
		vec2 k = vec2(cos(theta), sin(theta)) / currentDistanceA;
		depth = textureLod(gbufferD, texCoord + k, 0.0).r * 2.0 - 1.0;
		// vec3 pos = getPosNoEye(eyeLook, vray, depth, cameraProj) - currentPos;
		vec3 pos = getPos2NoEye(eye, invVP, depth, texCoord + k) - currentPos;
		fragColor += max(0, dot(pos, n) - currentDistanceB) / (dot(pos, pos) + 0.015);
	}

	#ifdef _CPostprocess
		fragColor *= (PPComp12.x * 0.3) / samples;
	#else
		fragColor *= (ssaoStrength * 0.3) / samples;
	#endif
	fragColor = 1.0 - fragColor;
}
