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
    "ListMcpResourcesTool", "ReadMcpResourceTool",
}
_INTERACTIVE_TOOLS = set()  # 预留


def _get_tool_name(data):
    """从 hook 输入数据中提取工具名。"""
    inner = data.get("hookSpecificInput") or data
    return inner.get("toolName") or inner.get("tool_name") or ""


# ═══════════════════════════════════════════════════════════════════════════
# 通用弹窗 GUI
# ═══════════════════════════════════════════════════════════════════════════

_POPUP_W = 440
_POPUP_H = 220
_BG = "#1e1e1e"
_FG = "#ffffff"
_FG_SECONDARY = "#cccccc"
_BTN_ALLOW_BG = "#2d8c3c"
_BTN_DENY_BG = "#8c2d2d"


def _popup_geometry(root, w, h):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


def _gui_permission_popup(data, tool_name):
    """模态弹窗 → 返回 True(允许) 或 False(拒绝)。"""
    root = tk.Tk()
    root.title("")
    root.resizable(False, False)
    root.overrideredirect(True)
    root.configure(bg=_BG)
    _popup_geometry(root, _POPUP_W, _POPUP_H)

    frame = tk.Frame(root, bg=_BG, padx=24, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="🔐  权限请求", font=(FONT, 14, "bold"),
             fg=_FG, bg=_BG, anchor="w").pack(fill="x")
    tk.Label(frame, text=f"工具：{tool_name}", font=(FONT, 12),
             fg=_FG_SECONDARY, bg=_BG, anchor="w").pack(fill="x", pady=(12, 4))
    tk.Label(frame, text="此操作将调用以上工具，是否继续？", font=(FONT, 10),
             fg="#888888", bg=_BG, anchor="w").pack(fill="x")

    btn_frame = tk.Frame(frame, bg=_BG)
    btn_frame.pack(fill="x", pady=(18, 0))

    result = {"v": False}

    def allow():
        result["v"] = True
        root.destroy()

    def deny():
        result["v"] = False
        root.destroy()

    tk.Button(btn_frame, text="✅ 允许", command=allow,
              font=(FONT, 11, "bold"), bg=_BTN_ALLOW_BG,
              fg="white", padx=24, pady=6, relief="flat",
              cursor="hand2", activebackground="#3aad4e"
              ).pack(side="right", padx=(10, 0))
    tk.Button(btn_frame, text="❌ 拒绝", command=deny,
              font=(FONT, 11), bg=_BTN_DENY_BG,
              fg="white", padx=24, pady=6, relief="flat",
              cursor="hand2", activebackground="#b03a3a"
              ).pack(side="right")

    root.protocol("WM_DELETE_WINDOW", deny)
    root.bind("<Escape>", lambda e: deny())
    root.lift()
    root.focus_force()
    root.grab_set()
    root.wait_window()
    return result["v"]


# ═══════════════════════════════════════════════════════════════════════════
# PermissionRequest — 旧版 hook 事件（部分工具触发）
# ═══════════════════════════════════════════════════════════════════════════

def show_permission_dialog(data):
    mode = _load_config()
    tool_name = _get_tool_name(data)

    if mode == "popup":
        allowed = _gui_permission_popup(data, tool_name)
        if allowed:
            return {"behavior": "allow", "updatedPermissions": []}
        return {"behavior": "deny"}

    # auto 模式
    if tool_name in _EXEC_TOOLS:
        return {"behavior": "allow", "updatedPermissions": []}
    _log(f"[auto-allow-unknown] {tool_name}")
    return {"behavior": "allow", "updatedPermissions": []}


# ═══════════════════════════════════════════════════════════════════════════
# PreToolUse — 新版 hook 事件（所有工具触发，含 Bash）
# ═══════════════════════════════════════════════════════════════════════════

def show_pre_tool_use(data):
    mode = _load_config()
    tool_name = _get_tool_name(data)

    if mode == "popup":
        allowed = _gui_permission_popup(data, tool_name)
        decision = "allow" if allowed else "deny"
        return {"permissionDecision": decision, "updatedInput": {}}

    # auto 模式
    return {"permissionDecision": "allow", "updatedInput": {}}


# ═══════════════════════════════════════════════════════════════════════════
# Stop — 回复完成提醒
# ═══════════════════════════════════════════════════════════════════════════

_DONE_AUTO_CLOSE_MS = 3000
_DONE_W = 280
_DONE_H = 64


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
    root.configure(bg=C_SUCCESS)
    _center(root, _DONE_W, _DONE_H)

    main = tk.Frame(root, bg=C_SUCCESS)
    main.pack(fill="both", expand=True)

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

        if mode == "decision":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "decision": result,
                }
            }
        elif mode == "permission":
            output = {
                "hookSpecificOutput": result,
                "systemMessage": "",
            }
        else:
            return

        print(json.dumps(output, ensure_ascii=False))
    except Exception:
        _log(f"[gui-error] {traceback.format_exc()}")


if __name__ == "__main__":
    main()
