# 安装指南

## 前置要求

- Claude Code（已安装并可用）
- Python 3.8+
- （Windows）VS Code / Code Insiders — 用于前台检测功能

---

## 安装步骤

### 1. 复制脚本

```bash
mkdir -p ~/.claude/hooks
cp hooks/notify.py ~/.claude/hooks/notify.py
```

### 2. （可选）复制配置文件

```bash
cp config.example.json ~/.claude/hooks/config.json
```

不复制配置文件则默认以 **`auto`（自动放行）** 模式运行，所有工具自动放行无弹窗。

### 3. 配置 Claude Code

编辑 Claude Code 的 settings.json，添加以下 hooks 配置：

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

配置文件位置：
- **用户级设置**：`~/.claude/settings.json`
- **项目级设置**：`.claude/settings.json`
- **VS Code 中打开**：`Ctrl+Shift+P` → `Claude Code: Open Settings (JSON)`

---

## 模式切换

编辑 `~/.claude/hooks/config.json`，修改 `mode` 字段：

```json
{ "mode": "auto" }     // 自动放行（默认，不弹窗）
{ "mode": "popup" }    // 弹窗授权，每步手动确认
```

修改后**立即生效**，无需重启 Claude Code。

---

## 验证安装

重启 Claude Code，观察以下行为：

**auto 模式：**
- 执行需要授权的操作 → 自动允许，无弹窗

**popup 模式：**
- 执行操作时（VSCode 后台）→ 弹出中文授权窗口
- 执行操作时（VSCode 前台）→ 终端显示原生权限提示
- Claude 提问时（后台）→ "🤖 Claude 正在问你问题"通知
- Claude 提问时（前台）→ 终端直接显示问题

**通用（两种模式）：**
- 回复完成时（后台）→ 绿色通知条 "✅ 回复已完成" 3 秒自动消失
- 回复完成时（前台）→ 无通知

---

## 卸载

```bash
# 1. 从 settings.json 中删除 hooks 配置
# 2. 删除脚本和配置文件
rm ~/.claude/hooks/notify.py
rm ~/.claude/hooks/config.json
```

---

## 故障排查

```bash
# 查看错误日志
cat ~/.claude/hooks/notify_error.log
```

常见问题：

| 问题 | 原因 | 解决 |
|------|------|------|
| 弹窗不出现 | hooks 配置错误 | 检查 settings.json 中 hooks 格式 |
| 弹窗不出现 | 当前为 auto 模式 | 修改 config.json 中 mode 为 "popup" |
| 弹窗闪一下就消失 | VSCode 在前台 | 切换到其他窗口，弹窗会保留 |
| 中文乱码 | 编码不匹配 | 确保 Python/终端使用 UTF-8 |
