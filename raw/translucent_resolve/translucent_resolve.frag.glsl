// Weighted blended OIT by McGuire and Bavoil
#version 450

#ifdef GL_ES
precision mediump float;
#endif

// uniform sampler2D gbufferD;
uniform sampler2D saccum; // accumTexture
uniform sampler2D srevealage; // revealageTexture

in vec2 texCoord;
out vec4 outColor;

void main() {
	vec4 accum = texture(saccum, texCoord);
	float revealage = accum.a;
	
	if (revealage == 1.0) {
        // Save the blending and color texture fetch cost
        discard;
    }
	
	float accumA = texture(srevealage, texCoord).r;
	
	// outColor = vec4(accum.rgb / clamp(accum.a, 1e-4, 5e4), revealage);

	const float epsilon = 0.00001;
	outColor = vec4(accum.rgb / max(accumA, epsilon), 1.0 - revealage);
}
