"""Fail when a tracked or relevant untracked text file has basic whitespace defects."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TEXT_SUFFIXES = {".md", ".py", ".toml", ".txt", ".yml", ".yaml"}


def candidate_paths() -> list[Path]:
    """Return Git-visible text files, including PR changes before staging."""
    completed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    return [
        Path(item.decode("utf-8"))
        for item in completed.stdout.split(b"\0")
        if item
        and Path(item.decode("utf-8")).is_file()
        and (Path(item.decode("utf-8")).suffix in TEXT_SUFFIXES)
    ]


def defects(path: Path) -> list[str]:
    """Return line-level whitespace defects without interpreting file content."""
    raw = path.read_bytes()
    if b"\0" in raw:
        return []
    issues: list[str] = []
    if raw and not raw.endswith(b"\n"):
        issues.append("missing final newline")
    for number, line in enumerate(raw.splitlines(), start=1):
        if line.rstrip(b" \t") != line:
            issues.append(f"trailing whitespace on line {number}")
    return issues


def main() -> int:
    """Print all defects and return a non-zero status if any are found."""
    failed = False
    for path in candidate_paths():
        for issue in defects(path):
            print(f"{path}: {issue}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
