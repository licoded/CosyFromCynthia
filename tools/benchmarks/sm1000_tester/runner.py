"""Core benchmark runner for SMV 1000 testing."""

import subprocess
import time
from pathlib import Path
from typing import List

import pandas as pd
import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, TimeRemainingColumn, TextColumn

from sm1000_tester.models import BenchmarkResult
from sm1000_tester.ui import PassStatsColumn
from sm1000_tester.utils import normalize_result


class CynthiaBenchmark:
    """Benchmark runner for Cynthia LTLf synthesis tool."""

    def __init__(
        self,
        app_path: Path,
        benchmark_dir: Path,
        verbose: bool = False,
        all_failures: bool = False,
        show_paths: bool = False,
    ):
        """Initialize the benchmark runner.

        Args:
            app_path: Path to cynthia-app executable
            benchmark_dir: Path to SMV 1000 benchmark directory
            verbose: Enable verbose output
            all_failures: Display all failed test cases
            show_paths: Display file paths for failures
        """
        self.app_path = Path(app_path)
        self.benchmark_dir = Path(benchmark_dir)
        self.verbose = verbose
        self.all_failures = all_failures
        self.show_paths = show_paths
        self.results: List[BenchmarkResult] = []
        self.console = Console()

        # Verify paths exist
        if not self.app_path.exists():
            raise typer.BadParameter(f"Cynthia app not found: {self.app_path}")
        if not self.benchmark_dir.exists():
            raise typer.BadParameter(f"Benchmark directory not found: {self.benchmark_dir}")

    def run_cynthia(
        self, formula_file: Path, partition_file: Path
    ) -> tuple[str, float]:
        """Run Cynthia on a single formula and return result with timing.

        Args:
            formula_file: Path to the .ltlf formula file
            partition_file: Path to the .part partition file

        Returns:
            Tuple of (result_string, duration_seconds)
        """
        start_time = time.time()

        cmd = [
            str(self.app_path),
            "-f", str(formula_file),
            "--part", str(partition_file),
            "-n",
        ]

        if self.verbose:
            cmd.append("-v")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse output to determine realizability
            # Check for "NOT REALIZABLE" or "UNREALIZABLE" FIRST to avoid
            # matching "REALIZABLE" in "NOT REALIZABLE"
            output = result.stdout + result.stderr
            output_upper = output.upper()
            if "UNREALIZABLE" in output_upper or "NOT REALIZABLE" in output_upper:
                outcome = "Unrealizable"
            elif "REALIZABLE" in output_upper:
                outcome = "Realizable"
            else:
                outcome = "Unknown"
        except subprocess.TimeoutExpired:
            outcome = "Timeout"
        except Exception as e:
            outcome = f"Error: {e}"

        duration = time.time() - start_time
        return outcome, duration

    def load_expected_results(self) -> pd.DataFrame:
        """Load expected results from CSV file.

        Returns:
            DataFrame with normalized column names
        """
        csv_path = self.benchmark_dir / "results.csv"
        if not csv_path.exists():
            raise typer.BadParameter(f"Results CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        return df

    def run_smv1000(self) -> List[BenchmarkResult]:
        """Run the complete SMV 1000 benchmark suite.

        Returns:
            List of benchmark results
        """
        df = self.load_expected_results()

        # Build lookup dict for expected results
        expected_map = {}
        for _, row in df.iterrows():
            folder = row.get("folder", row.get("folder", ""))
            filename = row.get("filename", row.get("filename", ""))
            result = row.get("result", row.get("result", ""))
            key = f"{folder}/{filename}"
            expected_map[key] = result

        total_tests = 1000
        results = []

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            PassStatsColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Running SMV 1000 benchmark...",
                total=total_tests,
            )

            # Process bench1 and bench2
            for bench_name in ["bench1", "bench2"]:
                bench_dir = self.benchmark_dir / bench_name
                if not bench_dir.exists():
                    self.console.print(
                        f"[yellow]Warning: {bench_dir} not found, skipping...[/yellow]"
                    )
                    continue

                for i in range(1, 501):
                    formula_file = bench_dir / f"f{i}.ltlf"
                    partition_file = bench_dir / f"f{i}.part"

                    if not formula_file.exists() or not partition_file.exists():
                        self.console.print(
                            f"[yellow]Warning: {formula_file.name} or {partition_file.name} "
                            f"not found, skipping...[/yellow]"
                        )
                        continue

                    # Run Cynthia
                    actual, duration = self.run_cynthia(formula_file, partition_file)

                    # Get expected result
                    key = f"{bench_name}/f{i}"
                    expected = expected_map.get(key, "Unknown")

                    # Normalize results for comparison
                    expected_normalized = normalize_result(expected)
                    actual_normalized = normalize_result(actual)
                    matched = expected_normalized == actual_normalized

                    results.append(BenchmarkResult(
                        folder=bench_name,
                        filename=f"f{i}",
                        expected=expected,
                        actual=actual,
                        matched=matched,
                        duration=duration,
                    ))

                    # Update pass statistics
                    passed = sum(1 for r in results if r.matched)
                    total_tested = len(results)
                    progress.update(task, advance=1, passed=passed, total_tested=total_tested)

        self.results = results
        return results

    def run_single_test(self, test_case: str) -> BenchmarkResult:
        """Run a single test case.

        Args:
            test_case: Test case identifier in format "bench1/f7" or "bench2/f123"

        Returns:
            BenchmarkResult for the single test

        Raises:
            typer.BadParameter: If test case format is invalid or files don't exist
        """
        # Parse test case identifier
        parts = test_case.split("/")
        if len(parts) != 2:
            raise typer.BadParameter(
                f"Invalid test case format: '{test_case}'. Expected format: 'bench1/f7' or 'bench2/f123'"
            )

        folder, filename = parts
        if folder not in ["bench1", "bench2"]:
            raise typer.BadParameter(
                f"Invalid folder: '{folder}'. Must be 'bench1' or 'bench2'"
            )

        # Verify filename format
        if not filename.startswith("f") or not filename[1:].isdigit():
            raise typer.BadParameter(
                f"Invalid filename: '{filename}'. Must be in format 'f<number>' (e.g., 'f7', 'f123')"
            )

        # Build file paths
        bench_dir = self.benchmark_dir / folder
        formula_file = bench_dir / f"{filename}.ltlf"
        partition_file = bench_dir / f"{filename}.part"

        # Verify files exist
        if not bench_dir.exists():
            raise typer.BadParameter(
                f"Benchmark directory not found: {bench_dir}"
            )
        if not formula_file.exists():
            raise typer.BadParameter(
                f"Formula file not found: {formula_file}"
            )
        if not partition_file.exists():
            raise typer.BadParameter(
                f"Partition file not found: {partition_file}"
            )

        # Load expected result from CSV
        df = self.load_expected_results()
        expected_map = {}
        for _, row in df.iterrows():
            folder_name = row.get("folder", "")
            file_name = row.get("filename", "")
            result = row.get("result", "")
            key = f"{folder_name}/{file_name}"
            expected_map[key] = result

        key = f"{folder}/{filename}"
        expected = expected_map.get(key, "Unknown")

        # Run Cynthia
        actual, duration = self.run_cynthia(formula_file, partition_file)

        # Normalize results for comparison
        expected_normalized = normalize_result(expected)
        actual_normalized = normalize_result(actual)
        matched = expected_normalized == actual_normalized

        return BenchmarkResult(
            folder=folder,
            filename=filename,
            expected=expected,
            actual=actual,
            matched=matched,
            duration=duration,
        )
