#ifndef _SSSR_GLSL_
#define _SSSR_GLSL_

// ============================================================================
// SSSR - Stochastic Screen-Space Reflections
// 随机化屏幕空间反射工具函数
// ============================================================================

// 蓝噪声采样模式
// 使用预计算的 64x64 蓝噪声纹理提供高质量的随机采样

uniform sampler2D sssrBlueNoiseTex;
uniform int sssrFrameIndex;
uniform vec2 sssrTexelSize;

// 旋转矩阵
mat2 rotateMatrix(float angle) {
    float s = sin(angle);
    float c = cos(angle);
    return mat2(c, -s, s, c);
}

// 获取旋转后的蓝噪声采样偏移
// 每帧旋转 90 度避免时间闪烁
vec2 getSSSRBlueNoise(vec2 uv, int frame) {
    // 从蓝噪声纹理获取基础随机值
    vec2 noise = textureLod(sssrBlueNoiseTex, uv * 4.0, 0.0).rg;
    
    // 每帧旋转 90 度 (PI/2)
    float angle = float(frame) * 1.57079632679;
    vec2 offset = rotateMatrix(angle) * (noise * 2.0 - 1.0);
    
    return offset;
}

// 获取采样方向
// 基于粗糙度和蓝噪声偏移生成随机反射方向
vec3 getSSSRSampleDirection(vec3 reflected, float roughness, vec2 noiseOffset) {
    // 粗糙度越高，随机化程度越大
    float jitter = roughness * length(noiseOffset);
    
    // 在反射方向周围随机化
    vec3 dir = reflected;
    dir.x += noiseOffset.x * jitter;
    dir.y += noiseOffset.y * jitter;
    
    return normalize(dir);
}

// 多采样累积
// 每帧执行多次采样并平均
const int SSSR_NUM_SAMPLES = 4;

vec4 sssrRayCastMulti(
    vec3 viewPos,
    vec3 reflected,
    float roughness,
    sampler2D tex,
    sampler2D gbufferD,
    sampler2D gbuffer0,
    sampler2D gbuffer1,
    mat4 P,
    mat3 V3,
    vec2 cameraProj,
    int frame
) {
    vec3 accumColor = vec3(0.0);
    float accumIntensity = 0.0;
    
    for (int i = 0; i < SSSR_NUM_SAMPLES; i++) {
        // 获取当前采样的蓝噪声偏移
        vec2 noiseOffset = getSSSRBlueNoise(gl_FragCoord.xy / 1920.0, frame + i);
        
        // 生成随机反射方向
        vec3 dir = getSSSRSampleDirection(reflected, roughness, noiseOffset);
        
        // TODO: 调用 rayCast 函数（需要从主着色器传入）
        // 这里简化处理，实际需要在主着色器中实现
    }
    
    return vec4(accumColor / float(SSSR_NUM_SAMPLES), accumIntensity);
}

// 时间累积权重计算
// 基于深度和法线差异决定历史数据可信度
float computeHistoryWeight(
    float currentDepth,
    float historyDepth,
    vec3 currentNormal,
    vec3 historyNormal
) {
    float depthDiff = abs(currentDepth - historyDepth);
    float normalDot = dot(currentNormal, historyNormal);
    
    // 深度差异权重
    float depthWeight = exp(-depthDiff * 100.0);
    
    // 法线差异权重
    float normalWeight = max(0.0, normalDot);
    
    return depthWeight * normalWeight;
}

// 混合历史数据
vec3 accumulateHistory(
    vec3 currentColor,
    vec3 historyColor,
    float weight
) {
    // 自适应混合：历史数据可信度高时增加权重
    float alpha = 0.1 + 0.8 * weight;
    return mix(historyColor, currentColor, alpha);
}

// 简化版 SVGF 去噪
// 基于深度和法线的双边滤波
vec3 sssrDenoise(
    vec2 uv,
    sampler2D colorTex,
    sampler2D depthTex,
    sampler2D normalTex
) {
    vec3 centerColor = textureLod(colorTex, uv, 0.0).rgb;
    float centerDepth = textureLod(depthTex, uv, 0.0).r;
    vec3 centerNormal = textureLod(normalTex, uv, 0.0).rgb;
    
    vec3 result = vec3(0.0);
    float totalWeight = 0.0;
    
    // 5x5 滤波核
    for (int dy = -2; dy <= 2; dy++) {
        for (int dx = -2; dx <= 2; dx++) {
            vec2 neighborUv = uv + vec2(dx, dy) * sssrTexelSize;
            
            float neighborDepth = textureLod(depthTex, neighborUv, 0.0).r;
            vec3 neighborNormal = textureLod(normalTex, neighborUv, 0.0).rgb;
            vec3 neighborColor = textureLod(colorTex, neighborUv, 0.0).rgb;
            
            // 深度权重
            float depthDiff = abs(centerDepth - neighborDepth);
            float depthWeight = exp(-depthDiff * 50.0);
            
            // 法线权重
            float normalDot = dot(centerNormal, neighborNormal);
            float normalWeight = max(0.0, normalDot);
            
            // 空间权重 (高斯)
            float dist = float(dx * dx + dy * dy);
            float spatialWeight = exp(-dist / 8.0);
            
            float weight = depthWeight * normalWeight * spatialWeight;
            result += neighborColor * weight;
            totalWeight += weight;
        }
    }
    
    return totalWeight > 0.0 ? result / totalWeight : centerColor;
}

#endif // _SSSR_GLSL_
