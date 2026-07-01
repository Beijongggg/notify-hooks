# 安装指南

## 前置要求

- Claude Code（已安装并可用）
- Python 3.8+
- （Windows 可选）VS Code / Code Insiders — 用于前台检测功能

> ⚠️ **风险提示**：本工具自动放行所有执行类工具，不会弹出授权确认弹窗。仅建议在个人/小型项目中使用，生产环境或涉及敏感操作请勿使用。

## 安装步骤

### 1. 复制脚本

```bash
# 确保 hooks 目录存在
mkdir -p ~/.claude/hooks

# 复制 notify.py
cp hooks/notify.py ~/.claude/hooks/notify.py
```

### 2. 配置 Claude Code

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
    "PermissionRequest": "python ~/.claude/hooks/notify.py",
    "Stop": "python ~/.claude/hooks/notify.py"
  }
}
```

### 3. 验证安装

重启 Claude Code，观察以下行为：

- 执行需要授权的操作时 → 自动允许，无弹窗
- Claude 完成回复时（VS Code 后台）→ 绿色通知条"✅ 回复已完成"3 秒自动消失
- Claude 完成回复时（VS Code 前台）→ 无通知

## 卸载

```bash
# 1. 从 settings.json 中删除 hooks 配置
# 2. 删除脚本文件
rm ~/.claude/hooks/notify.py
```

## 故障排查

如遇到问题，查看错误日志：

```bash
cat ~/.claude/hooks/notify_error.log
```
