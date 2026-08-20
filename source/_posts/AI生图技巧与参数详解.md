---
title: AI 生图技巧与参数详解（文生图 / 图生图从入门到会用）
date: 2026-08-20 18:30:00
tags: [AI绘画, Stable Diffusion, 文生图, 图生图, 参数详解, 提示词]
categories: 折腾笔记
top_img: /images/cover-sdtips.webp
cover: /images/cover-sdtips.webp
---

# AI 生图技巧与参数详解（文生图 / 图生图从入门到会用）

> 看完这篇，你就能用 Stable Diffusion 系列模型稳定出图，而不是靠玄学。
> 本文以 SD 1.5 为主，但 90% 的概念同样适用于 SDXL、Flux 等模型。

---

## 零、先建立心智模型

AI 生图不是「把一句话变成图」，而是**从一个纯噪声图开始，一步步去噪，最终收敛成和提示词相关的图**。

```
随机噪声  ──(逐步去噪)──>  模糊轮廓  ──(逐步去噪)──>  清晰图片
            ↑ 每一步都由 prompt 引导方向
```

所以你在调的每一个参数，本质上都是在回答两个问题：
1. **去噪多少步？**（num_inference_steps / 采样器）
2. **往提示词的哪个方向去？**（prompt / guidance_scale / 参考图）

---

## 一、两种生图模式

| 模式 | 英文 | 输入 | 输出 | 本质 |
| :--- | :--- | :--- | :--- | :--- |
| **文生图** | txt2img | 一段文字 | 一张图 | 从噪声「无中生有」 |
| **图生图** | img2img | 一张图 + 文字 | 一张新图 | 从原图「改头换面」 |

一句话记：**想全新创作用文生图，想改已有图用图生图。**

---

## 二、提示词（Prompt）—— 最重要的「方向盘」

### 2.1 正向提示词（prompt）

告诉模型「你要画什么」。SD 1.5 的 CLIP 只认**英文**，用**逗号分隔的短语**堆叠，不是写一句通顺句子。

**结构建议（从主体到细节）**：

```
[主体] , [媒介/风格] , [细节特征] , [灯光] , [构图/镜头] , [画质词]
```

**示例**：
```
a cute cat, pixel art, 2d game sprite, sitting on a wooden chair,
big round eyes, soft fur, warm sunlight, close-up, masterpiece, best quality
```

### 2.2 反向提示词（negative_prompt）

告诉模型「千万别出现什么」。这是**出图质量的半壁江山**，几乎每次都要带。

**通用保底反向词**（直接抄）：
```
low quality, lowres, worst quality, bad anatomy, bad hands,
extra fingers, blurry, jpeg artifacts, watermark, text, signature
```

### 2.3 提示词权重（进阶）

用括号调整某词的重要性：

| 写法 | 含义 |
| :--- | :--- |
| `(red hair)` | 权重 ×1.1 |
| `(red hair:1.3)` | 显式权重 1.3 |
| `[red hair]` | 权重降低 |
| `(red hair:1.1):1.1` | 可嵌套，越套越重 |

> ⚠️ 权重别拉太狠（>1.5），容易过饱和、崩坏。

### 2.4 提示词技巧清单

- **具体 > 抽象**：写 `golden retriever, fluffy` 比写 `beautiful dog` 出得好
- **画质词常驻**：`masterpiece, best quality, highly detailed`
- **风格词明确**：`pixel art` / `oil painting` / `anime style` / `realistic photo`
- **避免矛盾**：别同时写 `day` 和 `night`
- **权重分配**：主体和风格给高权重，次要细节正常写

---

## 三、文生图参数详解

```python
image = pipe_txt2img(
    prompt="...",
    negative_prompt="...",
    num_inference_steps=25,   # 步数
    guidance_scale=7.5,       # CFG 引导
    width=512, height=512,    # 尺寸
    generator=torch.Generator().manual_seed(42),  # 种子
).images[0]
```

### 3.1 num_inference_steps（推理步数）

去噪迭代次数。**越多越精细，但边际递减且更慢**。

| 步数 | 观感 |
| :--- | :--- |
| 10-15 | 快但偏糊，细节少 |
| 20-30 | **甜点区**，质量与速度平衡 |
| 40-50 | 几乎看不出提升，慢一倍 |
| >80 | 浪费时间 |

> 配合好的采样器（如 UniPC、DPM++），20 步就够。

### 3.2 guidance_scale（CFG 引导强度）

模型「听不听提示词」的程度。

| 值 | 效果 |
| :--- | :--- |
| 1-3 | 自由发挥，常常跑题 |
| **7-9** | **最常用区间**，贴合提示词 |
| 10-15 | 严格遵循，但可能过饱和、构图死板 |
| >20 | 容易出怪异 artifacts |

> 图生图时 CFG 可比文生图略低（6-8），保留原图感。

### 3.3 width / height（尺寸）

SD 1.5 在 **512×512** 上训练，这是黄金尺寸。

| 尺寸 | 结果 |
| :--- | :--- |
| 512×512 | 最佳，构图正常 |
| 512×768 / 768×512 | 可用（竖/横图） |
| ≥768×768 | 容易重复肢体、畸形脸（模型没学过） |
| 非 8 的倍数 | 部分模型直接报错 |

> 想要高清大图：先用 512 出图，再用**高清修复（Hires. fix）/ 放大模型（ESRGAN、R-ESRGAN）** 放大，而非直接拉高分辨率。
> 注意：必须是 **8 的倍数**（因为 VAE 下采样 8 倍）。

### 3.4 generator / seed（随机种子）

控制「从哪团噪声开始」。**固定种子 = 同参数可复现**。

```python
torch.Generator().manual_seed(42)   # 固定为 42
torch.Generator()                    # 不固定 = 每次随机
```

**工作流**：先随机出一批 → 挑一张喜欢的 → 固定它的种子 → 微调提示词精修。

---

## 四、图生图参数详解

```python
image = pipe_img2img(
    prompt="...",
    negative_prompt="...",
    image=init_image,         # 原图（必须传）
    strength=0.6,             # 重绘强度（图生图灵魂参数）
    num_inference_steps=25,
    guidance_scale=7,
    generator=torch.Generator().manual_seed(42),
).images[0]
```

### 4.1 strength（重绘强度）—— 图生图最核心

控制「在多大程度上改原图」：

| strength | 保留原图 | 改动 | 典型用途 |
| :--- | :--- | :--- | :--- |
| 0.1-0.3 | 95%+ | 极轻微 | 去瑕疵、轻微调色 |
| **0.4-0.6** | 50-70% | 中等 | **风格转换**（照片→动漫、手绘→像素） |
| 0.7-0.9 | 10-30% | 大幅 | 换服装、换姿势变体 |
| 1.0 | 0% | 完全重画 | 等价于文生图 |

**口诀**：想保持原结构 → 低 strength；想大变样 → 高 strength。

### 4.2 图生图尺寸

原图会被 resize 到目标尺寸再喂入。建议目标尺寸也用 512 基准，避免拉伸畸变。

### 4.3 透明背景处理（坑）

原图若有透明通道（RGBA），SD 不支持，会出现**蒙白雾 / 发白**。解决：先铺白底转 RGB：

```python
from PIL import Image
init = Image.open("a.png").convert("RGBA")
bg = Image.new("RGBA", init.size, (255, 255, 255, 255))
init = Image.alpha_composite(bg, init).convert("RGB")
```

（你部署脚本里的 `preprocess_image()` 已内置此逻辑。）

### 4.4 图生图实战场景

| 场景 | 做法 |
| :--- | :--- |
| 照片转动漫 | 原图 + `anime style` + strength 0.6 |
| 线稿上色 | 线稿 + `colored, flat color` + strength 0.8 |
| 换风格 | 原图 + 目标风格词 + strength 0.5 |
| 局部改 | 配合 inpainting（局部重绘）而非整图 img2img |

---

## 五、采样器（Scheduler）怎么选

采样器决定「怎么走完这 N 步去噪」。不同采样器速度与质量权衡不同。

| 采样器 | 速度 | 质量 | 推荐场景 |
| :--- | :--- | :--- | :--- |
| **UniPC** | 最快 | 中上 | CPU/日常首选，20 步够 |
| **DPM++ 2M Karras** | 慢 | 最高 | 追求极致，GPU 上香 |
| **DDIM** | 中 | 高 | 经典稳定，可复现性好 |
| **Euler / Euler a** | 快 | 中 | 轻量尝鲜 |
| **PNDM** | 中 | 高 | diffusers 默认 |

> **经验法则**：CPU 用 UniPC；GPU 且不计时间用 DPM++ 2M Karras；想要可控复现用 DDIM。
> 注意：带 `a` 的（如 Euler a）是**随机采样**，同种子也不完全可复现。

---

## 六、ControlNet —— 精确控制构图

当纯提示词控制不住姿势/构图时，用 ControlNet 把「参考图的结构」作为条件强塞给模型。

| 类型 | 控制什么 | 典型用途 |
| :--- | :--- | :--- |
| **OpenPose** | 人体骨骼姿势 | 指定角色动作 |
| **Canny** | 边缘/轮廓 | 按线稿、实物轮廓生成 |
| **Depth** | 深度/远近 | 保持空间透视 |
| **Lineart** | 线稿 | 上色、线稿转实图 |
| **Scribble** | 涂鸦 | 草图生图 |

**OpenPose 工作流**（你部署脚本已内置）：
```
上传人像 → 提取骨骼姿势图 → 姿势图 + 新提示词 → 生成同姿势新角色
```

> ControlNet 与提示词是「叠加约束」：提示词管长相风格，ControlNet 管姿势构图，两者互不冲突。

---

## 七、从 0 到出一张好图的完整流程

1. **定模式**：全新创作 → 文生图；改图 → 图生图
2. **写正向提示词**：主体 + 风格 + 细节 + 画质词
3. **写反向提示词**：套用通用保底词，加你不想要的内容
4. **设参数**：步数 25 / CFG 7.5 / 尺寸 512 / seed 随机
5. **选采样器**：CPU 用 UniPC
6. **出一批**（seed 随机，4-8 张）
7. **挑一张**喜欢的，固定它的 seed
8. **精修**：微调提示词权重、调 CFG、图生图换风格
9. **放大**：用超分模型出高清最终图

---

## 八、常见翻车与对策

| 现象 | 原因 | 对策 |
| :--- | :--- | :--- |
| 多手多脚 | 提示词/权重冲突、步数低 | 反向词加 `extra fingers`，步数提到 30 |
| 脸畸形 | 分辨率高、面部占比小 | 降到 512 基准，或加 `detailed face` |
| 太糊 | 步数低、CFG 过低 | 步数 25+，CFG 7+ |
| 过饱和/塑料感 | CFG 过高 | 降到 7-9 |
| 完全跑题 | CFG 过低 / 提示词矛盾 | CFG 8，检查矛盾词 |
| 图生图发白 | 透明通道 | 铺白底转 RGB |
| 图生图不像原图 | strength 太高 | 降到 0.4-0.6 |
| 图生图太像原图 | strength 太低 | 提到 0.7+ |

---

## 九、提示词模板（可直接改）

### 二次元角色
```
1girl, anime style, silver hair, blue eyes, school uniform,
smile, cherry blossoms background, soft lighting, masterpiece, best quality
```

### 写实照片
```
photorealistic, a man in coffee shop, natural lighting, 50mm lens,
shallow depth of field, detailed skin, 8k uhd, highly detailed
```

### 像素游戏素材
```
pixel art, game item, golden sword, isolated on white,
16-bit retro style, clean edges, no anti-aliasing
```

### 通用反向词
```
low quality, lowres, worst quality, bad anatomy, bad hands,
extra digits, fewer digits, blurry, jpeg artifacts, watermark,
text, signature, cropped, deformed
```

---

## 十、小结

AI 生图不是玄学，是一组可控的参数：

- **prompt / negative_prompt**：决定「画什么、不画什么」
- **num_inference_steps**：画多细（20-30 甜点）
- **guidance_scale**：听不听话（7-9 甜点）
- **width/height**：画多大（SD1.5 锁 512 基准）
- **seed**：能不能复现（挑中再固定）
- **strength（图生图）**：改多少（0.4-0.6 甜点）
- **采样器**：怎么画（CPU→UniPC，GPU→DPM++）
- **ControlNet**：构图兜底（姿势/边缘/深度）

记住心法：**先随机出一批挑喜欢的，固定种子再精修**。祝你出图愉快 🎨

> 本文参数与你的本地 SD 1.5 部署脚本（见上一篇《OpenVINO 本地部署 SD 1.5》）完全对应，可直接在 Gradio 界面里照着调。
