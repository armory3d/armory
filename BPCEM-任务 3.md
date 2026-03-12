# 🧊 任务 3: BPCEM - $100

**Box Projected Cubemap Environment Mapping**

**分支:** `feature/box-projected-cubemap`

---

## 📋 技术背景

### 什么是 BPCEM?
传统立方体贴图环境映射使用球面映射，而 **Box Projected Cubemap** 使用盒状投影：

- ✅ 更适合室内场景（墙壁、天花板、地板）
- ✅ 减少角落和边缘的扭曲
- ✅ 更好的视差效果

### 应用场景
- 室内光照探针
- 局部反射探针
- 混合多个环境贴图

---

## 🔍 现有代码分析

### 当前实现
```
armory/Shaders/probe_cubemap/
├── probe_cubemap.frag.glsl  # 立方体贴图采样
├── probe_cubemap.json       # 配置
```

### 需要实现
1. **盒状投影函数**
```glsl
vec3 boxProject(vec3 pos, vec3 boxMin, vec3 boxMax) {
    vec3 boxSize = boxMax - boxMin;
    vec3 boxCenter = (boxMin + boxMax) * 0.5;
    vec3 dir = pos - boxCenter;
    
    // 计算与盒子的交点
    vec3 absDir = abs(dir);
    float t = min(
        min((boxMax.x - boxCenter.x) / absDir.x,
            (boxCenter.x - boxMin.x) / absDir.x),
        ... // Y, Z 轴
    );
    
    return boxCenter + dir * t;
}
```

2. **UV 计算**
```glsl
vec2 cubeMapUV(vec3 dir) {
    // 根据主导轴选择面
    // 计算该面上的 2D UV
}
```

---

## 🚀 实施计划

### Phase 1: 核心算法
- [ ] 实现 box projection 函数
- [ ] 添加盒子参数 (min/max)
- [ ] 测试基本投影

### Phase 2: 着色器集成
- [ ] 修改 probe_cubemap.frag.glsl
- [ ] 添加混合模式
- [ ] 性能优化

### Phase 3: UI 和文档
- [ ] Blender UI 参数
- [ ] 示例场景
- [ ] 文档

---

*创建时间：2026-03-11 09:00*
