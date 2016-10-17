// Geometric Skinning with Approximate Dual Quaternion Blending, Kavan
// Based on https://github.com/tcoppex/aer-engine/blob/master/demos/aura/data/shaders/Skinning.glsl
uniform float skinBones[skinMaxBones * 8];

void getSkinningDualQuat(const ivec4 bone, vec4 weight, out vec4 A, inout vec4 B) {
	// Retrieve the real and dual part of the dual-quaternions
	mat4 matA, matB;
	matA[0][0] = skinBones[bone.x * 8 + 0];
	matA[0][1] = skinBones[bone.x * 8 + 1];
	matA[0][2] = skinBones[bone.x * 8 + 2];
	matA[0][3] = skinBones[bone.x * 8 + 3];
	matB[0][0] = skinBones[bone.x * 8 + 4];
	matB[0][1] = skinBones[bone.x * 8 + 5];
	matB[0][2] = skinBones[bone.x * 8 + 6];
	matB[0][3] = skinBones[bone.x * 8 + 7];
	matA[1][0] = skinBones[bone.y * 8 + 0];
	matA[1][1] = skinBones[bone.y * 8 + 1];
	matA[1][2] = skinBones[bone.y * 8 + 2];
	matA[1][3] = skinBones[bone.y * 8 + 3];
	matB[1][0] = skinBones[bone.y * 8 + 4];
	matB[1][1] = skinBones[bone.y * 8 + 5];
	matB[1][2] = skinBones[bone.y * 8 + 6];
	matB[1][3] = skinBones[bone.y * 8 + 7];
	matA[2][0] = skinBones[bone.z * 8 + 0];
	matA[2][1] = skinBones[bone.z * 8 + 1];
	matA[2][2] = skinBones[bone.z * 8 + 2];
	matA[2][3] = skinBones[bone.z * 8 + 3];
	matB[2][0] = skinBones[bone.z * 8 + 4];
	matB[2][1] = skinBones[bone.z * 8 + 5];
	matB[2][2] = skinBones[bone.z * 8 + 6];
	matB[2][3] = skinBones[bone.z * 8 + 7];
	matA[3][0] = skinBones[bone.w * 8 + 0];
	matA[3][1] = skinBones[bone.w * 8 + 1];
	matA[3][2] = skinBones[bone.w * 8 + 2];
	matA[3][3] = skinBones[bone.w * 8 + 3];
	matB[3][0] = skinBones[bone.w * 8 + 4];
	matB[3][1] = skinBones[bone.w * 8 + 5];
	matB[3][2] = skinBones[bone.w * 8 + 6];
	matB[3][3] = skinBones[bone.w * 8 + 7];
	// Handles antipodality by sticking joints in the same neighbourhood
	// weight.xyz *= sign(matA[3] * mat3x4(matA)).xyz;
	weight.xyz *= sign(matA[3] * matA).xyz;
	// Apply weights
	A = matA * weight; // Real part
	B = matB * weight; // Dual part
	// Normalize
	float invNormA = 1.0 / length(A);
	A *= invNormA;
	B *= invNormA;
}
