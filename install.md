# Installation Guide

## Prerequisites

- Claude Code (installed and working)
- Python 3.8+
- (Windows) VS Code / Code Insiders — required for foreground detection

---

## Installation

### One-liner (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/Beijongggg/notify-hooks/9b5b85edb41236becb4a1752de19c56c84e23ea1/install.py -o install.py && python install.py
```

Automatically downloads notify.py → creates config → merges hooks → verifies setup.

### Manual Installation

<details>
<summary>Expand manual steps</summary>

#### 1. Copy the script

```bash
mkdir -p ~/.claude/hooks
cp hooks/notify.py ~/.claude/hooks/notify.py
```

#### 2. (Optional) Copy config file

```bash
cp config.example.json ~/.claude/hooks/config.json
```

Without a config file, the hook runs in **`auto` (auto-approve)** mode — all tools are auto-approved with no dialogs.

#### 3. Configure Claude Code

Edit Claude Code's settings.json and add the following hooks:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/notify.py" }
        ]
      }
    ],
    "PermissionRequest": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/notify.py" }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/notify.py" }
        ]
      }
    ]
  }
}
```

Config file locations:
- **User-level**: `~/.claude/settings.json`
- **Project-level**: `.claude/settings.json`
- **Open in VS Code**: `Ctrl+Shift+P` → `Claude Code: Open Settings (JSON)`

</details>

---

## Switching Modes

Edit `~/.claude/hooks/config.json` and change the `mode` field:

```json
{ "mode": "auto" }     // Auto-approve (default, no dialogs)
{ "mode": "popup" }    // Permission dialog, manual confirmation for each action
```

Changes take effect **immediately** — no restart required.

---

## Verifying Installation

Restart Claude Code and observe the following behavior:

**auto mode:**
- Performing an action requiring authorization → Auto-approved, no dialog

**popup mode:**
- Performing an action (VSCode in background) → Permission dialog appears
- Performing an action (VSCode in foreground) → Terminal shows native permission prompt
- Claude asks a question (background) → "🤖 Claude is asking you a question" notification
- Claude asks a question (foreground) → Question appears directly in terminal

**Both modes:**
- Response complete (background) → Green toast "✅ Response complete" auto-dismiss in 3 seconds
- Response complete (foreground) → No notification

---

## Uninstall

```bash
# 1. Remove hooks config from settings.json
# 2. Delete script and config files
rm ~/.claude/hooks/notify.py
rm ~/.claude/hooks/config.json
```

---

## Troubleshooting

```bash
# View error log
cat ~/.claude/hooks/notify_error.log
```

Common issues:

| Issue | Cause | Solution |
|-------|-------|----------|
| Dialog not appearing | Hooks config is wrong | Check hooks format in settings.json |
| Dialog not appearing | Currently in auto mode | Change mode to "popup" in config.json |
| Dialog flashes and disappears | VSCode is in foreground | Switch to another window — dialog will persist |
| Chinese text garbled | Encoding mismatch | Ensure Python/terminal use UTF-8 |
