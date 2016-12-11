#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"

in vec3 pos;
in vec3 nor;
in vec2 tex;
#ifdef _Tex1
	in vec2 tex1;
#endif
#ifdef _VCols
	in vec3 col;
#endif
#ifdef _NorTex
	in vec3 tan;
#endif
#ifdef _Skinning
	in vec4 bone;
	in vec4 weight;
#endif
#ifdef _Instancing
	in vec3 off;
#endif

out vec3 v_position;
out vec3 v_normal;
out vec2 v_texCoord;
#ifdef _Tex1
	out vec2 v_texCoord1;
#endif
// #ifdef _VCols
	// out vec3 v_color;
// #endif
#ifdef _NorTex
	out vec3 v_tangent;
#endif
// #ifdef _Skinning
// 	out vec4 v_bone;
// 	out vec4 v_weight;
// #endif

// uniform sampler2D sheight;
// uniform float heightStrength;

void main() {
	v_position = pos;
#ifdef _Instancing
	v_position += off;
#endif

	v_texCoord = tex;
#ifdef _Tex1
	v_texCoord1 = tex1;
#endif
	v_normal = nor;
#ifdef _NorTex
	v_tangent = tan;
#endif
	// v_position += v_normal * texture(sheight, tex).r * heightStrength;

// #ifdef _VCols
	// v_color = col;
// #endif

// #ifdef _Skinning
// 	v_bone = bone;
// 	v_weight = weight;
// #endif
}
