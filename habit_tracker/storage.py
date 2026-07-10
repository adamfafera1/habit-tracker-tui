from __future__ import annotations

import json
from pathlib import Path

from habit_tracker.models import Habit

DEFAULT_DATA_PATH = Path.home() / ".habit-tracker-tui" / "habits.json"


def load_habits(path: Path = DEFAULT_DATA_PATH) -> list[Habit]:
    if not path.exists():
        return []

    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        Habit(
            id=item["id"],
            name=item["name"],
            created=item.get("created", ""),
            completions=item.get("completions", []),
        )
        for item in raw.get("habits", [])
    ]


def save_habits(habits: list[Habit], path: Path = DEFAULT_DATA_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "habits": [
            {
                "id": habit.id,
                "name": habit.name,
                "created": habit.created,
                "completions": habit.completions,
            }
            for habit in habits
        ]
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
