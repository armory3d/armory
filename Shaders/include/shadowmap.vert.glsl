#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"
#ifdef _Skinning
#include "../std/skinning.glsl"
// getSkinningDualQuat()
#endif

in vec3 pos;
in vec3 nor;
#ifdef _Tex
	in vec2 tex;
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

uniform mat4 LWVP;
#ifdef _Billboard
uniform mat4 WV;
uniform mat4 P;
#endif
#ifdef _Skinning
	//!uniform float skinBones[skinMaxBones * 8];
#endif

void main() {
	vec4 sPos = vec4(pos, 1.0);

#ifdef _Skinning
	vec4 skinA;
	vec4 skinB;
	getSkinningDualQuat(ivec4(bone), weight, skinA, skinB);
	sPos.xyz += 2.0 * cross(skinA.xyz, cross(skinA.xyz, sPos.xyz) + skinA.w * sPos.xyz); // Rotate
	sPos.xyz += 2.0 * (skinA.w * skinB.xyz - skinB.w * skinA.xyz + cross(skinA.xyz, skinB.xyz)); // Translate
#endif

#ifdef _Instancing
	sPos.xyz += off;
#endif

#ifdef _Billboard
	mat4 constrWV = WV;
	// Spherical
	constrWV[0][0] = 1.0; constrWV[0][1] = 0.0; constrWV[0][2] = 0.0;
	constrWV[1][0] = 0.0; constrWV[1][1] = 1.0; constrWV[1][2] = 0.0;
	constrWV[2][0] = 0.0; constrWV[2][1] = 0.0; constrWV[2][2] = 1.0;
	// Cylindrical
	//constrWV[0][0] = 1.0; constrWV[0][1] = 0.0; constrWV[0][2] = 0.0;
	//constrWV[2][0] = 0.0; constrWV[2][1] = 0.0; constrWV[2][2] = 1.0;
	gl_Position = P * constrWV * sPos;
#else
	gl_Position = LWVP * sPos;
#endif
}
