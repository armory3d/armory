#version 450

#include "../compiled.glsl"
#include "../std/gbuffer.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform sampler2D dist;

uniform vec2 dirInv; // texStep

in vec2 texCoord;
out float fragColor;

const float blurWeights[10] = float[] (0.132572, 0.125472, 0.106373, 0.08078, 0.05495, 0.033482, 0.018275, 0.008934, 0.003912, 0.001535);
const float discardThreshold = 0.95;

float doBlur(const float blurWeight, const int pos, const vec3 nor, const vec2 texCoord) {
	const float posadd = pos + 0.5;

	vec3 nor2 = getNor(texture(gbuffer0, texCoord + pos * dirInv).rg);
	float influenceFactor = step(discardThreshold, dot(nor2, nor));
	float col = texture(tex, texCoord + posadd * dirInv).r;
	fragColor += col * blurWeight * influenceFactor;
	float weight = blurWeight * influenceFactor;
	
	nor2 = getNor(texture(gbuffer0, texCoord - pos * dirInv).rg);
	influenceFactor = step(discardThreshold, dot(nor2, nor));
	col = texture(tex, texCoord - posadd * dirInv).r;
	fragColor += col * blurWeight * influenceFactor;
	weight += blurWeight * influenceFactor;
	
	return weight;
}

void main() {
	vec3 nor = getNor(texture(gbuffer0, texCoord).rg);
	
	float sm = texture(tex, texCoord).r;
	fragColor = sm * blurWeights[0];
	float weight = blurWeights[0];
	float d = texture(dist, texCoord).r;
	int numTaps = min(int(d * 10 * penumbraScale), 10 * penumbraScale);
	#ifdef _PenumbraScale
	for (int i = 1; i < numTaps; ++i) weight += doBlur(blurWeights[int(i / penumbraScale)], i, nor, texCoord);
	#else
	for (int i = 1; i < numTaps; ++i) weight += doBlur(blurWeights[i - 1], i, nor, texCoord);
	#endif
	fragColor /= weight;
}
