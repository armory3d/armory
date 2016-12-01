#version 450

#ifdef GL_ES
precision mediump float;
#endif

#ifdef _Translucent
	in vec2 texCoord;
#endif

out vec4 fragColor;

#ifdef _Translucent
	#ifdef _OpacTex
	uniform sampler2D sopacity;
	#else
		#ifdef _BaseTex
		uniform sampler2D sbase;
		#endif
	#endif
#endif

void main() {

#ifdef _Translucent
	#ifdef _OpacTex
	if (texture(sopacity, texCoord).r < 0.5) discard;
	#else
		#ifdef _BaseTex
		if (texture(sbase, texCoord).a < 0.5) discard;
		#endif
	#endif
#endif

	fragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
