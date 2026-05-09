"""Ubuntu-specific helpers: PPA registration, apt, and snap wrappers. Kept in a separate
module so utils.py stays focused on cross-platform plumbing — none of this runs off Ubuntu
(callers gate on systype="ubuntu" via PACKAGE_ORDER).
"""


def install_ppas(ppas, run_cmd):
    """`sudo add-apt-repository -y <ppa>` for each entry, then a single `apt-get update` so
    the new repos are visible to the subsequent `apt` install case. shortcircuit=False on the
    add because re-adding an existing PPA can exit non-zero on some distro releases."""
    for ppa in ppas:
        run_cmd(f"sudo add-apt-repository -y {ppa}", shortcircuit=False)
    run_cmd("sudo apt-get update")


def install_apt_packages(pkgs, run_cmd):
    """`sudo apt-get install -y <pkgs>` in one shot. apt handles already-installed packages
    gracefully (exits 0), so no per-package precheck is needed."""
    run_cmd("sudo apt-get install -y {0}".format(" ".join(pkgs)))


def install_snap_packages(pkgs, run_cmd):
    """`sudo snap install <pkg>` per entry. One at a time because some snaps need `--classic`
    or `--edge` flags which the user specifies inline (e.g. "code --classic" in config), and
    those flags aren't valid in a bulk invocation. shortcircuit=False so a single bad snap name
    doesn't kill the rest of the batch."""
    for pkg in pkgs:
        run_cmd(f"sudo snap install {pkg}", shortcircuit=False)
