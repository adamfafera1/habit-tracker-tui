from __future__ import annotations

from datetime import date

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Input, Label, Static

from habit_tracker.models import Habit
from habit_tracker.storage import load_habits, save_habits


class AddHabitScreen(ModalScreen[str | None]):
    """Prompt for a new habit name."""

    DEFAULT_CSS = """
    AddHabitScreen {
        align: center middle;
    }

    #add-dialog {
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #add-dialog Label {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="add-dialog"):
            yield Label("New habit name")
            yield Input(placeholder="e.g. Read for 20 minutes", id="habit-name")
            yield Static("Enter to save · Esc to cancel", classes="hint")

    def on_mount(self) -> None:
        self.query_one("#habit-name", Input).focus()

    @on(Input.Submitted, "#habit-name")
    def save_habit(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        self.dismiss(name if name else None)


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
        Binding("space", "toggle_selected", "Toggle"),
        Binding("d", "delete_habit", "Delete"),
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
        table.add_columns("Done", "Habit", "Streak")
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one("#habits-table", DataTable)
        table.clear()
        for habit in self.habits:
            done = "✓" if habit.is_done_today() else " "
            table.add_row(done, habit.name, str(habit.streak()), key=habit.id)

        done_count = sum(1 for habit in self.habits if habit.is_done_today())
        total = len(self.habits)
        summary = self.query_one("#summary", Static)
        summary.update(
            f"Today: {date.today().strftime('%A, %d %b %Y')}  ·  "
            f"Completed: {done_count}/{total}"
        )

    def persist(self) -> None:
        save_habits(self.habits)

    def selected_habit(self) -> Habit | None:
        table = self.query_one("#habits-table", DataTable)
        if table.cursor_row is None:
            return None
        row_key = table.get_row_key(table.cursor_row)
        if row_key is None:
            return None
        return next((habit for habit in self.habits if habit.id == str(row_key.value)), None)

    @work
    async def action_add_habit(self) -> None:
        name = await self.push_screen_wait(AddHabitScreen())
        if not name:
            return
        self.habits.append(Habit(name=name))
        self.persist()
        self.refresh_table()

    def action_toggle_selected(self) -> None:
        habit = self.selected_habit()
        if habit is None:
            return
        habit.toggle_today()
        self.persist()
        self.refresh_table()

    def action_delete_habit(self) -> None:
        habit = self.selected_habit()
        if habit is None:
            return
        self.habits = [item for item in self.habits if item.id != habit.id]
        self.persist()
        self.refresh_table()


def main() -> None:
    HabitTrackerApp().run()


if __name__ == "__main__":
    main()
