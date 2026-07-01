#!/usr/bin/env python3
"""notify-hooks 一键安装 — 从 GitHub 拉取并部署

用法（一行命令）:
    curl -fsSL https://raw.githubusercontent.com/Beijongggg/notify-hooks/master/install.py | python
    或
    python install.py          # 已下载脚本后本地执行
    python install.py --check  # 仅验证安装状态
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# ── 常量 ──────────────────────────────────────────────────────────────────────

GITHUB_RAW = "https://raw.githubusercontent.com/Beijongggg/notify-hooks/master"
NOTIFY_URL = f"{GITHUB_RAW}/hooks/notify.py"

HOME = Path(os.path.expanduser("~"))
HOOKS_DIR = HOME / ".claude" / "hooks"
TARGET_SCRIPT = HOOKS_DIR / "notify.py"
TARGET_CONFIG = HOOKS_DIR / "config.json"
SETTINGS_PATH = HOME / ".claude" / "settings.json"

# Hooks 配置模板
HOOK_ENTRY = {
    "matcher": "",
    "hooks": [{"type": "command", "command": "python ~/.claude/hooks/notify.py"}],
}

HOOKS_TEMPLATE = {
    "PreToolUse": [HOOK_ENTRY],
    "PermissionRequest": [HOOK_ENTRY],
    "Stop": [HOOK_ENTRY],
}

# 默认 config.json 内容
DEFAULT_CONFIG = """\
{
  "mode": "auto",
  "_description": "授权模式: 'auto' = 自动放行不弹窗（默认）; 'popup' = GUI弹窗授权，需手动确认"
}
"""

# ── 输出辅助 ──────────────────────────────────────────────────────────────────

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_CHECK = "[OK]"
_WARN = "[!!]"
_FAIL = "[XX]"


def ok(msg):
    print(f"  {_CHECK} {msg}")


def warn(msg):
    print(f"  {_WARN} {msg}")


def fail(msg):
    print(f"  {_FAIL} {msg}")


# ── 网络获取 ──────────────────────────────────────────────────────────────────

def fetch(url, dest):
    """从 URL 下载文件到 dest，带超时和重试。"""
    import urllib.request

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "notify-hooks-installer"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                dest.write_bytes(resp.read())
            return True
        except Exception as exc:
            if attempt == 2:
                fail(f"下载失败: {url} — {exc}")
                return False
            print(f"    重试 ({attempt + 2}/3)...")
    return False


# ── 安装步骤 ──────────────────────────────────────────────────────────────────

def check_python():
    ver = sys.version_info
    if ver < (3, 8):
        fail(f"需要 Python >= 3.8，当前 {ver.major}.{ver.minor}")
        return False
    ok(f"Python {ver.major}.{ver.minor}.{ver.micro}")
    return True


def download_notify():
    """从 GitHub 下载 notify.py。"""
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    if not fetch(NOTIFY_URL, TARGET_SCRIPT):
        return False
    ok(f"已下载 notify.py → {TARGET_SCRIPT}")
    return True


def create_config():
    """创建默认 config.json（仅当不存在时）。"""
    if TARGET_CONFIG.exists():
        ok("config.json 已存在，跳过")
        return True
    TARGET_CONFIG.write_text(DEFAULT_CONFIG, encoding="utf-8")
    ok(f"已创建 config.json → {TARGET_CONFIG}")
    return True


def merge_hooks():
    """合并 hooks 到 settings.json，保留已有配置。"""
    if SETTINGS_PATH.exists():
        try:
            cfg = json.loads(SETTINGS_PATH.read_text("utf-8"))
            if not isinstance(cfg, dict):
                cfg = {}
        except json.JSONDecodeError:
            warn("settings.json 格式错误，将覆盖")
            cfg = {}
    else:
        cfg = {}

    existing_hooks = cfg.get("hooks", {})
    if not isinstance(existing_hooks, dict):
        existing_hooks = {}

    added = []
    skipped = []
    for event in HOOKS_TEMPLATE:
        if _hook_already_registered(existing_hooks, event):
            skipped.append(event)
        elif event in existing_hooks:
            existing_hooks[event][0]["hooks"].append(
                HOOKS_TEMPLATE[event][0]["hooks"][0]
            )
            added.append(event)
        else:
            existing_hooks[event] = HOOKS_TEMPLATE[event]
            added.append(event)

    if added:
        cfg["hooks"] = existing_hooks
        # 备份
        if SETTINGS_PATH.exists():
            backup_path = SETTINGS_PATH.with_suffix(
                f".json.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            )
            shutil.copy2(SETTINGS_PATH, backup_path)
            ok(f"已备份 settings.json → {backup_path.name}")

        SETTINGS_PATH.write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        ok(f"已添加 hooks 事件: {', '.join(added)}")
    else:
        ok("hooks 配置已是最新，无需修改")

    if skipped:
        ok(f"已存在，跳过: {', '.join(skipped)}")

    return True


def _hook_already_registered(existing_hooks, event):
    entries = existing_hooks.get(event, [])
    for entry in entries:
        for h in entry.get("hooks", []):
            if "notify.py" in h.get("command", ""):
                return True
    return False


def verify():
    """验证安装。"""
    errors = []

    if not TARGET_SCRIPT.exists():
        errors.append(f"脚本缺失: {TARGET_SCRIPT}")

    if not SETTINGS_PATH.exists():
        errors.append(f"settings.json 不存在: {SETTINGS_PATH}")
    else:
        try:
            cfg = json.loads(SETTINGS_PATH.read_text("utf-8"))
            hooks = cfg.get("hooks", {})
            for event in HOOKS_TEMPLATE:
                if event not in hooks:
                    errors.append(f"settings.json 缺少 {event} hook")
        except json.JSONDecodeError:
            errors.append("settings.json 格式错误")

    if errors:
        for e in errors:
            fail(e)
        return False
    ok("安装验证通过")
    return True


# ── 入口 ──────────────────────────────────────────────────────────────────────

def install():
    print("notify-hooks 安装\n")
    steps = [
        ("Python 版本", check_python),
        ("下载 notify.py", download_notify),
        ("创建 config.json", create_config),
        ("合并 hooks", merge_hooks),
        ("验证安装", verify),
    ]

    for label, fn in steps:
        print(f"[{label}]")
        if not fn():
            print(f"\n安装中断: {label} 失败")
            return 1
        print()

    print("─" * 40)
    print("安装完成！")
    print(f"  模式: auto（默认自动放行）")
    print(f"  切换: 编辑 {TARGET_CONFIG}")
    print(f"  日志: {HOOKS_DIR / 'notify_error.log'}")
    print(f"  重启 Claude Code 即可生效")
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        print("notify-hooks 安装检查\n")
        sys.exit(0 if verify() else 1)
    sys.exit(install())
