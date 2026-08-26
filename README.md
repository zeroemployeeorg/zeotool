# ZeoTool

ZeoTool is a small, production-quality teaching tool for one concrete idea:
turn a typed local input into an observable local asset. It copies one existing
file into a chosen output directory through ZeoCore's public tool and
filesystem contracts. It makes no network calls and needs no credentials.

## What students learn

1. Model user input with Pydantic.
2. Implement `BaseZeoTool.run(request, context)` against immutable
   `ToolContext`.
3. Return structured `CapabilityResult` values for success and expected
   non-success outcomes.
4. Use the runner-provided `FileSystemService`, rather than ad-hoc file I/O,
   for the actual side effect.
5. Test the behavior with a real context and temporary directories.

The current exercise is deliberately narrow. It is a reliable foundation for
future asset transforms; it does not claim to resize, transcode, analyse, or
generate media.

## Run it

ZeoTool requires Python 3.13+ and uses the exact runtime dependency
`zeocore==0.5.0` (the resolved transitive graph is committed in `uv.lock`).

```bash
uv sync --locked --all-extras
uv run python -m zeotool examples/input.txt --output-dir examples/output \\
  --work-dir .
cat examples/output/input.txt
```

The command prints the destination path. Source and output must stay inside
`--work-dir` (the current directory by default), so the runner never grants
the tool unrestricted filesystem access. Traversal-style output names and
symlinks that resolve outside this boundary are refused before a file is read
or written. It also fails safely when the destination already exists.

Use `--overwrite` only when replacing a normal destination inside the output
directory is intentional. It replaces that destination with byte-identical
source content; it never permits an output symlink to redirect the write
outside the workspace.

For a completely temporary demonstration:

```bash
uv run python examples/local_copy.py
```

Remove local sample output with `rm -rf examples/output`; no reset command
touches source files or Git history.

## Verify

```bash
make verify
```

The gate performs a locked install, formatting check, lint, strict type check,
tests, and dependency consistency audit. It is secret-free and suitable for
pull-request CI.

## Migration boundary

ZeoTool is a clean API break from the former package and distribution name.
There is no compatibility package, command, import alias, or plugin shim for
the prior API. Update callers to import `zeotool` and run `python -m zeotool`.
Historical commits remain intact; [`RELICENSING.md`](RELICENSING.md) records
the authorized forward MIT relicensing.

The canonical repository is
[`profrodai/zeotool`](https://github.com/profrodai/zeotool). The distribution
and all current source surfaces use ZeoTool.

## API shape

```python
from zeotool import AssetCopyRequest, AssetCopyTool

# A runner supplies a real ZeoCore ToolContext with a FileSystemService.
result = AssetCopyTool().run(AssetCopyRequest(source="lesson.txt"), context)
```

On success, `result.data` contains the copied destination and byte count. On
an expected input or copy issue, the tool returns a structured skipped result
with a `ZEO_*` machine code for a runner to inspect.

## License

MIT. See [`LICENSE`](LICENSE) and the forward relicensing record.
