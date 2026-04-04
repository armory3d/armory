#version 450

// ============================================================================
// BPCEM - Box Projected Cubemap Environment Mapping
// 盒状投影立方体环境映射
// ============================================================================

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/box_projected_cubemap.glsl"

uniform samplerCube probeTex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform mat4 invVP;
uniform vec3 probep;
uniform vec3 eye;

// BPCEM 参数
uniform vec3 boxMin;
uniform vec3 boxMax;
uniform int useBoxProjection;

in vec4 wvpposition;
out vec4 fragColor;

void main() {
	vec2 texCoord = wvpposition.xy / wvpposition.w;
	texCoord = texCoord * 0.5 + 0.5;
	#ifdef _InvY
	texCoord.y = 1.0 - texCoord.y;
	#endif

	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	float roughness = g0.b;
	
    // 跳过完全粗糙的表面
	if (roughness > 0.95) {
		fragColor.rgb = vec3(0.0);
		return;
	}

	float spec = fract(textureLod(gbuffer1, texCoord, 0.0).a);
    // 跳过无金属度的表面
	if (spec == 0.0) {
		fragColor.rgb = vec3(0.0);
		return;
	}

	float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	vec3 wp = getPos2(invVP, depth, texCoord);

    // 解码法线
	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

    // 计算反射方向
	vec3 v = wp - eye;
	vec3 r = reflect(v, n);
	#ifdef _InvY
	r.y = -r.y;
	#endif
    
    // 盒状投影 vs 传统球面投影
    vec3 sampleDir;
    if (useBoxProjection == 1) {
        // 使用盒状投影
        sampleDir = boxProjectFast(wp, boxMin, boxMax, r);
    } else {
        // 传统立方体映射
        sampleDir = r;
    }
    
    // 采样立方体贴图
    vec3 envColor = texture(probeTex, sampleDir).rgb;
    
    // 计算强度 (基于位置和法线)
    float intensity = clamp((1.0 - roughness) * dot(wp - probep, n), 0.0, 1.0);
    
	fragColor.rgb = envColor * intensity;
}
