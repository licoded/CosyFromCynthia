"""Data models for SMV 1000 benchmark testing."""

from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""

    folder: str
    filename: str
    expected: str
    actual: str
    matched: bool
    duration: float

    def __repr__(self) -> str:
        """Return string representation of the result."""
        status = "✓" if self.matched else "✗"
        return f"{status} {self.folder}/{self.filename}: {self.expected} vs {self.actual} ({self.duration:.3f}s)"
