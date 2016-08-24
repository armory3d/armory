#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"

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
#endif
#ifdef _Skinning
	in vec4 bone;
	in vec4 weight;
#endif
#ifdef _Instancing
	in vec3 off;
#endif

uniform mat4 W;
uniform mat4 N;
uniform mat4 V;
uniform mat4 P;
uniform mat4 WVP;
uniform mat4 LWVP;
uniform vec4 albedo_color;
uniform vec3 eye;
#ifdef _Skinning
	uniform float skinBones[skinMaxBones * 12];
#endif

out vec3 position;
#ifdef _Tex
	out vec2 texCoord;
#endif
out vec4 lPos;
out vec4 matColor;
out vec3 eyeDir;
#ifdef _NorTex
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
	lPos = LWVP * sPos;

	mat4 WV = V * W;

#ifdef _Billboard
	// Spherical
	WV[0][0] = 1.0; WV[0][1] = 0.0; WV[0][2] = 0.0;
	WV[1][0] = 0.0; WV[1][1] = 1.0; WV[1][2] = 0.0;
	WV[2][0] = 0.0; WV[2][1] = 0.0; WV[2][2] = 1.0;
	// Cylindrical
	//WV[0][0] = 1.0; WV[0][1] = 0.0; WV[0][2] = 0.0;
	//WV[2][0] = 0.0; WV[2][1] = 0.0; WV[2][2] = 1.0;
#endif

	// gl_Position = P * WV * sPos;
	gl_Position = WVP * sPos;

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
#endif

	vec3 mPos = vec4(W * sPos).xyz;
	position = mPos;
	eyeDir = eye - mPos;

#ifdef _NorTex
	vec3 tangent = (mat3(N) * (tan));
	vec3 bitangent = normalize(cross(_normal, tangent));
	TBN = mat3(tangent, bitangent, _normal);
#else
	normal = _normal;
#endif
}
