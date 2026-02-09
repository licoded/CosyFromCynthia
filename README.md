# Cynthia

Cynthia is a tool for SDD-based Forward LTLf Synthesis.

## Preliminaries

- CMake, at least version 3.2;
- Flex & Bison
- SDD 2.0
```
git clone https://github.com/wannesm/PySDD.git
cd PySDD/pysdd/lib/sdd-2.0
git checkout v0.2.10
sudo cp -P lib/Linux/* /usr/local/lib/
sudo cp -Pr include/* /usr/local/include
```

## Build

Build as any CMake project:

```
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
```

## Development


The project uses `clang-format` for code formatting.
Install the tool `clang-format`, e.g. on Ubuntu using APT:
```
sudo apt install clang-format
```

To check the project satisfies the format:
```
./scripts/check-clang-format.sh
```

To apply the changes:
```
./scripts/apply-clang-format.sh
```

To check that copyright notices are OK:

```
python scripts/check_copyright_notice.py
```

## SMV 1000 Benchmark Tester

The project includes an automated benchmark testing tool for validating the Cynthia LTLf synthesis implementation against the SMV 1000 benchmark suite.

**Location:** `tools/benchmarks/sm1000_tester/`

**Setup:**
```bash
# Install dependencies (from project root)
uv sync
```

**Commands:**

Run the complete benchmark suite:
```bash
# Run with default paths
uv run sm1000-test smv1000

# Specify custom paths
uv run sm1000-test smv1000 --app-path /path/to/cynthia-app --benchmark-dir /path/to/sm1000

# Enable verbose output (show failed test details)
uv run sm1000-test smv1000 -v

# Show all failed test cases
uv run sm1000-test smv1000 -v --all-failures

# Show file paths for failed tests
uv run sm1000-test smv1000 -v --show-paths
```

Run a single test case:
```bash
# Run a specific test case
uv run sm1000-test run-single bench1/f7

# With verbose output (shows file paths)
uv run sm1000-test run-single bench2/f123 -v

# Specify custom paths
uv run sm1000-test run-single bench1/f1 --app-path /path/to/cynthia-app
```

**Benchmark Data:**
- `benchmarks/sm1000/bench1/`: 500 LTLf formulas (f1.ltlf - f500.ltlf)
- `benchmarks/sm1000/bench2/`: 500 LTLf formulas (f1.ltlf - f500.ltlf)
- `benchmarks/sm1000/results.csv`: Expected results for validation

**Implementation:**
- Python package: `sm1000-tester` (code in `tools/benchmarks/sm1000_tester/`)
- CLI command: `sm1000-test`
- Uses pandas, rich, and typer
