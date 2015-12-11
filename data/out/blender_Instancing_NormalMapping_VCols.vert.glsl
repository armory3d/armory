#define _Instancing
#define _NormalMapping
#define _VCols
//--------------------------------------------------------
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
attribute vec3 bitan;
#endif
#ifdef _Instancing
attribute vec3 off;
#endif

uniform mat4 M;
uniform mat4 V;
uniform mat4 P;
uniform mat4 lightMVP;
uniform vec4 diffuseColor;
uniform vec3 light;
uniform vec3 eye;

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

void kore() {

#ifdef _Instancing
	vec4 mPos = M * vec4(pos + off, 1.0);
	lPos = lightMVP * vec4(pos + off, 1.0);
#else
	vec4 mPos = M * vec4(pos, 1.0);
	lPos = lightMVP * vec4(pos, 1.0);
#endif
	gl_Position = P * V * mPos;
	position = mPos.xyz / mPos.w;
#ifdef _Texturing
	texCoord = tex;
#endif
	normal = normalize((M * vec4(nor, 0.0)).xyz);

	matColor = diffuseColor;
#ifdef _VCols
	matColor *= col;
#endif

	lightDir = normalize(light - position);
	eyeDir = normalize(eye - position);

#ifdef _NormalMapping
	vec3 vTangent = (tan);
	vec3 vBitangent = cross( normal, vTangent ) * 1.0;//tangent.w;
	//vec3 vBitangent = (bitan);
   
	mat3 TBN = transpose(mat3(vTangent, vBitangent, normal)); 
	//mat3 TBN = (mat3(vTangent, vBitangent, normal)); 
	lightDir = normalize(TBN * lightDir); 
	eyeDir = normalize(TBN * eyeDir); 
#endif
}


