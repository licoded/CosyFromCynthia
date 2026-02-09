"""Utility functions for SMV 1000 benchmark testing."""

from pathlib import Path


def normalize_result(result: str) -> str:
    """Normalize result string for comparison."""
    result = result.strip().lower()
    # Check "unrealizable" FIRST to avoid matching "realizable" in "unrealizable"
    if "unrealizable" in result:
        return "unrealizable"
    elif "realizable" in result:
        return "realizable"
    return result


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def format_path_display(label: str, path: Path, max_label_len: int = 10) -> str:
    """Format a path for CLI display with tab alignment.

    Args:
        label: The label text (e.g., "App:", "Benchmark:")
        path: The path to display
        max_label_len: Maximum label length for tab calculation

    Returns:
        Formatted string with label and path
    """
    tab_count = 2 - (len(label) // 8)
    tabs = "\t" * tab_count
    return f"{label}{tabs}[dim]{path}[/dim]"
