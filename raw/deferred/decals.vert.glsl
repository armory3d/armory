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
// in vec3 col;
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
// uniform mat4 MV;
uniform vec4 albedo_color;

#ifdef _RampID
uniform vec4 albedo_color2;
uniform int uid;
#endif

out vec4 mvpposition;
out vec4 mposition;
out vec4 matColor;
// out vec3 orientation;
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

#ifdef _RampID
float hash(vec2 p) {
	float h = dot(p, vec2(127.1, 311.7));	
    return fract(sin(h) * 43758.5453123);
}
#endif

void main() {
	vec4 sPos = (vec4(pos, 1.0));
	mposition = M * sPos;
	mvpposition = VP * mposition;

	// orientation = normalize(MV[1].xyz);

#ifdef _RampID
	vec2 p = vec2(float(uid), float(uid));
	float factor = hash(p);
	matColor = mix(albedo_color, albedo_color2, factor);
#else
	matColor = albedo_color;
#endif

	gl_Position = mvpposition;
}
