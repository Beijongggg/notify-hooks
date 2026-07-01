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
| **`popup`** | GUI 弹窗提示，手动点"允许/拒绝" | 谨慎操作，需要每步确认 |

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
