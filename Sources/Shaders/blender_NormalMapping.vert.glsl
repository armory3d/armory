//--------------------------------------------------------
#ifdef GL_ES
precision highp float;
#endif

attribute vec3 pos;
attribute vec2 tex;
attribute vec3 nor;
//attribute vec4 col;
attribute vec3 tan;
attribute vec3 bitan;

uniform mat4 M;
uniform mat4 V;
uniform mat4 P;
uniform mat4 lightMVP;
uniform vec4 diffuseColor;
uniform vec3 light;
uniform vec3 eye;

varying vec3 position;
varying vec2 texCoord;
varying vec3 normal;
varying vec4 lPos;
varying vec4 matColor;
varying vec3 lightDir;
varying vec3 eyeDir;

mat3 transpose(mat3 m) {
  return mat3(m[0][0], m[1][0], m[2][0],
              m[0][1], m[1][1], m[2][1],
              m[0][2], m[1][2], m[2][2]);
}

void kore() {

	vec4 mPos = M * vec4(pos, 1.0);
	gl_Position = P * V * mPos;
	position = mPos.xyz / mPos.w;
	texCoord = tex;
	normal = normalize((M * vec4(nor, 0.0)).xyz);

	lPos = lightMVP * vec4(pos, 1.0);

	matColor = diffuseColor;// * col;

	lightDir = normalize(light - position);
	eyeDir = normalize(eye - position);

	vec3 vTangent = tan; 
	vec3 vBitangent = bitan; 
   
	mat3 TBN = transpose(mat3(vTangent, vBitangent, normal)); 
	lightDir = normalize(TBN * lightDir); 
	eyeDir = normalize(TBN * eyeDir); 
}


