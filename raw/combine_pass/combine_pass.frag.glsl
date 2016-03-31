#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D tex2;

in vec2 texCoord;

const float exposure = 1.0;
const float gamma = 2.2;

void main() {
	vec3 col = texture(tex, texCoord).rgb;
	vec3 col2 = texture(tex2, texCoord).rgb;
	
	// // Additive blending
    col += col2;
	
    // // Tone mapping
    // vec3 result = vec3(1.0) - exp(-col * exposure);
    
	// // Gamma correction
    // result = pow(result, vec3(1.0 / gamma));
    // gl_FragColor = vec4(result, 1.0f);
	
	
	gl_FragColor = vec4(col, 1.0);
}
