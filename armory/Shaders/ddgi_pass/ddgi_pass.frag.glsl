// ============================================================================
// DDGI Pass - 漫反射全局光照渲染
// 使用探针网格计算间接光照
// ============================================================================

#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/ddgi.glsl"

// 输入
uniform sampler2D gbufferD;      // 深度
uniform sampler2D gbuffer0;      // 法线
uniform sampler2D gbuffer1;      // 颜色/Albedo
uniform sampler2D gbuffer2;      // 粗糙度/金属度

// DDGI 探针网格
uniform sampler3D ddgiProbeGrid;
uniform vec3 ddgiGridMin;
uniform vec3 ddgiGridMax;
uniform vec3 ddgiGridSize;

// 输出
layout(location = 0) out vec4 fragColor;

// 屏幕空间顶点
in vec2 texCoord;

void main() {
    // 采样 GBuffer
    float depth = textureLod(gbufferD, texCoord, 0.0).r;
    if (depth <= 0.0 || depth >= 1.0) {
        discard;
    }
    
    vec3 normal = textureLod(gbuffer0, texCoord, 0.0).rgb;
    vec3 albedo = textureLod(gbuffer1, texCoord, 0.0).rgb;
    vec3 roughnessMetallic = textureLod(gbuffer2, texCoord, 0.0).rgb;
    float roughness = roughnessMetallic.r;
    float metallic = roughnessMetallic.g;
    
    // 重建世界位置
    vec3 worldPos = getPosition();
    
    // 计算 DDGI 间接光照
    vec3 ddgiIrradiance = ddgiComputeLighting(
        worldPos,
        normalize(normal),
        ddgiProbeGrid,
        ddgiGridMin,
        ddgiGridMax,
        ddgiGridSize,
        1.0  // 强度
    );
    
    // 应用 Albedo
    vec3 indirectDiffuse = ddgiIrradiance * albedo;
    
    // 输出间接光照
    fragColor = vec4(indirectDiffuse, 1.0);
}
