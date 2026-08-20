---
title: Gitee 仓库自动镜像到 GitHub
date: 2026-08-20 17:22:18
tags: [Gitee, GitHub, 镜像同步, 部署]
categories: 折腾笔记
top_img: /images/cover-gitee.webp
cover: /images/cover-gitee.webp
---

## 一、为什么要做镜像？

很多托管平台（如 **Netlify、Vercel、Cloudflare Pages**）原生支持从 GitHub 拉取代码，但不一定支持 Gitee。

通过「Gitee → GitHub」镜像同步，你可以：

- 在 **Gitee** 上管理代码（国内访问快、推送稳定）
- 自动同步到 **GitHub**，享受海外平台的部署生态
- 两条腿走路，互不依赖

> 反向场景（GitHub → Gitee）同样常见，但本文聚焦 Gitee 主动推 GitHub 的单向镜像，正好满足 Netlify 部署需求。

## 二、操作步骤

### 1. 在 GitHub 创建一个空仓库

- 登录 [GitHub](https://github.com)，点击右上角 `+` → `New repository`
- **仓库名**：与 Gitee 仓库名一致（如 `robin`）
- **⚠️ 不要勾选** "Initialize this repository with a README"
- 点击 `Create repository`

> 保持空仓库，避免和 Gitee 的提交历史冲突导致同步失败。

### 2. 在 Gitee 配置镜像同步

- 进入 Gitee 仓库 → 点击 **「管理」**
- 左侧菜单 → **「仓库镜像管理」**
- 点击 **「添加镜像」**
- 目标地址填写：`https://github.com/你的GitHub用户名/你的仓库名.git`
- 授权 Gitee 访问你的 GitHub 账号

### 3. 获取 GitHub 私人令牌（Personal Access Token）

- GitHub → 头像 → **Settings** → **Developer settings** → **Personal access tokens**
- 选择 **Tokens (classic)** → **Generate new token (classic)**
- **Note**：填写 `Gitee-Mirror`
- **Expiration**：建议选 `90 days` 或 `No expiration`
- **Select scopes**：**只勾选 `repo`**（包含私有仓库读写权限）
- 点击 **Generate token**，**立即复制保存**（只显示一次！）

> 安全提示：Token 等同于你的 GitHub 密码，请勿提交到代码或泄露给他人。若怀疑泄露，立即在 GitHub 撤销。

### 4. 在 Gitee 镜像配置中填入 Token

- 用户名：GitHub 用户名
- 密码：粘贴刚才复制的私人令牌（不是 GitHub 登录密码）
- 保存配置

## 三、同步机制说明

| 项目 | 说明 |
| :--- | :--- |
| **触发方式** | 推送代码到 Gitee 后自动触发 |
| **同步间隔** | 最短 5 分钟 |
| **同步方向** | 仅 Gitee → GitHub（单向） |
| **超时时间** | 单次同步超过 30 分钟会失败 |
| **历史处理** | 强制推送，以 Gitee 为准覆盖 GitHub |

> 首次同步可能需要手动点一次「立即同步」来初始化，之后就是自动增量。

## 四、常用镜像排查

| 问题 | 解决方法 |
| :--- | :--- |
| Token 过期 | 重新生成并更新 Gitee 镜像配置 |
| 同步失败（403/401） | 检查 Token 是否有 `repo` 权限，或 GitHub 已开启两步验证必须用 Token |
| 仓库找不到 | 确认 GitHub 仓库名与 Gitee 仓库名一致，且目标地址拼写正确 |
| 同步一直 pending | 等待 5 分钟同步间隔，或手动点「立即同步」 |
| 私有仓库不同步 | 确认 Token 的 `repo` 权限覆盖私有库，且 Gitee 仓库也设为私有/公开一致 |

## 五、验证同步是否成功

1. 在 Gitee 推送一次代码
2. 等 5 分钟（或手动触发同步）
3. 打开 GitHub 仓库页面，确认最新提交已出现
4. 后续 Netlify 部署即基于 GitHub 的最新代码
