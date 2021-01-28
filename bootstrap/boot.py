from bootstrap import utils
from bootstrap.utils import (
    cmds,
    mkdirs,
    softlinks,
    vim,
    pipinstall,
    packages,
)


def boot(cfg: dict, name, redovim, systype, loctype):
    if systype == "mac":
        utils.BOOTSTRAPHOMEDIR = "/Users/{}".format(name)
        utils.BOOTSTRAPFISHPATH = "/usr/local/bin/fish"

    if systype == "arch":
        utils.BOOTSTRAPHOMEDIR = "/home/{}".format(name)
        utils.BOOTSTRAPFISHPATH = "/usr/bin/fish"

    # CURRENT ORDER (TODO, make this specifiable??)
    # 1. mkdirs
    # 2. generic softlinks
    # 3. location softlinks (ie work gitconfig etc)
    # 4. system specific commands
    # 5. generic commands
    # 6. packages (some system specific, some generic)
    mkdirs(cfg)
    softlinks(cfg, "all")
    softlinks(cfg, loctype)
    cmds(cfg, systype)
    cmds(cfg, "all")  # should cmds just do this too at the end?
    packages(cfg, systype)

    # TODO: ALL IOF THIS NEEDS TO BE MADE GENERIC (into config?), AND DELETED FROM HERE:
    if systype == "mac":
        # vim statusline  https://powerline.readthedocs.io/en/latest/installation/osx.html
        pipinstall("powerline-status", user=True)

    # this goes after os specific installs because that bootstraps various vim pluginery
    if redovim == "y":
        # TODO: this should be some kind of user supplied function
        vim()

    # Install fzf bindings  TODO: is there a yes/yes/yes option so we can do this automatically?
    print("******NOTE!!! Manually run the following which are not yet handled******")
    print("/usr/local/opt/fzf/install")
    print("vim +GoInstallBinaries +qall")
