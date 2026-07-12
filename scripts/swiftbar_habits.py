#!/usr/bin/env python3
"""Output habit status in SwiftBar's xbar-compatible format."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from habit_tracker.storage import load_habits, save_habits


def escape_swiftbar(text: str) -> str:
    return text.replace("|", "\\|")


def python_executable() -> Path:
    return Path(sys.executable).resolve()


def script_path() -> Path:
    return Path(__file__).resolve()


def habits_executable() -> Path | None:
    venv_habits = REPO_ROOT / ".venv" / "bin" / "habits"
    if venv_habits.exists():
        return venv_habits.resolve()

    for candidate in Path("/opt/homebrew/bin/habits"), Path("/usr/local/bin/habits"):
        if candidate.exists():
            return candidate.resolve()

    return None


def toggle_habit(habit_id: str) -> None:
    habits = load_habits()
    for habit in habits:
        if habit.id == habit_id:
            habit.toggle_today()
            save_habits(habits)
            return


def toggle_url(habit_id: str) -> str:
    python = python_executable()
    script = script_path()
    return (
        f"shell={python} "
        f"param1={script} "
        f"param2=--toggle "
        f"param3={habit_id} "
        f"refresh=true terminal=false"
    )


def render() -> None:
    habits = load_habits()
    today = date.today().strftime("%a, %d %b")

    if not habits:
        print("No habits")
        print("---")
        print("Add habits in the terminal app")
        return

    done = sum(1 for habit in habits if habit.is_done_today())
    total = len(habits)
    print(f"✅ {done}/{total}" if done == total else f"{done}/{total} habits")

    print("---")
    print(f"Today · {today} | size=12")
    print("---")

    for habit in habits:
        mark = "✅" if habit.is_done_today() else "⬜"
        name = escape_swiftbar(habit.name)
        streak = habit.streak()
        print(f"{mark} {name} · 🔥 {streak} | {toggle_url(habit.id)}")

    print("---")
    habits_bin = habits_executable()
    if habits_bin:
        print(f"Open habit tracker | shell={habits_bin} terminal=true refresh=true")
    else:
        print("Open habit tracker | terminal=true refresh=true")


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--toggle":
        toggle_habit(sys.argv[2])
        return

    render()


if __name__ == "__main__":
    main()
