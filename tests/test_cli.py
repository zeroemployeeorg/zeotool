"""End-to-end checks for the installed module entry point."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_module_cli_copies_a_local_file(tmp_path: Path) -> None:
    """``python -m zeotool`` invokes the actual tool and prints its output path."""
    source = tmp_path / "input.txt"
    source.write_text("hello learner\n", encoding="utf-8")
    output = tmp_path / "output"

    completed = subprocess.run(  # noqa: S603 -- fixed interpreter and test-controlled arguments
        [
            sys.executable,
            "-m",
            "zeotool",
            str(source),
            "--output-dir",
            str(output),
            "--work-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    destination = Path(completed.stdout.strip())
    assert destination == output / "input.txt"
    assert destination.read_text(encoding="utf-8") == "hello learner\n"
