// Exclusive to SSAO for now
#version 450

#include "compiled.glsl"
#include "std/gbuffer.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0;

uniform vec2 dirInv; // texStep

in vec2 texCoord;
out vec4 fragColor;

const float blurWeights[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
const float discardThreshold = 0.95;

float doBlur(const float blurWeight, const int pos, const vec3 nor, const vec2 texCoord) {
	const float posadd = pos + 0.5;

	vec3 nor2 = getNor(texture(gbuffer0, texCoord + pos * dirInv).rg);
	float influenceFactor = step(discardThreshold, dot(nor2, nor));
	float col = texture(tex, texCoord + posadd * dirInv).r;
	fragColor.r += col * blurWeight * influenceFactor;
	float weight = blurWeight * influenceFactor;
	
	nor2 = getNor(texture(gbuffer0, texCoord - pos * dirInv).rg);
	influenceFactor = step(discardThreshold, dot(nor2, nor));
	col = texture(tex, texCoord - posadd * dirInv).r;
	fragColor.r += col * blurWeight * influenceFactor;
	weight += blurWeight * influenceFactor;
	
	return weight;
}

void main() {
	vec2 tc = texCoord * ssaoTextureScale;
	vec3 nor = getNor(texture(gbuffer0, texCoord).rg);
	
	fragColor.r = texture(tex, tc).r * blurWeights[0];
	float weight = blurWeights[0];
	weight += doBlur(blurWeights[1], 1, nor, tc);
	weight += doBlur(blurWeights[2], 2, nor, tc);
	weight += doBlur(blurWeights[3], 3, nor, tc);
	weight += doBlur(blurWeights[4], 4, nor, tc);

	fragColor = vec4(fragColor.r / weight); // SSAO only
}