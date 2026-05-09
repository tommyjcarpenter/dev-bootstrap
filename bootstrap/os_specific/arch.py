"""Arch Linux-specific helpers: pacman (official repos) and yay (AUR) wrappers. Kept in a
separate module so utils.py stays focused on cross-platform plumbing — none of this runs off
Arch (callers gate on systype="arch" via PACKAGE_ORDER).
"""


def install_pacman_packages(pkgs, run_cmd):
    """`sudo pacman -S <pkgs> --noconfirm` in one shot. pacman handles already-installed
    packages gracefully (prints "is up to date -- reinstalling" and exits 0), so no per-package
    precheck is needed — unlike winget, which exits non-zero in that case."""
    run_cmd("sudo pacman -S {0} --noconfirm".format(" ".join(pkgs)))


def install_yay_packages(pkgs, run_cmd):
    """`yay -S <pkgs> --noconfirm`. yay (AUR helper) is invoked as the user — it shells out to
    sudo internally for the makepkg/pacman steps, so we deliberately do NOT prefix sudo here
    (running yay itself as root is unsupported and yay refuses to do it)."""
    run_cmd("yay -S {0} --noconfirm".format(" ".join(pkgs)))
