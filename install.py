#!/usr/bin/env python3
"""notify-hooks 一键安装脚本

用法:
    python install.py          # 安装
    python install.py --check  # 仅验证安装状态
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Windows 强制 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ASCII 兼容符号
_CHECK = "[OK]"
_WARN = "[!!]"
_FAIL = "[XX]"

# 路径常量
HOME = Path(os.path.expanduser("~"))
HOOKS_DIR = HOME / ".claude" / "hooks"
TARGET_SCRIPT = HOOKS_DIR / "notify.py"
TARGET_CONFIG = HOOKS_DIR / "config.json"
SETTINGS_PATH = HOME / ".claude" / "settings.json"

# 项目根目录（install.py 所在目录）
PROJECT_DIR = Path(os.path.abspath(__file__)).parent
SOURCE_SCRIPT = PROJECT_DIR / "hooks" / "notify.py"
SOURCE_CONFIG = PROJECT_DIR / "config.example.json"

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


# ═══════════════════════════════════════════════════════════════════════════════
# 辅助
# ═══════════════════════════════════════════════════════════════════════════════

def ok(msg):
    print(f"  {_CHECK} {msg}")


def warn(msg):
    print(f"  {_WARN} {msg}")


def fail(msg):
    print(f"  {_FAIL} {msg}")


def _hook_already_registered(existing_hooks, event):
    """检查 settings.json 中某个 hook 事件是否已注册 notify.py。"""
    entries = existing_hooks.get(event, [])
    for entry in entries:
        for h in entry.get("hooks", []):
            cmd = h.get("command", "")
            if "notify.py" in cmd:
                return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# 步骤
# ═══════════════════════════════════════════════════════════════════════════════

def check_python():
    """检查 Python 版本。"""
    ver = sys.version_info
    if ver < (3, 8):
        fail(f"需要 Python >= 3.8，当前 {ver.major}.{ver.minor}")
        return False
    ok(f"Python {ver.major}.{ver.minor}.{ver.micro}")
    return True


def copy_script():
    """复制 notify.py 到 ~/.claude/hooks/。"""
    if not SOURCE_SCRIPT.exists():
        fail(f"源文件不存在: {SOURCE_SCRIPT}")
        return False
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_SCRIPT, TARGET_SCRIPT)
    ok(f"已复制 notify.py → {TARGET_SCRIPT}")
    return True


def copy_config():
    """复制 config.example.json（仅当目标不存在时）。"""
    if TARGET_CONFIG.exists():
        ok("config.json 已存在，跳过")
        return True
    if SOURCE_CONFIG.exists():
        shutil.copy2(SOURCE_CONFIG, TARGET_CONFIG)
        ok(f"已复制 config.json → {TARGET_CONFIG}")
    else:
        warn("config.example.json 不存在，跳过（将使用默认 auto 模式）")
    return True


def merge_hooks():
    """合并 hooks 配置到 settings.json，保留已有设置。"""
    # 读取已有 settings
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

    # 检查是否需要添加
    added = []
    skipped = []
    for event in HOOKS_TEMPLATE:
        if _hook_already_registered(existing_hooks, event):
            skipped.append(event)
        elif event in existing_hooks:
            # 事件已存在但没有 notify.py → 追加到第一个 matcher 组
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
        backup_path = SETTINGS_PATH.with_suffix(
            f".json.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        if SETTINGS_PATH.exists():
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


def verify():
    """验证安装是否完整。"""
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


# ═══════════════════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════════════════

def install():
    print("notify-hooks 安装\n")
    steps = [
        ("Python 版本", check_python),
        ("复制脚本", copy_script),
        ("复制配置", copy_config),
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
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        print("notify-hooks 安装检查\n")
        sys.exit(0 if verify() else 1)
    sys.exit(install())
