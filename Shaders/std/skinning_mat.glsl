uniform vec4 skinBones[skinMaxBones * 3];

mat4 getBoneMat(const int boneIndex) {
	vec4 v0 = vec4(skinBones[boneIndex * 3].x,
				   skinBones[boneIndex * 3].y,
				   skinBones[boneIndex * 3].z,
				   skinBones[boneIndex * 3].w);
	vec4 v1 = vec4(skinBones[boneIndex * 3 + 1].x,
				   skinBones[boneIndex * 3 + 1].y,
				   skinBones[boneIndex * 3 + 1].z,
				   skinBones[boneIndex * 3 + 1].w);
	vec4 v2 = vec4(skinBones[boneIndex * 3 + 2].x,
				   skinBones[boneIndex * 3 + 2].y,
				   skinBones[boneIndex * 3 + 2].z,
				   skinBones[boneIndex * 3 + 2].w);
	return mat4(v0.x, v0.y, v0.z, v0.w, 
				v1.x, v1.y, v1.z, v1.w,
				v2.x, v2.y, v2.z, v2.w,
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

// mat4 skinningMat = getSkinningMat();
// mat3 skinningMatVec = getSkinningMatVec(skinningMat);
// sPos = sPos * skinningMat;
// vec3 _normal = normalize(mat3(N) * (nor * skinningMatVec));
