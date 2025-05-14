// Exclusive to SSAO for now
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0;

uniform vec2 dirInv; // texStep

in vec2 texCoord;
out vec3 fragColor;

// const float blurWeights[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
const float blurWeights[16] = float[](
    0.072572, 0.065472, 0.056373, 0.040780,
    0.024950, 0.013482, 0.008275, 0.003934,
    0.001912, 0.000535, 0.132572, 0.125472,
    0.106373, 0.080780, 0.054950, 0.033482
);
const float discardThreshold = 0.95;

void main() {
	vec3 nor = getNor(textureLod(gbuffer0, texCoord, 0.0).rg);
	fragColor = textureLod(tex, texCoord, 0.0).rgb * blurWeights[0];
	float weight = blurWeights[0];

	for (int i = 1; i < 16; ++i) {
		float posadd = i;// + 0.5;

		vec3 nor2 = getNor(textureLod(gbuffer0, texCoord + i * dirInv, 0.0).rg);
		float influenceFactor = smoothstep(0.5, discardThreshold, dot(nor2, nor));
		vec3 col = textureLod(tex, texCoord + posadd * dirInv, 0.0).rgb;
		float w = blurWeights[i] * influenceFactor;
		fragColor += col * w;
		weight += w;

		nor2 = getNor(textureLod(gbuffer0, texCoord - i * dirInv, 0.0).rg);
		influenceFactor = step(discardThreshold, dot(nor2, nor));
		col = textureLod(tex, texCoord - posadd * dirInv, 0.0).rgb;
		w = blurWeights[i] * influenceFactor;
		fragColor += col * w;
		weight += w;
	}

	fragColor = fragColor / weight;
}
