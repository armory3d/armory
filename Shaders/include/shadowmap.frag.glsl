#version 450

#ifdef GL_ES
precision mediump float;
#endif

#ifdef _Translucent
	in vec2 texCoord;
#endif

out vec4 fragColor;

#ifdef _Translucent
// #ifdef _BaseTex
	uniform sampler2D sbase;
// #endif
#endif

void main() {

#ifdef _Translucent
	float a = texture(sbase, texCoord).a;
	if (a < 0.5) {
		discard;
	}
#endif

	fragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
