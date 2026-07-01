# 更新日志

## v2.5

- **AskUserQuestion 通知弹窗**：popup 模式下，VS Code 后台时弹出"🤖 Claude 正在问你问题，请切回 VS Code 查看"轻量提示，切回前台自动关闭，终端正常提问
- **PreToolUse 钩子**：添加 `PreToolUse` 事件支持，settings.json 中配置，专门用于拦截 AskUserQuestion（不与其他工具冲突）
- **`_should_skip` 改进**：支持按模式判断，auto 模式跳过 AskUserQuestion，popup 模式拦截

*2026-07-01*

## v2.4

- **弹窗自动关闭**：弹窗模式下，后台切回前台时自动关闭审批弹窗，透传给终端
- **弹窗置顶修复**：`attributes("-topmost", True)` 确保弹窗始终在最前

*2026-07-01*

## v2.3

- **Popup 弹窗模式完成**：VS Code 后台时弹出中文置顶授权窗口（含工具名+操作详情）；前台时透传，终端显示原生权限提示
- **AskUserQuestion 始终透传**：两种模式下均不拦截，选项询问正常使用

*2026-07-01*

## v2.2

- **恢复 AskUserQuestion**：不再拦截交互提问弹窗，确保选项询问功能正常
- **清理无用逻辑**：移除 `_INTERACTIVE_TOOLS` 拒绝判断

*2026-07-01*

## v2.1

> ⚠️ **功能实现不完全** — PermissionRequest 权限钩子仅对 Write、Edit、Read 等部分工具触发，Bash 等工具不触发，popup 弹窗模式暂不能覆盖所有操作场景，v2 系列此功能不完整。

- **Hook 配置修复**：修正为数组格式确保生效；路径解析改用 `os.path.abspath` 兼容 Git Bash

*2026-07-01*

## v2

> ⚠️ **功能实现不完全** — 同上，popup 弹窗模式存在触发范围限制。

- **双模式切换**：新增 `config.json` 配置文件，支持 `auto`（自动放行）和 `popup`（弹窗授权）两种模式，切换立即生效

*2026-07-01*

## v1

- **PermissionRequest 自动授权**：拦截授权弹窗，自动放行执行类工具（Bash、Write、Edit、Agent 等），交互类工具自动拒绝
- **Stop 回复完成通知**：VS Code 前台时不通知，后台弹出绿色通知条 3 秒自消

*2026-06-30*
