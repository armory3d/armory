// Weighted blended OIT by McGuire and Bavoil
#version 450

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // saccum
uniform sampler2D gbuffer1; // srevealage

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec4 accum = texture(gbuffer0, texCoord);
	float revealage = accum.a;

	if (revealage == 1.0) {
		// Save the blending and color texture fetch cost
		discard;
	}
	
	accum.a = texture(gbuffer1, texCoord).r;
	
	// fragColor = vec4(accum.rgb / clamp(accum.a, 1e-4, 5e4), revealage);

	// const float epsilon = 0.00001;
	// fragColor = vec4(accum.rgb / max(accum.a, epsilon), 1.0 - revealage);
	
	fragColor = vec4(accum.rgb / clamp(accum.a, 1e-4, 5e4), 1.0 - revealage);
}
