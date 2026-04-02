# 🌍 任务 4: DDGI - $100

**Diffuse Diffuse Global Illumination**

**分支:** `feature/ddgi-global-illumination`  
**Issue:** https://github.com/armory3d/armory/issues/2610

---

## 📋 技术背景

### 什么是 DDGI?
**DDGI (Diffuse Diffuse Global Illumination)** 是一种实时全局光照技术：

- ✅ 使用光线追踪计算间接漫反射光照
- ✅ 比传统 SSGI 更准确
- ✅ 支持动态场景
- ✅ 可与时域累积结合减少噪声

### 与 SSGI 的区别
| 特性 | SSGI | DDGI |
|------|------|------|
| 采样方式 | 屏幕空间 | 世界空间探针 |
| 精度 | 受屏幕分辨率限制 | 独立分辨率 |
| 性能 | 较便宜 | 较昂贵 |
| 质量 | 有边缘伪影 | 更平滑准确 |

---

## 🔍 现有代码分析

### 当前实现
```
armory/Shaders/ssgi_pass/
├── ssgi_pass.frag.glsl  # SSGI 主着色器
├── ssgi_pass.json       # 配置
```

### 需要改进
1. **探针网格系统**
   - 在世界空间布置探针网格
   - 每个探针存储 irradiance

2. **光线追踪**
   - 从探针向半球发射射线
   - 累积间接光照

3. **插值**
   - 三线性插值相邻探针
   - 平滑过渡

---

## 🚀 实施计划

### Phase 1: 探针系统
- [ ] 定义探针网格结构
- [ ] 实现探针 irradiance 计算
- [ ] 添加探针更新机制

### Phase 2: 光照计算
- [ ] 半球采样
- [ ] 间接光照累积
- [ ] 能量守恒

### Phase 3: 优化
- [ ] 时域累积
- [ ] 空间滤波
- [ ] LOD 系统

---

*创建时间：2026-03-11 09:05*
