---
title: Netlify 对接 GitHub 部署 Hexo 博客
date: 2026-08-20 17:22:18
tags: [Netlify, 部署, Hexo, 静态托管]
categories: 折腾笔记
top_img: /images/cover-netlify.webp
cover: /images/cover-netlify.webp
---

## 一、什么是 Netlify？

Netlify 是一个现代化网站托管平台，特别适合**静态博客/站点**。它提供：

- **免费 `项目名.netlify.app` 域名**（无需备案，海外直接访问）
- **自动构建部署**：推送代码即自动上线，无需手动上传
- **全球 CDN 加速**
- **免费 SSL 证书**（自动 HTTPS）
- **预览部署**：每次 PR 都生成独立预览链接

> 同类平台还有 Vercel、Cloudflare Pages，流程大同小异。

## 二、准备工作

1. 确保 Hexo 博客源码已推送到 GitHub（参考《Gitee 仓库自动镜像到 GitHub》）
2. 注册 [Netlify](https://app.netlify.com) 账号（可用 GitHub 账号直接授权登录）

## 三、部署步骤

### 1. 登录 Netlify

访问 [app.netlify.com](https://app.netlify.com) 登录。

### 2. 创建新站点

点击 **「Add new site」** → **「Import an existing project」**。

### 3. 连接 GitHub

选择 **「Deploy with GitHub」**，授权 Netlify 访问你的 GitHub 仓库（注意勾选对应仓库的读取权限）。

### 4. 选择仓库

从列表中选择你的博客仓库（如 `robin`）。

### 5. 配置构建选项

| 配置项 | 填写内容 |
| :--- | :--- |
| **Branch to deploy** | `master`（或 `main`） |
| **Build command** | `npm run build` |
| **Publish directory** | `public` |

> 如果 Netlify 自动识别为 Hexo，则上方配置会自动填好，无需手动修改。
>
> 若你的 `package.json` 里 `build` 脚本不是 `hexo g`，请改为对应命令（Hexo 默认 `build` 即 `hexo generate`）。

### 6. 点击 **「Deploy site」**

等待 1-3 分钟，部署完成后会分配一个免费域名：`你的项目名.netlify.app`

## 四、后续更新流程

1. 在本地写文章 → `hexo new "文章名"`
2. 编辑文章内容
3. 推送代码到 Gitee：
   ```bash
   git add .
   git commit -m "发布新文章"
   git push
   ```
4. Gitee 自动同步到 GitHub（约 5 分钟内）
5. Netlify 检测到变更，自动重新构建部署（约 2-5 分钟）
6. 刷新博客页面，更新生效

> 想看实时进度？进 Netlify 后台 → **Deploys** 可查看每次构建日志与状态。

## 五、进阶：绑定自定义域名（可选）

1. Netlify 站点 → **Domain settings** → **Add custom domain**
2. 输入你的域名（如 `blog.example.com`）
3. 按提示到域名服务商处添加 **CNAME** 记录指向 `你的项目名.netlify.app`
4. Netlify 会自动签发 SSL 证书，开启 HTTPS

## 六、常见问题

| 问题 | 解决方法 |
| :--- | :--- |
| 部署后页面空白 | 检查 `_config.yml` 中 `root: /` 是否正确；若部署在子路径需对应修改 |
| 主题样式不生效 | 确认已安装主题所需的渲染器（如 `pug`、`stylus`）并已 `npm install` |
| 构建失败 | 查看 Netlify 部署日志，检查 `package.json` 是否完整、依赖是否声明 |
| 访问速度慢 | Netlify 免费域名在国内访问可能一般，可绑定自定义域名或用国内 CDN |
| 构建超时 | 精简依赖、清理无用插件，或升级 Netlify 套餐 |
