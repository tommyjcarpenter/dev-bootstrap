.PHONY: help install-dev test lint schema ci

# Python interpreter inside the project venv. Works on Windows GNU Make
# (forward slashes are fine) and on Linux/Mac.
PY := .venv/Scripts/python
ifeq ($(OS),)
PY := .venv/bin/python
endif

# ---- Default: show targets ----
help:
	@echo "Common targets:"
	@echo "  make test         Run the same unittest command CI runs (.github/workflows/test.yml)"
	@echo "  make lint         Run the same ruff checks CI runs (.github/workflows/lint.yml)"
	@echo "  make schema       Validate sample_config.json (.github/workflows/schema.yml)"
	@echo "  make ci           Full pre-push verification: lint + test + schema"
	@echo "  make install-dev  Install runtime + dev deps (adds ruff) via Poetry"

# `poetry install` alone leaves out the dev group, so `make lint` would fail
# on a fresh clone. `--with dev` pulls in ruff at the CI-pinned version.
# The committed poetry.toml pins virtualenvs.in-project = true so Poetry
# creates the venv at .venv/ inside the project, which is where the $(PY)
# above looks for it; without that, Poetry would cache the venv elsewhere
# and the subsequent test/lint/schema targets would not find Python.
install-dev:
	poetry install --with dev

# =============================================================================
# CI-equivalent targets. These mirror .github/workflows/*.yml exactly so a
# clean run locally means the GitHub run will also pass.
# =============================================================================

# Mirrors .github/workflows/test.yml — discovers and runs every unittest
# under tests/. The package itself imports cleanly on any OS (only the
# inner functions shell out to OS-specific tools), so the same command
# passes on the Linux/macOS/Windows runners CI matrixes over.
test:
	$(PY) -m unittest discover -v tests

# Mirrors .github/workflows/lint.yml — ruff check + ruff format --check.
lint:
	$(PY) -m ruff check bootstrap/
	$(PY) -m ruff format --check bootstrap/

# Mirrors .github/workflows/schema.yml — loads sample_config.json and runs
# it through bootstrap.schema.config_validate. Catches regressions where a
# schema change makes the documented sample config invalid.
schema:
	$(PY) -c "import json; from bootstrap.schema import config_validate; config_validate(json.load(open('sample_config.json'))); print('sample_config.json is valid')"

# Full pre-push verification: everything CI runs, in one shot.
ci: lint test schema
