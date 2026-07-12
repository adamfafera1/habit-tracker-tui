# Habit Tracker TUI

A simple terminal UI for tracking daily habits, built with [Textual](https://textual.textualize.io/).

## Quick install

On a new machine, clone the repo and run:

```bash
git clone <repo-url> habit-tracker-tui
cd habit-tracker-tui
./scripts/install.sh
```

This will:

- create a local `.venv` and install dependencies
- install `pipx` if needed
- install the global `habits` command

Restart your terminal if `habits` is not found, then run:

```bash
habits
```

For the macOS menu bar widget too:

```bash
./scripts/install.sh --swiftbar
```

Use a custom SwiftBar plugin folder if you already have one:

```bash
./scripts/install.sh --swiftbar ~/path/to/your/swiftbarplugins
```

## Manual setup

```bash
cd habit-tracker-tui
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```bash
habits
```

Or without installing globally:

```bash
python -m habit_tracker.app
```

## Install globally (manual)

To run `habits` from any terminal without activating the venv, install with [pipx](https://github.com/pypa/pipx):

```bash
brew install pipx
pipx ensurepath

cd habit-tracker-tui
pipx install -e .
```

Restart your terminal, then `habits` works everywhere.

## Features

- Daily habit list with current streak and best streak
- Toggle habits for today with one keypress
- Header showing today's date, completion count, and top streak
- Completed habits highlighted in green
- Weekly summary with a GitHub-style contribution grid (`w`)
- CSV export of all completions (`e`)
- macOS menu bar widget via SwiftBar (optional)

## Controls

Use arrow keys to move between habits in the main table.

### Main screen

| Key | Action |
|-----|--------|
| `a` | Add a new habit |
| `Space` / `Enter` | Toggle selected habit for today |
| `r` | Rename selected habit |
| `d` | Delete selected habit |
| `w` | Open weekly summary (last 7 days) |
| `e` | Export completions to CSV |
| `q` | Quit |

### Prompts (add / rename)

| Key | Action |
|-----|--------|
| `Enter` | Save |
| `Esc` | Cancel |

### Delete confirmation

| Key | Action |
|-----|--------|
| `y` | Confirm delete |
| `n` / `Esc` | Cancel |

### Weekly summary

| Key | Action |
|-----|--------|
| `Esc` / `q` | Close |

The weekly view shows a GitHub-style grid for the last 7 days: one row per habit, plus an **All** row with shaded squares based on how many habits were completed that day.

## Data

Habits are saved to `~/.habit-tracker-tui/habits.json`.

CSV exports are written to `~/.habit-tracker-tui/habits-export.csv`.

## Menu bar widget (macOS)

You can show today's habits in the menu bar with [SwiftBar](https://github.com/swiftbar/SwiftBar). The plugin reads the same `habits.json` file as the TUI, so changes sync both ways.

The installer can set this up for you:

```bash
./scripts/install.sh --swiftbar
```

Or follow these steps manually:

### 1. Install SwiftBar

```bash
brew install --cask swiftbar
```

### 2. Choose a plugin folder

Open SwiftBar. On first launch it asks for a plugin folder — pick or create one, for example:

```bash
mkdir -p ~/Desktop/swiftbarplugins
```

Use that same folder in SwiftBar's setup dialog.

### 3. Install the habits plugin

From the repo root (after setup above):

```bash
PLUGIN_DIR="$HOME/Desktop/swiftbarplugins"   # use the folder you chose in SwiftBar
REPO_ROOT="$(pwd)"

cat > "$PLUGIN_DIR/habits.1m.sh" << EOF
#!/bin/bash
# <swiftbar.hideFromHistory>true</swiftbar.hideFromHistory>

REPO_ROOT="$REPO_ROOT"
PYTHON="\${HABITS_PYTHON:-\$REPO_ROOT/.venv/bin/python3}"

if [[ ! -x "\$PYTHON" ]]; then
  PYTHON="\$(command -v python3)"
fi

exec "\$PYTHON" "\$REPO_ROOT/scripts/swiftbar_habits.py" "\$@"
EOF

chmod +x "$PLUGIN_DIR/habits.1m.sh"
```

If your plugin folder is somewhere else, change `PLUGIN_DIR` to match.

### 4. Launch and refresh

```bash
open -a SwiftBar
```

You should see something like `2/5 habits` or `✅ 2/2` in the menu bar. If not:

1. Click **Swiftbar** in the menu bar
2. Choose **Refresh all**

Enable **Launch at login** in SwiftBar preferences if you want it to start automatically.

### What you get

| Area | Behavior |
|------|----------|
| Menu bar | `2/5 habits`, or `✅ 2/2` when all habits are done |
| Dropdown | Each habit with ✅/⬜ and current streak |
| Click a habit | Toggle it for today |
| Open habit tracker | Launch the terminal app |

The plugin refreshes every minute (`habits.1m.sh`). Rename to `habits.30s.sh` or `habits.5m.sh` to change the interval.

## Try with Cursor

Good follow-up prompts:

- "Add monthly stats view"
- "Sort habits by streak"
- "Import habits from CSV"
- "Add habit categories or tags"
