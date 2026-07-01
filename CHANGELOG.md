# 更新日志

## v2（2026-07-01）

### ✨ 新增
- **双模式切换**：新增 `config.json` 配置文件，支持两种授权模式
  - `auto`（默认）— 自动放行执行类工具，不弹窗打扰
  - `popup` — GUI 弹窗授权，手动确认，适合后台/摸鱼场景
- **配置文件模板**：`config.example.json`，用户可按需复制

### 📝 文档
- 新增 `CHANGELOG.md` 版本跟踪
- 风险提示：README / install 增加仅限个人/小型项目的警告
- popup 模式设计目的说明（后台运行、摸鱼场景）

### 🔧 技术
- `_load_config()` 从 config.json 读取模式，失败静默降级 auto
- `_handle_auto()` / `_handle_popup()` 模式分发
- `_gui_permission_popup()` 模态弹窗，工具名显示 + 允许/拒绝按钮

---

## v1（2026-06-30）

### ✨ 新增
- **PermissionRequest 自动授权**：拦截授权弹窗，自动放行执行类工具
  - 白名单制：Bash、Write、Edit、Read、Agent 等工具静默通过
  - AskUserQuestion 等交互类工具自动拒绝

- **Stop 回复完成通知**：绿色轻量通知条 "✅ 回复已完成"
  - VS Code 前台时跳过（你在看终端）
  - VS Code 后台时弹出，3 秒自消
  - 支持 Windows / macOS / Linux

### 🔧 技术
- Windows VS Code 前台检测（Win32 API：GetForegroundWindow + GetModuleBaseNameW）
- 控制台窗口隐藏（避免弹 cmd 黑框）
- tkinter 无边框窗口，escape/click 关闭
- 错误日志 `notify_error.log`

### 📦 项目
- 发布到 GitHub：https://github.com/Beijongggg/notify-hooks
- hooks/notify.py + settings.example.json + install.md
