uniform vec4 skinBones[skinMaxBones * 3];

mat4 getBoneMat(const int boneIndex) {
	int bonei = boneIndex * 3;
	return mat4(skinBones[bonei], 
				skinBones[bonei + 1],
				skinBones[bonei + 2],
				0.0, 0.0, 0.0, 1.0);
}

mat4 getSkinningMat(const ivec4 bone, const vec4 weight) {
	return weight.x * getBoneMat(bone.x) +
		   weight.y * getBoneMat(bone.y) +
		   weight.z * getBoneMat(bone.z) +
		   weight.w * getBoneMat(bone.w);
}

mat3 getSkinningMatVec(const mat4 skinningMat) {
	return mat3(skinningMat[0].xyz, skinningMat[1].xyz, skinningMat[2].xyz);
}
