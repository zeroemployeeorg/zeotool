"""Behavioral tests for the real ZeoCore-native tool."""

from __future__ import annotations

import logging
from pathlib import Path

from zeo_core.core.fs import create_service
from zeo_core.tools import ToolContext

from zeotool import AssetCopyRequest, AssetCopyTool


def context(tmp_path: Path) -> ToolContext:
    """Build a genuine, isolated ZeoCore context for a test."""
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    return ToolContext(
        run_id="test-copy",
        tool_name="asset_copy",
        tool_version="0.2.0",
        logger=logging.getLogger("zeotool.tests"),
        fs=create_service(base_dir=tmp_path),
        work_dir=str(tmp_path),
        output_dir=str(output),
    )


def test_copies_bytes_and_reports_destination(tmp_path: Path) -> None:
    """The visible output is byte-identical and its path is reported."""
    source = tmp_path / "source.bin"
    source.write_bytes(b"student-visible asset\x00")

    result = AssetCopyTool().run(AssetCopyRequest(source=source), context(tmp_path))

    assert result.status == "success"
    assert result.data is not None
    assert result.data.destination.read_bytes() == b"student-visible asset\x00"
    assert result.data.bytes_written == len(b"student-visible asset\x00")


def test_refuses_missing_source_without_writing(tmp_path: Path) -> None:
    """A missing input is a structured skip, not a fabricated test fixture."""
    result = AssetCopyTool().run(
        AssetCopyRequest(source=tmp_path / "missing.txt"), context(tmp_path)
    )

    assert result.status == "skipped"
    assert result.machine_message == "ZEO_INPUT_MISSING"
    assert not (tmp_path / "output" / "missing.txt").exists()


def test_refuses_source_outside_work_directory(tmp_path: Path) -> None:
    """The workspace boundary prevents a context from reading arbitrary paths."""
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("not in this lab", encoding="utf-8")

    result = AssetCopyTool().run(AssetCopyRequest(source=outside), context(tmp_path))

    assert result.status == "skipped"
    assert result.machine_message == "ZEO_WORKSPACE_ESCAPE"


def test_refuses_existing_destination_without_overwrite(tmp_path: Path) -> None:
    """Copy uses the public FileSystemService overwrite boundary."""
    source = tmp_path / "lesson.txt"
    source.write_text("new", encoding="utf-8")
    output = tmp_path / "output"
    output.mkdir()
    (output / "lesson.txt").write_text("old", encoding="utf-8")

    result = AssetCopyTool().run(AssetCopyRequest(source=source), context(tmp_path))

    assert result.status == "skipped"
    assert result.machine_message == "ZEO_COPY_FAILED"
    assert (output / "lesson.txt").read_text(encoding="utf-8") == "old"
