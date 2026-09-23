.PHONY: verify install format-check metadata-check lint typecheck test audit sample

UV := uv

install:
	$(UV) sync --locked --all-extras

format-check:
	$(UV) run python tools/check_whitespace.py
	$(UV) run ruff format --check src tests examples tools

metadata-check:
	$(UV) run python tools/check_project_metadata_v2.py

lint:
	$(UV) run ruff check src tests examples tools

typecheck:
	$(UV) run mypy

test:
	$(UV) run pytest

audit:
	$(UV) pip check

sample:
	$(UV) run python -m zeotool examples/input.txt --output-dir examples/output --work-dir . --overwrite

verify: install format-check metadata-check lint typecheck test audit
