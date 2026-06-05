.PHONY: help install-dev test lint schema ci

# ---- Default: show targets ----
help:
	@echo "Common targets:"
	@echo "  make test         Run the same unittest command CI runs (.github/workflows/test.yml)"
	@echo "  make lint         Run the same ruff checks CI runs (.github/workflows/lint.yml)"
	@echo "  make schema       Validate sample_config.json (.github/workflows/schema.yml)"
	@echo "  make ci           Full pre-push verification: lint + test + schema"
	@echo "  make install-dev  Sync runtime + dev deps (adds ruff) via uv"

# `uv sync` creates the in-project .venv and installs runtime deps plus the
# `dev` dependency group (ruff at the CI-pinned version). The targets below use
# `uv run`, which syncs on demand, so this is only needed to pre-warm the venv.
install-dev:
	uv sync

# =============================================================================
# CI-equivalent targets. These mirror .github/workflows/*.yml exactly so a
# clean run locally means the GitHub run will also pass. `uv run` resolves the
# project venv on every platform, so no OS-specific interpreter path is needed.
# =============================================================================

# Mirrors .github/workflows/test.yml — discovers and runs every unittest
# under tests/. The package itself imports cleanly on any OS (only the
# inner functions shell out to OS-specific tools), so the same command
# passes on the Linux/macOS/Windows runners CI matrixes over.
test:
	uv run python -m unittest discover -v tests

# Mirrors .github/workflows/lint.yml — ruff check + ruff format --check.
lint:
	uv run ruff check bootstrap/
	uv run ruff format --check bootstrap/

# Mirrors .github/workflows/schema.yml — loads sample_config.json and runs
# it through bootstrap.schema.config_validate. Catches regressions where a
# schema change makes the documented sample config invalid.
schema:
	uv run python -c "import json; from bootstrap.schema import config_validate; config_validate(json.load(open('sample_config.json'))); print('sample_config.json is valid')"

# Full pre-push verification: everything CI runs, in one shot.
ci: lint test schema
