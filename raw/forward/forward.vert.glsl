#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _NMTex
#define _AMTex
#endif

in vec3 pos;
in vec3 nor;
#ifdef _AMTex
in vec2 tex;
#endif
#ifdef _VCols
in vec4 col;
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

uniform mat4 M;
uniform mat4 NM;
uniform mat4 V;
uniform mat4 P;
uniform mat4 LMVP;
uniform vec4 albedo_color;
uniform vec3 light;
uniform vec3 eye;
#ifdef _Skinning
uniform float skinBones[50 * 12];
#endif

out vec3 position;
#ifdef _AMTex
out vec2 texCoord;
#endif
out vec4 lPos;
out vec4 matColor;
out vec3 lightDir;
out vec3 eyeDir;
#ifdef _NMTex
out mat3 TBN;
#else
out vec3 normal;
#endif

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
	lPos = LMVP * sPos;

	mat4 VM = V * M;

#ifdef _Billboard
	// Spherical
	VM[0][0] = 1.0; VM[0][1] = 0.0; VM[0][2] = 0.0;
	VM[1][0] = 0.0; VM[1][1] = 1.0; VM[1][2] = 0.0;
	VM[2][0] = 0.0; VM[2][1] = 0.0; VM[2][2] = 1.0;
	// Cylindrical
	//VM[0][0] = 1.0; VM[0][1] = 0.0; VM[0][2] = 0.0;
	//VM[2][0] = 0.0; VM[2][1] = 0.0; VM[2][2] = 1.0;
#endif

	gl_Position = P * VM * sPos;

#ifdef _AMTex
	texCoord = tex;
#endif

#ifdef _Skinning
	vec3 _normal = normalize(mat3(NM) * (nor * skinningMatVec));
#else
	vec3 _normal = normalize(mat3(NM) * nor);
#endif

	matColor = albedo_color;

#ifdef _VCols
	matColor *= col;
#endif

	vec3 mPos = vec4(M * sPos).xyz;
	lightDir = light - mPos;
	eyeDir = eye - mPos;

#ifdef _NMTex
	vec3 tangent = (mat3(NM) * (tan));
	vec3 bitangent = normalize(cross(_normal, tangent));
	TBN = mat3(tangent, bitangent, _normal);
#else
	normal = _normal;
#endif
}
