#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;

out vec3 fragColor;

void main() {

	vec3 color = texture(tex, texCoord).rgb;
	float luminance = dot(color, vec3(0.30, 0.59, 0.11));
	
	fragColor.r = luminance;
}
