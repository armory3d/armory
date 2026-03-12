# 🎯 SSSR 开发任务

**任务来源：** https://github.com/armory3d/armory/issues/2611  
**Bounty:** $100  
**分支：** `feature/sssr-stochastic`

---

## 📋 实施清单

### Phase 1: 代码分析
- [ ] 阅读现有 SSR 实现 (`ssr_pass.frag.glsl`)
- [ ] 理解 `ssrs.glsl` 中的随机化函数
- [ ] 分析采样模式和噪声问题

### Phase 2: 实现 SSSR
- [ ] 实现随机化采样模式（蓝噪声/旋转噪声）
- [ ] 添加时间累积（Temporal Accumulation）
- [ ] 实现去噪滤波器（SVGF 或类似）
- [ ] 在 UI 中添加 SSSR 选项

### Phase 3: 测试优化
- [ ] 性能测试（对比 SSR）
- [ ] 视觉效果对比
- [ ] 边界情况处理

### Phase 4: 提交 PR
- [ ] 代码清理
- [ ] 文档更新
- [ ] 提交 PR

---

## 🔑 关键文件

```
armory/Shaders/ssr_pass/
├── ssr_pass.frag.glsl    # 主着色器
├── ssr_pass.vert.glsl    # 顶点着色器
└── ssr_pass.json         # 配置

armory/Shaders/std/
└── ssrs.glsl             # SSR 工具函数
```

---

## 💡 技术要点

1. **随机化采样：** 使用蓝噪声纹理或旋转采样模式
2. **时间累积：** 结合历史帧减少噪声
3. **去噪：** SVGF (Spatiotemporal Variance-Guided Filtering)
4. **性能：** 控制采样数，平衡质量/性能

---

*创建时间：2026-03-11 08:25*
