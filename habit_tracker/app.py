from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Input, Label, Static

from habit_tracker.models import Habit
from habit_tracker.storage import DEFAULT_DATA_PATH, load_habits, save_habits


class PromptScreen(ModalScreen[str | None]):
    """Collect a single line of text from the user."""

    DEFAULT_CSS = """
    PromptScreen {
        align: center middle;
    }

    #prompt-dialog {
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #prompt-dialog Label {
        margin-bottom: 1;
    }
    """

    def __init__(self, title: str, placeholder: str, initial: str = "") -> None:
        super().__init__()
        self.title = title
        self.placeholder = placeholder
        self.initial = initial

    def compose(self) -> ComposeResult:
        with Vertical(id="prompt-dialog"):
            yield Label(self.title)
            yield Input(
                value=self.initial,
                placeholder=self.placeholder,
                id="prompt-input",
            )
            yield Static("Enter to save · Esc to cancel", classes="hint")

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()

    @on(Input.Submitted, "#prompt-input")
    def submit(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value if value else None)


class ConfirmScreen(ModalScreen[bool]):
    """Ask the user to confirm a destructive action."""

    DEFAULT_CSS = """
    ConfirmScreen {
        align: center middle;
    }

    #confirm-dialog {
        width: 60;
        height: auto;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
    }

    #confirm-dialog Label {
        margin-bottom: 1;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    BINDINGS = [
        Binding("y", "confirm", "Yes", priority=True),
        Binding("n", "cancel", "No", priority=True),
        Binding("escape", "cancel", "No", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(self.message)
            yield Static("y = yes · n = no · Esc = cancel", classes="hint")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class WeekSummaryScreen(ModalScreen[None]):
    """Show the last seven days as a GitHub-style contribution grid."""

    _CONTRIB_EMPTY = "#161b22"
    _CONTRIB_LEVELS = ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353")

    DEFAULT_CSS = """
    WeekSummaryScreen {
        align: center middle;
    }

    #week-dialog {
        width: auto;
        min-width: 56;
        height: auto;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #week-content {
        margin-top: 1;
    }
    """

    def __init__(self, habits: list[Habit]) -> None:
        super().__init__()
        self.habits = habits

    BINDINGS = [
        Binding("escape", "close", "Close", priority=True),
        Binding("q", "close", "Close", priority=True),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="week-dialog"):
            yield Label("Last 7 days")
            yield Static(self._render_summary(), id="week-content")
            yield Static("Press Esc or q to close", classes="hint")

    def _append_cell(self, text: Text, level: int) -> None:
        text.append(" ")
        text.append("  ", style=f"on {self._CONTRIB_LEVELS[level]}")

    def _completion_level(self, count: int, total: int) -> int:
        if count <= 0 or total <= 0:
            return 0
        return min(4, max(1, round(count / total * 4)))

    def _render_summary(self) -> Text | str:
        if not self.habits:
            return "No habits yet."

        days = self.habits[0].week_marks()
        total = len(self.habits)
        name_width = min(20, max((len(habit.name) for habit in self.habits), default=8))
        text = Text()

        text.append(" " * (name_width + 1))
        for day, _ in days:
            text.append(f" {day.strftime('%a')[:2]} ", style="dim")
        text.append("\n")

        text.append(" " * (name_width + 1))
        for day, _ in days:
            text.append(f" {day.day:>2} ", style="dim")
        text.append("\n\n")

        text.append("All".ljust(name_width))
        for day, _ in days:
            count = sum(1 for habit in self.habits if habit.is_done_on(day))
            self._append_cell(text, self._completion_level(count, total))
        text.append("\n\n")

        for habit in self.habits:
            text.append(habit.name[:name_width].ljust(name_width))
            for day, _ in days:
                level = 4 if habit.is_done_on(day) else 0
                self._append_cell(text, level)
            text.append("\n")

        text.append("\nLess ", style="dim")
        for level in range(len(self._CONTRIB_LEVELS)):
            self._append_cell(text, level)
        text.append(" More", style="dim")

        return text

    def action_close(self) -> None:
        self.dismiss(None)


class HabitTrackerApp(App):
    """Track daily habits from the terminal."""

    CSS = """
    Screen {
        background: $surface;
    }

    #summary {
        height: 3;
        padding: 0 1;
        background: $boost;
        color: $text;
    }

    DataTable {
        height: 1fr;
    }

    .hint {
        color: $text-muted;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("a", "add_habit", "Add"),
        Binding("enter", "toggle_selected", "Toggle", show=False),
        Binding("space", "toggle_selected", "Toggle"),
        Binding("r", "rename_habit", "Rename"),
        Binding("d", "delete_habit", "Delete"),
        Binding("w", "week_summary", "Week"),
        Binding("e", "export_csv", "Export"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.habits: list[Habit] = load_habits()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="summary")
        yield DataTable(id="habits-table", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#habits-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("Done", "Habit", "Streak", "Best")
        self.refresh_table()
        table.focus()

    def refresh_table(self, *, keep_selection: str | None = None) -> None:
        table = self.query_one("#habits-table", DataTable)
        selected_id = keep_selection
        if selected_id is None:
            selected = self.selected_habit()
            selected_id = selected.id if selected else None

        table.clear()
        for habit in self.habits:
            done = Text("✓", style="bold green") if habit.is_done_today() else Text(" ")
            name = Text(habit.name, style="bold green") if habit.is_done_today() else habit.name
            table.add_row(done, name, str(habit.streak()), str(habit.best_streak()), key=habit.id)

        if selected_id:
            for index, habit in enumerate(self.habits):
                if habit.id == selected_id:
                    table.move_cursor(row=index)
                    break
        elif self.habits:
            table.move_cursor(row=0)

        done_count = sum(1 for habit in self.habits if habit.is_done_today())
        total = len(self.habits)
        best_overall = max((habit.best_streak() for habit in self.habits), default=0)
        summary = self.query_one("#summary", Static)
        summary.update(
            f"Today: {date.today().strftime('%A, %d %b %Y')}  ·  "
            f"Done: {done_count}/{total}  ·  "
            f"Top streak: {best_overall}"
        )

    def persist(self) -> None:
        save_habits(self.habits)

    def selected_habit(self) -> Habit | None:
        table = self.query_one("#habits-table", DataTable)
        if table.cursor_row is None or not table.is_valid_row_index(table.cursor_row):
            return None
        row_key = table.ordered_rows[table.cursor_row].key
        return next((habit for habit in self.habits if habit.id == row_key), None)

    def notify_short(self, message: str) -> None:
        self.notify(message, timeout=2)

    @work
    async def action_add_habit(self) -> None:
        name = await self.push_screen_wait(
            PromptScreen("New habit name", "e.g. Read for 20 minutes")
        )
        if not name:
            return
        self.habits.append(Habit(name=name))
        self.persist()
        self.refresh_table(keep_selection=self.habits[-1].id)
        self.notify_short(f"Added '{name}'")

    def action_toggle_selected(self) -> None:
        habit = self.selected_habit()
        if habit is None:
            return
        habit.toggle_today()
        self.persist()
        self.refresh_table(keep_selection=habit.id)

    @work
    async def action_rename_habit(self) -> None:
        habit = self.selected_habit()
        if habit is None:
            self.notify_short("Select a habit first")
            return

        new_name = await self.push_screen_wait(
            PromptScreen(
                f"Rename '{habit.name}'",
                "New habit name",
                initial=habit.name,
            )
        )
        if not new_name or new_name == habit.name:
            return
        habit.name = new_name
        self.persist()
        self.refresh_table(keep_selection=habit.id)
        self.notify_short(f"Renamed to '{new_name}'")

    @work
    async def action_delete_habit(self) -> None:
        habit = self.selected_habit()
        if habit is None:
            self.notify_short("Select a habit first")
            return

        confirmed = await self.push_screen_wait(
            ConfirmScreen(f"Delete '{habit.name}'? This cannot be undone.")
        )
        if not confirmed:
            return

        habit_id = habit.id
        self.habits = [item for item in self.habits if item.id != habit_id]
        self.persist()
        self.refresh_table()
        self.notify_short("Habit deleted")

    @work
    async def action_week_summary(self) -> None:
        await self.push_screen_wait(WeekSummaryScreen(self.habits))

    def action_export_csv(self) -> None:
        if not self.habits:
            self.notify_short("Nothing to export")
            return

        export_path = DEFAULT_DATA_PATH.parent / "habits-export.csv"
        with export_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["habit", "date", "completed"])
            for habit in self.habits:
                for day in sorted(habit.completions):
                    writer.writerow([habit.name, day, "yes"])

        self.notify_short(f"Exported to {export_path}")


def main() -> None:
    HabitTrackerApp().run()


if __name__ == "__main__":
    main()
