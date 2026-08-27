# 02-选型对比 + Rust 零基础够用版入门

> 读完本文，你应该能：1）拍板到底用 Tauri 还是 Electron；2）看懂 80% 常见的 Tauri Rust 命令代码；3）写简单的命令不被编译器骂懵。

---

## 第一部分：Tauri vs Electron 选型决策树

先问自己 5 个问题，顺着走就有答案。

```
你做的软件安装包能不能接受 150MB+？
        ├─ 能 → 下一题
        └─ 不能 → 选 Tauri ✅

你的团队/你自己完全不想碰 Rust，哪怕一点点？
        ├─ 完全不想 → 选 Electron ✅
        └─ 愿意花 1-2 周学点皮毛 → 下一题

你的项目重度依赖 Node 原生模块（ffmpeg/sharp/sqlite3/node-gyp 链）？
        ├─ 是，且很多，不想用 Rust 重写任何一个 → 选 Electron ✅
        └─ 不是，只有一两个/全是纯 JS 库 → 下一题

你要上架到 Windows 应用商店 / 微软 Intune / 企业分发？
        ├─ 是 → Tauri 有优势（体积小，审核通过率高）
        └─ 不是 → 下一题

目标用户有没有老系统（Win7 / macOS <10.15）？
        ├─ 有，且必须兼容 → 选 Electron ✅
        └─ 没有（Win10 1809+ 就行）→ 选 Tauri ✅
```

### 现实中的典型案例

| 项目类型 | 选 Tauri 还是 Electron？ | 为什么 |
| :--- | :--- | :--- |
| 个人/小团队做的本地工具（笔记/Markdown/Todo/截图录屏） | **Tauri** | 体积小，上架快，对 Node 原生模块依赖几乎为 0 |
| VSCode 那种超重型 IDE、Slack 聊天软件、Figma 客户端 | **Electron** | 生态全，团队 Node 经验多，不差那几百 MB 内存 |
| 公司内网的管理工具（给运维/HR/财务用） | **Tauri** | 装完只有 10MB 左右，邮件发用户就能跑，不会被 360 报「体积异常大」 |
| 做视频剪辑/图片批处理，依赖 ffmpeg/sharp | **都可以，倾向 Electron** | ffmpeg 可以用 Rust 版 `ffmpeg-sidecar` 或 shell 命令调，但 Electron 生态更成熟 |
| 做给国企/政府/事业单位客户，要走严格合规审计 | **Tauri** | 没有 Node，安全白名单模式，审计好通过 |
| 做 Web 套壳浏览器、需要用很多 npm 上的小众生态库 | **Electron** | Node 集成直接 require 就行 |

### Tauri 1.x 与 Tauri 2.x 的区别（你该学 2.x）

别浪费时间学 1.x。Tauri 2.0 在 2024 年 6 月正式发布，官方已经不再大力维护 1.x 了。

关键差异：

| 点 | Tauri 1.x | Tauri 2.x |
| :--- | :--- | :--- |
| 安全模式 | `tauri.conf.json` 里写 allowlist 白名单字符串 | 独立的 `capabilities/*.json` 文件，支持按窗口分配不同权限，支持 scope 细粒度 allow/deny |
| API 封装 | `@tauri-apps/api` 一个包包含所有 API | 拆成了 `@tauri-apps/api`（核心） + `@tauri-apps/plugin-*`（每个功能一个插件包），用哪个装哪个 |
| Rust 插件 | 官方插件少，第三方质量参差不齐 | 官方维护 20+ 个插件（dialog/fs/store/notification/shell/http/updater/sql...），接口统一，文档齐全 |
| 移动端 | 实验性，几乎不能做生产 | **正式支持 Android/iOS**，一套代码可以同时打桌面+移动（本文不涉及移动端，移动端要另配 Gradle/Xcode） |
| 学习资料 | 网上中文博客大部分是 1.x 的，过时了 | 官方中文文档已覆盖，坑少 |

**结论：所有新项目直接学 2.x。抄到带 `allowlist` 字样的旧博客代码别直接用，按 capabilities 改。**

---

## 第二部分：Rust 零基础够用版入门（按写 Tauri Commands 的需求裁剪）

你不要学完整的 Rust。按写 Tauri 命令需要的语法来学就行。下面只讲你写命令会用到的那 20% 语法，足够覆盖 80% 的场景。

### 2.1 变量、常量、类型

```rust
// 变量用 let，默认不可变（不能改），要改加 mut
let a = 5;          // 不可变
let mut b = 10;     // 可变
b = 20;             // OK，b 是 mut

// 类型大多时候能自动推断，写出来更稳
let name: &str = "张三";       // &str = 字符串字面量（只读切片）
let age: u32 = 28;             // u32 = 无符号 32 位整数，最大 40 亿
let price: f64 = 19.99;        // f64 = 64 位浮点数
let is_vip: bool = true;       // bool = true/false
```

常用类型对照：

| 你要表达的 | Rust 类型 | 何时用 |
| :--- | :--- | :--- |
| 整数（正数） | `u32` / `u64` | 计数、ID、字节数等不会负的数 |
| 整数（可能正可能负） | `i32` / `i64` | 温度、账本、偏移量等 |
| 小数 | `f32` / `f64` | 一般都用 f64，精度高 |
| 真/假 | `bool` | 标志位 |
| 字面量字符串（固定的） | `&'static str` 或 `&str` | 硬编码的常量文字 |
| 可拼接可修改的字符串 | `String` | 所有要处理/拼接/返回的字符串 |
| 未知大小的列表 | `Vec<T>` | 跟 JS 的 Array 差不多 |
| 键值对映射 | `HashMap<K, V>` | 跟 JS 的 Object/Map 差不多 |
| 可能有也可能没有的东西 | `Option<T>` | JS 的 `x ?? y` / `x?.y` 概念，返回 Some(data) 或 None |
| 可能成功可能失败的操作 | `Result<T, E>` | 成功返回 Ok(data)，失败返回 Err(err_msg)，**写命令必用** |
| 结构体（自定义对象） | `struct Name { 字段: 类型 }` | 跟 TS 的 interface / type 类似 |

### 2.2 函数

```rust
// 普通函数
fn add(a: i32, b: i32) -> i32 {
    a + b            // 注意：最后一行没有分号就是返回值（跟别的语言不一样！）
                     // 或者写 return a + b; 也行，但是啰嗦不地道
}

// 返回可能失败的结果（写 Tauri 命令几乎都用这个）
fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("不能除零".to_string())    // 失败：返回 Err(字符串错误信息)
    } else {
        Ok(a / b)                       // 成功：返回 Ok(结果)
    }
}
```

⚠️ Rust 的「返回值靠最后一行不加 `;` 的表达式」机制是新手最容易懵的。记不住就全写 `return xxx;`，永远不会错，就是不「Rust 风格」而已，编译器不会骂你。

### 2.3 String 与 &str（最容易懵的两个类型）

这个概念是 Rust 特有的，搞不懂也没关系，记住下面三条实操规则：

**实操 3 条：**
1. **命令的输入参数里，如果是传字符串（名字、路径、内容），写 `&str`。** Tauri 会自动处理。
2. **命令要返回字符串给前端，写 `Result<String, String>`，成功的地方 `.to_string()` 或 `format!()`。**
3. **拼接字符串用 `format!()` 宏，跟 JS 模板字符串差不多。**

```rust
#[tauri::command]
fn make_greeting(name: &str, age: u32) -> Result<String, String> {
    if name.is_empty() {
        return Err("名字不能为空".to_string());
    }
    // format! 里 {} 就是占位符，自动转成字符串
    Ok(format!("你好{}，今年{}岁，欢迎使用本软件！", name, age))
}
```

### 2.4 struct + serde（跟前端传对象时必用）

前端传给后端、后端返回给前端的结构化对象，都要用 `#[derive(Serialize, Deserialize)]` 宏标记一下，serde 会自动帮你 JSON 序列化。

```rust
use serde::{Deserialize, Serialize};

// 前端传给后端（查询参数）
#[derive(Deserialize)]
pub struct TodoQuery {
    pub page: u32,
    pub keyword: Option<String>,    // Option 表示这个字段可以不传（JS 里 undefined 就是 None）
    pub done: Option<bool>,
}

// 后端返回给前端（数据项）
#[derive(Serialize)]
pub struct TodoItem {
    pub id: u32,
    pub title: String,
    pub done: bool,
    pub created_at: String,
}

#[tauri::command]
pub fn list_todos(query: TodoQuery) -> Result<Vec<TodoItem>, String> {
    // 假装查了数据库
    let todos = vec![
        TodoItem {
            id: 1,
            title: "学 Tauri".to_string(),
            done: false,
            created_at: "2026-08-27 10:00".to_string(),
        },
        TodoItem {
            id: 2,
            title: "喂猫".to_string(),
            done: true,
            created_at: "2026-08-27 08:00".to_string(),
        },
    ];
    Ok(todos)
}
```

前端这边 TS 的 interface 直接对应写就好：

```ts
interface TodoItem {
  id: number
  title: string
  done: boolean
  created_at: string
}
const list = await invoke<TodoItem[]>('list_todos', {
  query: { page: 1, keyword: 'Tauri', done: null },
})
```

> `Option<T>` 的字段：传 null / undefined 到 Rust 就是 None，传具体值就是 Some(value)。不传字段也可以（前提是前端 TS 的类型标了 `?:` 可选）。

### 2.5 条件判断和循环

```rust
fn grade(score: u32) -> String {
    // if / else if / else
    if score >= 90 {
        "优秀".to_string()
    } else if score >= 60 {
        "及格".to_string()
    } else {
        "不及格".to_string()
    }
}

fn sum_1_to_n(n: u32) -> u32 {
    let mut sum = 0;
    let mut i = 1;
    // loop / while / for 三种循环，写命令常用 for
    while i <= n {
        sum += i;
        i += 1;
    }
    sum
}

fn print_names() {
    let names = vec!["张三", "李四", "王五"];
    // 遍历 Vec
    for name in names.iter() {
        println!("Hello, {}", name);
    }
}
```

### 2.6 错误处理：Result 与 `?` 操作符

写 Tauri 命令 99% 的返回值都是 `Result<T, String>`。你调用另一个可能失败的函数时，不想写一堆 `match Ok(...) Err(...)`，用 `?` 把错误自动向上传播。

```rust
use std::fs;

#[tauri::command]
fn read_file(path: &str) -> Result<String, String> {
    // fs::read_to_string 返回 Result<String, std::io::Error>
    // 末尾的 ? 意思是：失败了直接把错误转成 String 返回，成功了拿里面的值
    let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
    Ok(content)
}
```

上面的 `?` + `.map_err(|e| e.to_string())` 是最常用的组合。因为标准库的错误类型（比如 io::Error）不是 String，直接 `?` 会报错，用 `map_err` 把它转成字符串。

嫌这一行啰嗦的话，可以加 `anyhow` 这个 crate（下一节讲），错误处理会更干净。

### 2.7 所有权与借用（别怕，先看实操规则）

所有权系统是 Rust 最与众不同的点。网上无数文章写这个，你不用全懂，按下面三条做，写 Tauri 命令基本不会踩坑：

**实操 3 条（救命用）：**
1. **简单的基本类型：数值、bool、char，直接传，根本没所有权问题。** 你写个 `fn add(a: i32, b: i32)` 根本不用想所有权。
2. **字符串、Vec、struct 这种复合类型作为输入参数：只要是只读的就加引用 `&`。** 比如 `fn print_name(name: &str)`、`fn count_items(items: &Vec<u32>)`。
3. **字符串要修改/拼接：自己改成 `String`，不要跟调用者抢借用。** 比如 `fn full_name(first: &str, last: &str) -> String { format!("{} {}", first, last) }`，返回一个全新的 String 就没人跟你争。

别写复杂的自引用结构体、别在函数里返回引用（除非你真懂生命周期），按上面三条写，rust-analyzer 不会跟你过不去。

你真遇到 ownership 报错时，错误提示通常会直接告诉你怎么做：`help: consider cloning the value: .clone()`。编译器说让你 clone，你就 `.clone()`，别跟它较劲，又不是做高频交易系统，clone 一下性能丢不了多少。

### 2.8 异步命令（async）

耗时操作（读大文件、调 API、sleep）不能阻塞 Tauri 主进程，要写成 async 命令，用 `tokio` 这个 runtime：

```rust
use std::time::Duration;
use tokio::time::sleep;

#[tauri::command]
pub async fn long_task(total_steps: u32) -> Result<String, String> {
    for i in 1..=total_steps {
        sleep(Duration::from_millis(100)).await;
        println!("进度：{} / {}", i, total_steps);
    }
    Ok(format!("完成 {} 步！", total_steps))
}
```

前端调用跟同步命令一样，`await invoke('long_task', { totalSteps: 50 })`，Promise 自动等 async 执行完。

### 2.9 写命令最常用的「万能模板」

你写新命令时，直接套这个模板：

```rust
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct 你命令的输入参数 {
    // pub 字段名: 类型,
}

#[derive(Serialize)]
pub struct 你命令的返回结构 {
    // pub 字段名: 类型,
}

#[tauri::command]
pub fn 你的命令_snake_case(
    // 简单参数写这里: name: &str,
    // 复杂参数写结构体: param: 你命令的输入参数,
    // 要状态的话: state: State<AppState>,
    // 要 AppHandle / Window 的话直接加参数: app: AppHandle,
) -> Result<你命令的返回结构或String, String> {
    // 1. 校验参数
    // 2. 做正事
    // 3. 返回 Ok(结果) 或 Err(错误信息)
    todo!()
}
```

### 2.10 最值得先学的 10 个第三方 crate

Crate 就是 Rust 的 npm 包。下面 10 个是写 Tauri 命令迟早会用到的，`cargo add 名字` 就能加进依赖。

| crate 名 | 做什么的 | 典型使用场景 |
| :--- | :--- | :--- |
| `serde` + `serde_json` | 序列化/反序列化 JSON | 所有 struct 跟前端交互必装 |
| `tokio` | 异步 runtime | 写 async 命令、延迟、并发任务 |
| `chrono` | 时间日期 | 获取当前时间、格式化、时区转换 |
| `anyhow` + `thiserror` | 简化错误处理 | 不用每条错误都 `.map_err(|e| e.to_string())`，让 `?` 自动向上转 |
| `rand` | 随机数 | 抽奖、生成临时文件名、选一句鸡汤 |
| `dirs` | 获取系统目录路径 | 找「文档」「桌面」「下载」「AppData」这些路径，别硬写 |
| `reqwest` | HTTP 客户端（rust 版 axios） | Rust 端调外部 API（省得前端跨域） |
| `sqlx` / `rusqlite` | SQLite 数据库 | 本地持久化大量结构化数据（比 store 插件更灵活） |
| `walkdir` | 遍历文件夹 | 做文件管理器、搜索本地目录 |
| `tauri-plugin-*` 20 多个官方插件 | 不用自己造轮子 | 核心概念那篇最后列过，按需要加 |

---

## 3. 本章小测试（答案在文末，先自己做）

1. 写一个 `fn reverse(s: &str) -> String`，把传入字符串反转返回。
2. 写一个 `fn is_palindrome(s: &str) -> Result<bool, String>`，判断字符串是不是回文（正反读一样），空字符串返回 Err("不能为空")。
3. 定义一个 `User` struct：id(u32)/name(String)/email(String)，加 serde 宏，写一个命令 `get_user(id: u32) -> Result<User, String>`，id=1 返回张三，id=2 返回李四，其他返回 Err("用户不存在")。

---

## 4. 小测试参考答案

```rust
// 题 1
fn reverse(s: &str) -> String {
    s.chars().rev().collect()
}

// 题 2
fn is_palindrome(s: &str) -> Result<bool, String> {
    if s.is_empty() {
        return Err("不能为空".to_string());
    }
    Ok(s.chars().eq(s.chars().rev()))
}

// 题 3
use serde::{Deserialize, Serialize};
#[derive(Serialize, Deserialize)]
pub struct User {
    pub id: u32,
    pub name: String,
    pub email: String,
}
#[tauri::command]
pub fn get_user(id: u32) -> Result<User, String> {
    match id {
        1 => Ok(User { id: 1, name: "张三".into(), email: "zhang@ex.com".into() }),
        2 => Ok(User { id: 2, name: "李四".into(), email: "li@ex.com".into() }),
        _ => Err("用户不存在".into()),
    }
}
```
