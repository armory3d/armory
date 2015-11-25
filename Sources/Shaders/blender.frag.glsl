#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D stex;
uniform sampler2D shadowMap;
uniform bool texturing;
uniform bool lighting;
uniform bool receiveShadow;
uniform vec3 light;
uniform vec3 eye;
uniform float roughness;

varying vec3 position;
varying vec2 texCoord;
varying vec3 normal;
varying vec4 lPos;
varying vec4 matColor;

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
		vec3 l = light - position;
		l = normalize(l);
		vec3 v = eye - position;
		v = normalize(v);

		float dotNL = clamp(dot(n, l), 0.0, 1.0);

		float spec = LightingFuncGGX_OPT3(n, v, l, roughness, specular);
		vec3 rgb = spec + t * dotNL;

		outColor = vec4(vec3(rgb * visibility), 1.0);
	}
	else {
		outColor = vec4(t, 1.0);
	}

	if (texturing) {
		vec4 texel = texture2D(stex, texCoord);
		if(texel.a < 0.4)
			discard;

		outColor = vec4(texel * outColor);
	}
	else {
		outColor = vec4(outColor.rgb, 1.0);
	}

	gl_FragColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
}
