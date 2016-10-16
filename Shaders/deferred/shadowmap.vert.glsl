#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"

#ifdef _NorTex
#define _BaseTex
#endif

in vec3 pos;
in vec3 nor;
#ifdef _BaseTex
	in vec2 tex;
#endif
#ifdef _VCols
	in vec3 col;
#endif
#ifdef _NorTex
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

uniform mat4 LWVP;
#ifdef _Skinning
	uniform float skinBones[skinMaxBones * 8];
#endif

// out vec4 position;

#ifdef _Skinning
void getSkinningDualQuat(vec4 weights, out vec4 A, inout vec4 B) {
	// Retrieve the real and dual part of the dual-quaternions
	mat4 matA, matB;
	matA[0][0] = skinBones[int(bone.x) * 8 + 0];
	matA[0][1] = skinBones[int(bone.x) * 8 + 1];
	matA[0][2] = skinBones[int(bone.x) * 8 + 2];
	matA[0][3] = skinBones[int(bone.x) * 8 + 3];
	matB[0][0] = skinBones[int(bone.x) * 8 + 4];
	matB[0][1] = skinBones[int(bone.x) * 8 + 5];
	matB[0][2] = skinBones[int(bone.x) * 8 + 6];
	matB[0][3] = skinBones[int(bone.x) * 8 + 7];
	matA[1][0] = skinBones[int(bone.y) * 8 + 0];
	matA[1][1] = skinBones[int(bone.y) * 8 + 1];
	matA[1][2] = skinBones[int(bone.y) * 8 + 2];
	matA[1][3] = skinBones[int(bone.y) * 8 + 3];
	matB[1][0] = skinBones[int(bone.y) * 8 + 4];
	matB[1][1] = skinBones[int(bone.y) * 8 + 5];
	matB[1][2] = skinBones[int(bone.y) * 8 + 6];
	matB[1][3] = skinBones[int(bone.y) * 8 + 7];
	matA[2][0] = skinBones[int(bone.z) * 8 + 0];
	matA[2][1] = skinBones[int(bone.z) * 8 + 1];
	matA[2][2] = skinBones[int(bone.z) * 8 + 2];
	matA[2][3] = skinBones[int(bone.z) * 8 + 3];
	matB[2][0] = skinBones[int(bone.z) * 8 + 4];
	matB[2][1] = skinBones[int(bone.z) * 8 + 5];
	matB[2][2] = skinBones[int(bone.z) * 8 + 6];
	matB[2][3] = skinBones[int(bone.z) * 8 + 7];
	matA[3][0] = skinBones[int(bone.w) * 8 + 0];
	matA[3][1] = skinBones[int(bone.w) * 8 + 1];
	matA[3][2] = skinBones[int(bone.w) * 8 + 2];
	matA[3][3] = skinBones[int(bone.w) * 8 + 3];
	matB[3][0] = skinBones[int(bone.w) * 8 + 4];
	matB[3][1] = skinBones[int(bone.w) * 8 + 5];
	matB[3][2] = skinBones[int(bone.w) * 8 + 6];
	matB[3][3] = skinBones[int(bone.w) * 8 + 7];
	// Handles antipodality by sticking joints in the same neighbourhood
	// weights.xyz *= sign(matA[3] * mat3x4(matA)).xyz;
	weights.xyz *= sign(matA[3] * matA).xyz;
	// Apply weights
	A = matA * weights; // Real part
	B = matB * weights; // Dual part
	// Normalize
	float invNormA = 1.0 / length(A);
	A *= invNormA;
	B *= invNormA;
}
#endif

void main() {
	vec4 sPos = vec4(pos, 1.0);

#ifdef _Skinning
	vec4 skinA;
	vec4 skinB;
	getSkinningDualQuat(weight, skinA, skinB);
	sPos.xyz += 2.0 * cross(skinA.xyz, cross(skinA.xyz, sPos.xyz) + skinA.w * sPos.xyz); // Rotate
	sPos.xyz += 2.0 * (skinA.w * skinB.xyz - skinB.w * skinA.xyz + cross(skinA.xyz, skinB.xyz)); // Translate
#endif

#ifdef _Instancing
	sPos.xyz += off;
#endif

	gl_Position = LWVP * sPos;
	// position = gl_Position;
}
