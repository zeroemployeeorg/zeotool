"""Fail closed if current ZeoTool public metadata points at a legacy URL."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

CANONICAL_REPOSITORY = "https://github.com/profrodai/zeotool"
EXPECTED_URLS = {
    "Homepage": CANONICAL_REPOSITORY,
    "Issues": f"{CANONICAL_REPOSITORY}/issues",
}
README = Path("README.md")


def main() -> int:
    """Validate public package links and the primary repository documentation."""
    with Path("pyproject.toml").open("rb") as project_file:
        project = tomllib.load(project_file)

    urls = project["project"]["urls"]
    failures = [
        f"project.urls.{name} must be {expected!r}, got {urls.get(name)!r}"
        for name, expected in EXPECTED_URLS.items()
        if urls.get(name) != expected
    ]
    readme = README.read_text(encoding="utf-8")
    if CANONICAL_REPOSITORY not in readme:
        failures.append(f"{README} must link to {CANONICAL_REPOSITORY!r}")
    if "github.com/profrodai/quacktool" in readme:
        failures.append(f"{README} must not link to the legacy repository")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
