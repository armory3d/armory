#version 450

uniform sampler2D tex;
uniform sampler2D ssgitex;

in vec2 texCoord;
out vec3 fragColor;

void main() {
	vec3 color = textureLod(tex, texCoord, 0.0).rgb;
    color += textureLod(ssgitex, texCoord, 0.0).rgb;

	fragColor = color;
}
