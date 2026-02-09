# SMV 1000 Benchmark Tester

Automated benchmark testing and result comparison for the Cynthia LTLf synthesis tool.

## Setup

Install dependencies using uv (from project root):

```bash
# From project root
uv sync
```

The package configuration is at `pyproject.toml` (root), with the tester code in `tools/benchmarks/sm1000_tester/`.

## Usage

Run the SMV 1000 benchmark suite from the project root:

```bash
# Run with default paths (assumes cynthia-app is in build/apps/cynthia/)
uv run sm1000-test

# Specify custom paths
uv run sm1000-test --app-path /path/to/cynthia-app --benchmark-dir /path/to/sm1000

# Enable verbose output (show failed test details)
uv run sm1000-test -v

# Show all failed test cases (instead of limiting to 20)
uv run sm1000-test -v --all-failures

# Show .ltlf and .part file paths for failed tests
uv run sm1000-test -v --show-paths
```

## Benchmark Structure

The benchmark data is located at `benchmarks/sm1000/`:
- `bench1/`: 500 formulas (f1.ltlf - f500.ltlf)
- `bench2/`: 500 formulas (f1.ltlf - f500.ltlf)
- `results.csv`: Expected results for validation

## Output

The script produces:
1. Console output with real-time progress (rich progress bar)
2. Summary report showing:
   - Total tests run
   - Passed/Failed counts
   - Mismatches with expected results
   - Timing statistics
