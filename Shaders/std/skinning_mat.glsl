uniform float skinBones[skinMaxBones * 12];

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
				0.0, 0.0, 0.0, 1.0);
}

mat4 getSkinningMat(ivec4 bone, vec4 weight) {
	return weight.x * getBoneMat(bone.x) +
		   weight.y * getBoneMat(bone.y) +
		   weight.z * getBoneMat(bone.z) +
		   weight.w * getBoneMat(bone.w);
}

mat3 getSkinningMatVec(const mat4 skinningMat) {
	return mat3(skinningMat[0].xyz, skinningMat[1].xyz, skinningMat[2].xyz);
}

// mat4 skinningMat = getSkinningMat();
// mat3 skinningMatVec = getSkinningMatVec(skinningMat);
// sPos = sPos * skinningMat;
// vec3 _normal = normalize(mat3(N) * (nor * skinningMatVec));
