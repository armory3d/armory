// Antialiased Cel Shading
// http://prideout.net/blog/?p=22
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
uniform mat4 V;

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
	
	const float bias = 0.009;//0.005;
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

float stepmix(float edge0, float edge1, float E, float x) {
    float T = clamp(0.5 * (x - edge0 + E) / E, 0.0, 1.0);
    return mix(edge0, edge1, T);
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
			visibility = shadowTest(lPos);
			// visibility = 1.0;
		}
	}

#ifdef _AMTex
	vec4 texel = texture(salbedo, texCoord);
#ifdef _AlphaTest
	if(texel.a < 0.4)
		discard;
#endif
	vec3 baseColor = texel.rgb;
	baseColor = pow(baseColor.rgb, vec3(2.2));
#else
	vec3 baseColor = matColor.rgb;
#endif

	vec4 outColor;

	// Toon
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
	
	
	gl_FragColor = outColor;
	// gl_FragColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
}
