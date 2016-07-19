#version 450

#ifdef GL_ES
precision highp float;
#endif

// #ifdef _NMTex
// #define _AMTex
// #endif

in vec3 pos;
in vec3 nor;
#ifdef _Tex
	in vec2 tex;
#endif
#ifdef _VCols
	in vec3 col;
#endif
#ifdef _NMTex
	in vec3 tan;
#endif
#ifdef _Skinning
	in vec4 bone;
	in vec4 weight;
#endif
#ifdef _Instancing
	in vec3 off;
#endif

uniform mat4 LMVP;
#ifdef _Skinning
	uniform float skinBones[50 * 12];
#endif

out vec4 position;

#ifdef _Skinning
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

	position = LMVP * sPos;
	gl_Position = position;
}
