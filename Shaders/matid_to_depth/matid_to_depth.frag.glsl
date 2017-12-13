// Transfer material IDs to depth buffer
#version 450

uniform sampler2D tex;

in vec2 texCoord;

void main() {
	const float fstep = 1.0 / 16777216.0; // 24bit
	// const float fstep = 1.0 / 65536.0; // 16bit
	gl_FragDepth = texture(tex, texCoord).r * fstep; // materialID
}
