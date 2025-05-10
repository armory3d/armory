// Exclusive to SSAO for now
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0;

uniform vec2 dirInv; // texStep

in vec2 texCoord;
#ifdef _SSGI
out vec3 fragColor;
#else
out float fragColor;
#endif

// const float blurWeights[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
const float blurWeights[10] = float[] (0.132572, 0.125472, 0.106373, 0.08078, 0.05495, 0.033482, 0.018275, 0.008934, 0.003912, 0.001535);
const float discardThreshold = 0.95;

void main() {
	vec3 nor = getNor(textureLod(gbuffer0, texCoord, 0.0).rg);
	
	#ifdef _SSGI
	fragColor = textureLod(tex, texCoord, 0.0).rgb * blurWeights[0];
	#else
	fragColor = textureLod(tex, texCoord, 0.0).r * blurWeights[0];
	#endif
	float weight = blurWeights[0];

	for (int i = 1; i < 8; ++i) {
		float posadd = i;// + 0.5;

		vec3 nor2 = getNor(textureLod(gbuffer0, texCoord + i * dirInv, 0.0).rg);
		float influenceFactor = step(discardThreshold, dot(nor2, nor));
		#ifdef _SSGI
		vec3 col = textureLod(tex, texCoord + posadd * dirInv, 0.0).rgb;
		#else
		float col = textureLod(tex, texCoord + posadd * dirInv, 0.0).r;
		#endif
		float w = blurWeights[i] * influenceFactor;
		fragColor += col * w;
		weight += w;
		
		nor2 = getNor(textureLod(gbuffer0, texCoord - i * dirInv, 0.0).rg);
		influenceFactor = step(discardThreshold, dot(nor2, nor));
		#ifdef _SSGI
		col = textureLod(tex, texCoord - posadd * dirInv, 0.0).rgb;
		#else
		col = textureLod(tex, texCoord - posadd * dirInv, 0.0).r;
		#endif
		w = blurWeights[i] * influenceFactor;
		fragColor += col * w;
		weight += w;
	}

	fragColor = fragColor / weight;
}
