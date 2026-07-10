from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from uuid import uuid4


@dataclass
class Habit:
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    created: str = field(default_factory=lambda: date.today().isoformat())
    completions: list[str] = field(default_factory=list)

    def is_done_today(self) -> bool:
        return date.today().isoformat() in self.completions

    def is_done_on(self, day: date) -> bool:
        return day.isoformat() in self.completions

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

    def best_streak(self) -> int:
        if not self.completions:
            return 0

        days = sorted(date.fromisoformat(day) for day in self.completions)
        best = 1
        current = 1
        for index in range(1, len(days)):
            if days[index] == days[index - 1] + timedelta(days=1):
                current += 1
                best = max(best, current)
            else:
                current = 1
        return best

    def week_marks(self, *, end: date | None = None) -> list[tuple[date, bool]]:
        end = end or date.today()
        return [
            (end - timedelta(days=offset), self.is_done_on(end - timedelta(days=offset)))
            for offset in range(6, -1, -1)
        ]
