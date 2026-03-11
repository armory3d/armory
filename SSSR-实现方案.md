# 🎨 SSSR 实现方案

## 📊 现有 SSR 分析

### 当前实现
```glsl
// 简单的随机 jitter
vec3 dir = reflected * (1.0 - rand(texCoord) * ssrJitter * roughness) * 2.0;
```

### 问题
1. ❌ 单一采样模式 → 带状伪影
2. ❌ 无时间累积 → 每帧噪声独立
3. ❌ 无去噪 → 粗糙表面噪点多

---

## 🚀 SSSR 改进方案

### 1. 蓝噪声采样模式
**目标**：用预计算的蓝噪声纹理替代简单随机数

```glsl
// 使用蓝噪声纹理获取采样偏移
uniform sampler2D blueNoiseTex;
uniform float time; // 帧计数用于旋转

vec2 getBlueNoiseOffset(vec2 uv, float frame) {
    // 旋转蓝噪声图案避免时间闪烁
    float angle = frame * 90.0; // 每帧旋转 90 度
    vec2 offset = texture(blueNoiseTex, uv).rg;
    return rotateVector(offset, angle);
}
```

### 2. 多采样累积
**目标**：每帧采样多次，跨帧累积

```glsl
const int NUM_SAMPLES_PER_FRAME = 4;

for (int i = 0; i < NUM_SAMPLES_PER_FRAME; i++) {
    vec2 sampleOffset = getBlueNoiseOffset(texCoord, frame + i);
    vec3 sampleDir = getSampleDirection(reflected, roughness, sampleOffset);
    vec4 hit = rayCast(sampleDir);
    accumColor += textureLod(tex, hit.xy, 0.0).rgb * hit.w;
}
accumColor /= float(NUM_SAMPLES_PER_FRAME);
```

### 3. 时间累积缓冲区
**目标**：结合历史帧减少噪声

```glsl
// 需要额外的 GBuffer 存储历史数据
uniform sampler2D historyColor;
uniform sampler2D historyDepth;
uniform mat4 prevVP; // 上一帧的 VP 矩阵

vec3 reproject(vec3 worldPos, mat4 prevVP) {
    vec4 prevScreen = prevVP * vec4(worldPos, 1.0);
    prevScreen.xy /= prevScreen.w;
    return prevScreen.xy;
}

// 混合历史数据
vec3 accumulate(vec3 current, vec2 uv) {
    vec3 prevColor = textureLod(historyColor, uv, 0.0).rgb;
    float alpha = 0.1; // 累积权重
    return mix(prevColor, current, alpha);
}
```

### 4. SVGF 去噪
**目标**：空域 + 时域联合滤波

```glsl
// 简化版：基于法线和深度的双边滤波
vec3 denoise(vec2 uv, vec3 color, float depth, vec3 normal) {
    vec3 result = vec3(0.0);
    float totalWeight = 0.0;
    
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighborUv = uv + vec2(x, y) * texelSize;
            float neighborDepth = textureLod(gbufferD, neighborUv, 0.0).r;
            float depthDiff = abs(depth - neighborDepth);
            float weight = exp(-depthDiff * 100.0);
            result += textureLod(tex, neighborUv, 0.0).rgb * weight;
            totalWeight += weight;
        }
    }
    return result / totalWeight;
}
```

---

## 📁 修改文件清单

| 文件 | 修改内容 | 优先级 |
|------|---------|--------|
| `ssr_pass.frag.glsl` | 主着色器改造 | 🔴 高 |
| `ssr_pass.json` | 添加 SSSR 参数 | 🟡 中 |
| `std/ssrs.glsl` | 添加工具函数 | 🟡 中 |
| `RenderPath/Deferred.hlsl` | 添加历史缓冲区 | 🟢 低 |

---

## ⏱️ 实施计划

**Day 1:** 蓝噪声采样 + 多采样累积  
**Day 2:** 时间累积缓冲区  
**Day 3:** SVGF 去噪 + UI 选项  
**Day 4:** 测试优化 + PR 准备

---

*生成时间：2026-03-11 08:30*
