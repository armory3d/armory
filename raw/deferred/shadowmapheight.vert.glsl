#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"

in vec3 pos;
in vec3 nor;
in vec2 tex;
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
out vec2 v_texCoord;
out vec3 v_normal;

// uniform sampler2D sheight;
// uniform float heightStrength;

void main() {
	v_position = pos;
	v_texCoord = tex;
	v_normal = nor;
	// v_position += v_normal * texture(sheight, tex).r * heightStrength;
}
