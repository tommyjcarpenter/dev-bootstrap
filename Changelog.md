# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2026-06-05
- switch project tooling from Poetry to `uv`: PEP 621 `pyproject.toml`, `uv.lock`, hatchling build backend, `Makefile` and CI workflows driven by `uv sync`/`uv run`

## [1.3.0] - 2026-05-09

Windows support and the cross-platform refactors needed to make it land cleanly.

### Cross-platform
- replace shell `mkdir -p` and `ln -f -n -s` with Python primitives (`os.makedirs`, `os.symlink`); drops bash dependency for these ops on every platform
- HOMEDIR via `os.path.expanduser("~")` so Windows works without `$HOME`
- `_softlink` refuses to clobber a real directory at dest (safer than `ln -n`'s platform-dependent behavior) and handles broken symlinks via `os.path.lexists`

### Windows-specific
- new `winget`, `scoop`, `scoop_bucket` package types; `windows` systype auto-detected from `sys.platform`
- `winget list --id X` precheck so already-installed packages don't get logged as failures (winget exits non-zero with "no upgrade available")
- scoop installs run one package at a time with `shortcircuit=False`, so a single missing manifest doesn't abort the batch
- `_run_check` refreshes PATH from HKLM/HKCU registry before each precheck — a chain of skipped prechecks no longer leaves `os.environ` blind to packages installed in a prior bootstrap run
- Windows-specific helpers live in their own `bootstrap/windows.py`: `refresh_path`, `install_winget_packages`, `set_file_assoc`, `install_file_associations`

### Package types (cross-platform additions)
- new `pip` package type — `python3 -m pip install --user` on POSIX (PEP 668 / system-Python protections), `python -m pip install` on Windows (winget Python's Scripts dir is on PATH; the `--user` dir is not)
- `npm` on Windows skips `sudo` (Windows npm installs to a user-writable prefix and there is no `sudo`)

### File associations (Windows)
- new `file_associations` config section: per-user registration under `HKCU\Software\Classes` (no admin) with optional `name` (FriendlyAppName) and `icon` (DefaultIcon)
- preserves a user's "Always use this app" selection across re-runs — only clears UserChoice when it points to a different ProgID

### CLI
- **breaking**: remove `--systype`. Systype is always auto-detected from `sys.platform` and `/etc/os-release`. Pass nothing; if detection fails, runboot raises with the platform name so you can wire up support

### Other
- schema and README updated for `windows` section, `file_associations`, `pip`, `prereq_packages`
- `sample_config.json` rewritten — was using the pre-Windows schema and failed validation
- remove dead `_gitclone()` helper

## [1.1.0] - 2022-08-30
- start this changelog
- convert to poetry
- move the config file out of this repo
- add minimal ubuntu support
- move location of  bin py file
