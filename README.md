<div align="center">

# Claude Code Notify Hooks

**v1.0.0** — 为 Claude Code 提供权限管理 GUI 弹窗与回复完成通知

[![GitHub tag](https://img.shields.io/github/v/tag/Beijongggg/notify-hooks?label=version)](https://github.com/Beijongggg/notify-hooks/tags)

</div>

---

## 概览

本工具通过 Claude Code 的 Hooks 系统提供三项增强功能：

| Hook | 功能 | 适用场景 |
|------|------|----------|
| **PreToolUse** | 工具调用前弹出 GUI 授权窗口，显示工具名、操作详情 | 后台运行时远程确认 Claude 操作 |
| **Stop** | 回复完成后弹出绿色通知条"✅ 回复已完成" | 不盯着终端时掌握任务进度 |
| **PermissionRequest** | 兼容旧版事件，确保所有权限请求都被拦截 | 与 PreToolUse 配合使用确保覆盖 |

### 工作流程

```
VSCode 前台 → 终端原生权限提示（不打扰编辑）
VSCode 后台 → GUI 弹窗授权（远远看一眼就知道在做什么）
VSCode 后台回复完成 → 绿色通知条 3 秒自消
Claude 提问时后台 → "🤖 Claude 正在问你问题" 轻量通知
```

> ⚠️ **使用提醒**：本工具默认自动放行所有执行类工具，不弹窗确认。仅建议个人/小型项目使用，生产环境请谨慎。

---

## 授权模式

通过编辑 `~/.claude/hooks/config.json` 切换，修改立即生效：

| 模式 | 设置 | 行为 |
|------|------|------|
| **`auto`**（默认） | `"mode": "auto"` | 所有工具自动放行，无弹窗打扰 |
| **`popup`** | `"mode": "popup"` | 后台时弹出中文 GUI 授权窗口，手动确认 |

**💡 popup 模式设计目的**：在后台运行 Claude Code 时（休息、摸鱼、处理其他事务），授权弹窗浮在桌面上，配合绿色完成通知条，无需守在电脑前逐行看日志。

### 授权弹窗功能

- **工具中文名显示**：Bash → "执行命令"、Write → "写入文件"、Agent → "启动子任务" 等 20+ 工具
- **操作详情预览**：显示具体命令、文件路径、搜索内容等
- **三按钮授权**：❌ 拒绝 / 🔁 始终允许（缓存）/ ✅ 允许（一次）
- **始终允许缓存**：自动写入 `settings.json` 的 `permissions.allow` 列表，后续不再弹窗
- **覆盖工具**：Bash、Write、Read、Edit、WebSearch、WebFetch、Agent、Glob、Grep、Workflow、NotebookEdit、CronCreate、Skill、SendMessage 等

---

## 安装

### 1. 复制脚本

```bash
mkdir -p ~/.claude/hooks
cp hooks/notify.py ~/.claude/hooks/notify.py
```

### 2. （可选）配置文件

```bash
cp config.example.json ~/.claude/hooks/config.json
# 默认为 auto 模式，不复制也照常运行
```

### 3. 编辑 Claude Code 设置

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/notify.py" }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/notify.py" }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/notify.py" }
        ]
      }
    ]
  }
}
```

配置文件路径参考：
- **用户级**：`~/.claude/settings.json`
- **项目级**：`.claude/settings.json`
- **VS Code**：`Ctrl+Shift+P` → `Claude Code: Open Settings (JSON)`

详细安装说明见 [install.md](install.md)。

---

## 系统要求

- Claude Code（任意版本）
- Python 3.8+
- **Windows**：前台/后台检测完整功能
- **macOS / Linux**：通知功能基础支持

---

## 项目结构

```
notify-hooks/
├── hooks/
│   └── notify.py              ← 主脚本（含所有弹窗逻辑）
├── config.example.json        ← 配置文件模板
├── settings.example.json      ← 完整 settings.json 示例
├── install.md                 ← 详细安装指南
├── CHANGELOG.md               ← 版本历史
├── README.md                  ← 本文件
└── LICENSE
```

---

## 故障排查

```bash
cat ~/.claude/hooks/notify_error.log
```

常见问题：
- **弹窗不出现** → 检查 `settings.json` 中 hooks 配置是否正确，`mode` 是否设为 `"popup"`
- **中文显示乱码** → 确保终端/Python 使用 UTF-8 编码
- **权限不生效** → 重启 Claude Code 使 hooks 配置重新加载
