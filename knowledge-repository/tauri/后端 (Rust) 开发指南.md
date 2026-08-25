# 后端 (Rust) 开发指南

本文档深入介绍 Tauri 后端的 Rust 开发，包括项目结构、命令系统、插件开发、异步处理、文件系统、数据库集成等内容。

---

## 目录

1. [Rust 项目结构](#rust-项目结构)
2. [Cargo 配置](#cargo-配置)
3. [命令系统详解](#命令系统详解)
4. [异步编程](#异步编程)
5. [状态管理](#状态管理)
6. [错误处理](#错误处理)
7. [日志系统](#日志系统)
8. [文件系统操作](#文件系统操作)
9. [数据库集成 (SQLite)](#数据库集成-sqlite)
10. [HTTP 请求](#http-请求)
11. [后台任务与定时器](#后台任务与定时器)
12. [自定义插件开发](#自定义插件开发)
13. [单元测试](#单元测试)

---

## Rust 项目结构

推荐的 `src-tauri/src/` 目录组织方式：

```
src-tauri/src/
├── main.rs                 # 入口文件（通常无需修改）
├── lib.rs                  # 主库：Tauri Builder 配置
│
├── commands/               # 👉 前端可调用的命令
│   ├── mod.rs              # 模块导出 + 通用命令
│   ├── file_ops.rs         # 文件操作相关命令
│   ├── data_ops.rs         # 数据处理相关命令
│   └── settings.rs         # 设置相关命令
│
├── services/               # 👉 业务逻辑服务层（命令调用的内部实现）
│   ├── mod.rs              # 模块导出
│   ├── file_service.rs     # 文件处理业务逻辑
│   ├── data_service.rs     # 数据处理业务逻辑
│   └── search_service.rs   # 搜索服务（可能包含复杂逻辑）
│
├── models/                 # 👉 数据结构定义（DTO/Entity）
│   ├── mod.rs
│   ├── app_config.rs       # 应用配置结构体
│   ├── file_record.rs      # 文件记录模型
│   └── errors.rs           # 错误类型定义
│
├── utils/                  # 👉 工具函数
│   ├── mod.rs
│   ├── path.rs             # 路径处理工具
│   ├── time.rs             # 时间处理工具
│   └── crypto.rs           # 加密/哈希工具
│
├── plugins/                # 👉 自定义 Tauri 插件（可选）
│   └── mycubby_plugin/
│       ├── mod.rs
│       └── commands.rs
│
├── db/                     # 👉 数据库相关（可选）
│   ├── mod.rs
│   ├── connection.rs       # 连接管理
│   ├── migrations.rs       # 迁移脚本
│   └── schema.rs           # 表结构
│
└── config.rs               # 全局配置常量
```

### 建议的模块依赖方向

```
commands  ──调用──►  services  ──调用──►  models
                         │                   ▲
                         └──使用──►  utils ──┘
                                       │
                                       └──►  db
```

> 💡 原则：`commands` 只做参数校验和调用转发，不包含复杂业务逻辑；复杂逻辑放在 `services` 中，便于单元测试和复用。

---

## Cargo 配置

### 完整的 Cargo.toml 示例

```toml
[package]
name = "mycubby"
version = "0.1.0"
description = "MyCubby - 一个强大的 Tauri 桌面应用"
authors = ["MyCubby Team <team@mycubby.com>"]
edition = "2021"
rust-version = "1.74"
license = "MIT"

[lib]
name = "mycubby_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2.0", features = [] }

# ===== 核心依赖 =====
[dependencies]
tauri = { version = "2.0", features = ["tray-icon", "image-png"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# ===== Tauri 官方插件 =====
tauri-plugin-dialog = "2.0"
tauri-plugin-notification = "2.0"
tauri-plugin-shell = "2.0"
tauri-plugin-fs = "2.0"
tauri-plugin-os = "2.0"
tauri-plugin-path = "2.0"
tauri-plugin-store = "2.0"
tauri-plugin-process = "2.0"
tauri-plugin-clipboard-manager = "2.0"
tauri-plugin-global-shortcut = "2.0"
tauri-plugin-log = { version = "2.0", features = ["colored"] }
tauri-plugin-sql = "2.0"
tauri-plugin-updater = "2.0"
tauri-plugin-single-instance = "2.0"
tauri-plugin-autostart = "2.0"
tauri-plugin-http = "2.0"
tauri-plugin-positioner = "2.0"
tauri-plugin-deep-link = "2.0"

# ===== 异步运行时 =====
tokio = { version = "1", features = ["full"] }
futures = "0.3"

# ===== 错误处理 =====
thiserror = "1.0"
anyhow = "1.0"

# ===== 时间处理 =====
chrono = { version = "0.4", features = ["serde"] }

# ===== UUID =====
uuid = { version = "1.0", features = ["v4", "serde"] }

# ===== 加密哈希 =====
sha2 = "0.10"
md-5 = "0.10"
base64 = "0.22"

# ===== 数据处理 =====
csv = "1.3"
regex = "1.10"
walkdir = "2.5"

# ===== 日志 =====
log = "0.4"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

# ===== 配置文件解析 =====
toml = "0.8"

# ===== 开发依赖 =====
[dev-dependencies]
tempfile = "3.10"
assert_cmd = "2.0"
predicates = "3.1"

# ===== Profile 配置 =====
[profile.dev]
opt-level = 1           # 略微优化，编译速度稍慢但运行更快
debug = 1               # 精简调试信息（加快编译）
split-debuginfo = "unpacked"

[profile.release]
panic = "abort"         # 发生 panic 直接终止，无需展开栈信息
codegen-units = 1       # 单代码单元：编译慢但运行更快、体积更小
lto = "fat"             # 链接时优化：编译慢但性能高、体积小
opt-level = "s"         # 优化二进制体积（"z" 更小但可能牺牲性能）
strip = "symbols"       # 去除符号表：减小体积
debug = false           # 不含调试信息
rpath = false           # 禁用 rpath

# 针对特定依赖的优化（可选）
[profile.release.package."*"]
opt-level = 3           # 所有依赖都用最高级优化
```

> 💡 体积与编译速度权衡：
> - **开发期**：使用默认 `dev` profile，关注编译速度
> - **发布期**：使用 `release` profile，关注性能和体积

---

## 命令系统详解

### 命令参数类型支持

`#[tauri::command]` 支持多种参数类型：

```rust
use serde::{Deserialize, Serialize};
use tauri::{State, AppHandle, Manager, WebviewWindow, Emitter};
use std::path::PathBuf;
use std::sync::Mutex;

// ===== 普通类型参数 =====
#[tauri::command]
pub fn basic_types(
    name: String,      // 字符串
    count: i32,        // 整数
    rate: f64,         // 浮点数
    enabled: bool,     // 布尔
    ids: Vec<u64>,     // 数组
    meta: serde_json::Value,  // 任意 JSON
) -> String {
    format!("{}: count={}, rate={}, enabled={}, ids={:?}", name, count, rate, enabled, ids)
}

// ===== 结构体参数 =====
#[derive(Deserialize)]
pub struct SearchQuery {
    pub keyword: String,
    pub page: usize,
    pub page_size: usize,
    #[serde(default)]
    pub filters: Option<Vec<String>>,
}

#[derive(Serialize)]
pub struct SearchResult<T> {
    pub items: Vec<T>,
    pub total: usize,
    pub page: usize,
    pub page_count: usize,
}

#[derive(Serialize, Clone)]
pub struct FileItem {
    pub id: String,
    pub name: String,
    pub path: String,
    pub size: u64,
}

#[tauri::command]
pub fn search_files(query: SearchQuery, state: State<AppState>) -> SearchResult<FileItem> {
    // 业务逻辑
    let db = state.db.lock().unwrap();
    let (items, total) = db.search(&query.keyword, query.page, query.page_size);
    SearchResult {
        page_count: (total as f64 / query.page_size as f64).ceil() as usize,
        page: query.page,
        total,
        items,
    }
}

// ===== 特殊注入参数（不来自前端） =====
pub struct AppState {
    pub counter: Mutex<i32>,
    pub db: Mutex<Database>,
    pub app_dir: PathBuf,
}

#[tauri::command]
pub fn use_special_params(
    // 应用状态：通过 .manage() 注入
    state: State<'_, AppState>,
    // 调用命令的当前窗口
    window: WebviewWindow,
    // 全局 AppHandle
    app: AppHandle,
) -> Result<String, String> {
    // 自增计数器
    let mut cnt = state.counter.lock().map_err(|e| e.to_string())?;
    *cnt += 1;

    // 窗口操作
    println!("当前窗口: {}", window.label());

    // 发送事件到前端
    app.emit("counter-changed", *cnt).map_err(|e| e.to_string())?;

    Ok(format!("当前计数: {}", cnt))
}

// ===== Result 返回类型 =====
#[tauri::command]
pub fn divide(a: i32, b: i32) -> Result<f64, CommandError> {
    if b == 0 {
        return Err(CommandError::DivideByZero);
    }
    Ok(a as f64 / b as f64)
}

// 自定义错误类型
#[derive(thiserror::Error, Debug)]
pub enum CommandError {
    #[error("除数不能为 0")]
    DivideByZero,
    #[error("文件不存在: {0}")]
    FileNotFound(String),
    #[error("数据库错误: {0}")]
    Database(#[from] sqlite::Error),
    #[error("IO 错误: {0}")]
    Io(#[from] std::io::Error),
}

// 将自定义错误转换为 Tauri 可传输的类型
impl serde::Serialize for CommandError {
    fn serialize<S: serde::Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        s.serialize_str(&self.to_string())
    }
}
```

### 异步命令

```rust
use tokio::time::{sleep, Duration};
use tokio::process::Command;
use reqwest;

// 异步 I/O
#[tauri::command]
pub async fn download_file(url: String, save_path: String) -> Result<u64, String> {
    // 发送 HTTP 请求（异步）
    let resp = reqwest::get(&url)
        .await
        .map_err(|e| format!("下载失败: {}", e))?;

    if !resp.status().is_success() {
        return Err(format!("HTTP 错误: {}", resp.status()));
    }

    let bytes = resp.bytes().await.map_err(|e| e.to_string())?;
    let len = bytes.len() as u64;

    // 异步写入文件
    tokio::fs::write(&save_path, bytes)
        .await
        .map_err(|e| format!("保存失败: {}", e))?;

    Ok(len)
}

// 进度汇报
#[tauri::command]
pub async fn batch_process(
    app: AppHandle,
    files: Vec<String>,
) -> Result<usize, String> {
    let total = files.len();
    let mut success = 0;

    for (i, file) in files.iter().enumerate() {
        // 模拟处理
        sleep(Duration::from_millis(100)).await;

        // 发送进度事件
        app.emit(
            "batch-progress",
            serde_json::json!({
                "current": i + 1,
                "total": total,
                "file": file,
                "percent": ((i + 1) as f64 / total as f64 * 100.0) as u32,
            }),
        )
        .map_err(|e| e.to_string())?;

        // 处理逻辑
        if process_one(file).is_ok() {
            success += 1;
        }
    }

    Ok(success)
}
```

### 注册命令

```rust
// lib.rs
pub fn run() {
    tauri::Builder::default()
        // 注入共享状态
        .manage(AppState {
            counter: Mutex::new(0),
            db: Mutex::new(Database::open()),
            app_dir: std::env::current_dir().unwrap(),
        })
        // 注册命令（可以拆分到不同模块）
        .invoke_handler(tauri::generate_handler![
            // commands/mod.rs
            commands::basic_types,
            commands::search_files,
            commands::use_special_params,
            commands::divide,
            // commands/file_ops.rs
            commands::file_ops::read_file_bytes,
            commands::file_ops::scan_directory,
            commands::file_ops::zip_files,
            // commands/data_ops.rs
            commands::data_ops::import_csv,
            commands::data_ops::export_json,
            // 异步命令
            commands::download_file,
            commands::batch_process,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 异步编程

Tauri 2.x 内置 `tokio` 异步运行时。

### 并发处理多个任务

```rust
use tokio::task::JoinSet;
use futures::stream::{FuturesUnordered, StreamExt};

#[tauri::command]
pub async fn parallel_download(urls: Vec<String>) -> Result<Vec<(String, u64)>, String> {
    let mut handles = FuturesUnordered::new();

    for url in urls {
        handles.push(async move {
            let size = download_one(&url).await?;
            Ok::<(String, u64), String>((url, size))
        });
    }

    let mut results = Vec::new();
    while let Some(result) = handles.next().await {
        match result {
            Ok(item) => results.push(item),
            Err(e) => eprintln!("下载失败: {}", e),
        }
    }

    Ok(results)
}
```

### 阻塞操作处理

不要在异步命令中执行阻塞操作（如 CPU 密集型计算、同步 I/O）。使用 `spawn_blocking`：

```rust
use tokio::task;

#[tauri::command]
pub async fn compute_hash(file_path: String) -> Result<String, String> {
    // 将 CPU 密集型/阻塞操作移动到专门的阻塞线程池
    let result = task::spawn_blocking(move || -> Result<String, String> {
        use sha2::{Sha256, Digest};
        use std::fs::File;
        use std::io::{BufReader, Read};

        let file = File::open(&file_path).map_err(|e| e.to_string())?;
        let mut reader = BufReader::new(file);
        let mut hasher = Sha256::new();
        let mut buffer = [0u8; 8192];

        loop {
            let n = reader.read(&mut buffer).map_err(|e| e.to_string())?;
            if n == 0 { break; }
            hasher.update(&buffer[..n]);
        }

        Ok(hex::encode(hasher.finalize()))
    })
    .await
    .map_err(|e| format!("任务失败: {}", e))?;

    result
}
```

---

## 状态管理

### 定义状态结构

```rust
// src/state.rs
use std::sync::{Arc, RwLock};
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct AppConfig {
    pub theme: String,
    pub language: String,
    pub auto_update: bool,
    pub start_minimized: bool,
    pub default_download_dir: Option<String>,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            theme: "light".into(),
            language: "zh-CN".into(),
            auto_update: true,
            start_minimized: false,
            default_download_dir: None,
        }
    }
}

// 全局可变状态
pub struct ConfigState {
    pub config: RwLock<AppConfig>,
}

impl ConfigState {
    pub fn load() -> Self {
        let config = Self::read_from_disk().unwrap_or_default();
        Self { config: RwLock::new(config) }
    }

    fn read_from_disk() -> Option<AppConfig> {
        let path = Self::config_path().ok()?;
        let content = std::fs::read_to_string(path).ok()?;
        serde_json::from_str(&content).ok()
    }

    pub fn save(&self) -> anyhow::Result<()> {
        let config = self.config.read().unwrap().clone();
        let path = Self::config_path()?;
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::write(path, serde_json::to_string_pretty(&config)?)?;
        Ok(())
    }

    fn config_path() -> anyhow::Result<std::path::PathBuf> {
        let dir = tauri::api::path::app_config_dir(
            &tauri::generate_context!().config()
        ).ok_or_else(|| anyhow::anyhow!("无法获取配置目录"))?;
        Ok(dir.join("config.json"))
    }
}

// 缓存状态（经常修改，放在内存）
pub struct CacheState {
    pub recent_files: RwLock<Vec<String>>,
    pub last_index_time: RwLock<Option<chrono::DateTime<chrono::Local>>>,
}

impl Default for CacheState {
    fn default() -> Self {
        Self {
            recent_files: RwLock::new(Vec::new()),
            last_index_time: RwLock::new(None),
        }
    }
}
```

### 在命令中使用状态

```rust
// commands/settings.rs
use tauri::State;
use crate::state::{ConfigState, CacheState, AppConfig};

#[tauri::command]
pub fn get_config(state: State<ConfigState>) -> AppConfig {
    state.config.read().unwrap().clone()
}

#[tauri::command]
pub fn update_config(state: State<ConfigState>, new_config: AppConfig) -> Result<(), String> {
    *state.config.write().unwrap() = new_config;
    state.save().map_err(|e| e.to_string())
}

#[tauri::command]
pub fn patch_config(state: State<ConfigState>, patch: serde_json::Value) -> Result<AppConfig, String> {
    let mut config = state.config.write().unwrap();

    // 简单的部分更新：将 patch 合并到当前配置
    let merged = merge_json(
        serde_json::to_value(config.clone()).map_err(|e| e.to_string())?,
        patch,
    );

    *config = serde_json::from_value(merged).map_err(|e| e.to_string())?;
    drop(config);  // 提前释放锁，避免 save() 时死锁

    state.save().map_err(|e| e.to_string())?;
    Ok(state.config.read().unwrap().clone())
}

fn merge_json(a: serde_json::Value, b: serde_json::Value) -> serde_json::Value {
    match (a, b) {
        (serde_json::Value::Object(mut a), serde_json::Value::Object(b)) => {
            for (k, v) in b {
                let val = match a.remove(&k) {
                    Some(existing) => merge_json(existing, v),
                    None => v,
                };
                a.insert(k, val);
            }
            serde_json::Value::Object(a)
        }
        (_, b) => b,
    }
}
```

### 注册状态

```rust
// lib.rs
use crate::state::{ConfigState, CacheState};

pub fn run() {
    tauri::Builder::default()
        .manage(ConfigState::load())
        .manage(CacheState::default())
        // ...
        .run(tauri::generate_context!())
        .expect("error");
}
```

---

## 错误处理

### 统一错误类型

```rust
// src/models/errors.rs
use thiserror::Error;
use serde::Serialize;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("IO 错误: {0}")]
    Io(#[from] std::io::Error),

    #[error("JSON 解析错误: {0}")]
    Json(#[from] serde_json::Error),

    #[error("路径无效: {0}")]
    InvalidPath(String),

    #[error("权限不足: {0}")]
    PermissionDenied(String),

    #[error("未找到: {0}")]
    NotFound(String),

    #[error("参数错误: {0}")]
    InvalidArgument(String),

    #[error("配置错误: {0}")]
    Config(String),

    #[error("数据库错误: {0}")]
    Database(#[from] rusqlite::Error),

    #[error("其他错误: {0}")]
    Other(String),
}

impl From<anyhow::Error> for AppError {
    fn from(value: anyhow::Error) -> Self {
        AppError::Other(value.to_string())
    }
}

impl From<&str> for AppError {
    fn from(value: &str) -> Self {
        AppError::Other(value.to_string())
    }
}

// 让 Tauri 能通过 IPC 返回这个错误
impl Serialize for AppError {
    fn serialize<S: serde::Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        use serde::ser::SerializeStruct;
        let mut state = s.serialize_struct("AppError", 2)?;
        state.serialize_field("code", &self.error_code())?;
        state.serialize_field("message", &self.to_string())?;
        state.end()
    }
}

impl AppError {
    pub fn error_code(&self) -> i32 {
        match self {
            AppError::Io(_) => 1001,
            AppError::Json(_) => 1002,
            AppError::InvalidPath(_) => 2001,
            AppError::PermissionDenied(_) => 2002,
            AppError::NotFound(_) => 2003,
            AppError::InvalidArgument(_) => 3001,
            AppError::Config(_) => 4001,
            AppError::Database(_) => 5001,
            AppError::Other(_) => 9999,
        }
    }
}

// 命令返回类型别名
pub type CommandResult<T> = Result<T, AppError>;
```

### 在命令中使用

```rust
use crate::models::errors::{AppError, CommandResult};

#[tauri::command]
pub fn read_config_file(path: String) -> CommandResult<serde_json::Value> {
    use std::path::Path;

    // 参数校验
    if path.is_empty() {
        return Err(AppError::InvalidArgument("路径不能为空".into()));
    }

    let p = Path::new(&path);
    if !p.exists() {
        return Err(AppError::NotFound(format!("文件不存在: {}", path)));
    }
    if !p.is_file() {
        return Err(AppError::InvalidPath(format!("不是文件: {}", path)));
    }

    // 读取+解析，自动转换错误类型
    let content = std::fs::read_to_string(p)?;
    let json: serde_json::Value = serde_json::from_str(&content)?;

    Ok(json)
}
```

前端可获取结构化错误：

```typescript
try {
  await invoke('read_config_file', { path: '' })
} catch (err: any) {
  console.log('错误代码:', err.code)    // 3001
  console.log('错误信息:', err.message) // 参数错误: 路径不能为空
}
```

---

## 日志系统

### 使用 tauri-plugin-log

```toml
# Cargo.toml
tauri-plugin-log = { version = "2.0", features = ["colored", "file"] }
log = "0.4"
```

```rust
// lib.rs
pub fn run() {
    tauri::Builder::default()
        .plugin(
            tauri_plugin_log::Builder::default()
                .targets([
                    // 输出到标准输出（控制台）
                    tauri_plugin_log::LogTarget::Stdout,
                    // 输出到 WebView 控制台（前端 DevTools 可见）
                    tauri_plugin_log::LogTarget::Webview,
                    // 输出到文件
                    tauri_plugin_log::LogTarget::LogDir,
                ])
                .level(log::LevelFilter::Info)
                // 特定模块设置更详细的日志级别
                .level_for("mycubby", log::LevelFilter::Debug)
                .level_for("tauri", log::LevelFilter::Warn)
                // 日志文件滚动策略
                .rotation_strategy(tauri_plugin_log::RotationStrategy::KeepAll)
                .build(),
        )
        .setup(|_| {
            log::info!("MyCubby 应用启动");
            log::debug!("调试信息仅在开发模式可见");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error");
}
```

### 在任意位置记录日志

```rust
use log::{info, warn, error, debug, trace};

pub fn do_something(path: &str) {
    info!("开始处理文件: {}", path);
    debug!("详细参数: path={}", path);

    match std::fs::read(path) {
        Ok(bytes) => {
            info!("读取文件成功，大小: {} bytes", bytes.len());
        }
        Err(e) => {
            error!("读取文件失败: {} - {}", path, e);
        }
    }
}
```

---

## 文件系统操作

### 目录遍历与筛选

```rust
// services/file_service.rs
use walkdir::WalkDir;
use std::path::{Path, PathBuf};
use std::collections::HashSet;

#[derive(serde::Serialize, Clone)]
pub struct FileEntry {
    pub path: String,
    pub name: String,
    pub size: u64,
    pub is_dir: bool,
    pub modified: i64,
    pub extension: Option<String>,
}

pub fn scan_directory(
    root: &str,
    recursive: bool,
    extensions: Option<&[String]>,
    max_depth: usize,
) -> anyhow::Result<Vec<FileEntry>> {
    let root_path = Path::new(root);
    if !root_path.is_dir() {
        anyhow::bail!("{} 不是有效的目录", root);
    }

    let ext_set: Option<HashSet<&str>> = extensions
        .map(|list| list.iter().map(|s| s.as_str()).collect());

    let walker = if recursive {
        WalkDir::new(root_path).max_depth(max_depth)
    } else {
        WalkDir::new(root_path).max_depth(1)
    };

    let mut results = Vec::new();
    for entry in walker.into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        let is_dir = entry.file_type().is_dir();

        if let Some(allowed) = &ext_set {
            if !is_dir {
                let ext = path
                    .extension()
                    .and_then(|e| e.to_str())
                    .unwrap_or("");
                if !allowed.contains(ext) {
                    continue;
                }
            }
        }

        let name = path
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("")
            .to_string();

        let meta = entry.metadata().ok();
        let size = meta.as_ref().map(|m| m.len()).unwrap_or(0);
        let modified = meta
            .as_ref()
            .and_then(|m| m.modified().ok())
            .map(|t| {
                t.duration_since(std::time::UNIX_EPOCH)
                    .map(|d| d.as_secs() as i64)
                    .unwrap_or(0)
            })
            .unwrap_or(0);

        let extension = path
            .extension()
            .and_then(|e| e.to_str())
            .map(|s| s.to_lowercase());

        results.push(FileEntry {
            path: path.to_string_lossy().to_string(),
            name,
            size,
            is_dir,
            modified,
            extension,
        });
    }

    Ok(results)
}
```

### 文件哈希计算

```rust
// utils/crypto.rs
use sha2::{Sha256, Digest};
use md5::Md5;
use std::path::Path;
use std::fs::File;
use std::io::{BufReader, Read};

pub fn sha256_file(path: &str) -> anyhow::Result<String> {
    let file = File::open(path)?;
    let mut reader = BufReader::new(file);
    let mut hasher = Sha256::new();
    let mut buf = [0u8; 64 * 1024];

    loop {
        let n = reader.read(&mut buf)?;
        if n == 0 { break; }
        hasher.update(&buf[..n]);
    }

    Ok(hex::encode(hasher.finalize()))
}

pub fn md5_file(path: &str) -> anyhow::Result<String> {
    let file = File::open(path)?;
    let mut reader = BufReader::new(file);
    let mut hasher = Md5::new();
    let mut buf = [0u8; 64 * 1024];

    loop {
        let n = reader.read(&mut buf)?;
        if n == 0 { break; }
        hasher.update(&buf[..n]);
    }

    Ok(hex::encode(hasher.finalize()))
}
```

---

## 数据库集成 (SQLite)

使用 `tauri-plugin-sql` 或直接使用 `rusqlite`。以下展示更灵活的 `rusqlite` 集成方式。

### 添加依赖

```toml
# Cargo.toml
rusqlite = { version = "0.32", features = ["bundled", "chrono", "serde_json"] }
```

### 数据库模块

```rust
// db/mod.rs
use rusqlite::{params, Connection};
use std::sync::Mutex;
use anyhow::{Context, Result};

mod schema;
pub use schema::*;

pub struct Database {
    conn: Mutex<Connection>,
}

impl Database {
    pub fn open() -> Result<Self> {
        let db_path = get_db_path()?;
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent)?;
        }

        let conn = Connection::open(&db_path)
            .with_context(|| format!("无法打开数据库: {:?}", db_path))?;

        // 性能优化
        conn.pragma_update(None, "journal_mode", "WAL")?;
        conn.pragma_update(None, "foreign_keys", "ON")?;
        conn.pragma_update(None, "synchronous", "NORMAL")?;

        let db = Self { conn: Mutex::new(conn) };
        db.init_schema()?;
        Ok(db)
    }

    fn init_schema(&self) -> Result<()> {
        let conn = self.conn.lock().unwrap();

        // 版本表
        conn.execute_batch(r#"
            CREATE TABLE IF NOT EXISTS _schema_version (
                version INTEGER PRIMARY KEY
            );
        "#)?;

        // 读取当前版本
        let current_version: i32 = conn
            .query_row("SELECT COALESCE(MAX(version), 0) FROM _schema_version", [], |r| r.get(0))?;

        // 迁移
        for v in (current_version + 1)..=schema::VERSION {
            let migration = schema::get_migration(v);
            conn.execute_batch(migration.sql)?;
            conn.execute("INSERT INTO _schema_version (version) VALUES (?1)", params![v])?;
            log::info!("数据库迁移完成: v{}", v);
        }

        Ok(())
    }

    // ===== 文件记录 CRUD =====

    pub fn insert_file(&self, file: &FileRecord) -> Result<i64> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(r#"
            INSERT INTO files (path, name, size, hash, extension, modified_at)
            VALUES (?1, ?2, ?3, ?4, ?5, ?6)
        "#)?;
        let id = stmt.insert(params![
            file.path, file.name, file.size, file.hash,
            file.extension, file.modified_at,
        ])?;
        Ok(id)
    }

    pub fn find_file_by_path(&self, path: &str) -> Result<Option<FileRecord>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare("SELECT * FROM files WHERE path = ?1")?;
        let mut rows = stmt.query(params![path])?;
        match rows.next()? {
            Some(row) => Ok(Some(FileRecord::from_row(row)?)),
            None => Ok(None),
        }
    }

    pub fn search_files(&self, keyword: &str, page: usize, page_size: usize) -> (Vec<FileRecord>, usize) {
        let conn = self.conn.lock().unwrap();
        let like = format!("%{}%", keyword);

        let total: usize = conn
            .query_row(
                "SELECT COUNT(*) FROM files WHERE name LIKE ?1 OR path LIKE ?1",
                params![like],
                |r| r.get(0),
            )
            .unwrap_or(0);

        let offset = page.saturating_sub(1) * page_size;

        let mut stmt = conn
            .prepare(r#"
                SELECT * FROM files
                WHERE name LIKE ?1 OR path LIKE ?1
                ORDER BY modified_at DESC
                LIMIT ?2 OFFSET ?3
            "#)
            .unwrap();

        let items = stmt
            .query_map(params![like, page_size as i64, offset as i64], |row| {
                FileRecord::from_row(row)
            })
            .unwrap()
            .filter_map(|r| r.ok())
            .collect();

        (items, total)
    }
}

fn get_db_path() -> Result<std::path::PathBuf> {
    let ctx = tauri::generate_context!();
    let dir = tauri::api::path::app_data_dir(&ctx.config())
        .context("无法获取应用数据目录")?;
    Ok(dir.join("mycubby.db"))
}
```

```rust
// db/schema.rs
use rusqlite::Row;

pub const VERSION: i32 = 1;

pub struct Migration {
    pub version: i32,
    pub sql: &'static str,
}

pub fn get_migration(version: i32) -> Migration {
    match version {
        1 => Migration {
            version: 1,
            sql: r#"
                CREATE TABLE IF NOT EXISTS files (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    path        TEXT NOT NULL UNIQUE,
                    name        TEXT NOT NULL,
                    size        INTEGER NOT NULL DEFAULT 0,
                    hash        TEXT,
                    extension   TEXT,
                    modified_at INTEGER NOT NULL DEFAULT 0,
                    created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
                );
                CREATE INDEX IF NOT EXISTS idx_files_name ON files(name);
                CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_at);
            "#,
        },
        _ => panic!("未知的迁移版本"),
    }
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct FileRecord {
    pub id: i64,
    pub path: String,
    pub name: String,
    pub size: i64,
    pub hash: Option<String>,
    pub extension: Option<String>,
    pub modified_at: i64,
    pub created_at: i64,
}

impl FileRecord {
    pub fn from_row(row: &Row) -> rusqlite::Result<Self> {
        Ok(Self {
            id: row.get("id")?,
            path: row.get("path")?,
            name: row.get("name")?,
            size: row.get("size")?,
            hash: row.get("hash")?,
            extension: row.get("extension")?,
            modified_at: row.get("modified_at")?,
            created_at: row.get("created_at")?,
        })
    }
}
```

---

## HTTP 请求

### 使用 reqwest 发送请求

```toml
# Cargo.toml
reqwest = { version = "0.12", features = ["json", "stream", "multipart", "rustls-tls"], default-features = false }
```

```rust
// services/http_service.rs
use reqwest::{Client, multipart};
use serde::{de::DeserializeOwned, Serialize};
use anyhow::Result;

pub struct ApiClient {
    client: Client,
    base_url: String,
}

impl ApiClient {
    pub fn new(base_url: impl Into<String>) -> Self {
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(30))
            .user_agent("MyCubby/0.1.0")
            .build()
            .unwrap();
        Self { client, base_url: base_url.into() }
    }

    async fn request<R: DeserializeOwned>(
        &self,
        method: reqwest::Method,
        path: &str,
        body: Option<&impl Serialize>,
    ) -> Result<R> {
        let url = if path.starts_with("http") {
            path.to_string()
        } else {
            format!("{}{}", self.base_url, path)
        };

        let mut req = self.client.request(method, &url);
        if let Some(b) = body {
            req = req.json(b);
        }

        let resp = req.send().await?;
        let status = resp.status();

        if !status.is_success() {
            let text = resp.text().await.unwrap_or_default();
            anyhow::bail!("HTTP {} - {}", status, text);
        }

        let data = resp.json::<R>().await?;
        Ok(data)
    }

    pub async fn get<R: DeserializeOwned>(&self, path: &str) -> Result<R> {
        self.request(reqwest::Method::GET, path, None::<&()>).await
    }

    pub async fn post<S: Serialize, R: DeserializeOwned>(&self, path: &str, body: &S) -> Result<R> {
        self.request(reqwest::Method::POST, path, Some(body)).await
    }

    // 下载文件并报告进度
    pub async fn download_with_progress<F>(
        &self,
        url: &str,
        save_path: &str,
        mut on_progress: F,
    ) -> Result<u64>
    where
        F: FnMut(u64, u64),
    {
        use futures_util::StreamExt;
        use tokio::io::AsyncWriteExt;

        let resp = self.client.get(url).send().await?;
        let total = resp.content_length().unwrap_or(0);
        let mut stream = resp.bytes_stream();

        let mut file = tokio::fs::File::create(save_path).await?;
        let mut downloaded = 0u64;

        while let Some(chunk) = stream.next().await {
            let chunk = chunk?;
            file.write_all(&chunk).await?;
            downloaded += chunk.len() as u64;
            on_progress(downloaded, total);
        }

        file.flush().await?;
        Ok(downloaded)
    }

    // 上传文件
    pub async fn upload_file(&self, url: &str, file_path: &str) -> Result<serde_json::Value> {
        let path = std::path::PathBuf::from(file_path);
        let file_name = path.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("file")
            .to_string();

        let form = multipart::Form::new()
            .file("file", &path).await?
            .text("filename", file_name);

        let resp = self.client
            .post(url)
            .multipart(form)
            .send()
            .await?;

        Ok(resp.json().await?)
    }
}
```

---

## 后台任务与定时器

### setup 中启动后台任务

```rust
// lib.rs
use tokio::time::{interval, Duration};
use tauri::{Manager, Emitter};

pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let app_handle = app.handle().clone();

            // 1. 定时清理缓存（每 30 分钟）
            tauri::async_runtime::spawn(async move {
                let mut ticker = interval(Duration::from_secs(30 * 60));
                loop {
                    ticker.tick().await;
                    match clean_old_cache() {
                        Ok(n) => log::info!("清理了 {} 个旧缓存文件", n),
                        Err(e) => log::warn!("缓存清理失败: {}", e),
                    }
                }
            });

            // 2. 定时发送心跳到前端（每 5 秒）
            let handle2 = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let mut ticker = interval(Duration::from_secs(5));
                loop {
                    ticker.tick().await;
                    let _ = handle2.emit(
                        "heartbeat",
                        serde_json::json!({"ts": chrono::Local::now().timestamp()})
                    );
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error");
}

fn clean_old_cache() -> anyhow::Result<usize> {
    use std::time::SystemTime;

    let ctx = tauri::generate_context!();
    let cache_dir = tauri::api::path::app_cache_dir(&ctx.config())
        .ok_or_else(|| anyhow::anyhow!("无法获取缓存目录"))?;

    let cutoff = SystemTime::now() - Duration::from_secs(7 * 24 * 60 * 60); // 7 天前
    let mut count = 0;

    for entry in walkdir::WalkDir::new(&cache_dir).into_iter().filter_map(|e| e.ok()) {
        if entry.file_type().is_file() {
            if let Ok(meta) = entry.metadata() {
                if let Ok(modified) = meta.modified() {
                    if modified < cutoff {
                        let _ = std::fs::remove_file(entry.path());
                        count += 1;
                    }
                }
            }
        }
    }

    Ok(count)
}
```

---

## 自定义插件开发

当功能模块较大或需要跨项目复用时，可以封装为 Tauri 插件。

### 创建内置插件

```rust
// plugins/mycubby_search/mod.rs
use tauri::plugin::{Builder, TauriPlugin};
use tauri::{Runtime, Manager, AppHandle, State};
use std::sync::{Arc, Mutex};

mod commands;
mod engine;

use commands::*;
use engine::SearchEngine;

pub struct SearchState {
    pub engine: Mutex<SearchEngine>,
}

/// 初始化搜索插件
pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("mycubby-search")
        .setup(|app_handle| {
            // 插件初始化
            let engine = SearchEngine::new().map_err(|e| e.to_string())?;

            app_handle.manage(SearchState {
                engine: Mutex::new(engine),
            });

            log::info!("MyCubby 搜索插件初始化完成");
            Ok(())
        })
        // 插件提供的命令（带前缀调用）
        // 前端调用: invoke("plugin:mycubby-search|build_index", { ... })
        .invoke_handler(tauri::generate_handler![
            commands::build_index,
            commands::search,
            commands::search_status,
            commands::clear_index,
        ])
        .build()
}

// 插件扩展方法：允许在 Rust 端通过 `app.search_engine()` 调用
pub trait SearchExt {
    fn rebuild_index(&self, dirs: Vec<String>) -> anyhow::Result<()>;
}

impl<R: Runtime> SearchExt for AppHandle<R> {
    fn rebuild_index(&self, dirs: Vec<String>) -> anyhow::Result<()> {
        let state = self.state::<SearchState>();
        let mut engine = state.engine.lock().unwrap();
        engine.build_index(&dirs)?;
        Ok(())
    }
}
```

```rust
// plugins/mycubby_search/commands.rs
use tauri::State;
use crate::plugins::mycubby_search::{SearchState, engine::Progress};
use super::engine::SearchHit;

#[tauri::command]
pub fn build_index(
    state: State<SearchState>,
    app: tauri::AppHandle,
    dirs: Vec<String>,
) -> Result<(), String> {
    let mut engine = state.engine.lock().map_err(|e| e.to_string())?;
    engine.build_index_with_callback(&dirs, |progress: Progress| {
        let _ = app.emit("search-progress", progress);
    }).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn search(state: State<SearchState>, keyword: String, limit: usize) -> Vec<SearchHit> {
    let engine = state.engine.lock().unwrap();
    engine.search(&keyword, limit)
}

#[tauri::command]
pub fn search_status(state: State<SearchState>) -> serde_json::Value {
    let engine = state.engine.lock().unwrap();
    serde_json::json!({
        "total_docs": engine.total_docs(),
        "last_build": engine.last_build_time(),
    })
}

#[tauri::command]
pub fn clear_index(state: State<SearchState>) -> Result<(), String> {
    let mut engine = state.engine.lock().map_err(|e| e.to_string())?;
    engine.clear();
    Ok(())
}
```

### 注册使用插件

```rust
// lib.rs
pub fn run() {
    tauri::Builder::default()
        .plugin(plugins::mycubby_search::init())
        // ...
        .run(tauri::generate_context!())
        .expect("error");
}
```

前端调用插件命令（带命名空间前缀）：

```typescript
import { invoke } from '@tauri-apps/api/core'

// 插件命令的格式固定为：plugin:插件名|命令名
await invoke('plugin:mycubby-search|build_index', {
  dirs: ['C:/Users/Documents', 'C:/Work']
})

const results = await invoke('plugin:mycubby-search|search', {
  keyword: 'Tauri',
  limit: 20,
})
```

---

## 单元测试

### 为 Services 编写测试

```rust
// services/file_service.rs
// ... (上面的 scan_directory 实现)

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn setup_test_dir() -> TempDir {
        let dir = TempDir::new().unwrap();

        // 创建测试文件
        std::fs::write(dir.path().join("a.txt"), "hello").unwrap();
        std::fs::write(dir.path().join("b.txt"), "world").unwrap();
        std::fs::write(dir.path().join("image.png"), "fake data").unwrap();

        let sub = dir.path().join("sub");
        std::fs::create_dir(&sub).unwrap();
        std::fs::write(sub.join("c.txt"), "nested").unwrap();

        dir
    }

    #[test]
    fn test_scan_directory_not_recursive() {
        let dir = setup_test_dir();
        let files = scan_directory(dir.path().to_str().unwrap(), false, None, 1).unwrap();

        assert_eq!(files.len(), 4); // 3 个文件 + 1 个子目录
        assert!(files.iter().any(|f| f.name == "a.txt"));
        assert!(files.iter().any(|f| f.name == "sub" && f.is_dir));
    }

    #[test]
    fn test_scan_directory_filter_extensions() {
        let dir = setup_test_dir();
        let exts = vec!["txt".to_string()];
        let files = scan_directory(
            dir.path().to_str().unwrap(),
            true,
            Some(&exts),
            5,
        ).unwrap();

        assert_eq!(files.len(), 3); // a.txt, b.txt, sub/c.txt
        assert!(files.iter().all(|f| f.extension.as_deref() == Some("txt")));
    }

    #[test]
    fn test_scan_invalid_dir() {
        let result = scan_directory("/nonexistent/path", false, None, 1);
        assert!(result.is_err());
    }
}
```

### 运行测试

```bash
cd src-tauri

# 运行所有测试
cargo test

# 运行特定模块的测试
cargo test file_service

# 显示 println! 输出
cargo test -- --nocapture

# 运行单个测试
cargo test scan_directory_filter_extensions
```

---

## 下一步

完成后端开发后，请继续阅读：
- [构建、打包与部署](./build-deploy.md) - 学习如何构建生产版本和发布
- [最佳实践与常见问题](./best-practices.md) - 查看性能优化和常见问题解决方案
