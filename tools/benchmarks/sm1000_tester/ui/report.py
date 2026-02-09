"""Report generation for SMV 1000 benchmark testing."""

from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sm1000_tester.models import BenchmarkResult


class ReportGenerator:
    """Generate summary and failure reports for benchmark results."""

    def __init__(
        self,
        console: Console,
        benchmark_dir: Path,
        verbose: bool = False,
        all_failures: bool = False,
        show_paths: bool = False,
    ):
        """Initialize the report generator.

        Args:
            console: Rich console instance for output
            benchmark_dir: Path to benchmark directory
            verbose: Whether to show detailed failure information
            all_failures: Whether to show all failures or limit to 20
            show_paths: Whether to show file paths for failures
        """
        self.console = console
        self.benchmark_dir = benchmark_dir
        self.verbose = verbose
        self.all_failures = all_failures
        self.show_paths = show_paths

    def print_summary(self, results: List[BenchmarkResult]) -> None:
        """Print benchmark summary.

        Args:
            results: List of benchmark results to summarize
        """
        if not results:
            self.console.print("[yellow]No results to display[/yellow]")
            return

        total = len(results)
        passed = sum(1 for r in results if r.matched)
        failed = total - passed
        total_duration = sum(r.duration for r in results)

        # Summary table
        table = Table(
            title="SMV 1000 Benchmark Summary",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Total Tests", str(total))
        table.add_row("Passed", f"[green]{passed}[/green]")
        table.add_row("Failed", f"[red]{failed}[/red]" if failed > 0 else "0")
        table.add_row("Pass Rate", f"{passed/total*100:.1f}%")
        table.add_row("Total Duration", f"{total_duration:.2f}s")
        table.add_row("Avg Duration", f"{total_duration/total:.3f}s")

        self.console.print()
        self.console.print(table)

        # Show failures if any (only in verbose mode)
        if self.verbose:
            self._print_failures(results)
        elif failed > 0:
            self.console.print()
            self.console.print("[yellow]Use -v for detailed failure information[/yellow]")

    def _print_failures(self, results: List[BenchmarkResult]) -> None:
        """Print failure details.

        Args:
            results: List of benchmark results
        """
        failures = [r for r in results if not r.matched]
        if not failures:
            return

        self.console.print()

        # Determine how many failures to show
        display_failures = failures if self.all_failures else failures[:20]

        # Build failure lines
        failure_lines = []
        for r in display_failures:
            line = f"[red]{r.folder}/{r.filename}[/red]: expected '{r.expected}', got '{r.actual}'"
            failure_lines.append(line)
            # Add file paths if requested
            if self.show_paths:
                ltlf_file = self.benchmark_dir / r.folder / f"{r.filename}.ltlf"
                part_file = self.benchmark_dir / r.folder / f"{r.filename}.part"
                failure_lines.append(f"  ltlf: {ltlf_file}")
                failure_lines.append(f"  part: {part_file}")

        self.console.print(Panel(
            "\n".join(failure_lines),
            title=f"[bold red]Mismatches ({len(failures)})[/bold red]",
            border_style="red",
        ))

        if not self.all_failures and len(failures) > 20:
            self.console.print(
                f"[yellow]... and {len(failures) - 20} more (use --all-failures to view all)[/yellow]"
            )

    def print_single_result(self, result: BenchmarkResult) -> None:
        """Print a single test result.

        Args:
            result: Single benchmark result to display
        """
        # Status indicator
        status = "[green]✓ PASS[/green]" if result.matched else "[red]✗ FAIL[/red]"
        status_style = "green" if result.matched else "red"

        # Result table
        table = Table(
            title=f"Test Case: {result.folder}/{result.filename}",
            show_header=True,
            header_style="bold magenta",
            border_style=status_style,
        )
        table.add_column("Field", style="cyan")
        table.add_column("Value", justify="left")

        table.add_row("Status", status)
        table.add_row("Expected", result.expected)
        table.add_row("Actual", result.actual)
        table.add_row("Duration", f"{result.duration:.3f}s")

        self.console.print()
        self.console.print(table)

        # Show file paths in verbose mode
        if self.verbose or self.show_paths:
            self.console.print()
            ltlf_file = self.benchmark_dir / result.folder / f"{result.filename}.ltlf"
            part_file = self.benchmark_dir / result.folder / f"{result.filename}.part"
            self.console.print(f"[dim]Formula:   {ltlf_file}[/dim]")
            self.console.print(f"[dim]Partition: {part_file}[/dim]")
