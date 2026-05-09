"""macOS-specific helpers: Homebrew tap / formula / cask wrappers. Kept in a separate module
so utils.py stays focused on cross-platform plumbing — none of this runs off macOS (callers
gate on systype="mac" via PACKAGE_ORDER, and brew is required to be on PATH before this is
invoked).
"""


def install_brew_taps(taps, run_cmd):
    """`brew tap <tap>` for each entry. shortcircuit=False because re-tapping an already-tapped
    repo exits non-zero on some brew versions, and we don't want that to abort the run."""
    for tap in taps:
        run_cmd(f"brew tap {tap}", shortcircuit=False)


def install_brew_packages(pkgs, run_cmd):
    """`brew install <pkgs>` in one shot. shortcircuit=False because brew sometimes exits 1 in
    "fine" cases — e.g. a formula already installed at the latest version, or a post-install
    hook that prints a warning but doesn't actually fail the install."""
    run_cmd("brew install " + " ".join(pkgs), shortcircuit=False)


def install_brew_cask_packages(pkgs, run_cmd):
    """`brew install --cask <pkgs>`. Same shortcircuit rationale as install_brew_packages."""
    run_cmd("brew install --cask " + " ".join(pkgs), shortcircuit=False)
