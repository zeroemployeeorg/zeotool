"""The ZeoCore-native, local asset-copy capability."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from zeo_core.contracts import CapabilityResult
from zeo_core.tools import BaseZeoTool, ToolContext


class AssetCopyRequest(BaseModel):
    """Validated request for copying one file into the runner output directory."""

    source: Path = Field(description="Existing file to copy")
    output_name: str | None = Field(
        default=None,
        description="Destination filename; defaults to the source filename",
    )
    overwrite: bool = Field(default=False, description="Allow replacing a destination")

    @field_validator("output_name")
    @classmethod
    def output_name_is_filename(cls, value: str | None) -> str | None:
        """Reject traversal and directory-shaped output names."""
        if value is not None and (not value or Path(value).name != value):
            raise ValueError("output_name must be a non-empty filename, not a path")
        return value


class AssetCopyResponse(BaseModel):
    """Observable facts about a completed deterministic copy."""

    destination: Path
    bytes_written: int


class AssetCopyTool(BaseZeoTool):
    """Copy a local file through the filesystem service supplied by ZeoCore."""

    name = "asset_copy"
    version = "0.2.0"

    def run(
        self, request: AssetCopyRequest, ctx: ToolContext
    ) -> CapabilityResult[AssetCopyResponse]:
        """Copy one file and return its destination and byte count."""
        source = request.source.resolve()
        work_root = ctx.work_path.resolve()
        output_root = ctx.output_path.resolve()
        try:
            source.relative_to(work_root)
            output_root.relative_to(work_root)
        except ValueError:
            return CapabilityResult.skip(
                reason=(
                    "Source and output directory must remain inside the work directory"
                ),
                code="ZEO_WORKSPACE_ESCAPE",
                metadata={
                    "source": str(source),
                    "work_dir": str(work_root),
                    "output_dir": str(output_root),
                },
                run_id=ctx.run_id,
            )
        if not source.is_file():
            return CapabilityResult.skip(
                reason=f"Source file does not exist: {source}",
                code="ZEO_INPUT_MISSING",
                metadata={"source": str(source)},
                run_id=ctx.run_id,
            )

        destination = (output_root / (request.output_name or source.name)).resolve()
        if destination.parent != output_root:
            return CapabilityResult.skip(
                reason="Destination must remain inside the configured output directory",
                code="ZEO_OUTPUT_ESCAPE",
                metadata={"destination": str(destination)},
                run_id=ctx.run_id,
            )

        fs = ctx.require_fs()
        write_result = fs.copy(source, destination, overwrite=request.overwrite)
        if not write_result.ok or write_result.path is None:
            return CapabilityResult.skip(
                reason=write_result.error or write_result.message or "Copy failed",
                code="ZEO_COPY_FAILED",
                metadata={"source": str(source), "destination": str(destination)},
                run_id=ctx.run_id,
            )

        ctx.require_logger().info("Copied %s to %s", source, write_result.path)
        return CapabilityResult.ok(
            data=AssetCopyResponse(
                destination=write_result.path,
                bytes_written=write_result.bytes_written,
            ),
            msg="Asset copied",
            metadata={"tool": self.name, "version": self.version},
            run_id=ctx.run_id,
        )
