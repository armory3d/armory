#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D tex2;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec3 col = texture(tex, texCoord).rgb;
	vec3 col2 = texture(tex2, texCoord).rgb;
	fragColor.rgb = col + col2;
}
