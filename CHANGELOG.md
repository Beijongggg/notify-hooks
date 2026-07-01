# 更新日志

## v2（2026-07-01）

- **双模式切换**：新增 `config.json` 配置文件，支持 `auto`（自动放行）和 `popup`（弹窗授权）两种模式，切换立即生效
- **风险提示**：增加仅限个人/小型项目的使用警告

## v1（2026-06-30）

- **PermissionRequest 自动授权**：拦截授权弹窗，自动放行执行类工具（Bash、Write、Edit、Agent 等），交互类工具自动拒绝
- **Stop 回复完成通知**：VS Code 前台时不通知，后台弹出绿色通知条 3 秒自消
- 发布到 GitHub：https://github.com/Beijongggg/notify-hooks
