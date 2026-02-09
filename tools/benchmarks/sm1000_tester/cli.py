"""Command-line interface for SMV 1000 benchmark testing."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from sm1000_tester.models import BenchmarkResult
from sm1000_tester.ui.report import ReportGenerator
from sm1000_tester.runner import CynthiaBenchmark
from sm1000_tester.utils import format_path_display, get_project_root


app = typer.Typer(
    name="sm1000-test",
    help="Automated SMV 1000 benchmark testing for Cynthia LTLf synthesis tool",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def smv1000(
    ctx: typer.Context,
    help_flag: bool = typer.Option(
        False,
        "--help",
        "-h",
        help="Show help and exit.",
        is_eager=True,
    ),
    app_path: Optional[Path] = typer.Option(
        None,
        "--app-path",
        "-a",
        help="Path to cynthia-app executable",
        dir_okay=False,
    ),
    benchmark_dir: Optional[Path] = typer.Option(
        None,
        "--benchmark-dir",
        "-b",
        help="Path to SMV 1000 benchmark directory",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output (show failed test details)",
    ),
    all_failures: bool = typer.Option(
        False,
        "--all-failures",
        help="Display all failed test cases instead of limiting to first 20",
    ),
    show_paths: bool = typer.Option(
        False,
        "--show-paths",
        help="Display .ltlf and .part file paths for each failed test case",
    ),
):
    """Run the SMV 1000 benchmark suite and compare with expected results.

    The SMV 1000 benchmark consists of 1000 LTLf formulas split across
    bench1/ and bench2/ directories. This script runs Cynthia on each
    formula and compares the result with the expected output.
    """
    # Handle help flag
    if help_flag:
        typer.echo(ctx.get_help())
        raise typer.Exit()

    # Determine default paths relative to project root
    project_root = get_project_root()
    default_app_path = project_root / "build" / "apps" / "cynthia" / "cynthia-app"
    default_benchmark_dir = project_root / "benchmarks" / "sm1000"

    # Use provided paths or defaults
    app_path = app_path or default_app_path
    benchmark_dir = benchmark_dir or default_benchmark_dir
    csv_path = benchmark_dir / "results.csv"

    # Format paths with tabs for alignment
    max_label_len = max(len("App:"), len("Benchmark:"), len("CSV:"))

    console.print(Panel(
        f"[bold cyan]SMV 1000 Benchmark Test[/bold cyan]\n"
        f"{format_path_display('App:', app_path, max_label_len)}\n"
        f"{format_path_display('Benchmark:', benchmark_dir, max_label_len)}\n"
        f"{format_path_display('CSV:', csv_path, max_label_len)}",
        border_style="cyan",
    ))

    try:
        bench = CynthiaBenchmark(
            app_path=app_path,
            benchmark_dir=benchmark_dir,
            verbose=verbose,
            all_failures=all_failures,
            show_paths=show_paths,
        )
        results = bench.run_smv1000()

        # Generate and display report
        report_gen = ReportGenerator(
            console=console,
            benchmark_dir=benchmark_dir,
            verbose=verbose,
            all_failures=all_failures,
            show_paths=show_paths,
        )
        report_gen.print_summary(results)

    except typer.BadParameter as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def run_single(
    test_case: str = typer.Argument(
        ...,
        help="Test case to run (e.g., 'bench1/f7', 'bench2/f123')",
        metavar="TEST_CASE",
    ),
    app_path: Optional[Path] = typer.Option(
        None,
        "--app-path",
        "-a",
        help="Path to cynthia-app executable",
        dir_okay=False,
    ),
    benchmark_dir: Optional[Path] = typer.Option(
        None,
        "--benchmark-dir",
        "-b",
        help="Path to SMV 1000 benchmark directory",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output (show file paths)",
    ),
):
    """Run a single test case from the SMV 1000 benchmark suite.

    Test case format: bench1/f7 or bench2/f123

    Example: sm1000-test run-single bench1/f7
    """
    # Determine default paths relative to project root
    project_root = get_project_root()
    default_app_path = project_root / "build" / "apps" / "cynthia" / "cynthia-app"
    default_benchmark_dir = project_root / "benchmarks" / "sm1000"

    # Use provided paths or defaults
    app_path = app_path or default_app_path
    benchmark_dir = benchmark_dir or default_benchmark_dir

    # Display test info panel
    console.print(Panel(
        f"[bold cyan]Single Test Case[/bold cyan]\n"
        f"{format_path_display('Test:', test_case, 10)}\n"
        f"{format_path_display('App:', app_path, 10)}\n"
        f"{format_path_display('Benchmark:', benchmark_dir, 10)}",
        border_style="cyan",
    ))

    try:
        bench = CynthiaBenchmark(
            app_path=app_path,
            benchmark_dir=benchmark_dir,
            verbose=verbose,
        )

        # Run single test
        result: BenchmarkResult = bench.run_single_test(test_case)

        # Display result
        report_gen = ReportGenerator(
            console=console,
            benchmark_dir=benchmark_dir,
            verbose=verbose,
        )
        report_gen.print_single_result(result)

        # Exit with appropriate code
        if not result.matched:
            raise typer.Exit(1)

    except typer.BadParameter as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
