// Geometric Skinning with Approximate Dual Quaternion Blending, Kavan
// Based on https://github.com/tcoppex/aer-engine/blob/master/demos/aura/data/shaders/Skinning.glsl
uniform vec4 skinBones[skinMaxBones * 2];

void getSkinningDualQuat(const ivec4 bone, vec4 weight, out vec4 A, inout vec4 B) {
	// Retrieve the real and dual part of the dual-quaternions
	mat4 matA, matB;
	matA[0][0] = skinBones[bone.x * 2].x;
	matA[0][1] = skinBones[bone.x * 2].y;
	matA[0][2] = skinBones[bone.x * 2].z;
	matA[0][3] = skinBones[bone.x * 2].w;
	matB[0][0] = skinBones[bone.x * 2 + 1].x;
	matB[0][1] = skinBones[bone.x * 2 + 1].y;
	matB[0][2] = skinBones[bone.x * 2 + 1].z;
	matB[0][3] = skinBones[bone.x * 2 + 1].w;
	matA[1][0] = skinBones[bone.y * 2].x;
	matA[1][1] = skinBones[bone.y * 2].y;
	matA[1][2] = skinBones[bone.y * 2].z;
	matA[1][3] = skinBones[bone.y * 2].w;
	matB[1][0] = skinBones[bone.y * 2 + 1].x;
	matB[1][1] = skinBones[bone.y * 2 + 1].y;
	matB[1][2] = skinBones[bone.y * 2 + 1].z;
	matB[1][3] = skinBones[bone.y * 2 + 1].w;
	matA[2][0] = skinBones[bone.z * 2].x;
	matA[2][1] = skinBones[bone.z * 2].y;
	matA[2][2] = skinBones[bone.z * 2].z;
	matA[2][3] = skinBones[bone.z * 2].w;
	matB[2][0] = skinBones[bone.z * 2 + 1].x;
	matB[2][1] = skinBones[bone.z * 2 + 1].y;
	matB[2][2] = skinBones[bone.z * 2 + 1].z;
	matB[2][3] = skinBones[bone.z * 2 + 1].w;
	matA[3][0] = skinBones[bone.w * 2].x;
	matA[3][1] = skinBones[bone.w * 2].y;
	matA[3][2] = skinBones[bone.w * 2].z;
	matA[3][3] = skinBones[bone.w * 2].w;
	matB[3][0] = skinBones[bone.w * 2 + 1].x;
	matB[3][1] = skinBones[bone.w * 2 + 1].y;
	matB[3][2] = skinBones[bone.w * 2 + 1].z;
	matB[3][3] = skinBones[bone.w * 2 + 1].w;
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
