# Habit Tracker TUI

A simple terminal UI for tracking daily habits, built with [Textual](https://textual.textualize.io/).

## Setup

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

Or without installing:

```bash
python -m habit_tracker.app
```

## Controls

| Key | Action |
|-----|--------|
| `a` | Add a new habit |
| `Space` | Toggle selected habit for today |
| `d` | Delete selected habit |
| `q` | Quit |

## Data

Habits are saved to `~/.habit-tracker-tui/habits.json`.

## Try with Cursor

Good follow-up prompts:

- "Add a weekly summary view"
- "Color completed rows green"
- "Show longest streak in the header"
- "Export habits to CSV"
