#version 450

uniform sampler2D tex0;
uniform sampler2D tex1;

in vec2 texCoord;
out vec4 fragColor[2];

void main() {
	fragColor[0] = textureLod(tex0, texCoord, 0.0);
	fragColor[1] = textureLod(tex1, texCoord, 0.0);
}
