# Armory3D SSSR 开发日志

**日期：** 2026-03-11  
**任务：** SSSR (Stochastic Screen-Space Reflections)  
**分支：** `feature/sssr-stochastic`

---

## ✅ 已完成

### Phase 1: 代码分析 ✅
- [x] 阅读现有 SSR 实现
- [x] 分析 `ssr_pass.frag.glsl` 光线追踪逻辑
- [x] 分析 `ssrs.glsl` 工具函数
- [x] 识别改进点：随机化、时间累积、去噪

### Phase 2: 核心实现 ✅
- [x] 创建 `std/sssr.glsl` 工具库
  - [x] 蓝噪声采样函数 `getSSSRBlueNoise()`
  - [x] 随机方向生成 `getSSSRSampleDirection()`
  - [x] 时间累积权重 `computeHistoryWeight()`
  - [x] SVGF 去噪 `sssrDenoise()`
- [x] 修改主着色器 `ssr_pass.frag.glsl`
  - [x] 集成 SSSR 工具库
  - [x] 实现多采样累积 `sssrMultiSample()`
  - [x] 添加历史缓冲区支持
  - [x] 保留原有 SSR 兼容性

---

## 🚧 进行中

### Phase 3: 渲染管线集成
- [ ] 添加蓝噪声纹理资源
- [ ] 配置历史缓冲区 (RenderPath)
- [ ] 添加 SSSR uniform 参数
- [ ] 在 UI 中添加 SSSR 开关

---

## 📋 待办

### Phase 4: 测试优化
- [ ] 性能对比测试 (SSR vs SSSR)
- [ ] 视觉效果对比
- [ ] 边界情况处理
- [ ] 代码清理

### Phase 5: PR 准备
- [ ] 编写技术文档
- [ ] 准备演示截图/GIF
- [ ] 提交 PR

---

## 📊 技术要点

### 蓝噪声采样
```glsl
// 每帧旋转 90 度避免时间闪烁
float angle = float(frame) * 1.57079632679;
vec2 offset = rotateMatrix(angle) * (noise * 2.0 - 1.0);
```

### 多采样累积
```glsl
// 每帧 4 个样本，跨帧累积等效 16+ 样本
for (int i = 0; i < 4; i++) {
    vec2 noiseOffset = getSSSRBlueNoise(texCoord, frame + i);
    // ... 光线追踪
}
```

### SVGF 去噪
```glsl
// 5x5 滤波核，基于深度 + 法线权重
float depthWeight = exp(-depthDiff * 50.0);
float normalWeight = max(0.0, dot(currentNormal, neighborNormal));
```

---

## 🔧 下一步

1. **蓝噪声纹理** - 生成或导入 64x64 蓝噪声纹理
2. **RenderPath 修改** - 添加历史缓冲区和 uniform 传递
3. **UI 选项** - 在 Armory 编辑器中添加 SSSR 开关
4. **测试** - 在示例场景中验证效果

---

*最后更新：2026-03-11 08:35*
