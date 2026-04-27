// ============================================================================
// DDGI (Dynamic Diffuse Global Illumination) 工具库
// 动态漫反射全局光照 - 探针网格系统
// ============================================================================

#ifndef _DDGI_GLSL_
#define _DDGI_GLSL_

// DDGI 探针结构
struct DDGIProbe {
    vec3 position;      // 探针世界位置
    vec3 irradiance;    // 辐照度 (RGB)
    float visibility;   // 可见性
    vec3 normal;        // 法线 (用于法线引导插值)
    float radius;       // 影响半径
};

// 从 3D 纹理采样探针辐照度
vec3 ddgiSampleIrradiance(sampler3D ddgiGrid, vec3 uvw, vec3 gridMin, vec3 gridMax) {
    // UVW 坐标转换
    vec3 normalizedUVW = (uvw - gridMin) / (gridMax - gridMin);
    normalizedUVW = clamp(normalizedUVW, 0.0, 1.0);
    
    // 三线性插值采样
    return textureLod(ddgiGrid, normalizedUVW, 0.0).rgb;
}

// 多探针插值 (三线性)
vec3 ddgiInterpolateProbes(
    sampler3D ddgiGrid,
    vec3 position,
    vec3 gridMin,
    vec3 gridMax,
    vec3 gridSize
) {
    // 计算 UVW 坐标
    vec3 uvw = (position - gridMin) / (gridMax - gridMin);
    uvw = clamp(uvw, 0.0, 1.0);
    
    // 计算网格索引
    vec3 gridIdx = uvw * (gridSize - 1.0);
    vec3 gridIdx0 = floor(gridIdx);
    vec3 gridIdx1 = ceil(gridIdx);
    vec3 fracIdx = fract(gridIdx);
    
    // 采样 8 个角点
    vec3 samples[8];
    for (int x = 0; x < 2; x++) {
        for (int y = 0; y < 2; y++) {
            for (int z = 0; z < 2; z++) {
                vec3 idx = vec3(
                    x == 0 ? gridIdx0.x : gridIdx1.x,
                    y == 0 ? gridIdx0.y : gridIdx1.y,
                    z == 0 ? gridIdx0.z : gridIdx1.z
                );
                vec3 probeUVW = idx / (gridSize - 1.0);
                int sampleIdx = x + y * 2 + z * 4;
                samples[sampleIdx] = textureLod(ddgiGrid, probeUVW, 0.0).rgb;
            }
        }
    }
    
    // 三线性插值
    vec3 result = vec3(0.0);
    result = mix(
        mix(samples[0], samples[1], fracIdx.x),
        mix(samples[2], samples[3], fracIdx.x),
        fracIdx.y
    );
    vec3 top = mix(
        mix(samples[4], samples[5], fracIdx.x),
        mix(samples[6], samples[7], fracIdx.x),
        fracIdx.y
    );
    result = mix(result, top, fracIdx.z);
    
    return result;
}

// 计算方向遮蔽 (Direction Occlusion)
float ddgiComputeDirectionOcclusion(
    vec3 normal,
    vec3 direction,
    float bias
) {
    float ndotd = dot(normal, direction);
    return smoothstep(-bias, bias, ndotd);
}

// 探针可见性测试
float ddgiTestVisibility(
    vec3 probePos,
    vec3 surfacePos,
    vec3 normal,
    sampler2D gbufferD,
    mat4 VP
) {
    vec3 dir = surfacePos - probePos;
    float dist = length(dir);
    dir = normalize(dir);
    
    // 投影到屏幕空间
    vec4 screenPos = VP * vec4(surfacePos, 1.0);
    screenPos.xyz /= screenPos.w;
    screenPos.xy = screenPos.xy * 0.5 + 0.5;
    
    if (screenPos.x < 0.0 || screenPos.x > 1.0 ||
        screenPos.y < 0.0 || screenPos.y > 1.0) {
        return 0.0;
    }
    
    // 深度测试
    float sceneDepth = textureLod(gbufferD, screenPos.xy, 0.0).r;
    if (sceneDepth > 0.0 && sceneDepth < 1.0) {
        float depthDiff = abs(sceneDepth - screenPos.z);
        return step(depthDiff, 0.01);
    }
    
    return 1.0;
}

// 时间累积 - 指数移动平均
vec3 ddgiTemporalAccumulation(
    vec3 current,
    vec3 previous,
    float alpha
) {
    return mix(previous, current, alpha);
}

// 历史有效性检查
float ddgiCheckHistoryValidity(
    vec3 currentPos,
    vec3 previousPos,
    sampler2D gbufferD,
    mat4 invVP
) {
    // 检查位置是否发生显著变化
    float posDiff = length(currentPos - previousPos);
    if (posDiff > 0.1) {
        return 0.0;
    }
    
    // 检查深度是否一致
    vec4 screenPos = invVP * vec4(currentPos, 1.0);
    screenPos.xyz /= screenPos.w;
    screenPos.xy = screenPos.xy * 0.5 + 0.5;
    
    if (screenPos.x < 0.0 || screenPos.x > 1.0 ||
        screenPos.y < 0.0 || screenPos.y > 1.0) {
        return 0.0;
    }
    
    float currentDepth = textureLod(gbufferD, screenPos.xy, 0.0).r;
    float previousDepth = screenPos.z;
    
    return step(abs(currentDepth - previousDepth), 0.05);
}

// 法线引导插值权重
float ddgiComputeNormalWeight(vec3 probeNormal, vec3 surfaceNormal) {
    float ndotn = dot(probeNormal, surfaceNormal);
    return smoothstep(0.0, 1.0, max(0.0, ndotn));
}

// 距离衰减函数
float ddgiComputeDistanceWeight(float distance, float radius) {
    // 二次衰减
    float normalizedDist = distance / radius;
    return smoothstep(1.0, 0.0, normalizedDist);
}

// 完整的 DDGI 光照计算
vec3 ddgiComputeLighting(
    vec3 position,
    vec3 normal,
    sampler3D ddgiGrid,
    vec3 gridMin,
    vec3 gridMax,
    vec3 gridSize,
    float intensity
) {
    // 采样探针辐照度
    vec3 irradiance = ddgiInterpolateProbes(
        ddgiGrid, position, gridMin, gridMax, gridSize
    );
    
    // 应用法线余弦权重
    float cosWeight = max(0.0, normal.y); // 简化版，假设 Y 轴向上
    
    // 强度调节
    return irradiance * cosWeight * intensity;
}

#endif // _DDGI_GLSL_
