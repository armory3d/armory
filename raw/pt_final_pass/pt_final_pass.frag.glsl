#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbuffer;

in vec2 texCoord;
out vec4 outColor;

void main() {
	vec3 col = texture(gbuffer, texCoord).rgb;
	outColor = vec4(col, 1.0);
}
