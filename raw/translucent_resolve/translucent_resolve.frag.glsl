// Weighted blended OIT by McGuire and Bavoil
#version 450

#ifdef GL_ES
precision mediump float;
#endif

// uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // accumTexture
uniform sampler2D gbuffer1; // revealageTexture

in vec2 texCoord;

void main() {
	vec4 accum = texture(gbuffer0, texCoord);
	float revealage = accum.a;
	
	if (revealage == 1.0) {
        // Save the blending and color texture fetch cost
        discard; 
    }
	
	accum.a = texture(gbuffer1, texCoord).r;
	
	// gl_FragColor = vec4(accum.rgb / clamp(accum.a, 1e-4, 5e4), revealage);

	const float epsilon = 0.00001;
	gl_FragColor = vec4(accum.rgb / max(accum.a, epsilon), 1 - revealage);
}
