# 🌍 任务 4: DDGI - $100

**Dynamic Diffuse Global Illumination**

**分支:** `feature/ddgi-global-illumination`

---

## 📋 技术背景

### SSGI vs DDGI

| 特性 | SSGI (现有) | DDGI (目标) |
|------|------------|------------|
| 采样方式 | 屏幕空间射线 | 3D 探针网格 |
| 边界问题 | ❌ 有黑边 | ✅ 无边界 |
| 性能 | 中等 | 高 (预计算) |
| 动态物体 | ❌ 不支持 | ✅ 支持 |
| 内存 | 低 | 中 (探针缓存) |

### DDGI 核心原理
1. **探针网格**: 在场景中均匀分布探针
2. **双面光照**: 每个探针存储入射光照
3. **动态更新**: 只更新变化的探针
4. **插值采样**: 三线性插值获取光照

---

## 🔍 现有代码分析

### SSGI 实现 (`ssgi_pass.frag.glsl`)
```glsl
// 当前使用 5 条射线采样屏幕空间
rayCast(n);  // 法线方向
rayCast(mix(n, o1, angleMix));  // 切线方向
rayCast(mix(n, o2, angleMix));  // 副切线方向
// ...
```

**局限性:**
- 屏幕空间 → 视野外无数据
- 每帧重计算 → 性能开销大
- 无法处理动态物体遮挡

---

## 🚀 DDGI 实现方案

### Phase 1: 探针网格
```glsl
// 3D 纹理存储探针数据
uniform sampler3D ddgiProbeGrid;  // 光照数据
uniform vec3 probeGridMin;
uniform vec3 probeGridMax;
uniform vec3 probeGridSize;  // 探针数量 (x,y,z)

vec3 getProbeCoord(vec3 worldPos) {
    return (worldPos - probeGridMin) / (probeGridMax - probeGridMin);
}
```

### Phase 2: 探针更新
```hlsl
// 计算探针光照
void updateProbe(int x, int y, int z) {
    vec3 pos = getProbePosition(x, y, z);
    for (int i = 0; i < NUM_DIRECTIONS; i++) {
        vec3 dir = getDirection(i);
        float radiance = traceRay(pos, dir);
        storeProbeData(x, y, z, i, radiance);
    }
}
```

### Phase 3: 光照采样
```glsl
// 三线性插值采样
vec3 sampleDDGI(vec3 worldPos, vec3 normal) {
    vec3 uvw = getProbeCoord(worldPos);
    vec3 irradiance = textureLod(ddgiProbeGrid, uvw, 0.0).rgb;
    return irradiance * max(dot(normal, vec3(0,1,0)), 0.1);
}
```

---

## 📁 文件清单

| 文件 | 状态 | 说明 |
|------|------|------|
| `armory/Shaders/ddgi_pass/` | 🔴 新建 | DDGI 主着色器 |
| `armory/Shaders/std/ddgi.glsl` | 🔴 新建 | 工具函数 |
| `armory/Shaders/ddgi_update_pass/` | 🔴 新建 | 探针更新 |
| `armory/Sources/iron/DDGI.hx` | 🔴 新建 | 探针管理 |

---

## ⏱️ 实施计划

**Day 1:** 探针网格数据结构 + 3D 纹理  
**Day 2:** 探针更新逻辑 (Compute Shader)  
**Day 3:** 光照采样 + 三线性插值  
**Day 4:** Blender UI + 性能优化  

---

*创建时间：2026-03-11 09:05*
