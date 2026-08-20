---
title: OpenVINO 本地部署 SD 1.5（支持文生图、图生图、ControlNet 姿势控制）
date: 2026-08-20 18:00:00
tags: [OpenVINO, Stable Diffusion, 本地部署, AI绘画, 文生图, 图生图, ControlNet]
categories: 折腾笔记
top_img: /images/cover-openvino.webp
cover: /images/cover-openvino.webp
---

# OpenVINO 本地部署 SD 1.5（支持文生图、图生图、ControlNet 姿势控制）

> 基于实际可用的部署脚本整理，已在 Windows + Intel CPU 上验证通过

---

## 一、为什么用 OpenVINO 跑 SD？

Stable Diffusion 默认用 PyTorch + CUDA 跑在 NVIDIA 显卡上。但没有独显、只有 Intel CPU（或 Intel 核显）的机器怎么办？

**OpenVINO** 是 Intel 的推理加速工具包，能把模型转换到 Intel CPU / 核显 / NPU 上高效推理。本文的部署方案采用 **PyTorch 原生加载 + OpenVINO 可选加速** 的混合架构：默认用 PyTorch 直接加载 Pipeline 快速出图，有需要时可切换 OpenVINO IR 格式加速。

本文基于一套**实际可用**的部署脚本（`start_sd.py` + `gradio_helper.py`），整理出**文生图（txt2img）**、**图生图（img2img）**、**姿势控制（ControlNet）** 三种核心能力的完整本地部署流程。

---

## 二、环境准备

### 1. 获取 OpenVINO Notebooks

本项目基于 Intel 官方的 [openvino_notebooks](https://github.com/openvinotoolkit/openvino_notebooks) 仓库中的 `controlnet-stable-diffusion` 示例改造而来。

```bash
# 方式一：Git 克隆
git clone https://github.com/openvinotoolkit/openvino_notebooks.git

# 方式二：直接下载 ZIP
# 访问 https://github.com/openvinotoolkit/openvino_notebooks/releases
# 下载最新版本的压缩包，解压后重命名为 openvino_notebooks-latest
```

> 💡 当前项目中已包含该仓库的副本：`G:\program\tests\openvino_notebooks-latest`

### 2. Python 环境

推荐 Python 3.10+，使用虚拟环境隔离依赖：

```bash
python -m venv sd_env
sd_env\Scripts\activate
```

### 3. 安装依赖

```bash
# 核心推理
pip install torch torchvision
pip install diffusers transformers accelerate

# OpenVINO 加速（可选）
pip install openvino

# 界面与工具
pip install gradio controlnet_aux
pip install pillow numpy opencv-python matplotlib
```

> ⚠️ 注意：`torch` 安装时会自动检测 CPU/GPU 版本。纯 CPU 用户直接 `pip install torch` 即可，无需指定 CUDA 版本。

### 4. 配置国内镜像（必做）

HF 模型下载在国内极慢甚至失败，必须设置镜像加速：

```python
import os
os.environ['HF_HOME'] = r'G:\program\tests\hf_cache'                    # 模型缓存目录
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'        # HuggingFace 国内镜像
```

这些配置已写入 `start_sd.py` 开头，首次运行时生效。

---

## 三、模型下载与缓存

### 1. 需要的模型文件

脚本首次运行时会自动下载以下模型到 `G:\program\tests\hf_cache`：

| 模型 | 用途 | 大小 |
| :--- | :--- | :--- |
| `botp/stable-diffusion-v1-5` | SD 1.5 核心（文生图 + 图生图通用） | ~5GB |
| `lllyasviel/control_v11p_sd15_openpose` | ControlNet 姿势控制 | ~1.5GB |
| `lllyasviel/ControlNet` (OpenPose) | 从图片提取人体姿势 | ~300MB |

> 💡 模型会自动缓存，第二次启动无需重新下载。

### 2. SD 1.5 核心文件结构

`botp/stable-diffusion-v1-5` 模型内部包含三个关键组件：

| 文件 | 作用 |
| :--- | :--- |
| `unet/diffusion_pytorch_model.safetensors` | 去噪核心网络（UNet） |
| `text_encoder/model.safetensors` | 文本编码器（CLIP Text Encoder） |
| `vae/diffusion_pytorch_model.safetensors` | 图像编解码器（VAE） |

---

## 四、Pipeline 加载

SD 1.5 的三种能力对应 diffusers 中不同的 Pipeline 类。以下是 `start_sd.py` 的完整加载逻辑：

```python
import torch
from diffusers import (
    StableDiffusionPipeline,           # 文生图
    StableDiffusionImg2ImgPipeline,    # 图生图
    StableDiffusionControlNetPipeline, # ControlNet 姿势控制
    ControlNetModel,
    UniPCMultistepScheduler,
)
from controlnet_aux import OpenposeDetector

SD_MODEL = "botp/stable-diffusion-v1-5"

# 1. 加载 ControlNet 模型（姿势控制）
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_openpose",
    torch_dtype=torch.float32
)

# 2. 文生图 Pipeline
pipe_txt2img = StableDiffusionPipeline.from_pretrained(
    SD_MODEL,
    torch_dtype=torch.float32
)
pipe_txt2img.scheduler = UniPCMultistepScheduler.from_config(
    pipe_txt2img.scheduler.config
)

# 3. ControlNet Pipeline（复用 SD 1.5 + ControlNet）
pipe_controlnet = StableDiffusionControlNetPipeline.from_pretrained(
    SD_MODEL,
    controlnet=controlnet,
    torch_dtype=torch.float32
)
pipe_controlnet.scheduler = UniPCMultistepScheduler.from_config(
    pipe_controlnet.scheduler.config
)

# 4. 图生图 Pipeline
pipe_img2img = StableDiffusionImg2ImgPipeline.from_pretrained(
    SD_MODEL,
    torch_dtype=torch.float32
)
pipe_img2img.scheduler = UniPCMultistepScheduler.from_config(
    pipe_img2img.scheduler.config
)

# 5. 姿势提取器（ControlNet 前置处理）
pose_estimator = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
```

> 💡 三个 Pipeline 共享同一个 SD 1.5 模型权重，不会重复占用内存。`UniPCMultistepScheduler` 是推荐的调度器，在较少步数下获得更好质量。

---

## 五、文生图（txt2img）

给一句提示词，从无到有生成一张图：

```python
prompt = "cute cartoon game character, 2d pixel art, game asset, isolated on white background, best quality"
negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality"

image = pipe_txt2img(
    prompt=prompt,
    negative_prompt=negative_prompt,
    num_inference_steps=20,
    width=512,
    height=512,
    generator=torch.Generator().manual_seed(42),
).images[0]

image.save("output_txt2img.png")
```

### 关键参数说明

| 参数 | 说明 | 推荐值 |
| :--- | :--- | :--- |
| `prompt` | 正向提示词（英文） | 用逗号分隔多个关键词 |
| `negative_prompt` | 反向提示词（不想出现的内容） | `low quality, blurry` 等 |
| `num_inference_steps` | 推理步数，越多越精细越慢 | 20-30 |
| `width / height` | 图片尺寸（必须是 8 的倍数） | **512×512**（SD 1.5 原生最佳） |
| `guidance_scale` | CFG 引导强度，值越高越严格遵循提示词 | 7-12 |
| `generator` | 随机种子生成器，固定种子结果可复现 | `torch.Generator().manual_seed(42)` |

> ⚠️ **SD 1.5 尺寸限制**：SD 1.5 是在 512×512 上训练的，超过 768×768 可能出现模糊、重复图案等问题。如需高清大图，建议使用 SDXL 模型。

---

## 六、图生图（img2img）

以一张已有图片为基底，按提示词做风格/内容变换：

```python
from PIL import Image

init_image = Image.open("input.png").convert("RGB").resize((512, 512))

image = pipe_img2img(
    prompt="pixel art style, 2d game sprite, transparent background",
    negative_prompt="monochrome, lowres, bad anatomy, worst quality",
    image=init_image,
    strength=0.6,            # 核心参数：0=几乎不动原图，1=完全重绘
    num_inference_steps=20,
    guidance_scale=7,
    generator=torch.Generator().manual_seed(42),
).images[0]

image.save("output_img2img.png")
```

### 图生图特有的关键参数

| 参数 | 说明 | 推荐值 |
| :--- | :--- | :--- |
| `strength` | **重绘强度**，控制原图保留程度 | **0.4-0.7** |
| 图片预处理 | 自动处理 RGBA/透明背景 → 白底 RGB | 内置 `preprocess_image()` |

### `strength` 参数详解

| strength 值 | 效果 | 适用场景 |
| :--- | :--- | :--- |
| 0.1-0.3 | 轻微修改，保留原图大部分内容 | 修复瑕疵、增强细节 |
| 0.4-0.6 | 中度修改，风格变化明显 | 风格转换（如手绘→像素） |
| 0.7-0.9 | 大幅修改，保留大致结构 | 角色变体、换服装 |
| 1.0 | 完全重新生成 | 从头设计 |

### ⚠️ 图生图常见问题

| 问题 | 原因 | 解决方案 |
| :--- | :--- | :--- |
| 图片发白/蒙白雾 | 原图有透明通道（RGBA），SD 不支持 | 代码已内置 `preprocess_image()` 自动铺白底 |
| 生成结果太像原图 | `strength` 太低 | 调到 0.6-0.8 |
| 生成结果完全变形 | `strength` 太高 + 提示词太抽象 | 降低 `strength`，用更具体的提示词 |
| 颜色失真 | 原图色彩空间不匹配 | 确保输入是 RGB 格式 |

---

## 七、ControlNet 姿势控制

ControlNet 可以精确控制生成角色的姿势。流程是：**上传图片 → 提取姿势 → 按姿势生成新角色**。

```python
# Step 1: 从参考图提取姿势
pose_image = pose_estimator(Image.open("person.jpg"))

# Step 2: 按姿势生成
image = pipe_controlnet(
    prompt="cute cartoon character, pixel art style",
    negative_prompt="monochrome, lowres",
    image=pose_image,          # 姿势图作为条件
    num_inference_steps=20,
    generator=torch.Generator().manual_seed(42),
).images[0]
```

### ControlNet 支持的控制类型

当前脚本启用了 **OpenPose**（姿势控制），其他可选类型：

| 类型 | 模型 | 用途 |
| :--- | :--- | :--- |
| **OpenPose** | `control_v11p_sd15_openpose` | 控制人体姿势 ✅ 已启用 |
| Canny | `control_v11p_sd15_canny` | 控制边缘结构 |
| Depth | `control_v11p_sd15_depth` | 控制深度/透视 |
| Lineart | `control_v11p_sd15_lineart` | 控制线稿草图 |

---

## 八、采样器（调度器）选择

Gradio 界面支持 4 种采样器（调度器），对应不同的速度与质量权衡：

| 采样器 | 速度 | 质量 | 适用场景 |
| :--- | :--- | :--- | :--- |
| **UniPC** | ⚡⚡⚡ 最快 | ⭐⭐⭐ | 日常使用，20 步即可 |
| **DDIM** | ⚡⚡ 中等 | ⭐⭐⭐⭐ | 经典稳定 |
| **PNDM** | ⚡⚡ 中等 | ⭐⭐⭐⭐ | diffusers 默认 |
| **DPM++ 2M Karras** | 🐢 最慢 | ⭐⭐⭐⭐⭐ | 追求极致质量，CPU 上非常慢 |

> 💡 在 CPU 上推荐 **UniPC**，速度/质量比最优。DPM++ 在 CPU 上可能需要 10 分钟以上。

---

## 九、Gradio 交互界面

### 启动界面

```python
from gradio_helper import make_demo

demo = make_demo(
    txt2img_pipeline=txt2img_wrapper,
    pipeline=controlnet_wrapper,
    img2img_pipeline=img2img_wrapper,
    pose_estimator=pose_estimator,
)
demo.queue().launch(
    server_name="0.0.0.0",
    server_port=7860,
    inbrowser=True
)
```

### 界面功能一览

| Tab | 功能 | 输入 | 输出 |
| :--- | :--- | :--- | :--- |
| **📝 文字生成图片** | 文生图 | 提示词 + 参数 | 单张/批量图片 |
| **🖼️ 姿势控制（ControlNet）** | 姿势控制 | 参考图 + 提示词 | 姿势一致的新图 |
| **🖼️ 图片转图片** | 图生图 | 参考图 + 提示词 | 风格变换的新图 |

### 高级参数（所有 Tab 共享）

| 参数 | 说明 | 选项 |
| :--- | :--- | :--- |
| **采样器** | 调度器选择 | UniPC / DDIM / PNDM / DPM++ |
| **CFG Scale** | 提示词引导强度 | 1-20（默认 7） |
| **图片比例** | 宽高比 | 1:1 / 16:9 / 9:16 / 4:3 等 |
| **基准尺寸** | 像素大小 | 512 / 640 / 768 / 1024 |
| **实际尺寸** | 自动计算显示 | 根据比例 × 基准 |

### 其他功能

- **🎲 随机种子按钮**：快速生成随机种子
- **📦 批量生成**：一次生成 1-8 张图片，种子递增
- **⏹️ 停止服务按钮**：一键关闭
- **自动保存**：生成图片保存到 `generated_outputs/` 目录

---

## 十、一键启动脚本

### `启动SD.bat`

```bat
@echo off
chcp 65001 >nul
title AI Asset Generator
cd /d G:\program\tests
echo.
echo  ================================================
echo    AI Asset Generator Starting...
echo  ================================================
echo.
echo  If stuck, press Ctrl+C then run again.
echo.
python -u start_sd.py
if %errorlevel% neq 0 (
    echo.
    echo  ================================================
    echo  Failed! Error code: %errorlevel%
    echo  ================================================
    echo.
    pause
)
```

### 使用流程

```
1. 双击 启动SD.bat
2. 等待约 30-60 秒（首次加载模型较慢）
3. 浏览器自动打开 http://localhost:7860
4. 选择功能 Tab → 输入提示词 → 点击生成
5. 使用完毕点击「⏹️ 停止服务」或 Ctrl+C
```

---

## 十一、OpenVINO 加速（可选）

当前实现使用 **PyTorch 原生推理**（`torch.float32`）。如需进一步加速，可将模型转换为 OpenVINO IR 格式：

```python
import openvino as ov
from pathlib import Path

core = ov.Core()

# 转换 UNet（仅需一次）
if not Path("unet.xml").exists():
    ov.convert_model(
        pipe_txt2img.pipe.unet,
        output="unet.xml",
        weights="unet.bin"
    )

# 编译到 CPU
unet_ov = core.compile_model("unet.xml", device="CPU")
```

### OpenVINO vs PyTorch 对比

| 维度 | PyTorch（默认） | OpenVINO IR |
| :--- | :--- | :--- |
| **部署难度** | 简单，直接加载 | 需转换 + 手动拼装推理链 |
| **CPU 速度** | 基准 | 快 1.5-3x（Intel CPU） |
| **质量** | 原始精度 | 无损（FP32） |
| **灵活性** | 高，支持 diffusers 全功能 | 低，需手动实现 Pipeline |

> 💡 建议：先用 PyTorch 跑通流程，确实需要加速时再考虑 OpenVINO 转换。当前 PyTorch 模式功能最完整。

---

## 十二、常见问题排查

### Q1: 模型下载慢/超时

```python
# 确认镜像配置
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
# 清理缓存重新下载
# 删除 G:\program\tests\hf_cache 下的对应模型目录
```

### Q2: 生成速度慢

| 优化手段 | 效果 |
| :--- | :--- |
| 切换到 UniPC 采样器 | 速度翻倍 |
| 减少步数（20→15） | 快 25% |
| 降低分辨率（512→384） | 快 44% |
| OpenVINO IR 转换 | 快 1.5-3x |

### Q3: 图生图结果发白

- 原因：原图有透明通道（RGBA/Alpha）
- 解决：代码已内置 `preprocess_image()` 自动处理，确保使用最新版本

### Q4: 端口 7860 被占用

```bash
# 查看占用进程
netstat -ano | findstr :7860
# 强制终止
taskkill /F /PID <进程ID>
```

或直接重启 `启动SD.bat`，脚本会自动清理残留进程。

### Q5: 显存/内存不足

- 使用 `torch.float32`（而非 float16）
- 避免同时加载多个大模型 Pipeline
- 关闭其他占用内存的程序

### Q6: 中文提示词不生效

SD 1.5 的 CLIP 文本编码器仅支持英文。解决方案：
- 使用翻译工具将中文转为英文
- 或使用支持中文的模型（如腾讯混元、阿里通义万相）

### Q7: DPM++ 采样器报错

确保 `diffusers` 版本 ≥ 0.25.0：
```bash
pip install diffusers>=0.25.0
```

---

## 十三、小游戏素材 Prompt 速查

### 角色类
```
# 卡通角色
cute cartoon character, 2d game sprite, pixel art, 
transparent background, high quality, detailed

# 像素角色
pixel art hero, 16-bit style, game character, 
isolated, retro game, classic
```

### 道具类
```
# 金币
golden coin, shiny, game item, pixel art, isolated

# 武器
magic sword, glowing blade, game weapon, 
pixel art style, detailed
```

### UI 元素
```
# 按钮
game ui button, metallic, shiny, pixel art

# 图标
game icon, vector style, clean, isolated
```

### 反向词（通用）
```
monochrome, lowres, bad anatomy, worst quality, 
low quality, blurry, faded, washed out
```

---

## 十四、小结

本部署方案的核心设计思路：

1. **PyTorch 原生加载**：利用 diffusers 生态丰富的 Pipeline，快速实现文生图、图生图、ControlNet 三大能力
2. **三 Pipeline 共享权重**：同一套 SD 1.5 UNet/VAE/TextEncoder 被三个 Pipeline 复用，节省内存
3. **UniPC 调度器**：在 CPU 上实现速度与质量的最佳平衡
4. **Gradio 统一界面**：所有功能 Tab 化，高级参数折叠隐藏，新手友好
5. **国内镜像加速**：`hf-mirror.com` 解决模型下载痛点
6. **OpenVINO 可选加速**：需要时可切换，不影响现有功能

**文件结构**：
```
G:\program\tests\
├── start_sd.py              # 主启动脚本
├── 启动SD.bat                # 一键启动
└── openvino_notebooks-latest\
    └── notebooks\
        └── controlnet-stable-diffusion\
            ├── gradio_helper.py   # Gradio 界面
            └── ...
```

祝你出图愉快 🎮
