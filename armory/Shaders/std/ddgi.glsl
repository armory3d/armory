#ifndef _DDGI_GLSL_
#define _DDGI_GLSL_

// ============================================================================
// DDGI - Dynamic Diffuse Global Illumination
// 动态漫反射全局光照工具函数
// ============================================================================

// 探针网格参数
// ddgiGridMin: 网格最小世界坐标
// ddgiGridMax: 网格最大世界坐标
// ddgiGridSize: 每个轴的探针数量 (如 32x32x32)

uniform sampler3D ddgiProbeGrid;
uniform vec3 ddgiGridMin;
uniform vec3 ddgiGridMax;
uniform vec3 ddgiGridSize;
uniform float ddgiProbeSpacing;

// 探针数据结构 (每个探针存储的信息)
// R: 环境光强度
// G: 天空光强度
// B: 反射光强度
// A: 有效性标志

// 将世界坐标转换为探针网格 UV
vec3 worldToProbeUV(vec3 worldPos) {
    vec3 uvw = (worldPos - ddgiGridMin) / (ddgiGridMax - ddgiGridMin);
    return clamp(uvw, 0.0, 1.0);
}

// 获取探针索引
ivec3 getProbeIndex(vec3 worldPos) {
    vec3 uvw = worldToProbeUV(worldPos);
    return ivec3(uvw * (ddgiGridSize - 1.0));
}

// 三线性插值采样 DDGI
vec3 sampleDDGI(vec3 worldPos) {
    vec3 uvw = worldToProbeUV(worldPos);
    return textureLod(ddgiProbeGrid, uvw, 0.0).rgb;
}

// 采样并应用法线衰减
vec3 sampleDDGIWithNormal(vec3 worldPos, vec3 normal) {
    vec3 irradiance = sampleDDGI(worldPos);
    
    // 简单的 Lambertian 衰减
    float ndot = max(dot(normal, normalize(vec3(0, 1, 0))), 0.0);
    
    // 环境光 + 方向光混合
    return irradiance * (0.3 + 0.7 * ndot);
}

// 计算探针位置 (用于更新 pass)
vec3 getProbePosition(ivec3 probeIdx) {
    vec3 uvw = vec3(probeIdx) / (ddgiGridSize - 1.0);
    return mix(ddgiGridMin, ddgiGridMax, uvw);
}

// 射线 - 盒子相交测试 (用于探针可见性)
bool rayBoxIntersect(vec3 origin, vec3 dir, vec3 boxMin, vec3 boxMax, out float t) {
    vec3 invDir = 1.0 / dir;
    vec3 t0 = (boxMin - origin) * invDir;
    vec3 t1 = (boxMax - origin) * invDir;
    vec3 tmin = min(t0, t1);
    vec3 tmax = max(t0, t1);
    float tNear = max(max(tmin.x, tmin.y), tmin.z);
    float tFar = min(min(tmax.x, tmax.y), tmax.z);
    t = tNear;
    return tFar >= tNear && tNear >= 0.0;
}

// 探针可见性测试
float probeVisibility(vec3 probePos, vec3 samplePos, sampler2D depthTex, mat4 lightVP) {
    // 简化版本：深度测试
    vec4 lightSpace = lightVP * vec4(samplePos, 1.0);
    lightSpace.xyz /= lightSpace.w;
    lightSpace.xyz = lightSpace.xyz * 0.5 + 0.5;
    
    if (lightSpace.z < 0.0 || lightSpace.z > 1.0) return 0.0;
    
    float shadowMapDepth = textureLod(depthTex, lightSpace.xy, 0.0).r;
    float visibility = lightSpace.z <= shadowMapDepth + 0.001 ? 1.0 : 0.0;
    
    return visibility;
}

// 混合多个探针 (用于平滑过渡)
vec3 blendProbes(vec3 worldPos, vec3 normal) {
    ivec3 baseIdx = getProbeIndex(worldPos);
    vec3 frac = fract(worldToProbeUV(worldPos) * (ddgiGridSize - 1.0));
    
    vec3 result = vec3(0.0);
    float totalWeight = 0.0;
    
    // 8 个角落探针三线性插值
    for (int z = 0; z <= 1; z++) {
        for (int y = 0; y <= 1; y++) {
            for (int x = 0; x <= 1; x++) {
                ivec3 idx = baseIdx + ivec3(x, y, z);
                vec3 probePos = getProbePosition(idx);
                
                // 权重基于距离
                float dist = distance(worldPos, probePos);
                float weight = 1.0 / (1.0 + dist * dist);
                
                vec3 probeData = textureLod(ddgiProbeGrid, 
                    vec3(idx) / (ddgiGridSize - 1.0), 0.0).rgb;
                
                result += probeData * weight;
                totalWeight += weight;
            }
        }
    }
    
    return totalWeight > 0.0 ? result / totalWeight : vec3(0.0);
}

#endif // _DDGI_GLSL_
