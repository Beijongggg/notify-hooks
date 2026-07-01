# Claude Code Notify Hooks

> ⚠️ **仅适用于个人/小型项目**
>
> 本工具默认自动放行所有执行类工具（Bash、Write、Edit、Agent 等），**不会弹出授权确认弹窗**。
> 这意味着 Claude 的任何操作都将静默执行，请自行承担使用风险。如涉及生产环境或敏感操作，**请勿使用本工具**。

为 Claude Code 提供智能权限管理与回复完成通知的 hooks 工具。支持两种授权模式，可通过 `config.json` 自由切换。

## 功能

| Hook | 行为 |
|------|------|
| **PermissionRequest** | 见下方模式说明 |
| **Stop** | **VS Code 前台** → 不通知；**后台** → 绿色轻量通知 3 秒自消 |

### 两种授权模式

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| **`auto`**（默认） | 自动放行执行类工具，不弹窗打扰 | 日常使用，信任 Claude |
| **`popup`** | GUI 弹窗提示，手动点"允许/拒绝" | 后台摸鱼/离开座位时使用 |

**💡 popup 模式的设计目的**：当你在后台运行 Claude Code 时（例如去休息、摸鱼、处理其他事情），
弹窗会浮在桌面上，你远远看一眼就知道 Claude 正在调用什么工具、是否需要确认。
配合 Stop 通知的绿色提示条，即使不盯着终端也能掌握任务进度。**无需守在电脑前逐行看日志。**

**切换方式**：编辑 `config.json` 中的 `mode` 字段：

```json
{ "mode": "popup" }   ← 弹窗模式
{ "mode": "auto" }    ← 自动放行模式
```

修改后**立即生效**，无需重启 Claude Code。

## 安装

```bash
# 1. 复制 hooks 脚本和配置文件
cp hooks/notify.py ~/.claude/hooks/notify.py
cp config.example.json ~/.claude/hooks/config.json   # 可选，默认自动模式

# 2. 编辑 ~/.claude/settings.json，添加：
```

```json
{
  "hooks": {
    "PermissionRequest": "python ~/.claude/hooks/notify.py",
    "Stop": "python ~/.claude/hooks/notify.py"
  }
}
```

详细安装说明见 [install.md](install.md)。

## 更新日志

各版本变更详情见 [CHANGELOG.md](CHANGELOG.md)。

## 项目结构

```
notify-hooks/
├── hooks/
│   └── notify.py              ← 主脚本
├── config.example.json        ← 配置文件模板
├── settings.example.json      ← hooks 配置示例
├── install.md                 ← 详细安装指南
├── README.md                  ← 本文件
└── LICENSE
```

## 系统要求

- Claude Code
- Python 3.8+
- Windows（VS Code 前台检测功能） / macOS / Linux（通知功能）
