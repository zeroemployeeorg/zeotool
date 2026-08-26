"""Credential-free command-line entry point for ZeoTool."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from zeo_core.core.fs import create_service
from zeo_core.tools import ToolContext

from zeotool import __version__
from zeotool.tool import AssetCopyRequest, AssetCopyTool


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser without executing a command."""
    parser = argparse.ArgumentParser(
        prog="zeotool", description="Copy one local asset using ZeoCore."
    )
    parser.add_argument("source", type=Path, help="Existing file to copy")
    parser.add_argument(
        "--output-dir", type=Path, required=True, help="Output directory"
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path.cwd(),
        help=(
            "Sandbox root containing source and output (defaults to current directory)"
        ),
    )
    parser.add_argument("--name", help="Destination filename (defaults to source name)")
    parser.add_argument("--overwrite", action="store_true", help="Replace destination")
    parser.add_argument("--version", action="version", version=f"zeotool {__version__}")
    return parser


def main() -> None:
    """Run the copy capability and print the resulting output path."""
    args = build_parser().parse_args()
    work_dir = args.work_dir.resolve()
    output_dir = args.output_dir.resolve()
    try:
        output_dir.relative_to(work_dir)
    except ValueError as error:
        raise SystemExit("zeotool: --output-dir must be inside --work-dir") from error
    output_dir.mkdir(parents=True, exist_ok=True)
    context = ToolContext(
        run_id="zeotool-cli",
        tool_name=AssetCopyTool.name,
        tool_version=AssetCopyTool.version,
        logger=logging.getLogger("zeotool"),
        fs=create_service(base_dir=work_dir),
        work_dir=str(work_dir),
        output_dir=str(output_dir),
    )
    result = AssetCopyTool().run(
        AssetCopyRequest(
            source=args.source, output_name=args.name, overwrite=args.overwrite
        ),
        context,
    )
    if result.data is None:
        raise SystemExit(f"zeotool: {result.human_message}")
    print(result.data.destination)
