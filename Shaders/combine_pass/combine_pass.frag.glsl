#version 450

uniform sampler2D tex;
uniform sampler2D tex2;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	fragColor.rgb = texture(tex, texCoord).rgb + texture(tex2, texCoord).rgb;
}
