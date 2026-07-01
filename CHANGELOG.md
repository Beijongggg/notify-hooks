# 更新日志

## v1.0.0（2026-07-01）— 首个正式版

- **按钮布局修复**：权限弹窗按钮改用 Label + grid uniform 布局，彻底解决 Windows 下文字不居中问题
- **AskUserQuestion 通知优化**：新增「知道了」关闭按钮，无需等待 30 秒超时
- **全工具覆盖验证**：14 种工具（Bash/Write/Read/Edit/WebSearch/WebFetch/Agent/Glob/Grep/Workflow/NotebookEdit/CronCreate/Skill/SendMessage）后台弹窗均正常
- **永久允许缓存**：已加入 settings.json allow 列表的工具自动放行，不弹窗
- **前台/后台分离**：VSCode 前台时透传终端原生提示，后台时弹出中文授权窗
