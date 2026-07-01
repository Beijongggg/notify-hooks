<div align="center">

# Claude Code Notify Hooks

**v1.0.0** — 为 Claude Code 提供权限管理 GUI 弹窗与回复完成通知

[![Version](https://img.shields.io/github/v/tag/Beijongggg/notify-hooks?label=version)](https://github.com/Beijongggg/notify-hooks/tags)
[![License](https://img.shields.io/github/license/Beijongggg/notify-hooks)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)

</div>

---

## 📖 概览

通过 Claude Code Hooks 系统，在后台运行时用 GUI 弹窗代替终端原生权限提示。

| Hook | 用途 |
|------|------|
| **PreToolUse** | 工具调用前弹出中文授权窗，显示工具名与操作详情 |
| **Stop** | 回复完成后弹出绿色通知条「✅ 回复已完成」 |
| **PermissionRequest** | 兼容旧版事件，确保所有权限请求都被拦截 |

```
VSCode 前台 → 终端原生提示（不打扰编辑）
VSCode 后台 → GUI 授权弹窗（远远看一眼就知道在做什么）
回复完成     → 绿色通知条 3 秒自消
Claude 提问   → 轻量通知提醒
```

> ⚠️ **默认自动放行所有执行工具**，仅建议个人/小型项目使用。

---

## 🚀 快速开始

```bash
# 锁定 commit — 防截断 + 防篡改（推荐）
curl -fsSL https://raw.githubusercontent.com/Beijongggg/notify-hooks/9b5b85edb41236becb4a1752de19c56c84e23ea1/install.py -o install.py && python install.py
```

重启 Claude Code 即可生效。

> `&&` 保证 curl 完整下载后才执行，杜绝管道截断攻击；锁定 commit sha256 防止上游被篡改。
> 详细步骤见 [install.md](install.md)。

---

## 🔀 授权模式

编辑 `~/.claude/hooks/config.json` 切换，修改立即生效：

| 模式 | 设置 | 行为 |
|------|------|------|
| **auto**（默认） | `"mode": "auto"` | 所有工具自动放行，无弹窗 |
| **popup** | `"mode": "popup"` | 后台时弹出中文 GUI 授权窗，手动确认 |

### 授权弹窗特性

- 工具中文名显示（Bash → "执行命令"、Write → "写入文件" 等 20+ 工具）
- 操作详情预览（命令、文件路径、搜索内容）
- ❌ 拒绝 / 🔁 始终允许（缓存）/ ✅ 允许（一次）
- 始终允许自动写入 `settings.json`，后续不弹窗

---

## 📁 项目结构

```
notify-hooks/
├── hooks/notify.py           ← 主脚本（含所有弹窗逻辑）
├── config.example.json       ← 配置文件模板
├── settings.example.json     ← 完整 settings.json 示例
├── install.md                ← 详细安装指南
├── CHANGELOG.md              ← 版本历史
└── README.md                 ← 本文件
```

---

## 💻 系统要求

- Claude Code（任意版本）
- Python 3.8+
- **Windows**：前台/后台检测完整功能
- **macOS / Linux**：通知功能基础支持

---

## 🔧 故障排查

```bash
cat ~/.claude/hooks/notify_error.log
```

- **弹窗不出现** → 检查 hooks 配置，确认 `mode` 已设为 `"popup"`
- **中文显示乱码** → 确保终端 / Python 使用 UTF-8 编码
- **权限不生效** → 重启 Claude Code 使 hooks 重新加载

详见 [install.md](install.md)。
