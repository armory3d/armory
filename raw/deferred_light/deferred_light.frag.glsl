#version 450

#ifdef GL_ES
precision mediump float;
#endif

#define PI 3.1415926535
#define TwoPI (2.0 * PI)

uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1; 
uniform sampler2D gbuffer2;

uniform sampler2D ssaotex;

uniform sampler2D shadowMap;
uniform sampler2D senvmapRadiance;
uniform sampler2D senvmapIrradiance;
uniform sampler2D senvmapBrdf;

uniform mat4 LMVP;
uniform vec3 light;
uniform vec3 eye;

in vec2 texCoord;

vec2 envMapEquirect(vec3 normal) {
	float phi = acos(normal.z);
	float theta = atan(-normal.y, normal.x) + PI;
	return vec2(theta / TwoPI, phi / PI);
}

float getMipLevelFromRoughness(float roughness) {
	// First mipmap level = roughness 0, last = roughness = 1
	// 6 mipmaps + base
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

float PCF(vec2 size, vec2 uv, float compare){
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

void main() {
	
	vec4 g0 = texture(gbuffer0, texCoord); // Normals, depth
	float depth = g0.a;
	if (depth >= 1.0) discard;
	
	vec4 g1 = texture(gbuffer1, texCoord); // Positions, roughness
	vec4 g2 = texture(gbuffer2, texCoord); // Base color, metalness
	float ao = texture(ssaotex, texCoord).r; // Normals, depth

	vec3 n = g0.rgb;
	vec3 p = g1.rgb;
	//n = normalize(n);
	vec3 baseColor = g2.rgb;
	
	float roughness = g1.a;
	float metalness = g2.a;
	// float occlusion = g2.a;
	
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

	vec4 outColor = vec4(vec3(direct * visibility + indirect * ao), 1.0);
	
	// outColor.rgb *= occlusion;
	// outColor.rgb *= ao;

	gl_FragColor = vec4(pow(outColor.rgb, vec3(1.0 / 2.2)), outColor.a);
	// vec4 aocol = texture(ssaotex, texCoord);
	// gl_FragColor = aocol;
}
