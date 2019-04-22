#version 450

uniform sampler2D tex;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	const float speed = 0.01;
	fragColor.a = speed;
	fragColor.rgb = textureLod(tex, vec2(0.5, 0.5), 0.0).rgb +
					textureLod(tex, vec2(0.2, 0.2), 0.0).rgb +
					textureLod(tex, vec2(0.8, 0.2), 0.0).rgb +
					textureLod(tex, vec2(0.2, 0.8), 0.0).rgb +
					textureLod(tex, vec2(0.8, 0.8), 0.0).rgb;
	fragColor.rgb /= 5.0;
}
