# 更新日志

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
