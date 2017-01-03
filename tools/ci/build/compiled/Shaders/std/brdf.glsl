
vec2 LightingFuncGGX_FV(const float dotLH, const float roughness) {
	float alpha = roughness * roughness;

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

float LightingFuncGGX_D(const float dotNH, const float roughness) {
	float alpha = roughness * roughness;
	float alphaSqr = alpha * alpha;
	float pi = 3.14159;
	float denom = dotNH * dotNH * (alphaSqr - 1.0) + 1.0;

	float D = alphaSqr / (pi * denom * denom);
	return D;
}

// John Hable - Optimizing GGX Shaders
// http://www.filmicworlds.com/2014/04/21/optimizing-ggx-shaders-with-dotlh/
float LightingFuncGGX_OPT3(const float dotNL, const float dotLH, const float dotNH, const float roughness, const float F0) {
	// vec3 H = normalize(V + L);
	// float dotNL = clamp(dot(N, L), 0.0, 1.0);
	// float dotLH = clamp(dot(L, H), 0.0, 1.0);
	// float dotNH = clamp(dot(N, H), 0.0, 1.0);

	float D = LightingFuncGGX_D(dotNH, roughness);
	vec2 FV_helper = LightingFuncGGX_FV(dotLH, roughness);
	float FV = F0 * FV_helper.x + (1.0 - F0) * FV_helper.y;
	float specular = dotNL * D * FV;

	return specular;
}

vec3 f_schlick(const vec3 f0, const float vh) {
	return f0 + (1.0-f0)*exp2((-5.55473 * vh - 6.98316)*vh);
}

float v_smithschlick(const float nl, const float nv, const float a) {
	return 1.0 / ( (nl*(1.0-a)+a) * (nv*(1.0-a)+a) );
}

float d_ggx(const float nh, const float a) {
	float a2 = a*a;
	float denom = pow(nh*nh * (a2-1.0) + 1.0, 2.0);
	return a2 * (1.0 / 3.1415926535) / denom;
}

vec3 specularBRDF(const vec3 f0, const float roughness, const float nl, const float nh, const float nv, const float vh) {
	float a = roughness * roughness;
	return d_ggx(nh, a) * clamp(v_smithschlick(nl, nv, a), 0.0, 1.0) * f_schlick(f0, vh) / 4.0;
	//return vec3(LightingFuncGGX_OPT3(nl, lh, nh, roughness, f0[0]));
}

vec3 orenNayarDiffuseBRDF(const vec3 albedo, const float roughness, const float nv, const float nl, const float vh) {
	float a = roughness * roughness;
	float s = a;
	float s2 = s * s;
	float vl = 2.0 * vh * vh - 1.0; // Double angle identity
	float Cosri = vl - nv * nl;
	float C1 = 1.0 - 0.5 * s2 / (s2 + 0.33);
	float test = 1.0;
	if (Cosri >= 0.0) test = (1.0 / (max(nl, nv)));
	float C2 = 0.45 * s2 / (s2 + 0.09) * Cosri * test;
	return albedo * max(0.0, nl) * (C1 + C2) * (1.0 + roughness * 0.5);
}

vec3 lambertDiffuseBRDF(const vec3 albedo, const float nl) {
	return albedo * max(0.0, nl);
}

vec3 surfaceAlbedo(const vec3 baseColor, const float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(const vec3 baseColor, const float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
}

float getMipFromRoughness(const float roughness, const float numMipmaps) {
	// First mipmap level = roughness 0, last = roughness = 1
	return roughness * numMipmaps;
}

float wardSpecular(vec3 N, vec3 H, float dotNL, float dotNV, float dotNH, vec3 fiberDirection, float shinyParallel, float shinyPerpendicular) {
	if(dotNL < 0.0 || dotNV < 0.0) {
		return 0.0;
	}
	// fiberDirection - parse from rotation
	// shinyParallel - roughness
	// shinyPerpendicular - anisotropy
	
	vec3 fiberParallel = normalize(fiberDirection);
	vec3 fiberPerpendicular = normalize(cross(N, fiberDirection));
	float dotXH = dot(fiberParallel, H);
	float dotYH = dot(fiberPerpendicular, H);
	const float PI = 3.1415926535;
	float coeff = sqrt(dotNL/dotNV) / (4.0 * PI * shinyParallel * shinyPerpendicular); 
	float theta = (pow(dotXH/shinyParallel, 2.0) + pow(dotYH/shinyPerpendicular, 2.0)) / (1.0 + dotNH);
	return clamp(coeff * exp(-2.0 * theta), 0.0, 1.0);
}
