#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"
#ifdef _Skinning
#include "../std/skinning.glsl"
// getSkinningDualQuat()
#endif
#ifdef _VR
#include "../std/vr.glsl"
// undistort()
#endif

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

uniform mat4 N;
#ifdef _Billboard
	uniform mat4 WV;
	uniform mat4 P;
#endif
uniform mat4 W;
uniform mat4 V;
uniform mat4 P;
#ifndef _NoShadows
	uniform mat4 LWVP;
#endif
#ifdef _Skinning
	//!uniform float skinBones[skinMaxBones * 8];
#endif
#ifdef _VR
// !uniform mat4 U;
// !uniform float maxRadSq;
#endif

out vec3 v_position;
out vec2 v_texCoord;
#ifdef _Tex1
	out vec2 v_texCoord1;
#endif
out vec3 v_normal;
#ifdef _NorTex
	out vec3 v_tangent;
#endif

void main() {
	vec4 sPos = vec4(pos, 1.0);

#ifdef _Skinning
	vec4 skinA;
	vec4 skinB;
	getSkinningDualQuat(ivec4(bone), weight, skinA, skinB);
	sPos.xyz += 2.0 * cross(skinA.xyz, cross(skinA.xyz, sPos.xyz) + skinA.w * sPos.xyz); // Rotate
	sPos.xyz += 2.0 * (skinA.w * skinB.xyz - skinB.w * skinA.xyz + cross(skinA.xyz, skinB.xyz)); // Translate
	vec3 _normal = normalize(mat3(N) * (nor + 2.0 * cross(skinA.xyz, cross(skinA.xyz, nor) + skinA.w * nor)));
#else
	vec3 _normal = normalize(mat3(N) * nor);
#endif

#ifdef _Instancing
	sPos.xyz += off;
#endif

// 	mat4 WV = V * W;

// #ifdef _Billboard
// 	// Spherical
// 	WV[0][0] = 1.0; WV[0][1] = 0.0; WV[0][2] = 0.0;
// 	WV[1][0] = 0.0; WV[1][1] = 1.0; WV[1][2] = 0.0;
// 	WV[2][0] = 0.0; WV[2][1] = 0.0; WV[2][2] = 1.0;
// 	// Cylindrical
// 	//WV[0][0] = 1.0; WV[0][1] = 0.0; WV[0][2] = 0.0;
// 	//WV[2][0] = 0.0; WV[2][1] = 0.0; WV[2][2] = 1.0;
// #endif

	v_texCoord = tex;
#ifdef _Tex1
	v_texCoord1 = tex1;
#endif

	v_position = sPos.xyz;

	v_normal = nor;
#ifdef _NorTex
	v_tangent = tan;
#endif
}
