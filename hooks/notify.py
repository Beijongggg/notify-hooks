#!/usr/bin/env python3
"""
Claude Code Hooks — v2
  授权模式（通过 config.json 切换）:
    auto  (默认) — PermissionRequest / PreToolUse 自动放行，不弹窗
    popup         — 弹窗授权，手动确认（PreToolUse 覆盖所有工具含 Bash）

  Stop → VS Code 后台时轻量完成通知，前台时跳过
"""

import os
import sys
import json
import traceback
import threading
import tkinter as tk
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# 使用 os.path.abspath 而非 Path.resolve()，避免 Git Bash 下路径解析异常
BASE_DIR = Path(os.path.abspath(__file__)).parent
CONFIG_PATH = BASE_DIR / "config.json"
ERROR_LOG = BASE_DIR / "notify_error.log"
_MAX_STDIN_BYTES = 2 * 1024 * 1024
_LOG_LOCK = threading.Lock()


def _log(msg):
    try:
        with _LOG_LOCK:
            with open(ERROR_LOG, "a", encoding="utf-8") as f:
                f.write(f"[{__import__('datetime').datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════════════════
# 配置加载
# ═══════════════════════════════════════════════════════════════════════════

def _load_config():
    """读取 config.json，失败时静默降级为 auto。"""
    try:
        if CONFIG_PATH.exists():
            raw = CONFIG_PATH.read_text("utf-8").strip()
            if raw:
                cfg = json.loads(raw)
                mode = cfg.get("mode", "auto")
                if mode in ("auto", "popup"):
                    return mode
                _log(f"[config] unknown mode '{mode}', fallback to auto")
    except Exception as exc:
        _log(f"[config] read error: {exc}")
    return "auto"


# ═══════════════════════════════════════════════════════════════════════════
# 平台适配
# ═══════════════════════════════════════════════════════════════════════════

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass
    FONT = "Microsoft YaHei UI"
elif sys.platform == "darwin":
    FONT = "Helvetica Neue"
else:
    FONT = "Noto Sans"

C_SUCCESS = "#059669"


# ═══════════════════════════════════════════════════════════════════════════
# VS Code 前台检测
# ═══════════════════════════════════════════════════════════════════════════

def _is_vscode_foreground():
    """检测 VS Code / Code Insiders 是否为前台窗口（仅 Windows）。"""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return False

        pid = wintypes.DWORD(0)
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return False

        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        h_proc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                                       False, pid.value)
        if not h_proc:
            return False
        try:
            buf = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            if psapi.GetModuleBaseNameW(h_proc, None, buf, size):
                return buf.value.lower() in ("code.exe", "code-insiders.exe")
            return False
        finally:
            kernel32.CloseHandle(h_proc)
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════
# 工具名提取 & 分类
# ═══════════════════════════════════════════════════════════════════════════

_EXEC_TOOLS = {
    "Bash", "Write", "Edit", "Read",
    "Glob", "Grep",
    "WebFetch", "WebSearch",
    "NotebookEdit",
    "TaskStop", "CronCreate",
    "Task", "Agent", "Workflow",
    "Skill",
    "EnterPlanMode", "ExitPlanMode",
    "ListMcpResourcesTool", "ReadMcpResourceTool", "ReadMcpResourceDirTool",
}
_INTERACTIVE_TOOLS = set()  # 预留


def _get_tool_name(data):
    """从 hook 输入数据中提取工具名。"""
    inner = data.get("hookSpecificInput") or data
    return inner.get("toolName") or inner.get("tool_name") or ""


# ═══════════════════════════════════════════════════════════════════════════
# 通用弹窗 GUI — 中文授权窗口
# ═══════════════════════════════════════════════════════════════════════════

_POPUP_W = 530
_POPUP_H = 310
_BG = "#1e1e1e"
_BORDER = "#333333"          # 窗口边框色
_DESC_BG = "#252525"         # 详情区背景（略亮于主背景）
_FG = "#ffffff"
_FG_SECONDARY = "#cccccc"
# 按钮色 — 鲜明现代
_BTN_ALLOW_BG      = "#2ea043"
_BTN_ALLOW_HOVER   = "#3fb950"
_BTN_ALWAYS_BG     = "#1f6feb"
_BTN_ALWAYS_HOVER  = "#388bfd"
_BTN_DENY_BG       = "#da3633"
_BTN_DENY_HOVER    = "#f85149"

# 固定分区高度
_TITLE_H = 36       # 标题
_TOOLNAME_H = 24    # 工具名行
_DESC_H = 120       # 详情滚动区
_PROMPT_H = 24      # "是否允许" 提示
_BTN_H = 40         # 按钮行
_PAD_TOP = 16
_PAD_SIDE = 20

# 工具中文名映射（覆盖 _EXEC_TOOLS 全量及常用工具）
_TOOL_CN = {
    "Bash": "执行命令",
    "Write": "写入文件",
    "Edit": "编辑文件",
    "Read": "读取文件",
    "Glob": "搜索文件",
    "Grep": "搜索内容",
    "Agent": "启动子任务",
    "Workflow": "启动工作流",
    "WebSearch": "搜索网页",
    "WebFetch": "获取网页",
    "Task": "后台任务",
    "TaskStop": "停止任务",
    "Skill": "调用技能",
    "NotebookEdit": "编辑笔记本",
    "CronCreate": "创建定时任务",
    "EnterPlanMode": "进入计划模式",
    "ExitPlanMode": "退出计划模式",
    "ListMcpResourcesTool": "列出 MCP 资源",
    "ReadMcpResourceTool": "读取 MCP 资源",
    "ReadMcpResourceDirTool": "读取 MCP 资源目录",
    "SendMessage": "发送消息",
    "ReportFindings": "报告检查结果",
    "ScheduleWakeup": "计划唤醒",
    "DesignSync": "设计同步",
    "TodoWrite": "更新任务列表",
    "CronDelete": "删除定时任务",
    "CronList": "列出定时任务",
}


def _tool_action_desc(tool_name, tool_input):
    """提取操作参数详情，用于弹窗详情区（不含中文工具名——工具名行已显示）。"""
    if not tool_input:
        return ""
    t = tool_name
    if t == "Bash":
        cmd = (tool_input.get("command") or tool_input.get("cmd") or "")
        return cmd[:2000]
    if t in ("Write", "Edit", "Read"):
        return tool_input.get("file_path", "")
    if t == "Glob":
        return tool_input.get("pattern", "")
    if t in ("WebSearch",):
        return tool_input.get("query", "")
    if t == "WebFetch":
        return tool_input.get("url", "")
    if t in ("Agent", "Workflow"):
        desc = (tool_input.get("prompt") or tool_input.get("description") or "")
        return desc[:2000]
    # 通用 fallback
    for v in tool_input.values():
        if isinstance(v, str) and len(v) > 5:
            return v[:2000]
    return ""


def _popup_geometry(root, w, h):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


def _can_always_allow(data):
    """检查 permission_suggestions 是否支持始终允许。

    根据 suggestions 中的 type 判断：
      - addRules 等可持久化的类型 → 支持始终允许
      - 仅有 addDirectories (session) 等临时类型 → 不支持
    """
    suggestions = data.get("permission_suggestions")
    if suggestions is None:
        return True  # 无 suggestions → 默认支持（向后兼容）
    if isinstance(suggestions, list):
        for s in suggestions:
            if not isinstance(s, dict):
                continue
            stype = s.get("type", "")
            # 可持久化的 suggestion 类型 → 支持始终允许
            if stype in ("addRules", "addGlobalPermission", "persistPermission"):
                return True
            if "rules" in s or "globalPermission" in s:
                # 验证 rules/globalPermission 非空才有意义
                rules_val = s.get("rules")
                gp_val = s.get("globalPermission")
                if isinstance(rules_val, list) and len(rules_val) > 0:
                    return True
                if isinstance(gp_val, str) and gp_val:
                    return True
        # 没有可持久化的建议 → 只有通过与不通过
        return False
    return True  # 其他格式 → 默认支持


def _gui_permission_popup(data, tool_name, show_always=True):
    """模态弹窗 → 返回 "allow" | "always" | "deny" | None(透传)。

    布局：固定分区，详情区可滚动。
    """
    # 从 hookSpecificInput 中提取 tool_input（兼容不同数据格式）
    inner = data.get("hookSpecificInput") or data
    tool_input = inner.get("tool_input") or {}
    action_desc = _tool_action_desc(tool_name, tool_input)

    root = tk.Tk()
    root.title("")
    root.resizable(False, False)
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg=_BORDER)  # 边框色
    _popup_geometry(root, _POPUP_W, _POPUP_H)

    # 主容器 — padx/pady=1 露出 root 背景作为 1px 边框
    frame = tk.Frame(root, bg=_BG)
    frame.pack(fill="both", expand=True, padx=1, pady=1)

    # ── 标题区 ──
    title_lbl = tk.Label(frame, text="🔐  权限请求", font=(FONT, 14, "bold"),
                          fg=_FG, bg=_BG, anchor="w")
    title_lbl.pack(fill="x", padx=_PAD_SIDE - 1, pady=(_PAD_TOP - 1, 0))

    # ── 分隔线 ──
    sep = tk.Frame(frame, bg=_BORDER, height=1)
    sep.pack(fill="x", padx=_PAD_SIDE - 1, pady=(8, 0))

    # ── 工具名行（显示英文+中文） ──
    cn_name = _TOOL_CN.get(tool_name, "")
    tool_text = f"工具：{tool_name}" + (f"  —  {cn_name}" if cn_name else "")
    tool_lbl = tk.Label(frame, text=tool_text, font=(FONT, 11),
                         fg=_FG_SECONDARY, bg=_BG, anchor="w")
    tool_lbl.pack(fill="x", padx=_PAD_SIDE - 1, pady=(6, 0))

    # ── 详情滚动区（固定 _DESC_H） ──
    desc_container = tk.Frame(frame, bg=_DESC_BG, height=_DESC_H)
    desc_container.pack(fill="x", padx=_PAD_SIDE - 1, pady=(6, 0))
    desc_container.pack_propagate(False)

    desc_text = tk.Text(desc_container, font=(FONT, 10),
                         fg="#bbbbbb", bg=_DESC_BG,
                         wrap="char", padx=8, pady=6,
                         relief="flat", borderwidth=0,
                         highlightthickness=0)
    desc_text.insert("1.0", action_desc)
    desc_text.config(state="disabled")

    desc_scroll = tk.Scrollbar(desc_container, orient="vertical",
                                command=desc_text.yview,
                                bg="#555555", troughcolor=_DESC_BG,
                                activebackground="#888888", elementborderwidth=1)
    desc_text.config(yscrollcommand=desc_scroll.set)

    desc_text.pack(side="left", fill="both", expand=True)
    desc_scroll.pack(side="right", fill="y")

    # ── 提示文字 ──
    tk.Label(frame, text="是否允许此操作？", font=(FONT, 10),
             fg="#888888", bg=_BG, anchor="w"
             ).pack(fill="x", padx=_PAD_SIDE - 1, pady=(8, 0))

    # ── 按钮行（固定高度） ──
    btn_frame = tk.Frame(frame, bg=_BG, height=_BTN_H)
    btn_frame.pack(fill="x", padx=_PAD_SIDE - 1, pady=(8, _PAD_TOP - 1))
    btn_frame.pack_propagate(False)

    result = {"v": "deny"}  # "allow" | "always" | "deny" | None(透传)

    # 轮询：切回前台时自动关闭弹窗并透传
    def _poll_foreground():
        if _is_vscode_foreground():
            result["v"] = None  # 透传信号
            root.destroy()
        else:
            root.after(500, _poll_foreground)
    root.after(500, _poll_foreground)

    def allow():
        result["v"] = "allow"
        root.destroy()

    def always_allow():
        result["v"] = "always"
        root.destroy()

    def deny():
        result["v"] = "deny"
        root.destroy()

    # 等宽按钮——Label 模拟，Windows 下文字居中可靠
    btn_defs = [("❌ 拒绝", _BTN_DENY_BG, _BTN_DENY_HOVER, deny)]
    if show_always:
        btn_defs.append(("🔁 始终允许", _BTN_ALWAYS_BG, _BTN_ALWAYS_HOVER, always_allow))
    btn_defs.append(("✅ 允许（一次）", _BTN_ALLOW_BG, _BTN_ALLOW_HOVER, allow))
    n_btns = len(btn_defs)
    for i in range(n_btns):
        btn_frame.grid_columnconfigure(i, weight=1, uniform="cbtn")
    for ci, (text, bg, hover, cmd) in enumerate(btn_defs):
        lbl = tk.Label(btn_frame, text=text, font=(FONT, 11, "bold"),
                       fg="white", bg=bg, anchor="center", cursor="hand2")
        lbl.bind("<Button-1>", lambda e: cmd())
        lbl.bind("<Enter>", lambda e: lbl.config(bg=hover))
        lbl.bind("<Leave>", lambda e: lbl.config(bg=bg))
        lbl.bind("<ButtonRelease-1>", lambda e: cmd())
        lbl.grid(row=0, column=ci, padx=(0, 4) if ci < n_btns - 1 else 0, sticky="nsew")

    root.protocol("WM_DELETE_WINDOW", deny)
    root.bind("<Escape>", lambda e: deny())
    root.lift()
    root.focus_force()
    root.grab_set()
    root.wait_window()
    return result["v"]


# ═══════════════════════════════════════════════════════════════════════════
# AskUserQuestion 通知弹窗 — 感知通知，无选项交互
# ═══════════════════════════════════════════════════════════════════════════

_NOTE_W = 320
_NOTE_H = 130


def _gui_ask_notification():
    """后台时弹轻量通知"Claude 正在问你问题"，切回前台自动关闭。"""
    result = {"v": False}

    root = tk.Tk()
    root.title("")
    root.resizable(False, False)
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg=_BORDER)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{_NOTE_W}x{_NOTE_H}+{(sw - _NOTE_W) // 2}+{sh - _NOTE_H - 80}")

    # 边框层
    outer = tk.Frame(root, bg=_BG)
    outer.pack(fill="both", expand=True, padx=1, pady=1)

    # 内容
    frame = tk.Frame(outer, bg=_BG)
    frame.pack(fill="both", expand=True, padx=16, pady=(12, 10))

    tk.Label(frame, text="🤖  Claude 正在问你问题",
             font=(FONT, 12, "bold"), fg=_FG, bg=_BG, anchor="w"
             ).pack(fill="x")
    tk.Label(frame, text="请切回 VS Code 查看",
             font=(FONT, 10), fg=_FG_SECONDARY, bg=_BG, anchor="w"
             ).pack(fill="x", pady=(4, 0))

    def _dismiss():
        result["v"] = True
        root.destroy()

    tk.Button(frame, text="知道了", command=_dismiss,
              font=(FONT, 10, "bold"), bg=_BTN_ALLOW_BG,
              fg="white", padx=20, pady=4, relief="flat",
              cursor="hand2", activebackground=_BTN_ALLOW_HOVER,
              ).pack(pady=(10, 0))

    # 轮询：切回前台时自动关闭
    def _poll():
        if _is_vscode_foreground():
            result["v"] = True
            root.destroy()
        else:
            root.after(500, _poll)
    root.after(500, _poll)

    root.bind("<Escape>", lambda e: root.destroy())
    root.after(30000, root.destroy)  # 最长 30s 自消
    root.lift()
    root.grab_set()
    root.wait_window()
    return result["v"]


# ═══════════════════════════════════════════════════════════════════════════
# PermissionRequest — 旧版 hook 事件（部分工具触发）
# ═══════════════════════════════════════════════════════════════════════════

def show_permission_dialog(data):
    """PermissionRequest — 旧版 hook 事件。

    弹出模式下：静默允许（不弹窗），让 PreToolUse 处理弹窗交互
    auto 模式下：自动放行（兼容旧版 Claude Code 只触发 PermissionRequest 的场景）
    """
    mode = _load_config()
    tool_name = _get_tool_name(data)

    if mode == "popup":
        # PreToolUse 已处理弹窗交互，这里确认决策且不覆盖 PreToolUse 的缓存
        if _is_vscode_foreground():
            return None  # 前台 → 透传
        return {"behavior": "allow"}

    # auto 模式：自动放行
    if tool_name in _EXEC_TOOLS:
        return {"behavior": "allow", "updatedPermissions": []}
    _log(f"[auto-allow-unknown] {tool_name}")
    return {"behavior": "allow", "updatedPermissions": []}


# ═══════════════════════════════════════════════════════════════════════════
# PreToolUse — 新版 hook 事件（所有工具触发，含 Bash）
# ═══════════════════════════════════════════════════════════════════════════

_SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")


def _is_permanently_allowed(tool_name):
    """检查工具是否已在 settings.json 的永久允许列表中。"""
    try:
        if not os.path.exists(_SETTINGS_PATH):
            return False
        with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return tool_name in config.get("permissions", {}).get("allow", [])
    except Exception:
        return False


def _add_to_permanent_allow(tool_name):
    """将工具名永久加入 settings.json 的 permissions.allow 列表。"""
    try:
        if not os.path.exists(_SETTINGS_PATH):
            _log(f"[add-perm] settings.json not found")
            return
        with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        allow = config.setdefault("permissions", {}).setdefault("allow", [])
        if tool_name not in allow:
            allow.append(tool_name)
            with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            _log(f"[add-perm] {tool_name} added to permanent allow")
        else:
            _log(f"[add-perm] {tool_name} already in permanent allow")
    except Exception as exc:
        _log(f"[add-perm-error] {exc}")


def show_pre_tool_use(data):
    """PreToolUse — 新版 hook 事件（所有工具触发）。"""
    tool_name = _get_tool_name(data)
    mode = _load_config()

    # ── AskUserQuestion：全局通知行为 ──
    if tool_name == "AskUserQuestion":
        if _is_vscode_foreground():
            return None  # 前台 → 透传，终端正常显示问题
        _gui_ask_notification()
        return None  # 透传，终端正常提问

    # ── 其他工具：权限检查 ──
    if mode == "popup":
        if _is_vscode_foreground():
            return None  # 前台 → 透传，终端显示原生权限提示

        # 已永久允许 → 直接放行，不弹窗
        if _is_permanently_allowed(tool_name):
            return {"permissionDecision": "allow", "updatedInput": {}}

        # 后台 → 弹出中文 GUI 授权
        show_always = _can_always_allow(data)
        decision = _gui_permission_popup(data, tool_name, show_always)
        if decision is None:
            return None  # 切回前台 → 透传
        if decision == "always":
            _add_to_permanent_allow(tool_name)
            return {"permissionDecision": "allow", "updatedInput": {},
                    "updatedPermissions": [tool_name]}
        if decision == "allow":
            return {"permissionDecision": "allow", "updatedInput": {}}
        return {"permissionDecision": "deny", "updatedInput": {}}

    # auto 模式：自动放行
    if tool_name not in _EXEC_TOOLS:
        _log(f"[auto-allow-unknown] {tool_name}")
    return {"permissionDecision": "allow", "updatedInput": {}}


# ═══════════════════════════════════════════════════════════════════════════
# Stop — 回复完成提醒
# ═══════════════════════════════════════════════════════════════════════════

_DONE_AUTO_CLOSE_MS = 3000
_DONE_W = 320
_DONE_H = 70
_DONE_BORDER = "#047857"  # 边框色（比背景深一号）


def _center(root, w, h):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{sh - h - 60}")


def show_done_dialog(data):
    """回复结束时弹轻量通知（VS Code 前台时跳过）。"""
    if _is_vscode_foreground():
        return {"behavior": "continue"}

    root = tk.Tk()
    root.title("")
    root.resizable(False, False)
    root.overrideredirect(True)
    root.configure(bg=_DONE_BORDER)
    _center(root, _DONE_W, _DONE_H)

    main = tk.Frame(root, bg=C_SUCCESS)
    main.pack(fill="both", expand=True, padx=1, pady=1)

    tk.Label(main,
             text="✅ 回复已完成 — 等待你的下一步",
             font=(FONT, 11, "bold"), fg="#ffffff", bg=C_SUCCESS
             ).pack(expand=True)

    closed = {"v": False}

    def close():
        if closed["v"]:
            return
        closed["v"] = True
        root.destroy()

    root.after(_DONE_AUTO_CLOSE_MS, close)
    root.bind("<Escape>", lambda e: close())
    root.bind("<Return>", lambda e: close())
    root.bind("<Button-1>", lambda e: close())
    root.protocol("WM_DELETE_WINDOW", close)
    root.lift()
    root.focus_force()
    root.mainloop()
    return {"behavior": "continue"}


# ═══════════════════════════════════════════════════════════════════════════
# 事件路由
# ═══════════════════════════════════════════════════════════════════════════

HANDLERS = {
    "PermissionRequest": ("decision",   show_permission_dialog),
    "PreToolUse":        ("permission", show_pre_tool_use),
    "Stop":              ("decision",   show_done_dialog),
}


def main():
    try:
        raw = sys.stdin.buffer.read(_MAX_STDIN_BYTES + 1)
        if not raw:
            return
        if len(raw) > _MAX_STDIN_BYTES:
            _log(f"[stdin-rejected] input too large: {len(raw)} bytes")
            return
        data = json.loads(raw.decode())
    except Exception:
        _log(f"[stdin-error] {traceback.format_exc()}")
        return

    event = data.get("hook_event_name", "")
    try:
        entry = HANDLERS.get(event)
        if entry is None:
            _log(f"Unknown event: {event}")
            return

        mode, handler = entry
        result = handler(data)

        if result is None:
            return  # 透传，不输出决策，Claude Code 走默认行为

        if mode == "decision":
            # PermissionRequest: result 是 behavior dict，直接放 hookSpecificOutput
            # Stop 等其他 decision 事件：保留原有的 hookEventName/decision 嵌套
            if event == "PermissionRequest":
                output = {
                    "hookSpecificOutput": result,
                }
            else:
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": event,
                        "decision": result,
                    }
                }
        elif mode == "permission":
            output = {
                "hookSpecificOutput": {"updatedInput": result.get("updatedInput", {})},
                "systemMessage": "",
            }
            pd = result.get("permissionDecision")
            if pd:
                output["permissionDecision"] = pd
            up = result.get("updatedPermissions")
            if up:
                output["updatedPermissions"] = up
        else:
            return

        print(json.dumps(output, ensure_ascii=False), flush=True)
    except Exception:
        _log(f"[gui-error] {traceback.format_exc()}")


if __name__ == "__main__":
    main()
