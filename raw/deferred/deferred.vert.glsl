#version 450

#ifdef GL_ES
precision highp float;
#endif

#ifdef _HMTex
#define _NMTex
#endif
// #ifdef _NMTex
// #define _Tex
// #endif

in vec3 pos;
in vec3 nor;
#ifdef _Tex
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

uniform mat4 NM;
uniform mat4 MV;
uniform mat4 P;
uniform mat4 LMVP;
uniform vec4 albedo_color;
#ifdef _HMTex
	uniform vec3 eye;
	uniform vec3 light;
	uniform mat4 M;
#endif
#ifdef _Skinning
	uniform float skinBones[50 * 12];
#endif
#ifdef _Probes
	uniform mat4 M;
#endif


out vec4 mvpposition;
#ifdef _Tex
	out vec2 texCoord;
#endif
	out vec4 lPos;
	out vec4 matColor;
#ifdef _NMTex
	out mat3 TBN;
#else
	out vec3 normal;
#endif
#ifdef _HMTex
	out vec3 tanLightDir;
	out vec3 tanEyeDir;
#endif

#ifdef _Probes
	out vec4 mpos;
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

#ifdef _Billboard
	// Spherical
	MV[0][0] = 1.0; MV[0][1] = 0.0; MV[0][2] = 0.0;
	MV[1][0] = 0.0; MV[1][1] = 1.0; MV[1][2] = 0.0;
	MV[2][0] = 0.0; MV[2][1] = 0.0; MV[2][2] = 1.0;
	// Cylindrical
	//MV[0][0] = 1.0; MV[0][1] = 0.0; MV[0][2] = 0.0;
	//MV[2][0] = 0.0; MV[2][1] = 0.0; MV[2][2] = 1.0;
#endif

#ifdef _Probes
	mpos = M * sPos;
#endif

	gl_Position = P * MV * sPos;

#ifdef _Tex
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

	mvpposition = gl_Position;

#ifdef _NMTex
	vec3 tangent = normalize(mat3(NM) * (tan));
	vec3 bitangent = normalize(cross(_normal, tangent)); // Use cross() * tangent.w for handedness 
	TBN = mat3(tangent, bitangent, _normal);
#else
	normal = _normal;
#endif

#ifdef _HMTex
	vec4 wpos = M * sPos; // Prevent calculating world pos twice when probes are enabled
	vec3 lightDir = light - wpos.xyz;
	vec3 eyeDir = /*normalize*/eye - wpos.xyz;
	// Wrong bitangent handedness?
	tanLightDir = vec3(dot(lightDir, tangent), dot(lightDir, -bitangent), dot(lightDir, _normal));
	tanEyeDir = vec3(dot(eyeDir, tangent), dot(eyeDir, -bitangent), dot(eyeDir, _normal));
#endif
}
