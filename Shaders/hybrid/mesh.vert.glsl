#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"
#ifdef _Skinning
#include "../std/skinning.glsl"
// getSkinningDualQuat()
#endif

in vec3 pos;
in vec3 nor;
#ifdef _Tex
	in vec2 tex;
#endif
#ifdef _Tex1
	in vec2 tex1;
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
#ifdef _Billboard
	uniform mat4 WV;
	uniform mat4 P;
#endif
uniform mat4 WVP;
uniform mat4 LWVP;
uniform vec4 baseCol;
uniform vec3 eye;
#ifdef _Skinning
	//!uniform float skinBones[skinMaxBones * 8];
#endif

out vec3 position;
#ifdef _Tex
	out vec2 texCoord;
#endif
#ifdef _Tex1
	out vec2 texCoord1;
#endif
out vec4 lampPos;
out vec4 matColor;
out vec3 eyeDir;
#ifdef _NorTex
	out mat3 TBN;
#else
	out vec3 normal;
#endif

void main() {
	vec4 sPos = vec4(pos, 1.0);

#ifdef _Skinning
	vec4 skinA;
	vec4 skinB;
	getSkinningDualQuat(ivec4(bone), weight, skinA, skinB);
	sPos.xyz += 2.0 * cross(skinA.xyz, cross(skinA.xyz, sPos.xyz) + skinA.w * sPos.xyz); // Rotate
	sPos.xyz += 2.0 * (skinA.w * skinB.xyz - skinB.w * skinA.xyz + cross(skinA.xyz, skinB.xyz)); // Translate
	vec3 _normal = normalize(mat3(N) * (nor + 2.0 * cross(skinA.xyz, cross(skinA.xyz, nor) + skinA.w * nor)));
#else
	vec3 _normal = normalize(mat3(N) * nor);
#endif

#ifdef _Instancing
	sPos.xyz += off;
#endif

	lampPos = LWVP * sPos;

#ifdef _Billboard
	mat4 constrWV = WV;
	// Spherical
	constrWV[0][0] = 1.0; constrWV[0][1] = 0.0; constrWV[0][2] = 0.0;
	constrWV[1][0] = 0.0; constrWV[1][1] = 1.0; constrWV[1][2] = 0.0;
	constrWV[2][0] = 0.0; constrWV[2][1] = 0.0; constrWV[2][2] = 1.0;
	// Cylindrical
	//constrWV[0][0] = 1.0; constrWV[0][1] = 0.0; constrWV[0][2] = 0.0;
	//constrWV[2][0] = 0.0; constrWV[2][1] = 0.0; constrWV[2][2] = 1.0;
	gl_Position = P * constrWV * sPos;
#else
	gl_Position = WVP * sPos;
#endif

#ifdef _Tex
	texCoord = tex;
#endif
#ifdef _Tex1
	texCoord1 = tex1;
#endif

	matColor = baseCol;

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
