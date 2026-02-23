"""
install everything
"""

import os
import shutil
import subprocess
import sys

from bootstrap import log

HOMEDIR = os.environ.get("HOME")
SHELLPATH = os.environ.get("SHELL")

# Package installation order by OS - some types must run before others
# (e.g., ppa before apt to add repos, brew_tap before brew)
# Cross-platform types (npm, go_install, etc.) MUST come after OS-specific ones
# because they depend on tools installed by OS package managers (e.g., npm from nodejs)
CROSS_PLATFORM_PACKAGE_ORDER = ["npm", "go_install", "cargo", "fisher"]
OS_SPECIFIC_PACKAGE_ORDER = ["brew_tap", "brew", "brew_cask", "pacman", "yay", "ppa", "apt", "snap"]
PACKAGE_ORDER = {
    "mac": ["brew_tap", "brew", "brew_cask"] + CROSS_PLATFORM_PACKAGE_ORDER,
    "arch": ["pacman", "yay"] + CROSS_PLATFORM_PACKAGE_ORDER,
    "ubuntu": ["ppa", "apt", "snap"] + CROSS_PLATFORM_PACKAGE_ORDER,
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


def _mkdirrec(dest, delete_first=False):
    """recurisvely make a directory"""
    dest = _replace_home(dest)
    if delete_first and os.path.isdir(dest):
        log.action("Remove flag is ON, and destination exists, deleting!")
        shutil.rmtree(dest)
    _run_cmd("mkdir -p  " + dest)
    assert os.path.isdir(dest)


def _softlink(src, dest, cwd=None):
    """remove dest, then softline src to dest"""
    src = _replace_home(src)
    dest = _replace_home(dest)
    log.action(f"linking {src} to {dest}")
    _run_cmd("ln -f -n -s " + src + " " + dest, cwd)
    assert os.path.exists(dest)


def _gitclone(repo, dest):
    """clone a git repo"""
    dest = _replace_home(dest)
    _run_cmd("git clone " + repo + " " + dest)
    assert os.path.isdir(dest)


# These take the config and execute a series of installs:


def mkdirs(config, section):
    """recursively make needed dirs for a given section (all, mac, arch, ubuntu)"""
    if "initial_mkdirs" not in config or section not in config["initial_mkdirs"]:
        log.skip(f"No initial_mkdirs for section {section} in config")
        return
    for d in config["initial_mkdirs"][section]:
        _mkdirrec(d["dir"], delete_first=d["delfirst"] if "delfirst" in d else False)


def softlinks(config, section):
    """make all softlinks"""
    if "links" not in config or section not in config["links"]:
        log.skip(f"No links for section {section} in config")
        return
    for link in config["links"][section]:
        _softlink(link["src"], link["dst"])


def _run_check(check_cmd):
    """Run a precheck command. Returns True if check passes (exit 0)."""
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
                for tap in inner["brew_tap"]:
                    _run_cmd("brew tap " + tap, shortcircuit=False)
            case "brew":
                # sometimes brew will return a status of 1 in cases where it's "fine"
                _run_cmd("brew install " + " ".join(inner["brew"]), shortcircuit=False)
            case "brew_cask":
                _run_cmd("brew install --cask " + " ".join(inner["brew_cask"]), shortcircuit=False)
            case "yay":
                _run_cmd("yay -S {0} --noconfirm".format(" ".join(inner["yay"])))
            case "pacman":
                _run_cmd("sudo pacman -S {0} --noconfirm".format(" ".join(inner["pacman"])))
            case "ppa":
                # Ubuntu PPAs - must be added before apt install
                for ppa in inner["ppa"]:
                    _run_cmd(f"sudo add-apt-repository -y {ppa}", shortcircuit=False)
                _run_cmd("sudo apt-get update")
            case "apt":
                _run_cmd("sudo apt-get install -y {0}".format(" ".join(inner["apt"])))
            case "snap":
                # some snaps need --classic, specify as "package --classic" in config
                for pkg in inner["snap"]:
                    _run_cmd(f"sudo snap install {pkg}", shortcircuit=False)
            # note, these could be in "all" or package specific
            case "fisher":
                _run_cmd("fisher install " + " ".join(inner["fisher"]))
            case "npm":
                _run_cmd("sudo npm install {0} -g".format(" ".join(inner["npm"])))
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
