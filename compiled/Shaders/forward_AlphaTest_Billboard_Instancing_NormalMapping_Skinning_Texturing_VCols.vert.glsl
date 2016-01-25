#define _AlphaTest
#define _Billboard
#define _Instancing
#define _NormalMapping
#define _Skinning
#define _Texturing
#define _VCols
#ifdef GL_ES
precision highp float;
#endif

#ifdef _NormalMapping
#define _Texturing
#endif

attribute vec3 pos;
attribute vec3 nor;
#ifdef _Texturing
attribute vec2 tex;
#endif
#ifdef _VCols
attribute vec4 col;
#endif
#ifdef _NormalMapping
attribute vec3 tan;
#endif
#ifdef _Skinning
attribute vec4 bone;
attribute vec4 weight;
#endif
#ifdef _Instancing
attribute vec3 off;
#endif

uniform mat4 M;
uniform mat4 NM;
uniform mat4 V;
uniform mat4 P;
uniform mat4 lightMVP;
uniform vec4 diffuseColor;
uniform vec3 light;
uniform vec3 eye;
#ifdef _Skinning
uniform float skinBones[50 * 12];
#endif

varying vec3 position;
#ifdef _Texturing
varying vec2 texCoord;
#endif
varying vec3 normal;
varying vec4 lPos;
varying vec4 matColor;
varying vec3 lightDir;
varying vec3 eyeDir;

#ifdef _NormalMapping
mat3 transpose(mat3 m) {
  return mat3(m[0][0], m[1][0], m[2][0],
              m[0][1], m[1][1], m[2][1],
              m[0][2], m[1][2], m[2][2]);
}
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
	lPos = lightMVP * sPos;

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
	
	vec4 mPos = M * sPos;
	position = mPos.xyz / mPos.w;

#ifdef _Texturing
	texCoord = tex;
#endif

#ifdef _Skinning
	normal = normalize(mat3(NM) * (nor * skinningMatVec));
#else
	normal = normalize(mat3(NM) * nor);
#endif

	matColor = diffuseColor;

#ifdef _VCols
	matColor *= col;
#endif

#ifdef _NormalMapping
	vec3 vtan = (tan);
	vec3 vbitan = cross(normal, vtan) * 1.0;//tangent.w;
   
	mat3 TBN = transpose(mat3(vtan, vbitan, normal));
	lightDir = normalize(TBN * lightDir); 
	eyeDir = normalize(TBN * eyeDir); 
#else
	lightDir = normalize(light - position);
	eyeDir = normalize(eye - position);
#endif
}
