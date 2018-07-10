#version 450

uniform sampler2D tex0;
uniform sampler2D tex1;

in vec2 texCoord;
out vec4 fragColor[2];

void main() {
	fragColor[0] = texture(tex0, texCoord);
	fragColor[1] = texture(tex1, texCoord);
}
