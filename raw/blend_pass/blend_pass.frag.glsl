#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;

void main() {
	gl_FragColor = texture(tex, texCoord);
}
