"""
install everything
"""
import os
import shutil
import subprocess
import sys

HOMEDIR = os.environ.get("HOME")
SHELLPATH = os.environ.get("SHELL")


def _replace_home(path):
    """fix home with full path"""
    return path.replace("~", HOMEDIR)


def _run_cmd(args, cwd=None, shortcircuit=True):
    """run a command"""
    # I was having issues where this wasn't resolving home properly
    args = [_replace_home(x) for x in args] if isinstance(args, list) else _replace_home(args)

    if cwd:
        cwd = _replace_home(cwd)

    print(
        "\nRunning: {0} {1}".format(
            " ".join(args) if isinstance(args, list) else args,
            "from: {}".format(cwd) if cwd else "",
        ),
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
        executable=SHELLPATH,
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
    src = _replace_home(src)
    dest = _replace_home(dest)
    print("linking {0} to {1}".format(src, dest))
    _run_cmd("ln -f -s " + src + " " + dest, cwd)
    assert os.path.exists(dest)


def _gitclone(repo, dest):
    """clone a git repo"""
    dest = _replace_home(dest)
    _run_cmd("git clone " + repo + " " + dest)
    assert os.path.isdir(dest)


def _pipinstall(package, sudo=False, python3=True, user=True):
    """use pip to install a package"""
    sudoclause = "sudo " if sudo else ""
    pipclause = "pip " if python3 is False else "pip3 "
    userclause = " --user " if user else ""
    _run_cmd(sudoclause + pipclause + "install " + userclause + package)


# These take the config and execute a series of installs:


def mkdirs(config):
    """recurisvely make needed dirs"""
    for d in config["initial_mkdirs"]:
        _mkdirrec(d["dir"], delete_first=d["delfirst"] if "delfirst" in d else False)


def softlinks(config, section):
    """make all softlinks"""
    for link in config["links"][section]:
        _softlink(link["src"], link["dst"])


def cmds(config, systype):
    """run all commands"""
    if systype in config["commands"]:
        for c in config["commands"][systype]:
            _run_cmd(c)


def packages(config, systype):
    """install all packages"""
    inner = config["packages"][systype]
    print(f"Sections to process: {inner} for systpe {systype}")
    for ptype in inner:
        print(f"Processing {ptype}")
        match ptype:
            case "brew_tap":
                for tap in inner["brew_tap"]:
                    _run_cmd("brew tap " + tap, shortcircuit=False)
            case "brew":
                # sometimes brew will return a status of 1 in cases where it's "fine"
                _run_cmd("brew install " + " ".join(inner["brew"]), shortcircuit=False)
            case "yay":
                _run_cmd("yay -S {0} --noconfirm".format(" ".join(inner["yay"])))
            case "pacman":
                _run_cmd("sudo pacman -S {0} --noconfirm".format(" ".join(inner["pacman"])))
            case "apt":
                _run_cmd("sudo apt-get install -y {0}".format(" ".join(inner["apt"])))
            # note, these could be in "all" or package specific
            case "fisher":
                _run_cmd("fisher install " + " ".join(inner["fisher"]))
            case "npm":
                _run_cmd("npm install {0} -g".format(" ".join(inner["npm"])))
            case "pip":
                for pkg in inner["pip"]:
                    _pipinstall(pkg)
            case _:
                # TODO: have a json schema validate
                raise ValueError(f"Unsupported package type {ptype}!")


def vim():
    """
    install my custom vim setup
    TODO: this should be written as some kind of user-pluiginable-function
    """
    _mkdirrec("~/.vim/plugged", delete_first=True)

    print("\nthe following vim command takes some time, be patient!\n")
    # https://github.com/junegunn/vim-plug/issues/225
    # have used:  vim +PlugInstall +qall +silent >/dev/null
    _run_cmd("vim +PlugInstall +qall")

    # This is my attempt to run coc installs then exit
    # this definitely runs when run within vim, but questionable on the CMD line
    # https://github.com/neoclide/coc.nvim/issues/3802
    _run_cmd("vim -c 'CocInstall -sync coc-go coc-json coc-html coc-pyright coc-yaml coc-git|qall'")
