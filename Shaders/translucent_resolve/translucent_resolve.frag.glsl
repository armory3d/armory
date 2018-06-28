// Weighted blended OIT by McGuire and Bavoil
#version 450

#include "compiled.glsl"

// uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // saccum
uniform sampler2D gbuffer1; // srevealage

uniform vec2 texSize;

in vec2 texCoord;
out vec4 fragColor;

float maxComponent(vec4 v) {
	return max(max(max(v.x, v.y), v.z), v.w);
}

void main() {

	#ifdef _Legacy
	vec4 accum = texture(gbuffer0, texCoord);
	#else
	vec4 accum = texelFetch(gbuffer0, ivec2(texCoord * texSize), 0);
	#endif
	float revealage = 1.0 - accum.a;

	// Save the blending and color texture fetch cost
	if (revealage == 0.0) {
		discard;
		return;
	}

	if (isinf(maxComponent(abs(accum)))) {
		accum.rgb = vec3(revealage);
	}
	
	#ifdef _Legacy
	float f = texture(gbuffer1, texCoord).r;
	#else
	float f = texelFetch(gbuffer1, ivec2(texCoord * texSize), 0).r;
	#endif
	fragColor = vec4(accum.rgb / clamp(f, 1e-4, 5e4), revealage);
}
