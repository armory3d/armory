// Based on work by David Li(http://david.li/waves)
#version 450

#ifdef GL_ES
precision mediump float;
#endif

in vec2 texCoord;
out vec4 fragColor;

uniform sampler2D texDisplacement;
const float resolution = 512.0;
const float size = 250.0;

void main() {
	float texel = 1.0 / resolution;
	float texelSize = size / resolution;

	vec3 center = texture(texDisplacement, texCoord).rgb;
	vec3 right = vec3(texelSize, 0.0, 0.0) + texture(texDisplacement, texCoord + vec2(texel, 0.0)).rgb - center;
	vec3 left = vec3(-texelSize, 0.0, 0.0) + texture(texDisplacement, texCoord + vec2(-texel, 0.0)).rgb - center;
	vec3 top = vec3(0.0, 0.0, -texelSize) + texture(texDisplacement, texCoord + vec2(0.0, -texel)).rgb - center;
	vec3 bottom = vec3(0.0, 0.0, texelSize) + texture(texDisplacement, texCoord + vec2(0.0, texel)).rgb - center;

	vec3 topRight = cross(right, top);
	vec3 topLeft = cross(top, left);
	vec3 bottomLeft = cross(left, bottom);
	vec3 bottomRight = cross(bottom, right);

	fragColor = vec4(normalize(topRight + topLeft + bottomLeft + bottomRight), 1.0);
}
