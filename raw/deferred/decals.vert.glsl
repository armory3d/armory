#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _NorTex
#define _BaseTex
#endif

in vec3 pos;
// in vec3 nor;
// #ifdef _BaseTex
// in vec2 tex;
// #endif
// #ifdef _VCols
// in vec3 col;
// #endif
// #ifdef _NorTex
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
uniform mat4 W;
// uniform mat4 WV;
uniform vec4 albedo_color;

#ifdef _RampID
uniform vec4 albedo_color2;
uniform int uid;
#endif

out vec4 wvpposition;
out vec4 matColor;
// out vec3 orientation;
// #ifdef _BaseTex
// out vec2 texCoord;
// #endif
// out vec4 lPos;
// out vec4 matColor;
// #ifdef _NorTex
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
	wvpposition = VP * W * sPos;

	// orientation = normalize(WV[1].xyz);

#ifdef _RampID
	vec2 p = vec2(float(uid), float(uid));
	float factor = hash(p);
	matColor = mix(albedo_color, albedo_color2, factor);
#else
	matColor = albedo_color;
#endif

	gl_Position = wvpposition;
}
