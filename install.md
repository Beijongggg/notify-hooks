# 安装指南

> ⚠️ **风险提示**：本工具自动放行所有执行类工具，不会弹出授权确认弹窗。仅建议在个人/小型项目中使用，生产环境或涉及敏感操作请勿使用。

## 前置要求

- Claude Code（已安装并可用）
- Python 3.8+
- （Windows 可选）VS Code / Code Insiders — 用于前台检测功能

## 安装步骤

### 1. 复制脚本

```bash
# 确保 hooks 目录存在
mkdir -p ~/.claude/hooks

# 复制 notify.py
cp hooks/notify.py ~/.claude/hooks/notify.py
```

### 2. （可选）复制配置文件

```bash
# config.json 与 notify.py 在同一目录
cp config.example.json ~/.claude/hooks/config.json
```

如果不复制配置文件，默认以 **`auto`（自动放行）** 模式运行。

### 3. 配置 Claude Code

编辑 Claude Code 的 settings.json 文件：

**VS Code 用户：**
```
Ctrl+Shift+P → "Claude Code: Open Settings (JSON)"
```

**或直接编辑：**
```bash
# 用户级设置
code ~/.claude/settings.json
# 或项目级设置
code .claude/settings.json
```

添加 hooks 配置：

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/notify.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/notify.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/notify.py"
          }
        ]
      }
    ]
  }
}
```

## 模式切换（v2）

编辑 `~/.claude/hooks/config.json`，修改 `mode` 字段：

```json
{ "mode": "auto" }     # 自动放行（默认，不弹窗）
{ "mode": "popup" }    # 弹窗授权（每步手动确认）
```

修改后**立即生效**。

**💡 popup 模式的适用场景**：当你让 Claude 在后台跑任务时，不用一直盯着终端。
授权弹窗会浮在桌面上，远远看一眼就知道正在做什么；Stop 通知条会告诉你任务已完成；
Claude 提问时会弹出提示"🤖 Claude 正在问你问题"，切回前台即可回答。
适合摸鱼、离开座位、多任务处理时使用。

## 验证安装

重启 Claude Code，观察以下行为：

**auto 模式：**
- 执行需要授权的操作时 → 自动允许，无弹窗

**popup 模式：**
- 执行需要授权的操作时（VS Code 后台）→ 弹出授权窗口，手动点"允许"或"拒绝"
- 执行需要授权的操作时（VS Code 前台）→ 终端显示原生权限提示
- Claude 提问时（VS Code 后台）→ 弹出通知"🤖 Claude 正在问你问题"，切回前台后在终端回答
- Claude 提问时（VS Code 前台）→ 终端直接显示问题

**通用（两种模式）：**
- Claude 完成回复时（VS Code 后台）→ 绿色通知条"✅ 回复已完成"3 秒自动消失
- Claude 完成回复时（VS Code 前台）→ 无通知

## 卸载

```bash
# 1. 从 settings.json 中删除 hooks 配置
# 2. 删除脚本和配置文件
rm ~/.claude/hooks/notify.py
rm ~/.claude/hooks/config.json
```

## 故障排查

如遇到问题，查看错误日志：

```bash
cat ~/.claude/hooks/notify_error.log
```
