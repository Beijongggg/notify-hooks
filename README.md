# Claude Code Notify Hooks

为 Claude Code 提供智能权限管理与回复完成通知的 hooks 工具。

## 功能

| Hook | 行为 |
|------|------|
| **PermissionRequest** | 自动允许，不弹窗打扰。你在前台盯着终端时任务静默继续 |
| **Stop** | **VS Code 前台** → 不通知（你在看终端）；**后台** → 绿色轻量通知 3 秒自消 |

## 快速安装

```bash
# 1. 复制 hooks 脚本
cp hooks/notify.py ~/.claude/hooks/notify.py

# 2. 编辑 settings.json，添加以下配置：
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

## 项目结构

```
notify-hooks/
├── hooks/
│   └── notify.py              ← 主脚本
├── settings.example.json      ← hooks 配置示例
├── install.md                 ← 详细安装指南
├── README.md                  ← 本文件
└── LICENSE
```

## 系统要求

- Claude Code
- Python 3.8+
- Windows（VS Code 前台检测功能） / macOS / Linux（通知功能）
