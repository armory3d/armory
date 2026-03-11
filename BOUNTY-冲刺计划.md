# 🎯 Armory3D $400 Bounty - 冲刺计划

**目标：** 100% 完成 4 个任务，提交 PR 收款

**时间：** 2026-03-11 起，全力以赴

---

## 📋 任务清单

### ✅ 任务 2: 手柄修复 - $100
**状态：** 已完成！
**分支：** `feature/gamepad-fix`
**提交：** 2 commits

**修复内容：**
- 使用状态机检测 0.5 阈值跨越
- 避免 L2/R2 模拟按键多次触发 started
- 虚拟按键映射使用 0.2/0.8 阈值

**下一步：** 等待 PR 合并

---

### 🟢 任务 1: SSSR - $100
**状态：** 85%
**分支：** `feature/sssr-stochastic`
**提交：** 3 commits

**已完成：**
- ✅ 蓝噪声采样函数
- ✅ 多采样累积 (4 样本/帧)
- ✅ 蓝噪声纹理生成
- ✅ SVGF 去噪框架

**待完成：**
- [ ] 时间累积缓冲区集成
- [ ] RenderPath 配置
- [ ] UI 开关选项
- [ ] 视觉效果测试

**预计完成：** 1-2 天

---

### 🟢 任务 3: BPCEM - $100
**状态：** 75%
**分支：** `feature/box-projected-cubemap`
**提交：** 2 commits

**已完成：**
- ✅ `std/box_projected_cubemap.glsl` 工具库
- ✅ boxProject() 核心算法
- ✅ textureBoxProjected() 采样函数
- ✅ blendBoxProbes() 多探针混合

**待完成：**
- [ ] probe_cubemap.frag.glsl 集成
- [ ] Blender UI 参数
- [ ] 室内场景测试

**预计完成：** 1 天

---

### 🟡 任务 4: DDGI - $100
**状态：** 60%
**分支：** `feature/ddgi-global-illumination`
**提交：** 2 commits

**已完成：**
- ✅ `std/ddgi.glsl` 工具库
- ✅ ddgi_pass.frag.glsl 框架
- ✅ ddgi_update.comp.glsl Compute Shader

**待完成：**
- [ ] 真实射线追踪实现
- [ ] 3D 纹理分配
- [ ] 时间累积优化
- [ ] 性能测试

**预计完成：** 2-3 天

---

## ⏱️ 时间规划

| 日期 | 任务 | 目标 |
|------|------|------|
| Day 1 (今天) | SSSR + BPCEM | 90% + 85% |
| Day 2 | SSSR 完成 + DDGI | 100% + 75% |
| Day 3 | BPCEM + DDGI | 100% + 90% |
| Day 4 | DDGI 完成 + PR | 100% ✅ |

---

## 💰 收款流程

1. **完成代码** → 本地测试通过
2. **提交 PR** → armory3d/armory
3. **代码审查** → 修复反馈
4. **合并收款** → $400 到手

---

## 🔗 相关链接

- **Issue:** https://github.com/armory3d/armory/issues/2611
- **Fork:** https://github.com/ma-moon/armory
- **Bounty:** $400 (4 任务 × $100)

---

*全力以赴，早日收款！* 💪🐱
