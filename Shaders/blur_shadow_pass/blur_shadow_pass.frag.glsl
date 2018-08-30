#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform sampler2D dist;

uniform vec2 dirInv; // texStep

in vec2 texCoord;
out float fragColor;

const float blurWeights[10] = float[] (0.132572, 0.125472, 0.106373, 0.08078, 0.05495, 0.033482, 0.018275, 0.008934, 0.003912, 0.001535);
const float discardThreshold = 0.95;

float doBlur(const float blurWeight, const int pos, const vec3 nor, const float depth, const vec2 texCoord) {
	const float posadd = pos + 0.5;

	vec4 g0 = texture(gbuffer0, texCoord + pos * dirInv);
	vec3 nor2 = getNor(g0.rg);
	float influenceFactor = step(discardThreshold, dot(nor2, nor)) * step(abs(depth - g0.a), 0.001);
	float col = texture(tex, texCoord + posadd * dirInv).r;
	fragColor += col * blurWeight * influenceFactor;
	float weight = blurWeight * influenceFactor;
	
	g0 = texture(gbuffer0, texCoord - pos * dirInv);
	nor2 = getNor(g0.rg);
	influenceFactor = step(discardThreshold, dot(nor2, nor)) * step(abs(depth - g0.a), 0.001);
	col = texture(tex, texCoord - posadd * dirInv).r;
	fragColor += col * blurWeight * influenceFactor;
	weight += blurWeight * influenceFactor;
	
	return weight;
}

void main() {
	vec4 g0 = texture(gbuffer0, texCoord);
	vec3 nor = getNor(g0.rg);
	float depth = g0.a;
	
	float sm = texture(tex, texCoord).r;
	fragColor = sm * blurWeights[0];
	float weight = blurWeights[0];
	float d = texture(dist, texCoord).r;
	int numTaps = clamp(int(d * 10 * penumbraScale), 2, 10 * penumbraScale);
	#ifdef _PenumbraScale
	for (int i = 1; i < numTaps; ++i) weight += doBlur(blurWeights[int(i / penumbraScale)], i, nor, depth, texCoord);
	#else
	for (int i = 1; i < numTaps; ++i) weight += doBlur(blurWeights[i - 1], i, nor, depth, texCoord);
	#endif
	fragColor /= weight;
}
