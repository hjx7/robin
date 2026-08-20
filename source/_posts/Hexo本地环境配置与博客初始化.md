---
title: Hexo 本地环境配置与博客初始化
date: 2026-08-20 17:22:18
tags: [Hexo, 教程, 环境配置]
categories: 折腾笔记
top_img: /images/cover-hexo.webp
cover: /images/cover-hexo.webp
---

## 一、什么是 Hexo？

Hexo 是一个快速、简洁且高效的**静态博客框架**。你只需要用 Markdown 写文章，Hexo 就能在几秒内把纯文本渲染成完整的静态网页（HTML/CSS/JS）。

它的核心优势：

- **极速生成**：基于 Node.js，几百篇文章也能秒级构建
- **零数据库**：所有内容都是静态文件，部署到任何静态托管平台都行
- **主题丰富**：社区有大量成熟主题（如 Butterfly、NexT、Fluid）
- **插件生态**：搜索、评论、图床、SEO 等都有现成方案

## 二、环境准备

> 建议安装顺序：Node.js → Git → Hexo。三者缺一不可。

### 1. 安装 Node.js

访问 [Node.js 官网](https://nodejs.org/) 下载 **LTS（长期支持）** 版本并安装。

安装完成后在命令行验证：

```bash
node -v
npm -v
```

> 建议 Node.js 版本 ≥ 18（部分新版主题/插件要求更高）。可用 `nvm` 管理多版本。

### 2. 安装 Git

访问 [Git 官网](https://git-scm.com/) 下载安装包安装。

验证：

```bash
git --version
```

> Windows 用户建议安装时勾选「Use Git from the command line」，方便在 PowerShell/CMD 直接使用 `git`。

### 3. 安装 Hexo

```bash
npm install -g hexo-cli
```

验证安装成功：

```bash
hexo -v
```

## 三、初始化博客项目

```bash
# 创建一个博客文件夹（名字可自定义，这里叫 robin）
hexo init robin
cd robin
npm install
```

初始化完成后，建议立刻初始化 Git 仓库并做首次提交：

```bash
git init
git add .
git commit -m "init: hexo blog"
```

## 四、目录结构说明

```
robin/
├── _config.yml          # 站点核心配置文件（全局）
├── _config.landscape.yml # 默认主题的独立配置文件（如有）
├── package.json          # 项目依赖管理
├── .gitignore            # Git 忽略文件配置
├── source/               # 文章源文件（核心工作区）
│   └── _posts/           # 文章存放目录（写文章的地方）
│       └── hello-world.md
│   └── about/            # 独立页面（about、tags 等）
├── themes/               # 主题文件夹
│   └── landscape/        # 默认主题
├── scaffolds/            # 文章模板（new 命令的母版）
└── public/               # 构建后生成的静态文件（被 .gitignore 忽略）
```

> `public/` 是 `hexo g` 生成的产物，一般**不纳入 Git 版本管理**，由部署平台自动构建。

## 五、常用命令

| 命令 | 作用 |
| :--- | :--- |
| `hexo new "文章标题"` | 创建新文章（默认在 `source/_posts/`） |
| `hexo new page "页面名"` | 创建独立页面（如 about、tags） |
| `hexo clean` | 清除缓存与旧 `public/` |
| `hexo g` (generate) | 生成静态文件到 `public/` |
| `hexo s` (server) | 启动本地预览（http://localhost:4000） |
| `hexo d` (deploy) | 部署（需配置 `_config.yml` 的 deploy） |
| `npm install --save 插件名` | 安装并保存依赖插件 |

本地预览建议组合：

```bash
hexo clean && hexo g && hexo s
```

## 六、核心配置 `_config.yml`

```yaml
# 站点信息
title: 你的博客名称
subtitle: 副标题（可选）
description: 站点描述（SEO 用）
author: 你的名字
language: zh-CN

# URL 设置（部署到 Netlify 等平台时修改）
url: https://你的域名
root: /
```

> ⚠️ 若博客部署在子路径（如 `https://域名/robin/`），`root` 需改为 `/robin/`，否则页面样式会加载失败（白屏）。

## 七、写一篇测试文章

```bash
hexo new "我的第一篇正式文章"
```

编辑生成的 `source/_posts/我的第一篇正式文章.md`，Hexo 会自动在文件顶部加上 Front Matter：

```markdown
---
title: 我的第一篇正式文章
date: 2026-08-20 17:22:18
tags: [生活, 随笔]
categories: 随笔
---

## 正文标题

在这里用 Markdown 写作即可。
```

保存后执行 `hexo g && hexo s`，访问 http://localhost:4000 即可看到效果。
