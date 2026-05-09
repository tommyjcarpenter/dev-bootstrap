"""install everything"""

import os
import shutil
import subprocess
import sys

from bootstrap import log
from bootstrap.os_specific import arch, mac, ubuntu, windows

HOMEDIR = os.path.expanduser("~")
SHELLPATH = os.environ.get("SHELL")  # None on Windows; subprocess defaults to %COMSPEC% (cmd.exe)


# Package installation order by OS — some types must run before others (e.g. ppa before apt to add
# repos, brew_tap before brew). Cross-platform types (npm, go_install, etc.) MUST come after the
# OS-specific ones because they depend on tools installed by the OS package managers (e.g. npm
# comes from nodejs, go_install needs a Go toolchain).
CROSS_PLATFORM_PACKAGE_ORDER = ["pip", "npm", "go_install", "cargo", "fisher"]
OS_SPECIFIC_PACKAGE_ORDER = [
    "brew_tap",
    "brew",
    "brew_cask",
    "pacman",
    "yay",
    "ppa",
    "apt",
    "snap",
    "winget",
    "scoop_bucket",
    "scoop",
]
PACKAGE_ORDER = {
    "mac": ["brew_tap", "brew", "brew_cask"] + CROSS_PLATFORM_PACKAGE_ORDER,
    "arch": ["pacman", "yay"] + CROSS_PLATFORM_PACKAGE_ORDER,
    "ubuntu": ["ppa", "apt", "snap"] + CROSS_PLATFORM_PACKAGE_ORDER,
    "windows": ["winget", "scoop_bucket", "scoop"] + CROSS_PLATFORM_PACKAGE_ORDER,
    "all": CROSS_PLATFORM_PACKAGE_ORDER,
}
# OS-specific package types first, then cross-platform (ensures npm/go are installed before used)
ALL_KNOWN_PACKAGE_TYPES = OS_SPECIFIC_PACKAGE_ORDER + CROSS_PLATFORM_PACKAGE_ORDER


def _replace_home(path):
    """fix home with full path"""
    return path.replace("~", HOMEDIR)


def _run_cmd(args, cwd=None, shortcircuit=True):
    """run a command"""
    # I was having issues where this wasn't resolving home properly
    args = [_replace_home(x) for x in args] if isinstance(args, list) else _replace_home(args)

    if cwd:
        cwd = _replace_home(cwd)

    log.cmd(
        "{0} {1}".format(
            " ".join(args) if isinstance(args, list) else args,
            f"from: {cwd}" if cwd else "",
        )
    )

    # does anybody actually understand how subprocess works?  ¯\_(ツ)_/¯
    proc = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,  # None is fine to pass: https://docs.python.org/3/library/subprocess.html
        shell=True,
        executable=SHELLPATH,
    )

    out, err = proc.communicate()
    status = proc.returncode
    if status != 0:
        log.error("FAILED!")
        opt = f"out: {out}, err: {err}"
        log.error(f"Status: {status}, Output: {opt}")
        if shortcircuit:
            log.error("Aborting due to short circuit flag, and a failure!")
            sys.exit(1)

    windows.refresh_path()


def _mkdirrec(dest, delete_first=False, sudo=False):
    """recursively make a directory (cross-platform via os.makedirs)"""
    dest = _replace_home(dest)
    if delete_first and os.path.isdir(dest):
        log.action("Remove flag is ON, and destination exists, deleting!")
        if sudo:
            _run_cmd("sudo rm -rf " + dest)
        else:
            shutil.rmtree(dest)
    if sudo:
        # sudo paths still shell out — they're rare and platform-specific (linux only)
        _run_cmd("sudo mkdir -p " + dest)
    else:
        log.action(f"mkdir -p {dest}")
        os.makedirs(dest, exist_ok=True)
    assert os.path.isdir(dest)


def _softlink(src, dest, cwd=None, sudo=False):
    """remove dest if present, then symlink src -> dest (cross-platform via os.symlink)

    On Windows, requires Developer Mode to be enabled (or running as admin) so that
    os.symlink succeeds without SeCreateSymbolicLinkPrivilege.
    """
    src = _replace_home(src)
    dest = _replace_home(dest)
    log.action(f"linking {src} to {dest}")

    if sudo:
        # sudo path: shell out (rare, linux-only for system paths like /usr/share/...)
        _run_cmd("sudo ln -f -n -s " + src + " " + dest, cwd)
        assert os.path.exists(dest)
        return

    # Remove existing dest (file, dir-symlink, or broken symlink)
    if os.path.lexists(dest):
        if os.path.isdir(dest) and not os.path.islink(dest):
            # Real directory at dest — refuse to clobber, mirrors `ln -n` behavior
            raise RuntimeError(f"Refusing to replace real directory at {dest}")
        os.unlink(dest)

    # target_is_directory matters on Windows (file-symlink vs dir-symlink are different there)
    os.symlink(src, dest, target_is_directory=os.path.isdir(src))
    assert os.path.exists(dest) or os.path.islink(dest)


# These take the config and execute a series of installs:


def mkdirs(config, section):
    """recursively make needed dirs for a given section (all, mac, arch, ubuntu)"""
    if "initial_mkdirs" not in config or section not in config["initial_mkdirs"]:
        log.skip(f"No initial_mkdirs for section {section} in config")
        return
    for d in config["initial_mkdirs"][section]:
        _mkdirrec(d["dir"], delete_first=d.get("delfirst", False), sudo=d.get("sudo", False))


def softlinks(config, section):
    """make all softlinks"""
    if "links" not in config or section not in config["links"]:
        log.skip(f"No links for section {section} in config")
        return
    for link in config["links"][section]:
        _softlink(link["src"], link["dst"], sudo=link.get("sudo", False))


def _run_check(check_cmd):
    """Run a precheck command. Returns True if check passes (exit 0)."""
    windows.refresh_path()
    try:
        result = subprocess.run(
            check_cmd,
            shell=True,
            executable=SHELLPATH,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def cmds(config, systype):
    """run all commands"""
    if "commands" not in config:
        log.skip("No commands in config")
        return
    if systype in config["commands"]:
        for c in config["commands"][systype]:
            if isinstance(c, str):
                _run_cmd(c)
            else:
                label = c.get("label") or c["cmd"][:60]
                if "check" in c:
                    log.info(f"Precheck for: {label}")
                    if _run_check(c["check"]):
                        log.skip(f"Precheck passed, skipping: {label}")
                        continue
                _run_cmd(c["cmd"])


def _install_packages(inner, label):
    """
    Internal function to install packages from a dict of package types.
    label is used for logging (e.g., "systype ubuntu" or "loctype work")
    """
    # Use cross-platform order as default since env-specific packages won't have OS-specific types
    # Process in defined order, only if present in config
    ptypes_to_process = [p for p in ALL_KNOWN_PACKAGE_TYPES if p in inner]
    # Add any unknown types at the end (future-proofing)
    ptypes_to_process += [p for p in inner if p not in ALL_KNOWN_PACKAGE_TYPES]
    log.info(f"Sections to process: {ptypes_to_process} for {label}")
    for ptype in ptypes_to_process:
        log.info(f"Processing {ptype}")
        match ptype:
            case "brew_tap":
                mac.install_brew_taps(inner["brew_tap"], _run_cmd)
            case "brew":
                mac.install_brew_packages(inner["brew"], _run_cmd)
            case "brew_cask":
                mac.install_brew_cask_packages(inner["brew_cask"], _run_cmd)
            case "yay":
                arch.install_yay_packages(inner["yay"], _run_cmd)
            case "pacman":
                arch.install_pacman_packages(inner["pacman"], _run_cmd)
            case "ppa":
                ubuntu.install_ppas(inner["ppa"], _run_cmd)
            case "apt":
                ubuntu.install_apt_packages(inner["apt"], _run_cmd)
            case "snap":
                ubuntu.install_snap_packages(inner["snap"], _run_cmd)
            case "winget":
                windows.install_winget_packages(inner["winget"], _run_cmd)
            case "scoop_bucket":
                for bucket in inner["scoop_bucket"]:
                    _run_cmd(f"scoop bucket add {bucket}", shortcircuit=False)
            case "scoop":
                # one at a time so a single missing manifest or transient failure doesn't take
                # out the rest of the batch — `scoop install P1 P2 P3` stops at the first error
                for pkg in inner["scoop"]:
                    _run_cmd(f"scoop install {pkg}", shortcircuit=False)
            # the package types below can appear in "all" or in any OS-specific section
            case "fisher":
                _run_cmd("fisher install " + " ".join(inner["fisher"]))
            case "npm":
                # Windows npm has no sudo and doesn't need it; POSIX requires sudo for -g installs
                prefix = "" if sys.platform == "win32" else "sudo "
                _run_cmd("{0}npm install {1} -g".format(prefix, " ".join(inner["npm"])))
            case "pip":
                # Windows: winget Python is a per-user install at %LOCALAPPDATA%\Programs\Python\PythonXX\
                # whose Scripts dir is already on PATH; plain `pip install` writes there. We deliberately
                # AVOID --user on Windows because that puts scripts under %APPDATA%\Python\PythonXX\Scripts
                # which is NOT on PATH by default, making tools "installed but invisible".
                # POSIX: --user is needed for system Pythons (PEP 668 / apt protection).
                cmd = "python -m pip install" if sys.platform == "win32" else "python3 -m pip install --user"
                _run_cmd("{0} {1}".format(cmd, " ".join(inner["pip"])), shortcircuit=False)
            case "go_install":
                for pkg in inner["go_install"]:
                    _run_cmd(f"go install {pkg}")
            case "cargo":
                for pkg in inner["cargo"]:
                    # Use full path to cargo in case it was installed via rustup
                    _run_cmd(f"$HOME/.cargo/bin/cargo install {pkg}")
            case _:
                raise ValueError(f"Unsupported package type {ptype}!")


def prereq_packages(config, systype):
    """install prerequisite packages (rust/cargo, go, poetry) for a given systype"""
    if "prereq_packages" not in config or systype not in config["prereq_packages"]:
        log.skip(f"No prereq_packages defined for systype {systype}")
        return
    log.header(f"Installing prerequisite packages for {systype}")
    _install_packages(config["prereq_packages"][systype], f"prereq {systype}")


def packages(config, systype):
    """install all packages for a given systype (mac/arch/ubuntu/all)"""
    if "packages" not in config or systype not in config["packages"]:
        log.skip(f"No packages defined for systype {systype}")
        return
    _install_packages(config["packages"][systype], f"systype {systype}")
