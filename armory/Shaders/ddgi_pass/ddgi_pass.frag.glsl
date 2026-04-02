#version 450

// ============================================================================
// DDGI - Dynamic Diffuse Global Illumination
// 动态漫反射全局光照
// ============================================================================

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/ddgi.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler3D ddgiProbeGrid;
uniform mat4 invVP;
uniform vec3 ddgiGridMin;
uniform vec3 ddgiGridMax;
uniform vec3 ddgiGridSize;

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

void main() {
    vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
    float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
    
    // 解码法线
    vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);
    
    // 世界空间位置
    vec3 worldPos = getPos2(invVP, d, texCoord);
    
    // 采样 DDGI 探针网格
    vec3 uvw = (worldPos - ddgiGridMin) / (ddgiGridMax - ddgiGridMin);
    uvw = clamp(uvw, 0.0, 1.0);
    
    // 三线性插值获取辐照度
    vec3 irradiance = textureLod(ddgiProbeGrid, uvw, 0.0).rgb;
    
    // 应用法线衰减
    float ndot = max(dot(n, vec3(0, 1, 0)), 0.1);
    fragColor.rgb = irradiance * ndot;
    fragColor.a = 1.0;
}
