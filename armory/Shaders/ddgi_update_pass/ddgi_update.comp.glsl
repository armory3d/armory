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
    
    // 从探针位置向 6 个方向射线追踪
    vec3 irradiance = vec3(0.0);
    vec3 directions[6] = vec3[6](
        vec3(1, 0, 0), vec3(-1, 0, 0),
        vec3(0, 1, 0), vec3(0, -1, 0),
        vec3(0, 0, 1), vec3(0, 0, -1)
    );
    
    for (int i = 0; i < 6; i++) {
        vec3 dir = directions[i];
        
        // 简化的射线追踪（实际应该使用场景几何）
        // 这里从 GBuffer 采样近似
        float radiance = 1.0;  // TODO: 实现射线追踪
        
        irradiance += radiance;
    }
    
    irradiance /= 6.0;
    
    // 写入 3D 纹理
    imageStore(ddgiProbeGrid, probeIdx, vec4(irradiance, 1.0));
}
