"""Progress display components for SMV 1000 benchmark testing."""

from rich.progress import ProgressColumn, TaskID
from rich.text import Text


class PassStatsColumn(ProgressColumn):
    """A column showing pass statistics: passed/total(rate%)."""

    def __init__(self) -> None:
        super().__init__()

    def render(self, task: TaskID) -> Text:
        """Render pass statistics for the task."""
        passed = task.fields.get("passed", 0)
        total_tested = task.fields.get("total_tested", 0)
        if total_tested > 0:
            rate = passed / total_tested * 100
            return Text(
                f"{passed}/{total_tested}({rate:.2f}%)",
                style="green" if rate >= 90 else "yellow" if rate >= 70 else "red",
            )
        return Text("0/0(0.00%)")
