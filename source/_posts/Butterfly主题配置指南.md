---
title: Butterfly 主题配置指南
date: 2026-08-20 17:22:18
tags: [Hexo, Butterfly, 主题, 美化]
categories: 折腾笔记
top_img: /images/cover-butterfly.webp
cover: /images/cover-butterfly.webp
---

## 一、什么是 Butterfly？

Butterfly 是 Hexo 生态中最受欢迎的现代主题之一，特点是：

- 卡片式设计，界面美观
- 自带夜间模式（暗黑模式）
- 支持页面加载动画
- 丰富的侧边栏组件（文章目录、最新文章、标签云等）
- 强大的自定义能力（背景图、字体、配色）

官方文档：[hexo-theme-butterfly 文档](https://butterfly.js.org/)

## 二、安装主题

### 1. 下载主题

在博客根目录执行：

```bash
git clone https://github.com/jerryc127/hexo-theme-butterfly.git themes/butterfly
```

> 如果想固定版本，可加 `--branch 版本号`。建议用 Git 方式安装，方便后续 `git pull` 升级。

### 2. 安装必要渲染器

Butterfly 的模板使用 `pug`、样式使用 `stylus`，必须安装对应渲染器：

```bash
npm install hexo-renderer-pug hexo-renderer-stylus --save
```

> 缺少这两个渲染器会导致构建报错或页面样式错乱。

### 3. 应用主题

修改根目录 `_config.yml`：

```yaml
theme: butterfly
```

保存后执行 `hexo clean && hexo g` 验证是否生效。

## 三、创建独立主题配置文件（强烈推荐）

在博客根目录新建 `_config.butterfly.yml`，将 `themes/butterfly/_config.yml` 的**全部内容复制进去**。

> **好处**：Hexo 会优先读取根目录的 `_config.butterfly.yml`，以后升级主题（`git pull`）时，你的自定义配置不会被覆盖。

升级主题流程：

```bash
cd themes/butterfly
git pull
```

只要不动根目录的 `_config.butterfly.yml`，配置就不会丢。

## 四、常用配置

### 1. 导航菜单

在 `_config.butterfly.yml` 中：

```yaml
menu:
  首页: / || fas fa-home
  归档: /archives/ || fas fa-archive
  分类: /categories/ || fas fa-folder-open
  标签: /tags/ || fas fa-tags
  留言板: /messageboard/ || fas fa-comment
  关于: /about/ || fas fa-heart
```

> 图标来自 [Font Awesome](https://fontawesome.com/icons)。格式为 `名称: 路径 || 图标类名`。

### 2. 页面顶部背景图

```yaml
# 全局默认
default_top_img: /images/default-bg.jpg

# 各页面独立
index_img: /images/home-bg.jpg
archive_img: /images/archive-bg.jpg
category_img: /images/category-bg.jpg
tag_img: /images/tag-bg.jpg
```

> 图片放在 `source/images/` 目录下（需自行创建），构建后会拷贝到 `public/images/`。

### 3. 开启本地搜索

**安装插件**：

```bash
npm install hexo-generator-searchdb --save
```

**修改根目录 `_config.yml`**：

```yaml
search:
  path: search.xml
  field: post
  content: true
```

**修改 `_config.butterfly.yml`**：

```yaml
search:
  use: local_search
  placeholder: 搜索...
```

### 4. 切换夜间模式

```yaml
# 默认开启暗黑模式
darkmode: true
```

> 也可设置为 `false` 由用户手动切换，或配置 `start_time` / `end_time` 按时间段自动切换。

## 五、创建页面

Butterfly 需要为菜单项创建对应的页面文件：

```bash
hexo new page categories
hexo new page tags
hexo new page about
hexo new page messageboard
```

然后编辑对应的 `index.md` 文件，添加 `type` 字段：

```markdown
---
title: 分类
date: 2026-08-20 17:22:18
type: "categories"
---
```

各页面 `type` 对应关系：

| 页面 | type |
| :--- | :--- |
| 分类 | `categories` |
| 标签 | `tags` |
| 关于 | （无需 type，普通页面） |
| 留言板 | （无需 type，普通页面） |

## 六、语言配置

确保根目录 `_config.yml`：

```yaml
language: zh-CN
```

各页面 `title` 建议统一使用中文，与菜单项保持一致，避免导航显示错位。

## 七、常用命令速查

```bash
# 本地预览
hexo clean && hexo g && hexo s

# 推送部署
git add . && git commit -m "更新配置" && git push
```

## 八、配置检查清单

- [ ] 已安装 `hexo-renderer-pug` 和 `hexo-renderer-stylus`
- [ ] 根目录 `_config.yml` 中 `theme: butterfly`
- [ ] 已创建 `_config.butterfly.yml` 并填写自定义项
- [ ] 菜单中的页面均已 `hexo new page` 创建并加好 `type`
- [ ] 背景图已放入 `source/images/`
- [ ] 本地 `hexo g && hexo s` 预览无误后再推送
