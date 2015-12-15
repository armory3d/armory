#define _AlphaTest
#define _Instancing
#define _NormalMapping
//--------------------------------------------------------
#ifdef GL_ES
precision highp float;
#endif

#ifdef _NormalMapping
#define _Texturing
#endif

#ifdef _Skinning
#define SKIN_TEX_SIZE 2048.0 
#define BINDS_OFFSET 1024.0
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
#ifdef _Skinning
attribute vec4 bone;
attribute vec4 weight;
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
#ifdef _Skinning
uniform sampler2D skinTex;
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
vec4 readSkin(float id) {
	return texture2D(skinTex, vec2(0.0, (id / (SKIN_TEX_SIZE - 1.0))));
}

mat4 skinMatrix(vec4 bone) {
	float o = BINDS_OFFSET;
	vec4 v0,v1,v2;
	
	float b = (bone[0]) * 3.0; 			
	v0 = readSkin(b);
	v1 = readSkin(b + 1.0);
	v2 = readSkin(b + 2.0);
	mat4 j0 = mat4(v0.x, v0.y, v0.z, v0.w, 
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);
	v0 = readSkin(b + o);
	v1 = readSkin(b + 1.0 + o);
	v2 = readSkin(b + 2.0 + o);
	mat4 b0 = mat4(v0.x, v0.y, v0.z, v0.w,
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);
	
	b = (bone[1]) * 3.0; 
	v0 = readSkin(b);
	v1 = readSkin(b + 1.0);
	v2 = readSkin(b + 2.0);
	mat4 j1 = mat4(v0.x, v0.y, v0.z, v0.w,
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);
	v0 = readSkin(b + o);
	v1 = readSkin(b + 1.0 + o);
	v2 = readSkin(b + 2.0 + o);
	mat4 b1 = mat4(v0.x, v0.y, v0.z, v0.w,
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);
	
	b = (bone[2]) * 3.0; 
	v0 = readSkin(b);
	v1 = readSkin(b + 1.0);
	v2 = readSkin(b + 2.0);
	mat4 j2 = mat4(v0.x, v0.y, v0.z, v0.w,
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);
	v0 = readSkin(b + o);
	v1 = readSkin(b + 1.0 + o);
	v2 = readSkin(b + 2.0 + o);
	mat4 b2 = mat4(v0.x, v0.y, v0.z, v0.w,
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);
	
	b = (bone[3]) * 3.0; 
	v0 = readSkin(b);
	v1 = readSkin(b + 1.0);
	v2 = readSkin(b + 2.0);
	mat4 j3 = mat4(v0.x, v0.y, v0.z, v0.w,
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);			
	v0 = readSkin(b + o);
	v1 = readSkin(b + 1.0 + o);
	v2 = readSkin(b + 2.0 + o);
	mat4 b3 = mat4(v0.x, v0.y, v0.z, v0.w,
				   v1.x, v1.y, v1.z, v1.w,
				   v2.x, v2.y, v2.z, v2.w,
				   0, 0, 0, 1);
	
	//return mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1);
	return  ((b0 * j0) * weight[0]) +
	        ((b1 * j1) * weight[1]) +
	        ((b2 * j2) * weight[2]) +
	        ((b3 * j3) * weight[3]);
}
#endif

void kore() {

#ifdef _Skinning
mat4 SM = skinMatrix(bone);
	#ifdef _Instancing
		vec4 mPos = M * SM * vec4(pos + off, 1.0);
		lPos = lightMVP * vec4(pos + off, 1.0);
	#else
		vec4 mPos = M * SM * vec4(pos, 1.0);
		lPos = lightMVP * vec4(pos, 1.0);
	#endif
#else
	#ifdef _Instancing
		vec4 mPos = M * vec4(pos + off, 1.0);
		lPos = lightMVP * vec4(pos + off, 1.0);
	#else
		vec4 mPos = M * vec4(pos, 1.0);
		lPos = lightMVP * vec4(pos, 1.0);
	#endif
#endif

	gl_Position = P * V * mPos;
	position = mPos.xyz / mPos.w;

#ifdef _Texturing
	texCoord = tex;
#endif

#ifdef _Skinning
	// TODO: * mat3(SM); // TODO: shadowmap
	normal = normalize((M * SM * vec4(nor, 0.0)).xyz);
#else
	normal = normalize((M * vec4(nor, 0.0)).xyz);
#endif

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


