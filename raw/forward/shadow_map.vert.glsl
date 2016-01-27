#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _NormalMapping
#define _Texturing
#endif

in vec3 pos;
#ifdef _Texturing
in vec2 tex;
#endif
in vec3 nor;
#ifdef _VCols
in vec4 col;
#endif
#ifdef _NormalMapping
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

uniform mat4 lightMVP;

out vec4 position;

void main() {
#ifdef _Instancing
	gl_Position = lightMVP * vec4(pos + off, 1.0);
#else
	gl_Position = lightMVP * vec4(pos, 1.0);
#endif
	position = gl_Position;
}
