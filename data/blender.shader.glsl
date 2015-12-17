@context blender

-set depth_write = true
-set compare_mode = less
-set cull_mode = counter_clockwise
-set blend_source = blend_one
-set blend_destination = blend_zero

-link M = _modelMatrix
-link NM = _normalMatrix
-link V = _viewMatrix
-link P = _projectionMatrix
-link lightMVP = _lightMVP
-link light = _lightPosition
-link eye = _cameraPosition
-ifdef _Skinning
-link skinBones = _skinBones
-endif

-vert blender.vert.glsl
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

void kore() {

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
	vec4 mPos = M * sPos;
	lPos = lightMVP * sPos;

	gl_Position = P * V * mPos;
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


-frag blender.frag.glsl
//--------------------------------------------------------
#ifdef GL_ES
precision mediump float;
#endif

#ifdef _NormalMapping
#define _Texturing
#endif

#ifdef _Texturing
uniform sampler2D stex;
#endif
uniform sampler2D shadowMap;
#ifdef _NormalMapping
uniform sampler2D normalMap;
#endif
uniform bool lighting;
uniform bool receiveShadow;
uniform float roughness;

varying vec3 position;
#ifdef _Texturing
varying vec2 texCoord;
#endif
varying vec3 normal;
varying vec4 lPos;
varying vec4 matColor;
varying vec3 lightDir;
varying vec3 eyeDir;

float shadowSimple(vec4 lPos) {

	vec4 lPosH = lPos / lPos.w;
	
	lPosH.x = (lPosH.x + 1.0) / 2.0;
    lPosH.y = 1.0 - ((-lPosH.y + 1.0) / (2.0));
	
	vec4 packedZValue = texture2D(shadowMap, lPosH.st);

	float distanceFromLight = packedZValue.z;

	//float bias = clamp(0.005*tan(acos(dotNL)), 0, 0.01);
	float bias = 0.0;//0.0005;

	// 1.0 = not in shadow, 0.0 = in shadow
	return float(distanceFromLight > lPosH.z - bias);
}

vec2 LightingFuncGGX_FV(float dotLH, float roughness) {

	float alpha = roughness*roughness;

	// F
	float F_a, F_b;
	float dotLH5 = pow(1.0 - dotLH, 5.0);
	F_a = 1.0;
	F_b = dotLH5;

	// V
	float vis;
	float k = alpha / 2.0;
	float k2 = k * k;
	float invK2 = 1.0 - k2;
	//vis = rcp(dotLH * dotLH * invK2 + k2);
	vis = inversesqrt(dotLH * dotLH * invK2 + k2);

	return vec2(F_a * vis, F_b * vis);
}

float LightingFuncGGX_D(float dotNH, float roughness) {

	float alpha = roughness * roughness;
	float alphaSqr = alpha * alpha;
	float pi = 3.14159;
	float denom = dotNH * dotNH * (alphaSqr - 1.0) + 1.0;

	float D = alphaSqr / (pi * denom * denom);
	return D;
}

// John Hable - Optimizing GGX Shaders
// http://www.filmicworlds.com/2014/04/21/optimizing-ggx-shaders-with-dotlh/
float LightingFuncGGX_OPT3(vec3 N, vec3 V, vec3 L, float roughness, float F0) {

	vec3 H = normalize(V + L);

	float dotNL = clamp(dot(N, L), 0.0, 1.0);
	float dotLH = clamp(dot(L, H), 0.0, 1.0);
	float dotNH = clamp(dot(N, H), 0.0, 1.0);

	float D = LightingFuncGGX_D(dotNH, roughness);
	vec2 FV_helper = LightingFuncGGX_FV(dotLH, roughness);
	float FV = F0 * FV_helper.x + (1.0 - F0) * FV_helper.y;
	float specular = dotNL * D * FV;

	return specular;
}

void kore() {

	float visibility = 1.0;
	if (receiveShadow && lPos.w > 0.0) {
		visibility = shadowSimple(lPos);
		visibility = (visibility * 0.8) + 0.2;
	}

	vec4 outColor;
	vec3 t = pow(matColor.rgb, vec3(2.2));

	if (lighting) {
		float specular = 0.1;

		vec3 n = normalize(normal);
		vec3 l = lightDir;
		vec3 v = eyeDir;

		float dotNL = 0.0;
#ifdef _NormalMapping
		vec3 tn = normalize(texture2D(normalMap, texCoord).rgb * 2.0 - 1.0);
		dotNL = clamp(dot(tn, l), 0.0, 1.0);
#else
		dotNL = clamp(dot(n, l), 0.0, 1.0);
#endif

		float spec = LightingFuncGGX_OPT3(n, v, l, roughness, specular);
		vec3 rgb = spec + t * dotNL;

		outColor = vec4(vec3(rgb * visibility), 1.0);
	}
	else {
		outColor = vec4(t * visibility, 1.0);
	}

#ifdef _Texturing
	vec4 texel = texture2D(stex, texCoord);
	
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif

	outColor = vec4(texel * outColor);
#else
	outColor = vec4(outColor.rgb, 1.0);
#endif

	gl_FragColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
}
