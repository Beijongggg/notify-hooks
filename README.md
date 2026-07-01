<div align="center">

# Claude Code Notify Hooks

**v1.0.0** — GUI permission dialogs & completion notifications for Claude Code

[![Version](https://img.shields.io/github/v/tag/Beijongggg/notify-hooks?label=version)](https://github.com/Beijongggg/notify-hooks/tags)
[![License](https://img.shields.io/github/license/Beijongggg/notify-hooks)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)

</div>

---

## 📖 Overview

Replaces native terminal permission prompts with GUI dialogs when Claude Code runs in the background, via the Claude Code Hooks system.

| Hook | Purpose |
|------|---------|
| **PreToolUse** | Shows a permission dialog (in Chinese) with tool name & operation details before tool execution |
| **Stop** | Shows a green notification toast "✅ Response complete" after Claude finishes |
| **PermissionRequest** | Legacy event support — ensures all permission requests are intercepted |

```
VSCode foreground → Native terminal prompts (no distraction while editing)
VSCode background → GUI permission dialog (glance and know what's happening)
Response complete   → Green toast, auto-dismiss in 3 seconds
Claude asks question → Lightweight notification reminder
```

> ⚠️ **Auto-approves all execution tools by default.** Recommended for personal/small projects only.

---

## 🚀 Quick Start

```bash
curl -fsSL https://raw.githubusercontent.com/Beijongggg/notify-hooks/9b5b85edb41236becb4a1752de19c56c84e23ea1/install.py -o install.py && python install.py
```

Restart Claude Code and you're good to go.

> See [install.md](install.md) for detailed instructions.

---

## 🔀 Permission Modes

Edit `~/.claude/hooks/config.json` to switch modes — takes effect immediately:

| Mode | Setting | Behavior |
|------|---------|----------|
| **auto** (default) | `"mode": "auto"` | All tools auto-approved, no dialogs |
| **popup** | `"mode": "popup"` | GUI permission dialog when in background, manual confirmation required |

### Dialog Features

- Chinese display names for 20+ tools (Bash → "Execute Command", Write → "Write File", etc.)
- Operation detail preview (command, file path, search query)
- ❌ Deny / 🔁 Always Allow (cached) / ✅ Allow (once)
- "Always Allow" auto-writes to `settings.json`, no more prompts for that tool

---

## 📁 Project Structure

```
notify-hooks/
├── hooks/notify.py           ← Main script (all dialog logic)
├── config.example.json       ← Config file template
├── settings.example.json     ← Full settings.json example
├── install.md                ← Detailed installation guide
├── CHANGELOG.md              ← Version history
└── README.md                 ← This file
```

---

## 💻 Requirements

- Claude Code (any version)
- Python 3.8+
- **Windows**: Full foreground/background detection
- **macOS / Linux**: Basic notification support

---

## 🔧 Troubleshooting

```bash
cat ~/.claude/hooks/notify_error.log
```

- **Dialog not showing** → Check hooks config, make sure `mode` is set to `"popup"`
- **Chinese text garbled** → Ensure terminal / Python uses UTF-8 encoding
- **Permissions not taking effect** → Restart Claude Code to reload hooks

See [install.md](install.md) for more details.
