#ifndef _BOX_PROJECTED_CUBEMAP_GLSL_
#define _BOX_PROJECTED_CUBEMAP_GLSL_

// ============================================================================
// BPCEM - Box Projected Cubemap Environment Mapping
// 盒状投影立方体环境映射
// ============================================================================

// 盒子结构体
struct Box {
    vec3 min;
    vec3 max;
    vec3 center;
    vec3 size;
};

// 初始化盒子
Box createBox(vec3 boxMin, vec3 boxMax) {
    Box box;
    box.min = boxMin;
    box.max = boxMax;
    box.center = (boxMin + boxMax) * 0.5;
    box.size = boxMax - boxMin;
    return box;
}

// ============================================================================
// 核心盒状投影函数
// ============================================================================

/**
 * 计算从位置到盒子表面的投影方向
 * 
 * @param pos 世界空间位置
 * @param box 盒子边界
 * @param rayDir 射线方向（通常是反射方向）
 * @return 投影后的方向向量
 */
vec3 boxProject(vec3 pos, Box box, vec3 rayDir) {
    vec3 absDir = abs(rayDir);
    
    // 计算射线与盒子各面的交点距离
    vec3 tMin = (box.min - pos) / rayDir;
    vec3 tMax = (box.max - pos) / rayDir;
    
    // 取最近的正面交点
    vec3 t = min(tMin, tMax);
    
    // 找到最小的正交点（最近的盒子面）
    float minT = min(min(t.x, t.y), t.z);
    
    // 如果所有交点都是负的，说明在盒子内部，使用中心到表面的方向
    if (minT < 0.0) {
        vec3 toCenter = pos - box.center;
        vec3 absToCenter = abs(toCenter);
        
        // 找到主导轴
        if (absToCenter.x > absToCenter.y && absToCenter.x > absToCenter.z) {
            return normalize(vec3(sign(toCenter.x), 0.0, 0.0));
        } else if (absToCenter.y > absToCenter.x && absToCenter.y > absToCenter.z) {
            return normalize(vec3(0.0, sign(toCenter.y), 0.0));
        } else {
            return normalize(vec3(0.0, 0.0, sign(toCenter.z)));
        }
    }
    
    // 计算交点位置
    vec3 hitPos = pos + rayDir * minT;
    
    // 返回从盒子中心到交点的方向
    return normalize(hitPos - box.center);
}

// ============================================================================
// 简化版本：快速盒状投影
// ============================================================================

/**
 * 快速盒状投影（适用于性能敏感场景）
 * 使用轴对齐的简化计算
 */
vec3 boxProjectFast(vec3 pos, vec3 boxMin, vec3 boxMax, vec3 rayDir) {
    vec3 boxCenter = (boxMin + boxMax) * 0.5;
    vec3 boxSize = boxMax - boxMin;
    vec3 halfSize = boxSize * 0.5;
    
    vec3 absDir = abs(rayDir);
    
    // 避免除以零
    absDir = max(absDir, vec3(0.0001));
    
    // 计算到各面的距离
    vec3 tPos = (boxMax - pos) / absDir;
    vec3 tNeg = (pos - boxMin) / absDir;
    
    // 选择正确的面（根据射线方向）
    vec3 t = mix(tPos, tNeg, step(vec3(0.0), rayDir));
    
    // 找到最近的交点
    float minT = min(min(t.x, t.y), t.z);
    
    // 计算交点
    vec3 hitPos = pos + rayDir * minT;
    
    return normalize(hitPos - boxCenter);
}

// ============================================================================
// 立方体贴图 UV 计算
// ============================================================================

/**
 * 根据方向向量计算立方体贴图的 UV 坐标
 * 
 * @param dir 方向向量
 * @return vec3(xy=UV, z=faceIndex)
 */
vec3 getCubeMapUV(vec3 dir) {
    vec3 absDir = abs(dir);
    float maxAbs = max(max(absDir.x, absDir.y), absDir.z);
    
    vec2 uv;
    float faceIndex;
    
    if (maxAbs == absDir.x) {
        faceIndex = dir.x > 0.0 ? 0.0 : 1.0;
        uv = dir.zy / absDir.x;
    } else if (maxAbs == absDir.y) {
        faceIndex = dir.y > 0.0 ? 2.0 : 3.0;
        uv = dir.xz / absDir.y;
    } else {
        faceIndex = dir.z > 0.0 ? 4.0 : 5.0;
        uv = dir.xy / absDir.z;
    }
    
    // 转换到 [0, 1] 范围
    uv = uv * 0.5 + 0.5;
    
    return vec3(uv, faceIndex);
}

// ============================================================================
// 盒状投影立方体贴图采样
// ============================================================================

/**
 * 使用盒状投影采样立方体贴图
 * 
 * @param probeTex 立方体贴图
 * @param pos 世界空间位置
 * @param boxMin 盒子最小角
 * @param boxMax 盒子最大角
 * @param rayDir 射线方向
 * @param lod LOD 级别
 * @return 采样的颜色
 */
vec4 textureBoxProjected(
    samplerCube probeTex,
    vec3 pos,
    vec3 boxMin,
    vec3 boxMax,
    vec3 rayDir,
    float lod
) {
    Box box = createBox(boxMin, boxMax);
    vec3 projectedDir = boxProject(pos, box, rayDir);
    return textureLod(probeTex, projectedDir, lod);
}

// 快速版本（无 LOD）
vec4 textureBoxProjectedFast(
    samplerCube probeTex,
    vec3 pos,
    vec3 boxMin,
    vec3 boxMax,
    vec3 rayDir
) {
    vec3 projectedDir = boxProjectFast(pos, boxMin, boxMax, rayDir);
    return texture(probeTex, projectedDir);
}

// ============================================================================
// 混合多个盒状投影探针
// ============================================================================

/**
 * 混合多个盒状投影探针
 * 根据距离和权重平滑过渡
 */
vec4 blendBoxProbes(
    samplerCube[] probes,
    vec3[] boxMins,
    vec3[] boxMaxs,
    vec3 pos,
    vec3 rayDir,
    int numProbes
) {
    vec4 accumColor = vec4(0.0);
    float totalWeight = 0.0;
    
    for (int i = 0; i < numProbes; i++) {
        // 计算到探针中心的距离
        vec3 center = (boxMins[i] + boxMaxs[i]) * 0.5;
        float dist = distance(pos, center);
        
        // 距离权重（越近权重越大）
        float weight = 1.0 / (1.0 + dist * dist);
        
        vec4 probeColor = textureBoxProjectedFast(
            probes[i], pos, boxMins[i], boxMaxs[i], rayDir
        );
        
        accumColor += probeColor * weight;
        totalWeight += weight;
    }
    
    return totalWeight > 0.0 ? accumColor / totalWeight : vec4(0.0);
}

#endif // _BOX_PROJECTED_CUBEMAP_GLSL_
