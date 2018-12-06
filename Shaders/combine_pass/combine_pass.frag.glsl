#version 450

uniform sampler2D tex;
uniform sampler2D tex2;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	fragColor.rgb = textureLod(tex, texCoord, 0.0).rgb + textureLod(tex2, texCoord, 0.0).rgb;
}
