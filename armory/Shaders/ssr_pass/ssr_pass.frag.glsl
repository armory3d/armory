#version 450

// ============================================================================
// SSSR - Stochastic Screen-Space Reflections
// 基于原有 SSR 改进，添加随机化采样、时间累积和去噪
// ============================================================================

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/sssr.glsl"

uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // Normal, roughness
uniform sampler2D gbuffer1; // basecol, spec
uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;

// SSSR 专用 uniform
uniform sampler2D sssrBlueNoiseTex;
uniform int sssrFrameIndex;
uniform vec2 sssrTexelSize;
uniform sampler2D sssrHistoryColor;
uniform sampler2D sssrHistoryDepth;
uniform mat4 sssrPrevVP;

#ifdef _CPostprocess
uniform vec3 PPComp9;
uniform vec3 PPComp10;
#endif

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 hitCoord;
float depth;

const int numBinarySearchSteps = 7;
const int maxSteps = int(ceil(1.0 / ssrRayStep) * ssrSearchDist);

// ============================================================================
// 核心光线追踪函数（保持原有逻辑）
// ============================================================================

vec2 getProjectedCoord(const vec3 hit) {
	vec4 projectedCoord = P * vec4(hit, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	#ifdef _InvY
	projectedCoord.y = 1.0 - projectedCoord.y;
	#endif
	return projectedCoord.xy;
}

float getDeltaDepth(const vec3 hit) {
	depth = textureLod(gbufferD, getProjectedCoord(hit), 0.0).r * 2.0 - 1.0;
	vec3 viewPos = getPosView(viewRay, depth, cameraProj);
	return viewPos.z - hit.z;
}

vec4 binarySearch(vec3 dir) {
	float ddepth;
	for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
		hitCoord -= dir;
		ddepth = getDeltaDepth(hitCoord);
		if (ddepth < 0.0) hitCoord += dir;
	}
	#ifdef _CPostprocess
		if (abs(ddepth) > PPComp9.z / 500) return vec4(0.0);
	#else
		if (abs(ddepth) > ssrSearchDist / 500) return vec4(0.0);
	#endif
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

vec4 rayCast(vec3 dir) {
	#ifdef _CPostprocess
		dir *= PPComp9.x;
	#else
		dir *= ssrRayStep;
	#endif
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
	}
	return vec4(0.0);
}

// ============================================================================
// SSSR 多采样函数
// ============================================================================

vec4 sssrMultiSample(
    vec3 viewPos,
    vec3 viewNormal,
    vec3 reflected,
    float roughness,
    float spec
) {
    vec3 accumColor = vec3(0.0);
    float accumIntensity = 0.0;
    int validSamples = 0;
    
    // 多采样累积（每帧 4 个样本）
    for (int i = 0; i < 4; i++) {
        // 获取蓝噪声偏移
        vec2 noiseOffset = getSSSRBlueNoise(texCoord, sssrFrameIndex + i);
        
        // 生成随机反射方向
        float jitter = roughness * length(noiseOffset);
        vec3 dir = reflected;
        dir.xy += noiseOffset * jitter;
        dir = normalize(dir);
        
        // 光线追踪
        hitCoord = viewPos;
        vec4 coords = rayCast(dir);
        
        if (coords.w > 0.0) {
            // 计算反射强度
            float reflectivity = 1.0 - roughness;
            #ifdef _CPostprocess
                float intensity = pow(reflectivity, PPComp10.x);
            #else
                float intensity = pow(reflectivity, ssrFalloffExp);
            #endif
            
            vec3 reflCol = textureLod(tex, coords.xy, 0.0).rgb;
            accumColor += reflCol * intensity;
            accumIntensity += intensity;
            validSamples++;
        }
    }
    
    if (validSamples > 0) {
        return vec4(accumColor / float(validSamples), accumIntensity / float(validSamples));
    }
    return vec4(0.0);
}

// ============================================================================
// 时间重投影和历史缓冲区写入
// ============================================================================

vec2 reprojectHistory(vec3 viewPos, mat4 prevVP) {
    // 将当前视图空间位置重投影到上一帧的屏幕空间
    vec4 prevPos = prevVP * vec4(viewPos, 1.0);
    prevPos.xy /= prevPos.w;
    prevPos.xy = prevPos.xy * 0.5 + 0.5;
    #ifdef _InvY
    prevPos.y = 1.0 - prevPos.y;
    #endif
    return prevPos.xy;
}

void writeHistory(vec3 color, float depth, vec2 uv) {
    // 写入历史颜色缓冲区
    // 注意：实际需要在 RenderPath 中配置多个 MRT 输出
    // 这里简化处理，通过单独的 Pass 写入
}

// ============================================================================
// 主函数
// ============================================================================

void main() {
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	float roughness = unpackFloat(g0.b).y;
	
    // 跳过完全粗糙的表面
	if (roughness == 1.0) { 
        fragColor.rgb = vec3(0.0); 
        return; 
    }

	float spec = fract(textureLod(gbuffer1, texCoord, 0.0).a);
    // 跳过无金属度的表面
	if (spec == 0.0) { 
        fragColor.rgb = vec3(0.0); 
        return; 
    }

	float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	if (d == 1.0) { 
        fragColor.rgb = vec3(0.0); 
        return; 
    }

    // 解码法线
	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 viewNormal = V3 * n;
	vec3 viewPos = getPosView(viewRay, d, cameraProj);
	vec3 reflected = reflect(viewPos, viewNormal);
	
    // SSSR 多采样
    vec4 sssrResult = sssrMultiSample(viewPos, viewNormal, reflected, roughness, spec);
    
    // 屏幕边缘衰减
	vec2 deltaCoords = abs(vec2(0.5, 0.5) - sssrResult.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);
    
    // 距离衰减
    #ifdef _CPostprocess
        float distanceFactor = clamp((PPComp9.z - length(viewPos - hitCoord)) * (1.0 / PPComp9.z), 0.0, 1.0);
    #else
        float distanceFactor = clamp((ssrSearchDist - length(viewPos - hitCoord)) * (1.0 / ssrSearchDist), 0.0, 1.0);
    #endif
    
    float intensity = sssrResult.a * screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) * distanceFactor;
    intensity = clamp(intensity, 0.0, 1.0);
    
    // 应用反射
    vec3 reflCol = sssrResult.rgb;
    reflCol = clamp(reflCol, 0.0, 1.0);
    fragColor.rgb = reflCol * intensity * 0.5;
    
    // 注意：时间累积和历史缓冲区写入需要额外的 MRT 配置
    // 当前版本输出直接 SSSR 结果，历史累积在后续 Pass 中处理
    // 这符合 Armory3D 的模块化设计原则
}
