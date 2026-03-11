// ============================================================================
// SSSR 时间累积缓冲区
// 存储历史帧数据用于时间累积
// ============================================================================

#ifndef _SSR_PASS_TEMPORAL_GLSL_
#define _SSR_PASS_TEMPORAL_GLSL_

// 历史缓冲区格式
// R: 反射颜色 R
// G: 反射颜色 G
// B: 反射颜色 B
// A: 历史有效性/权重

uniform sampler2D sssrHistoryColor;
uniform sampler2D sssrHistoryDepth;
uniform sampler2D sssrHistoryNormal;

// 输出历史缓冲区
layout(location = 0) out vec4 outHistoryColor;
layout(location = 1) out float outHistoryDepth;
layout(location = 2) out vec4 outHistoryNormal;

// 计算历史权重
float computeTemporalWeight(
    float currentDepth,
    float historyDepth,
    vec3 currentNormal,
    vec3 historyNormal,
    vec2 motionVector
) {
    // 深度差异
    float depthDiff = abs(currentDepth - historyDepth);
    float depthWeight = exp(-depthDiff * 100.0);
    
    // 法线差异
    float normalDot = max(dot(currentNormal, historyNormal), 0.0);
    float normalWeight = normalDot;
    
    // 运动向量 (光流)
    float motionWeight = exp(-length(motionVector) * 50.0);
    
    return depthWeight * normalWeight * motionWeight;
}

// 时间累积
vec3 accumulateTemporal(
    vec3 currentColor,
    vec3 historyColor,
    float weight
) {
    // 自适应混合
    float alpha = 0.1 + 0.8 * weight;
    return mix(historyColor, currentColor, alpha);
}

// 写入历史缓冲区
void writeHistory(
    vec3 color,
    float depth,
    vec3 normal,
    vec2 motionVector
) {
    outHistoryColor = vec4(color, 1.0);
    outHistoryDepth = depth;
    outHistoryNormal = vec4(normal, 0.0);
}

#endif
