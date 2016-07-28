#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D tex2;

in vec2 texCoord;

void main() {
	vec3 col = texture(tex, texCoord).rgb;
	vec3 col2 = texture(tex2, texCoord).rgb;
	
	gl_FragColor.rgb = (col + col2) / 2.0;
	// gl_FragColor.rgb = col;
}
