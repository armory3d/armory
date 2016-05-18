#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _NMTex
#define _AMTex
#endif

in vec3 pos;
// in vec3 nor;
// #ifdef _AMTex
// in vec2 tex;
// #endif
// #ifdef _VCols
// in vec4 col;
// #endif
// #ifdef _NMTex
// in vec3 tan;
// #endif
// #ifdef _Skinning
// in vec4 bone;
// in vec4 weight;
// #endif
// #ifdef _Instancing
// in vec3 off;
// #endif

uniform mat4 VP;
uniform mat4 M;
uniform vec4 albedo_color;

out vec4 mvpposition;
out vec4 mposition;
out vec4 matColor;
// #ifdef _AMTex
// out vec2 texCoord;
// #endif
// out vec4 lPos;
// out vec4 matColor;
// #ifdef _NMTex
// out mat3 TBN;
// #else
// out vec3 normal;
// #endif

void main() {
	vec4 sPos = (vec4(pos, 1.0));
	mposition = M * sPos;
	mvpposition = VP * mposition;
	matColor = albedo_color;
	gl_Position = mvpposition;
}
