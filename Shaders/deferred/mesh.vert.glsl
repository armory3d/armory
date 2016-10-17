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

uniform mat4 WVP;
uniform mat4 N;
uniform vec4 baseCol;
#ifdef _Billboard
	uniform mat4 WV;
	uniform mat4 P;
#endif
#ifdef _Skinning
	//!uniform float skinBones[skinMaxBones * 8];
#endif
#ifdef _Probes
	uniform mat4 W;
#endif
#ifdef _Veloc
	uniform mat4 prevWVP;
#endif

out vec4 matColor;
#ifdef _Tex
	out vec2 texCoord;
#endif
#ifdef _NorTex
	out mat3 TBN;
#else
	out vec3 normal;
#endif
#ifdef _Probes
	out vec4 wpos;
#endif
#ifdef _Veloc
	out vec4 wvppos;
	out vec4 prevwvppos;
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

#ifdef _Probes
	wpos = W * sPos;
#endif

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

#ifdef _Veloc
	wvppos = gl_Position;
	prevwvppos = prevWVP * sPos;
#endif

#ifdef _Tex
	texCoord = tex;
#endif

	matColor = baseCol;

#ifdef _VCols
	matColor.rgb *= col;
	// matColor.rgb *= pow(col, vec3(2.2));
#endif

#ifdef _NorTex
	vec3 tangent = normalize(mat3(N) * (tan));
	vec3 bitangent = normalize(cross(_normal, tangent)); // Use cross() * tangent.w for handedness 
	TBN = mat3(tangent, bitangent, _normal);
#else
	normal = _normal;
#endif
}
