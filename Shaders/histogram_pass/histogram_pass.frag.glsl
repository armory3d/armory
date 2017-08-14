#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;

out vec4 fragColor;

void main() {
	vec3 color = texture(tex, texCoord).rgb;
	// const vec3 W = vec3(0.2125, 0.7154, 0.0721);
	float luminance = dot(color, vec3(0.30, 0.59, 0.11));
	fragColor.r = luminance;
	// Gen mipmaps
	// To 64x1 1D histogram
}
