@context blender

-set depth_write = true
-set compare_mode = less
-set cull_mode = counter_clockwise

-link M = _modelMatrix
-link V = _viewMatrix
-link P = _projectionMatrix
-link lightMVP = _lightMVP
-link light = _lightPosition
-link eye = _cameraPosition

-vert blender.vert.glsl
//--------------------------------------------------------
#ifdef GL_ES
precision highp float;
#endif

attribute vec3 pos;
attribute vec2 tex;
attribute vec3 nor;
//attribute vec4 col;
#ifdef _NormalMapping
attribute vec3 tan;
attribute vec3 bitan;
#endif

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

#ifdef _NormalMapping
	vec3 vTangent = tan; 
	vec3 vBitangent = bitan; 
   
	mat3 TBN = transpose(mat3(vTangent, vBitangent, normal)); 
	lightDir = normalize(TBN * lightDir); 
	eyeDir = normalize(TBN * eyeDir); 
#endif
}


-frag blender.frag.glsl
//--------------------------------------------------------
#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D stex;
uniform sampler2D shadowMap;
#ifdef _NormalMapping
uniform sampler2D normalMap;
#endif
uniform bool texturing;
uniform bool lighting;
uniform bool receiveShadow;
uniform float roughness;

varying vec3 position;
varying vec2 texCoord;
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
		vec3 tn = normalize(texture2D(normalMap, vec2(texCoord.x, 1.0 - texCoord.y)).rgb * 2.0 - 1.0);
		dotNL = clamp(dot(tn, l), 0.0, 1.0);
#else
		dotNL = clamp(dot(n, l), 0.0, 1.0);
#endif

		float spec = LightingFuncGGX_OPT3(n, v, l, roughness, specular);
		vec3 rgb = spec + t * dotNL;

		outColor = vec4(vec3(rgb * visibility), 1.0);
	}
	else {
		outColor = vec4(t, 1.0);
	}

	if (texturing) {
		vec4 texel = texture2D(stex, texCoord);
		//if(texel.a < 0.4)
		//	discard;

		outColor = vec4(texel * outColor);
	}
	else {
		outColor = vec4(outColor.rgb, 1.0);
	}

	gl_FragColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
}


//--------------------------------------------------------
//--------------------------------------------------------
@context shadow_map

-set depth_write = true
-set compare_mode = less
-set cull_mode = clockwise

-link lightMVP = _lightMVP

-vert shadow_map.vert.glsl
//--------------------------------------------------------
#ifdef GL_ES
precision highp float;
#endif

attribute vec3 pos;
attribute vec2 tex;
attribute vec3 nor;
attribute vec4 col;
#ifdef _NormalMapping
attribute vec3 tan;
attribute vec3 bitan;
#endif

uniform mat4 lightMVP;

varying vec4 position;

void kore() {

	gl_Position = lightMVP * vec4(pos, 1.0);
	position = gl_Position;
}


-frag shadow_map.frag.glsl
//--------------------------------------------------------
#ifdef GL_ES
precision mediump float;
#endif

varying vec4 position;

void kore() {

    float normalizedDistance = position.z / position.w;
    normalizedDistance += 0.005;
 
    gl_FragColor = vec4(normalizedDistance, normalizedDistance, normalizedDistance, 1.0);
}
