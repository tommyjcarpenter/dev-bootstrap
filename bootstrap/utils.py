"""
install everything
"""
import json
import subprocess
import os
import shutil
import sys

# NOTE: Cant add the installation of fish itself into this script without breaking it up, because the commands in here are executed using fish itself. So, just install that ahead of time.

BOOTSTRAPHOMEDIR = None
BOOTSTRAPFISHPATH = None


def _replace_home(path):
    """fix home with full path"""
    return path.replace("~", BOOTSTRAPHOMEDIR)


def _run_cmd(args, cwd=None, shortcircuit=True):
    """run a command"""
    fish_path = BOOTSTRAPFISHPATH

    # I was having issues where this wasn't resolving home properly
    args = [_replace_home(x) for x in args] if isinstance(args, list) else _replace_home(args)

    if cwd:
        cwd = _replace_home(cwd)

    print(
        "\nRunning: {0} from: {1}".format(" ".join(args) if isinstance(args, list) else args, cwd),
        flush=True,
    )

    # does anybody actually understand how subprocess works?  ¯\_(ツ)_/¯
    proc = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,  # None is fine to pass: https://docs.python.org/3/library/subprocess.html
        shell=True,
        executable=fish_path,
    )

    out, err = proc.communicate()
    status = proc.returncode
    if status != 0:
        print("FAILED!", flush=True)
        opt = "out: {0}, err: {1}".format(out, err)
        print("Status: {0}, Output: {1}\n\n".format(status, opt))
        if shortcircuit:
            print("Aborting due to short circuit flag, and a failure!")
            sys.exit(1)


def _mkdirrec(dest, delete_first=False):
    """recurisvely make a directory"""
    dest = _replace_home(dest)
    if delete_first and os.path.isdir(dest):
        print("Remove flag is ON, and destination exists, deleting!")
        shutil.rmtree(dest)
    _run_cmd("mkdir -p  " + dest)
    assert os.path.isdir(dest)


def _softlink(src, dest, cwd=None):
    """remove dest, then softline src to dest"""
    print("removing: {0}".format(dest))
    _run_cmd("rm -f {0}".format(dest))
    src = _replace_home(src)
    dest = _replace_home(dest)
    print("linking {0} to {1}".format(src, dest))
    _run_cmd("ln -s " + src + " " + dest, cwd)
    assert os.path.exists(dest)


def _gitclone(repo, dest):
    """clone a git repo"""
    dest = _replace_home(dest)
    _run_cmd("git clone " + repo + " " + dest)
    assert os.path.isdir(dest)


# These should be made Private:


def pipinstall(package, sudo=False, python3=False, user=False):
    """use pip to install a package"""
    sudoclause = "sudo " if sudo else ""
    pipclause = "pip " if python3 is False else "pip3 "
    userclause = " --user " if user else ""
    _run_cmd(sudoclause + pipclause + "install " + userclause + package)


# These take the config and execute a series of installs:


def mkdirs(config):
    """recurisvely make needed dirs"""
    for k, v in config["initial_mkdirs"].items():
        _mkdirrec(k, delete_first=v)


def softlinks(config, section):
    for k, v in config["links"][section].items():
        _softlink(k, v)


def cmds(config, systype):
    if systype in config["commands"]:
        cmds = config["commands"][systype]
        for c in cmds:
            _run_cmd(c)


def packages(config, systype):
    if systype not in config["packages"]:
        return
    inner = config["packages"][systype]
    for ptype in inner:
        if ptype == "brew":
            # sometimes brew will return a status of 1 in cases where it's "fine"
            _run_cmd("brew install " + " ".join(inner["brew"]), shortcircuit=False)
        if ptype == "yay":
            _run_cmd("yay -S {0} --noconfirm".format(" ".join(inner["yay"])))
        if ptype == "pacman":
            _run_cmd("sudo pacman -S {0} --noconfirm".format(" ".join(inner["pacman"])))
        # note that some of these are system agnostic and are repeated. Maybe we can have an "all" section in config?
        if ptype == "fisher":
            _run_cmd("fisher install " + " ".join(inner["fisher"]))
        if ptype == "npm":
            _run_cmd("'npm install {0} -g".format(" ".join(inner["npm"])))


def vim():
    # TODO: this should be written as some kind of user-pluiginable-function
    _mkdirrec("~/.vim/plugged", delete_first=True)

    print("\nthe following vim command takes some time, be patient!\n")
    # https://github.com/junegunn/vim-plug/issues/225
    # have used:  vim +PlugInstall +qall +silent >/dev/null
    _run_cmd("vim +PlugInstall +qall")

    # FORMERLY NOTE: on arch, hit this issue: https://github.com/Valloric/YouCompleteMe/issues/778
    # had to do pacman -S clang; ./install.py --clang-completer --system-libclang
    _run_cmd("git submodule update --init --recursive", cwd="~/.vim/plugged/YouCompleteMe")
    # https://github.com/ycm-core/YouCompleteMe
    # --all requires java
    _run_cmd(
        "./install.py --clangd-completer --go-completer --ts-completer",
        cwd="~/.vim/plugged/YouCompleteMe",
    )

    # TODO: this does not always return, or complete in Docker, because it wants to install black
    # TODO: this tries to install black, which puts out a promt; have to fix that to renable this
    # Install go binaries https://github.com/fatih/vim-go/issues/1475
    # _run_cmd("vim +GoInstallBinaries +qall")
