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

uniform bool lighting;
uniform bool receiveShadow;

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

// Just for testing, unrealiable on low precisions
float rand(vec2 co) {
    return fract(sin(dot(co.xy ,vec2(12.9898, 78.233))) * 43758.5453);
}

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
    for (int x = -1; x <= 1; x++){
        for(int y = -1; y <= 1; y++){
            vec2 off = vec2(x, y) / size;
            result += texture2DShadowLerp(size, uv + off, compare);
        }
    }
    return result / 9.0;
}

float shadowTest(vec4 lPos, float dotNL) {
	vec4 lPosH = lPos / lPos.w;
	lPosH.x = (lPosH.x + 1.0) / 2.0;
    lPosH.y = 1.0 - ((-lPosH.y + 1.0) / (2.0));
	
	return PCF(vec2(2048.0, 2048.0), lPosH.st, lPosH.z - 0.005);
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
			visibility = shadowTest(lPos, dotNL);
			visibility = 1.0;
		}
	}

#ifdef _AMTex
	vec4 texel = texture(salbedo, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	vec3 baseColor = texel.rgb;
#else
	vec3 baseColor = matColor.rgb;
#endif

	baseColor = pow(baseColor.rgb, vec3(2.2));
	vec4 outColor;

	if (lighting) {
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

		// Direct
		vec3 direct = diffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH, dotLV) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH, dotLH);	
		
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

		outColor = vec4(vec3(direct * visibility + indirect), 1.0);
		
#ifdef _OMTex
		vec3 occlusion = texture(som, texCoord).rgb;
		outColor.rgb *= occlusion; 
#endif
	}
	else {
		outColor = vec4(baseColor * visibility, 1.0);
	}

	gl_FragColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
}
