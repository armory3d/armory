#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415926535
#define TwoPI (2.0 * PI)

#ifdef _NMTex
#define _AMTex
#endif

#ifdef _AMTex
uniform sampler2D salbedo;
#endif
uniform sampler2D shadowMap;
uniform sampler2D senvmapRadiance;
uniform sampler2D senvmapIrradiance;
uniform sampler2D senvmapBrdf;
// uniform sampler2D sltcMat;
// uniform sampler2D sltcMag;
#ifdef _NMTex
uniform sampler2D snormal;
#endif
#ifdef _OMTex
uniform sampler2D som;
#endif
#ifdef _RMTex
uniform sampler2D srm;
#else
uniform float roughness;
#endif
#ifdef _MMTex
uniform sampler2D smm;
#else
uniform float metalness;
#endif

uniform float envmapStrength;

uniform bool receiveShadow;
uniform vec3 lightColor;
uniform float lightStrength;

// LTC
uniform vec3 light;
// const float roughness = 0.25;
const vec3  dcolor = vec3(1.0, 1.0, 1.0);
const vec3  scolor = vec3(1.0, 1.0, 1.0);
const float intensity = 4.0; // 0-10
const float width = 4.0;
const float height = 4.0;
const vec2  resolution = vec2(800.0, 600.0);
const int   sampleCount = 0;
const int   NUM_SAMPLES = 8;
const float LUT_SIZE  = 64.0;
const float LUT_SCALE = (LUT_SIZE - 1.0)/LUT_SIZE;
const float LUT_BIAS  = 0.5/LUT_SIZE;
// vec2 mys[NUM_SAMPLES];		
vec3 L0 = vec3(0.0);
vec3 L1 = vec3(0.0);
vec3 L2 = vec3(0.0);
vec3 L3 = vec3(0.0);
vec3 L4 = vec3(0.0);


in vec3 position;
#ifdef _AMTex
in vec2 texCoord;
#endif
in vec4 lPos;
in vec4 matColor;
in vec3 lightDir;
in vec3 eyeDir;
#ifdef _NMTex
in mat3 TBN;
#else
in vec3 normal;
#endif

// float linstep(float low, float high, float v) {
//     return clamp((v - low) / (high - low), 0.0, 1.0);
// }

// float VSM(vec2 uv, float compare) {
//     vec2 moments = texture(shadowMap, uv).xy;
//     float p = smoothstep(compare - 0.02, compare, moments.x);
//     float variance = max(moments.y - moments.x * moments.x, -0.001);
//     float d = compare - moments.x;
//     float p_max = linstep(0.2, 1.0, variance / (variance + d * d));
//     return clamp(max(p, p_max), 0.0, 1.0);
// }

// float rand(vec2 co) {
    // return fract(sin(dot(co.xy ,vec2(12.9898, 78.233))) * 43758.5453);
// }

float texture2DCompare(vec2 uv, float compare){
    float depth = texture(shadowMap, uv).r * 2.0 - 1.0;
    return step(compare, depth);
}

float texture2DShadowLerp(vec2 size, vec2 uv, float compare){
    vec2 texelSize = vec2(1.0) / size;
    vec2 f = fract(uv * size + 0.5);
    vec2 centroidUV = floor(uv * size + 0.5) / size;

    float lb = texture2DCompare(centroidUV + texelSize * vec2(0.0, 0.0), compare);
    float lt = texture2DCompare(centroidUV + texelSize * vec2(0.0, 1.0), compare);
    float rb = texture2DCompare(centroidUV + texelSize * vec2(1.0, 0.0), compare);
    float rt = texture2DCompare(centroidUV + texelSize * vec2(1.0, 1.0), compare);
    float a = mix(lb, lt, f.y);
    float b = mix(rb, rt, f.y);
    float c = mix(a, b, f.x);
    return c;
}

float PCF(vec2 size, vec2 uv, float compare){
    float result = 0.0;
    // for (int x = -1; x <= 1; x++){
    //     for(int y = -1; y <= 1; y++){
    //         vec2 off = vec2(x, y) / size;
    //         result += texture2DShadowLerp(size, uv + off, compare);
				
				vec2 off = vec2(-1, -1) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(-1, 0) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(-1, 1) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(0, -1) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(0, 0) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(0, 1) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(1, -1) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(1, 0) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
				off = vec2(1, 1) / size;
				result += texture2DShadowLerp(size, uv + off, compare);
    //     }
    // }
    return result / 9.0;
}

float shadowTest(vec4 lPos) {
	vec4 lPosH = lPos / lPos.w;
	lPosH.x = (lPosH.x + 1.0) / 2.0;
    lPosH.y = 1.0 - ((-lPosH.y + 1.0) / (2.0));
	
	const float bias = 0.008;
	return PCF(vec2(2048.0, 2048.0), lPosH.st, lPosH.z - bias);
	// return VSM(lPosH.st, lPosH.z);
	
	// shadow2DSampler
	// return texture(shadowMap, vec3(lPosH.st, (lPosH.z - 0.005) / lPosH.w));
	
	// Basic
	// float distanceFromLight = texture(shadowMap, lPosH.st).r;
	// float bias = 0.0;
	// return float(distanceFromLight > lPosH.z - bias);
}


vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / TwoPI, phi / PI);
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
float LightingFuncGGX_OPT3(float dotNL, float dotLH, float dotNH, float roughness, float F0) {
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

vec3 f_schlick(vec3 f0, float vh) {
	return f0 + (1.0-f0)*exp2((-5.55473 * vh - 6.98316)*vh);
}

float v_smithschlick(float nl, float nv, float a) {
	return 1.0 / ( (nl*(1.0-a)+a) * (nv*(1.0-a)+a) );
}

float d_ggx(float nh, float a) {
	float a2 = a*a;
	float denom = pow(nh*nh * (a2-1.0) + 1.0, 2.0);
	return a2 * (1.0 / 3.1415926535) / denom;
}

vec3 specularBRDF(vec3 f0, float roughness, float nl, float nh, float nv, float vh, float lh) {
	float a = roughness * roughness;
	return d_ggx(nh, a) * clamp(v_smithschlick(nl, nv, a), 0.0, 1.0) * f_schlick(f0, vh) / 4.0;
	//return vec3(LightingFuncGGX_OPT3(nl, lh, nh, roughness, f0[0]));
}


vec3 lambert(vec3 albedo, float nl) {
	return albedo * max(0.0, nl);
}

vec3 burley(vec3 albedo, float roughness, float NoV, float NoL, float VoH) {
	float FD90 = 0.5 + 2 * VoH * VoH * roughness;
	float FdV = 1 + (FD90 - 1) * pow( 1 - NoV, 5 );
	float FdL = 1 + (FD90 - 1) * pow( 1 - NoL, 5 );
	return albedo * ( (1.0 / 3.1415926535) * FdV * FdL );
}

vec3 orenNayar(vec3 albedo, float roughness, float NoV, float NoL, float VoH ) {
	float pi = 3.1415926535;
	float a = roughness * roughness;
	float s = a;// / ( 1.29 + 0.5 * a );
	float s2 = s * s;
	float VoL = 2.0 * VoH * VoH - 1.0;		// double angle identity
	float Cosri = VoL - NoV * NoL;
	float C1 = 1.0 - 0.5 * s2 / (s2 + 0.33);
	float test = 1.0;
	if (Cosri >= 0.0) test = (1.0 / ( max( NoL, NoV ) ));
	float C2 = 0.45 * s2 / (s2 + 0.09) * Cosri * test;
	return albedo / pi * ( C1 + C2 ) * ( 1.0 + roughness * 0.5 );
}

vec3 diffuseBRDF(vec3 albedo, float roughness, float nv, float nl, float vh, float lv) {
	return lambert(albedo, nl);
	//return burley(albedo, roughness, nv, nl, vh);
	//return orenNayar(albedo, roughness, lv, nl, nv);
}

vec3 surfaceAlbedo(vec3 baseColor, float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(vec3 baseColor, float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
}

float getMipLevelFromRoughness(float roughness) {
	// First mipmap level = roughness 0, last = roughness = 1
	// 6 mipmaps + base
	return roughness * 7.0;
}


// Linearly Transformed Cosines
vec3 mul(mat3 m, vec3 v) {
    return m * v;
}
mat3 mul(mat3 m1, mat3 m2) {
    return m1 * m2;
}
mat3 transpose2(mat3 v) {
    mat3 tmp;
    tmp[0] = vec3(v[0].x, v[1].x, v[2].x);
    tmp[1] = vec3(v[0].y, v[1].y, v[2].y);
    tmp[2] = vec3(v[0].z, v[1].z, v[2].z);

    return tmp;
}
float IntegrateEdge(vec3 v1, vec3 v2) {
    float cosTheta = dot(v1, v2);
    cosTheta = clamp(cosTheta, -0.9999, 0.9999);
    float theta = acos(cosTheta);    
    float res = cross(v1, v2).z * theta / sin(theta);
    return res;
}
int ClipQuadToHorizon(/*inout vec3 L[5], out int n*/) {
    // detect clipping config
    int config = 0;
    if (L0.z > 0.0) config += 1;
    if (L1.z > 0.0) config += 2;
    if (L2.z > 0.0) config += 4;
    if (L3.z > 0.0) config += 8;

    // clip
    int n = 0;
    if (config == 0) {
        // clip all
    }
    else if (config == 1) { // V1 clip V2 V3 V4
        n = 3;
        L1 = -L1.z * L0 + L0.z * L1;
        L2 = -L3.z * L0 + L0.z * L3;
    }
    else if (config == 2) { // V2 clip V1 V3 V4
        n = 3;
        L0 = -L0.z * L1 + L1.z * L0;
        L2 = -L2.z * L1 + L1.z * L2;
    }
    else if (config == 3) { // V1 V2 clip V3 V4
        n = 4;
        L2 = -L2.z * L1 + L1.z * L2;
        L3 = -L3.z * L0 + L0.z * L3;
    }
    else if (config == 4) { // V3 clip V1 V2 V4
        n = 3;
        L0 = -L3.z * L2 + L2.z * L3;
        L1 = -L1.z * L2 + L2.z * L1;
    }
    else if (config == 5) { // V1 V3 clip V2 V4) impossible
        n = 0;
    }
    else if (config == 6) { // V2 V3 clip V1 V4
        n = 4;
        L0 = -L0.z * L1 + L1.z * L0;
        L3 = -L3.z * L2 + L2.z * L3;
    }
    else if (config == 7) { // V1 V2 V3 clip V4
        n = 5;
        L4 = -L3.z * L0 + L0.z * L3;
        L3 = -L3.z * L2 + L2.z * L3;
    }
    else if (config == 8) { // V4 clip V1 V2 V3
        n = 3;
        L0 = -L0.z * L3 + L3.z * L0;
        L1 = -L2.z * L3 + L3.z * L2;
        L2 =  L3;
    }
    else if (config == 9) { // V1 V4 clip V2 V3
        n = 4;
        L1 = -L1.z * L0 + L0.z * L1;
        L2 = -L2.z * L3 + L3.z * L2;
    }
    else if (config == 10) { // V2 V4 clip V1 V3) impossible
        n = 0;
    }
    else if (config == 11) { // V1 V2 V4 clip V3
        n = 5;
        L4 = L3;
        L3 = -L2.z * L3 + L3.z * L2;
        L2 = -L2.z * L1 + L1.z * L2;
    }
    else if (config == 12) { // V3 V4 clip V1 V2
        n = 4;
        L1 = -L1.z * L2 + L2.z * L1;
        L0 = -L0.z * L3 + L3.z * L0;
    }
    else if (config == 13) { // V1 V3 V4 clip V2
        n = 5;
        L4 = L3;
        L3 = L2;
        L2 = -L1.z * L2 + L2.z * L1;
        L1 = -L1.z * L0 + L0.z * L1;
    }
    else if (config == 14) { // V2 V3 V4 clip V1
        n = 5;
        L4 = -L0.z * L3 + L3.z * L0;
        L0 = -L0.z * L1 + L1.z * L0;
    }
    else if (config == 15) { // V1 V2 V3 V4
        n = 4;
    }
    
    if (n == 3)
        L3 = L0;
    if (n == 4)
        L4 = L0;
	return n;
}
vec3 LTC_Evaluate(vec3 N, vec3 V, vec3 P, mat3 Minv, vec3 points0, vec3 points1, vec3 points2, vec3 points3, bool twoSided) {
    // construct orthonormal basis around N
    vec3 T1, T2;
    T1 = normalize(V - N*dot(V, N));
    T2 = cross(N, T1);

    // rotate area light in (T1, T2, R) basis
    Minv = mul(Minv, transpose2(mat3(T1, T2, N)));

    // polygon (allocate 5 vertices for clipping)
    // vec3 L[5];
    L0 = mul(Minv, points0 - P);
    L1 = mul(Minv, points1 - P);
    L2 = mul(Minv, points2 - P);
    L3 = mul(Minv, points3 - P);

    int n = ClipQuadToHorizon(/*L, n*/);
    
    if (n == 0) {
        return vec3(0, 0, 0);
	}

    // project onto sphere
    L0 = normalize(L0);
    L1 = normalize(L1);
    L2 = normalize(L2);
    L3 = normalize(L3);
    L4 = normalize(L4);

    // integrate
    float sum = 0.0;

    sum += IntegrateEdge(L0, L1);
    sum += IntegrateEdge(L1, L2);
    sum += IntegrateEdge(L2, L3);
	
	if (n >= 4) {
        sum += IntegrateEdge(L3, L4);
	}
    if (n == 5) {
        sum += IntegrateEdge(L4, L0);
	}

    sum = twoSided ? abs(sum) : max(0.0, -sum);

    vec3 Lo_i = vec3(sum, sum, sum);

    return Lo_i;
}

#ifdef _Toon
float stepmix(float edge0, float edge1, float E, float x) {
    float T = clamp(0.5 * (x - edge0 + E) / E, 0.0, 1.0);
    return mix(edge0, edge1, T);
}
#endif


void main() {
	
#ifdef _NMTex
	vec3 n = (texture(snormal, texCoord).rgb * 2.0 - 1.0);
	n = normalize(TBN * normalize(n));
	
	// vec3 nn = normalize(normal);
    // vec3 dp1 = dFdx( position );
    // vec3 dp2 = dFdy( position );
    // vec2 duv1 = dFdx( texCoord );
    // vec2 duv2 = dFdy( texCoord );
    // vec3 dp2perp = cross( dp2, nn );
    // vec3 dp1perp = cross( nn, dp1 );
    // vec3 T = dp2perp * duv1.x + dp1perp * duv2.x;
    // vec3 B = dp2perp * duv1.y + dp1perp * duv2.y; 
    // float invmax = inversesqrt( max( dot(T,T), dot(B,B) ) );
    // mat3 TBN = mat3(T * invmax, B * invmax, nn);
	// vec3 n = normalize(TBN * nn);
#else
	vec3 n = normalize(normal);
#endif

	vec3 l = normalize(lightDir);
	float dotNL = max(dot(n, l), 0.0);
	
	float visibility = 1.0;
	if (receiveShadow) {
		if (lPos.w > 0.0) {
			visibility = shadowTest(lPos);
			// visibility = 1.0;
		}
	}


	vec3 baseColor = matColor.rgb;
#ifdef _AMTex
	vec4 texel = texture(salbedo, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	texel.rgb = pow(texel.rgb, vec3(2.2));
	baseColor *= texel.rgb;
#endif

	vec4 outColor;

	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);

	float dotNV = max(dot(n, v), 0.0);
	float dotNH = max(dot(n, h), 0.0);
	float dotVH = max(dot(v, h), 0.0);
	float dotLV = max(dot(l, v), 0.0);
	float dotLH = max(dot(l, h), 0.0);

#ifdef _MMTex
	float metalness = texture(smm, texCoord).r;
#endif
	vec3 albedo = surfaceAlbedo(baseColor, metalness);
	vec3 f0 = surfaceF0(baseColor, metalness);

#ifdef _RMTex
	float roughness = texture(srm, texCoord).r;
#endif




#ifdef _Toon
	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);
    
	const vec3 ambientMaterial = baseColor * vec3(0.35, 0.35, 0.35) + vec3(0.15);
	const vec3 diffuseMaterial = baseColor;
	const vec3 specularMaterial = vec3(0.45, 0.35, 0.35);
	const float shininess = 0.5;
	
	float df = max(0.0, dotNL);
	float sf = max(0.0, dot(n, h));
    sf = pow(sf, shininess);
	
	const float A = 0.1;
    const float B = 0.3;
    const float C = 0.6;
    const float D = 1.0;
    float E = fwidth(df);
	bool f = false;
	if (df > A - E) if (df < A + E) {
		f = true;
		df = stepmix(A, B, E, df);
	}
	
	/*else*/if (!f) if (df > B - E) if(df < B + E) {
		f = true;
		df = stepmix(B, C, E, df);
	}
	
	/*else*/if (!f) if (df > C - E) if (df < C + E) {
		f = true;
		df = stepmix(C, D, E, df);
	}
	/*else*/if (!f) if (df < A) {
		df = 0.0;
	}
	else if (df < B) {
		df = B;
	}
	else if (df < C) {
		df = C;
	}
	else df = D;
	
	E = fwidth(sf);
    if (sf > 0.5 - E && sf < 0.5 + E) {
        sf = smoothstep(0.5 - E, 0.5 + E, sf);
    }
    else {
        sf = step(0.5, sf);
    }
	
	outColor.rgb = ambientMaterial + (df * diffuseMaterial + sf * specularMaterial) * visibility;
    float edgeDetection = (dot(v, n) < 0.1) ? 0.0 : 1.0;
	outColor.rgb *= edgeDetection;
	
	// const int levels = 4;
	// const float scaleFactor = 1.0 / levels;
	
	// float diffuse = max(0, dotNL);
	// const float material_kd = 0.8;
	// const float material_ks = 0.3;
	// vec3 diffuseColor = vec3(0.40, 0.60, 0.70);
	// diffuseColor = diffuseColor * material_kd * floor(diffuse * levels) * scaleFactor;
	// float specular = 0.0;
	// if(dotNL > 0.0) {
	// 	specular = material_ks * pow( max(0, dot( h, n)), shininess);
	// }
	// // Limit specular
	// float specMask = (pow(dot(h, n), shininess) > 0.4) ? 1.0 : 0.0;
	
	// float edgeDetection = (dot(v, n) > 0.3) ? 1.0 : 0.0;
	// outColor.rgb = edgeDetection * ((diffuseColor + specular * specMask) * visibility + ambientMaterial);
#endif


	// LTC
	// const float rectSizeX = 2.5;
	// const float rectSizeY = 1.2;
	// vec3 ex = vec3(1, 0, 0)*rectSizeX;
	// vec3 ey = vec3(0, 0, 1)*rectSizeY;
	// vec3 p1 = light - ex + ey;
	// vec3 p2 = light + ex + ey;
	// vec3 p3 = light + ex - ey;
	// vec3 p4 = light - ex - ey;
	// float theta = acos(dotNV);
	// vec2 tuv = vec2(roughness, theta/(0.5*PI));
	// tuv = tuv*LUT_SCALE + LUT_BIAS;

	// vec4 t = texture(sltcMat, tuv);		
	// mat3 Minv = mat3(
	// 	vec3(  1, t.y, 0),
	// 	vec3(  0, 0,   t.z),
	// 	vec3(t.w, 0,   t.x)
	// );
	
	// vec3 ltcspec = LTC_Evaluate(n, v, position, Minv, p1, p2, p3, p4, true);
	// ltcspec *= texture(sltcMag, tuv).a;
	// vec3 ltcdiff = LTC_Evaluate(n, v, position, mat3(1), p1, p2, p3, p4, true); 
	// vec3 ltccol = ltcspec + ltcdiff * albedo;
	// ltccol /= 2.0*PI;



	// Direct
	vec3 direct = diffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH, dotLV) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH, dotLH);	
	direct = direct * lightColor * lightStrength;
	
	// Indirect
	vec3 indirectDiffuse = texture(senvmapIrradiance, envMapEquirect(n)).rgb;
	indirectDiffuse = pow(indirectDiffuse, vec3(2.2)) * albedo;
	
	vec3 reflectionWorld = reflect(-v, n); 
	float lod = getMipLevelFromRoughness(roughness);// + 1.0;
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
	prefilteredColor = pow(prefilteredColor, vec3(2.2));
	
	vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
	vec3 indirectSpecular = prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
	
	vec3 indirect = indirectDiffuse + indirectSpecular;
	indirect = indirect * lightColor * lightStrength * envmapStrength;

	outColor = vec4(vec3(direct * visibility + indirect), 1.0);
	
#ifdef _OMTex
	vec3 occlusion = texture(som, texCoord).rgb;
	outColor.rgb *= occlusion; 
#endif
	// LTC
	// outColor.rgb = ltccol * 10.0 * visibility + indirect / 14.0;

	gl_FragColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
}
