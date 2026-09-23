"""Run a complete credential-free ZeoTool asset-copy example."""

from __future__ import annotations

import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from zeo_core.core.fs import create_service
from zeo_core.tools import ToolContext

from zeotool import AssetCopyRequest, AssetCopyTool


def main() -> None:
    """Copy an in-memory example asset to a temporary output directory."""
    with TemporaryDirectory(prefix="zeotool_example_") as temporary_directory:
        root = Path(temporary_directory)
        source = root / "lesson.txt"
        source.write_text("Build observable tools.\n", encoding="utf-8")
        output = root / "output"
        output.mkdir()
        context = ToolContext(
            run_id="example-copy",
            tool_name="asset_copy",
            tool_version="0.2.0",
            logger=logging.getLogger("zeotool.example"),
            fs=create_service(base_dir=root),
            work_dir=str(root),
            output_dir=str(output),
        )
        result = AssetCopyTool().run(AssetCopyRequest(source=source), context)
        if result.data is None:
            raise RuntimeError(result.human_message)
        print(result.data.destination.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
