#version 450

// ============================================================================
// DDGI Update Pass - 探针光照更新
// 使用 Compute Shader 渲染到 3D 纹理
// ============================================================================

#include "compiled.inc"
#include "std/math.glsl"
#include "std/ddgi.glsl"

// 输入
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;  // 法线
uniform sampler2D gbuffer1;  // 颜色
uniform mat4 invVP;
uniform vec3 ddgiGridMin;
uniform vec3 ddgiGridMax;
uniform vec3 ddgiGridSize;

// 输出到 3D 纹理
uniform image3D ddgiProbeGrid;

layout(local_size_x = 8, local_size_y = 8, local_size_z = 8) in;

void main() {
    ivec3 probeIdx = ivec3(gl_GlobalInvocationID);
    
    // 检查边界
    if (probeIdx.x >= int(ddgiGridSize.x) || 
        probeIdx.y >= int(ddgiGridSize.y) || 
        probeIdx.z >= int(ddgiGridSize.z)) {
        return;
    }
    
    // 计算探针世界位置
    vec3 uvw = vec3(probeIdx) / (ddgiGridSize - 1.0);
    vec3 probePos = mix(ddgiGridMin, ddgiGridMax, uvw);
    
    // 从探针位置向多个方向射线追踪 (Hammersley 采样)
    vec3 irradiance = vec3(0.0);
    const int numSamples = 32;
    
    for (int i = 0; i < numSamples; i++) {
        // Hammersley 序列生成方向
        float phi = 2.0 * 3.14159265 * (float(i) / float(numSamples));
        float cosTheta = 1.0 - 2.0 * float(i) / float(numSamples);
        float sinTheta = sqrt(1.0 - cosTheta * cosTheta);
        
        vec3 dir = vec3(sinTheta * cos(phi), sinTheta * sin(phi), cosTheta);
        
        // 射线追踪 (简化版：从 GBuffer 深度测试)
        float visibility = 1.0;
        float maxDist = 10.0;
        vec3 samplePos = probePos + dir * maxDist;
        
        // 投影到屏幕空间采样深度
        vec4 screenPos = invVP * vec4(samplePos, 1.0);
        screenPos.xyz /= screenPos.w;
        screenPos.xy = screenPos.xy * 0.5 + 0.5;
        
        if (screenPos.x >= 0.0 && screenPos.x <= 1.0 &&
            screenPos.y >= 0.0 && screenPos.y <= 1.0) {
            float sceneDepth = textureLod(gbufferD, screenPos.xy, 0.0).r;
            if (sceneDepth > 0.0 && sceneDepth < 1.0) {
                vec3 scenePos = textureLod(gbuffer1, screenPos.xy, 0.0).rgb;
                float distToScene = length(samplePos - scenePos);
                visibility = smoothstep(0.5, 0.0, distToScene);
            }
        }
        
        // 余弦加权
        float cosWeight = max(dir.y, 0.0);
        irradiance += vec3(visibility * cosWeight);
    }
    
    irradiance *= (1.0 / float(numSamples));
    
    // 写入 3D 纹理
    imageStore(ddgiProbeGrid, probeIdx, vec4(irradiance, 1.0));
}
