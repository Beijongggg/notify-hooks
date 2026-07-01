# 更新日志

## v1.0.0（2026-07-01）— 首个正式版

- **按钮布局修复**：权限弹窗按钮改用 Label + grid uniform 布局，彻底解决 Windows 下文字不居中问题
- **AskUserQuestion 通知优化**：新增「知道了」关闭按钮，无需等待 30 秒超时
- **全工具覆盖验证**：14 种工具（Bash/Write/Read/Edit/WebSearch/WebFetch/Agent/Glob/Grep/Workflow/NotebookEdit/CronCreate/Skill/SendMessage）后台弹窗均正常
- **永久允许缓存**：已加入 settings.json allow 列表的工具自动放行，不弹窗
- **前台/后台分离**：VSCode 前台时透传终端原生提示，后台时弹出中文授权窗
- **稳定版本起步**：之前所有测试版版本号归入测试阶段，此版本为正式起点

---

### 测试版

#### v3.1（测试版）

- **PreToolUse 全面接管权限弹窗**：
  - PreToolUse handler 现在处理所有工具的权限弹窗（不只是 AskUserQuestion）
  - 修复了大部分工具实际走 PreToolUse 事件但 handler 直接透传导致弹窗"允许"无效的 bug
- **PermissionRequest 输出格式修正**：
  - 去掉 `hookSpecificOutput` 中多余的 `decision`/`hookEventName` 嵌套，改为 flat 结构
  - 解决旧版 PermissionRequest 事件点允许后终端无响应的 bug
- **permission_suggestions 检测**：
  - 新增 `_can_always_allow()` 函数，根据 suggestions 类型判断是否支持始终允许
  - 不支持始终允许时隐藏对应按钮，返回纯 `{"behavior": "allow"}` 不带 `updatedPermissions`
- **输出可靠性**：`print()` 增加 `flush=True` 确保 hook 输出不被缓冲

*2026-07-01*

#### v3.0（测试版）

- **弹窗新增"始终允许"按钮**：授权弹窗增加 🔁 始终允许 选项，选择后缓存该工具权限，后续自动放行
- **完整中文工具名映射**：补全 EnterPlanMode、ExitPlanMode、TaskStop、CronCreate、MCP 工具等中文化
- **弹窗布局优化**：三按钮布局（允许一次 / 始终允许 / 拒绝），对齐终端原生权限提示行为

*2026-07-01*

#### v2.6（测试版）

- **全局行为规范化**：
  - AskUserQuestion 任何模式都不跳过，后台弹通知提醒，前台透传终端
  - 回复结束提醒不再依赖 mode 配置，全局生效
- **代码简化**：`_should_skip` 中 AskUserQuestion 不再检查 mode；`show_pre_tool_use` 去掉 mode 分支

*2026-07-01*

#### v2.5（测试版）

- **AskUserQuestion 通知弹窗**：popup 模式下，VS Code 后台时弹出"🤖 Claude 正在问你问题，请切回 VS Code 查看"轻量提示，切回前台自动关闭，终端正常提问
- **PreToolUse 钩子**：添加 `PreToolUse` 事件支持，settings.json 中配置，专门用于拦截 AskUserQuestion（不与其他工具冲突）
- **`_should_skip` 改进**：支持按模式判断，auto 模式跳过 AskUserQuestion，popup 模式拦截

*2026-07-01*

#### v2.4（测试版）

- **弹窗自动关闭**：弹窗模式下，后台切回前台时自动关闭审批弹窗，透传给终端
- **弹窗置顶修复**：`attributes("-topmost", True)` 确保弹窗始终在最前

*2026-07-01*

#### v2.3（测试版）

- **Popup 弹窗模式完成**：VS Code 后台时弹出中文置顶授权窗口（含工具名+操作详情）；前台时透传，终端显示原生权限提示
- **AskUserQuestion 始终透传**：两种模式下均不拦截，选项询问正常使用

*2026-07-01*

#### v2.2（测试版）

- **恢复 AskUserQuestion**：不再拦截交互提问弹窗，确保选项询问功能正常
- **清理无用逻辑**：移除 `_INTERACTIVE_TOOLS` 拒绝判断

*2026-07-01*

#### v2.1（测试版）

> ⚠️ **功能实现不完全** — PermissionRequest 权限钩子仅对 Write、Edit、Read 等部分工具触发，Bash 等工具不触发。

- **Hook 配置修复**：修正为数组格式确保生效；路径解析改用 `os.path.abspath` 兼容 Git Bash

*2026-07-01*

#### v2（测试版）

> ⚠️ **功能实现不完全** — popup 弹窗模式存在触发范围限制。

- **双模式切换**：新增 `config.json` 配置文件，支持 `auto`（自动放行）和 `popup`（弹窗授权）两种模式，切换立即生效

*2026-07-01*

#### v1（测试版）

- **PermissionRequest 自动授权**：拦截授权弹窗，自动放行执行类工具（Bash、Write、Edit、Agent 等）
- **Stop 回复完成提醒**：VS Code 前台时不通知，后台弹出绿色通知条 3 秒自消

*2026-06-30*
