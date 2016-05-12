#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415926535
#define TwoPI (2.0 * PI)

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1; 
uniform sampler2D gbuffer2; 

uniform sampler2D ssaotex;

uniform sampler2D shadowMap;
uniform sampler2D senvmapRadiance;
uniform sampler2D senvmapIrradiance;
uniform sampler2D senvmapBrdf;
// uniform sampler2D sltcMat;
// uniform sampler2D sltcMag;

// uniform mat4 invVP;
uniform mat4 LMVP;
uniform vec3 light;
uniform vec3 eye;
uniform vec3 eyeLook;



// LTC
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





in vec2 texCoord;
in vec3 viewRay;


// Separable SSS Transmittance Function, ref to sss_pass
vec3 SSSSTransmittance(float translucency, float sssWidth, vec3 worldPosition, vec3 worldNormal, vec3 lightDir) {
	float scale = 8.25 * (1.0 - translucency) / sssWidth;
    vec4 shrinkedPos = vec4(worldPosition - 0.005 * worldNormal, 1.0);
    vec4 shadowPosition = LMVP * shrinkedPos;
    float d1 = texture(shadowMap, shadowPosition.xy / shadowPosition.w).r; // 'd1' has a range of 0..1
    float d2 = shadowPosition.z; // 'd2' has a range of 0..'lightFarPlane'
    const float lightFarPlane = 120 / 3.5;
	d1 *= lightFarPlane; // So we scale 'd1' accordingly:
    float d = scale * abs(d1 - d2);

    float dd = -d * d;
    vec3 profile = vec3(0.233, 0.455, 0.649) * exp(dd / 0.0064) +
                     vec3(0.1,   0.336, 0.344) * exp(dd / 0.0484) +
                     vec3(0.118, 0.198, 0.0)   * exp(dd / 0.187)  +
                     vec3(0.113, 0.007, 0.007) * exp(dd / 0.567)  +
                     vec3(0.358, 0.004, 0.0)   * exp(dd / 1.99)   +
                     vec3(0.078, 0.0,   0.0)   * exp(dd / 7.41);
    return profile * clamp(0.3 + dot(lightDir, -worldNormal), 0.0, 1.0);
}

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / TwoPI, phi / PI);
}

float getMipLevelFromRoughness(float roughness) {
	// First mipmap level = roughness 0, last = roughness = 1
	// 6 mipmaps + baseColor
	// TODO: set number of mipmaps
	return roughness * 7.0;
}

vec3 surfaceAlbedo(vec3 baseColor, float metalness) {
	return mix(baseColor, vec3(0.0), metalness);
}

vec3 surfaceF0(vec3 baseColor, float metalness) {
	return mix(vec3(0.04), baseColor, metalness);
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

vec3 diffuseBRDF(vec3 albedo, float roughness, float nv, float nl, float vh, float lv) {
	return lambert(albedo, nl);
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

float PCF(vec2 size, vec2 uv, float compare) {
    float result = 0.0;
    // for (int x = -1; x <= 1; x++){
        // for(int y = -1; y <= 1; y++){
            // vec2 off = vec2(x, y) / size;
            // result += texture2DShadowLerp(size, uv + off, compare);
			
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
        // }
    // }
    return result / 9.0;
}

float shadowTest(vec4 lPos) {
	vec4 lPosH = lPos / lPos.w;
	lPosH.x = (lPosH.x + 1.0) / 2.0;
    lPosH.y = 1.0 - ((-lPosH.y + 1.0) / (2.0));
	
	return PCF(vec2(2048, 2048), lPosH.st, lPosH.z - 0.005);
}

vec2 octahedronWrap(vec2 v) {
    return (1.0 - abs(v.yx)) * (vec2(v.x >= 0.0 ? 1.0 : -1.0, v.y >= 0.0 ? 1.0 : -1.0));
}

vec3 getPos(float depth) {	
    // vec4 pos = vec4(coord * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    // vec4 pos = vec4(coord * 2.0 - 1.0, depth, 1.0);
    // pos = invVP * pos;
    // pos.xyz /= pos.w;
    // return pos.xyz;
	
	vec3 vray = normalize(viewRay);
	const float znear = 0.1;
	const float zfar = 1000.0;
	const float projectionA = zfar / (zfar - znear);
	const float projectionB = (-zfar * znear) / (zfar - znear);
	// float linearDepth = projectionB / (depth - projectionA);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}

vec2 unpackFloat(float f) {
	float index = floor(f) / 1000.0;
	float alpha = fract(f);
	return vec2(index, alpha);
}





// Linearly Transformed Cosines
// https://eheitzresearch.wordpress.com/415-2/
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


void main() {
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// float depth = 1.0 - g0.a;
	// if (depth == 0.0) discard;
	if (depth == 1.0) discard;
	
	vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, mask, depth
	
	vec4 g1 = texture(gbuffer1, texCoord); // Base color.rgb, roughn/met
	float ao = texture(ssaotex, texCoord).r;

	vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);

	vec3 p = getPos(depth);
	vec3 baseColor = g1.rgb;
	vec2 roughmet = unpackFloat(g1.a);
	float roughness = roughmet.x;
	float metalness = roughmet.y;
	
    vec3 lightDir = light - p.xyz;
    vec3 eyeDir = eye - p.xyz;
	vec3 l = normalize(lightDir);
	vec3 v = normalize(eyeDir);
	vec3 h = normalize(v + l);

	float dotNL = max(dot(n, l), 0.0);
	float dotNV = max(dot(n, v), 0.0);
	float dotNH = max(dot(n, h), 0.0);
	float dotVH = max(dot(v, h), 0.0);
	float dotLV = max(dot(l, v), 0.0);
	float dotLH = max(dot(l, h), 0.0);
	
	vec3 albedo = surfaceAlbedo(baseColor, metalness);
	vec3 f0 = surfaceF0(baseColor, metalness);
	
	vec4 lPos = LMVP * vec4(vec3(p), 1.0);
	float visibility = 1.0;
	if (lPos.w > 0.0) {
		visibility = shadowTest(lPos);
		// visibility = 1.0;
	}
	
	// Direct
	vec3 direct = diffuseBRDF(albedo, roughness, dotNV, dotNL, dotVH, dotLV) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH, dotLH);
	
	// SSS only masked objects
	if (texture(gbuffer0, texCoord).b == 2.0) {
		direct.rgb = direct.rgb * SSSSTransmittance(1.0, 0.005, p, n, lightDir);
	}

	// Indirect
	vec3 indirectDiffuse = texture(senvmapIrradiance, envMapEquirect(n)).rgb;
	// indirectDiffuse = pow(indirectDiffuse, vec3(2.2));
	indirectDiffuse *= albedo;
	
	vec3 reflectionWorld = reflect(-v, n); 
	float lod = getMipLevelFromRoughness(roughness);// + 1.0;
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
	// prefilteredColor = pow(prefilteredColor, vec3(2.2));
	
	vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;
	vec3 indirectSpecular = prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
	vec3 indirect = indirectDiffuse + indirectSpecular;

	vec4 outColor = vec4(vec3(direct * visibility + indirect * ao), 1.0);
	
	
	
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
	
	// vec3 ltcspec = LTC_Evaluate(n, v, p, Minv, p1, p2, p3, p4, true);
	// ltcspec *= texture(sltcMag, tuv).a;
	// vec3 ltcdiff = LTC_Evaluate(n, v, p, mat3(1), p1, p2, p3, p4, true); 
	// vec3 ltccol = ltcspec + ltcdiff * albedo;
	// ltccol /= 2.0*PI;
	// // outColor.rgb = ltccol * 12.0 * visibility + (indirect / 14.0 * ao);
	// outColor.rgb = ltccol * visibility + (indirect / 2.0 * ao);
	
	
	
	
	// outColor.rgb *= occlusion;
	// outColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
	gl_FragColor = vec4(outColor.rgb, outColor.a);
}
