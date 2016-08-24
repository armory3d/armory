#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"

#ifdef _HeightTex
#define _NorTex
#endif
// #ifdef _NorTex
// #define _Tex
// #endif

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

uniform mat4 WVP;
uniform mat4 N;
uniform vec4 albedo_color;
#ifdef _Billboard
	uniform mat4 WV;
	uniform mat4 P;
#endif
#ifdef _HeightTex
	uniform vec3 eye;
	uniform vec3 light;
	uniform mat4 W;
#endif
#ifdef _Skinning
	uniform float skinBones[skinMaxBones * 12]; // Default to 50
#endif
#ifdef _Probes
	uniform mat4 W; // TODO: Conflicts with _HeightTex
#endif
#ifdef _Veloc
	uniform mat4 prevWVP;
#endif

out vec4 matColor;
#ifdef _Tex
	out vec2 texCoord;
#endif
#ifdef _NorTex
	out mat3 TBN;
#else
	out vec3 normal;
#endif
#ifdef _HeightTex
	out vec3 tanLightDir;
	out vec3 tanEyeDir;
#endif
#ifdef _Probes
	out vec4 mpos;
#endif
#ifdef _Veloc
	out vec4 wvppos;
	out vec4 prevwvppos;
#endif

#ifdef _Skinning
// Geometric Skinning with Approximate Dual Quaternion Blending, Kavan
// Based on https://github.com/tcoppex/aer-engine/blob/master/demos/aura/data/shaders/Skinning.glsl
// void getSkinningDualQuat(vec4 weights, inout vec3 v, inout vec3 n) {
// 	// Retrieve the real and dual part of the dual-quaternions
// 	mat4 matA, matB;
// 	vec4 indices = vec4(2.0) * bone;
// 	matA[0] = skinBones[int(indices.x) + 0];
// 	matB[0] = skinBones[int(indices.x) + 1];
// 	matA[1] = skinBones[int(indices.y) + 0];
// 	matB[1] = skinBones[int(indices.y) + 1];
// 	matA[2] = skinBones[int(indices.z) + 0];
// 	matB[2] = skinBones[int(indices.z) + 1];
// 	matA[3] = skinBones[int(indices.w) + 0];
// 	matB[3] = skinBones[int(indices.w) + 1];
// 	// Handles antipodality by sticking joints in the same neighbourhood
// 	weights.xyz *= sign(matA[3] * mat3x4(matA));
// 	// Apply weights
// 	vec4 A = matA * weights; // Real part
// 	vec4 B = matB * weights; // Dual part
// 	// Normalize
// 	float invNormA = 1.0 / length(A);
// 	A *= invNormA;
// 	B *= invNormA;
// 	// Position
// 	v += 2.0 * cross(A.xyz, cross(A.xyz, v) + A.w * v); // Rotate
// 	v += 2.0 * (A.w * B.xyz - B.w * A.xyz + cross(A.xyz, B.xyz)); // Translate
// 	// Normal
// 	n += 2.0 * cross(A.xyz, cross(A.xyz, n) + A.w * n);
// }
mat4 getBoneMat(const int boneIndex) {
	vec4 v0 = vec4(skinBones[boneIndex * 12 + 0],
				   skinBones[boneIndex * 12 + 1],
				   skinBones[boneIndex * 12 + 2],
				   skinBones[boneIndex * 12 + 3]);
	vec4 v1 = vec4(skinBones[boneIndex * 12 + 4],
				   skinBones[boneIndex * 12 + 5],
				   skinBones[boneIndex * 12 + 6],
				   skinBones[boneIndex * 12 + 7]);
	vec4 v2 = vec4(skinBones[boneIndex * 12 + 8],
				   skinBones[boneIndex * 12 + 9],
				   skinBones[boneIndex * 12 + 10],
				   skinBones[boneIndex * 12 + 11]);
	return mat4(v0.x, v0.y, v0.z, v0.w, 
				v1.x, v1.y, v1.z, v1.w,
				v2.x, v2.y, v2.z, v2.w,
				0, 0, 0, 1);
}
mat4 getSkinningMat() {
	return weight.x * getBoneMat(int(bone.x)) +
		   weight.y * getBoneMat(int(bone.y)) +
		   weight.z * getBoneMat(int(bone.z)) +
		   weight.w * getBoneMat(int(bone.w));
}
mat3 getSkinningMatVec(const mat4 skinningMat) {
	return mat3(skinningMat[0].xyz, skinningMat[1].xyz, skinningMat[2].xyz);
}
#endif

void main() {

#ifdef _Instancing
	vec4 sPos = (vec4(pos + off, 1.0));
#else
	vec4 sPos = (vec4(pos, 1.0));
#endif
#ifdef _Skinning
	mat4 skinningMat = getSkinningMat();
	mat3 skinningMatVec = getSkinningMatVec(skinningMat);
	sPos = sPos * skinningMat;
#endif

#ifdef _Probes
	mpos = W * sPos;
#endif

#ifdef _Billboard
	// Spherical
	WV[0][0] = 1.0; WV[0][1] = 0.0; WV[0][2] = 0.0;
	WV[1][0] = 0.0; WV[1][1] = 1.0; WV[1][2] = 0.0;
	WV[2][0] = 0.0; WV[2][1] = 0.0; WV[2][2] = 1.0;
	// Cylindrical
	//WV[0][0] = 1.0; WV[0][1] = 0.0; WV[0][2] = 0.0;
	//WV[2][0] = 0.0; WV[2][1] = 0.0; WV[2][2] = 1.0;
	gl_Position = P * WV * sPos;
#else
	gl_Position = WVP * sPos;
#endif

#ifdef _Veloc
	wvppos = gl_Position;
	prevwvppos = prevWVP * sPos;
#endif

#ifdef _Tex
	texCoord = tex;
#endif

#ifdef _Skinning
	vec3 _normal = normalize(mat3(N) * (nor * skinningMatVec));
#else
	vec3 _normal = normalize(mat3(N) * nor);
#endif

	matColor = albedo_color;

#ifdef _VCols
	matColor.rgb *= col;
	// matColor.rgb *= pow(col, vec3(2.2));
#endif

#ifdef _NorTex
	vec3 tangent = normalize(mat3(N) * (tan));
	vec3 bitangent = normalize(cross(_normal, tangent)); // Use cross() * tangent.w for handedness 
	TBN = mat3(tangent, bitangent, _normal);
#else
	normal = _normal;
#endif

#ifdef _HeightTex
	#ifndef _Probes
		vec4 mpos = W * sPos;
	#endif
	vec3 lightDir = light - mpos.xyz;
	vec3 eyeDir = /*normalize*/eye - mpos.xyz;
	// Wrong bitangent handedness?
	tanLightDir = vec3(dot(lightDir, tangent), dot(lightDir, -bitangent), dot(lightDir, _normal));
	tanEyeDir = vec3(dot(eyeDir, tangent), dot(eyeDir, -bitangent), dot(eyeDir, _normal));
#endif
}
