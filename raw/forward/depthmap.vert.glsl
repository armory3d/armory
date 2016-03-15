#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _NMTex
#define _AMTex
#endif

in vec3 pos;
in vec3 nor;
#ifdef _AMTex
in vec2 tex;
#endif
#ifdef _VCols
in vec4 col;
#endif
#ifdef _NMTex
in vec3 tan;
in vec3 bitan;
#endif
#ifdef _Skinning
in vec4 bone;
in vec4 weight;
#endif
#ifdef _Instancing
in vec3 off;
#endif

uniform mat4 M;
uniform mat4 NM;
uniform mat4 V;
uniform mat4 P;

out vec4 position;

void main() {
// #ifdef _Instancing
	// gl_Position = M * vec4(pos + off, 1.0);
// #else
	// gl_Position = M * vec4(pos, 1.0);
// #endif

	gl_Position = P * V * M * vec4(pos, 1.0);

	position = gl_Position;
}
