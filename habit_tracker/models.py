from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass
class Habit:
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created: str = field(default_factory=lambda: date.today().isoformat())
    completions: list[str] = field(default_factory=list)

    def is_done_today(self) -> bool:
        return date.today().isoformat() in self.completions

    def toggle_today(self) -> None:
        today = date.today().isoformat()
        if today in self.completions:
            self.completions.remove(today)
        else:
            self.completions.append(today)

    def streak(self) -> int:
        if not self.completions:
            return 0

        done = {date.fromisoformat(day) for day in self.completions}
        current = date.today()
        if current not in done:
            current = current.fromordinal(current.toordinal() - 1)

        streak = 0
        while current in done:
            streak += 1
            current = current.fromordinal(current.toordinal() - 1)
        return streak
