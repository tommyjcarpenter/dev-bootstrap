from bootstrap.utils import cmds, mkdirs, packages, softlinks, vim


def boot(cfg: dict, name, redovim, systype, loctype):
    """
    CURRENT ORDER (TODO, make this specifiable??)
    1. mkdirs
    2. generic softlinks
    3. location softlinks (ie work gitconfig etc)
    4. system specific commands
    5. generic commands
    6. packages (some system specific, some generic)
    """
    mkdirs(cfg)
    softlinks(cfg, "all")
    softlinks(cfg, loctype)
    cmds(cfg, systype)
    cmds(cfg, "all")  # should cmds just do this too at the end?
    packages(cfg, systype)

    # this goes after os specific installs because that bootstraps various vim pluginery
    if redovim == "y":
        # TODO: this should be some kind of user supplied function
        vim()

    # Install fzf bindings  TODO: is there a yes/yes/yes option so we can do this automatically?
    print(
        "\n\n******NOTE!!! Manually run the following which are not yet handled******"
    )
    print("vim +GoInstallBinaries +qall")
    print("open vim and do")
    print("vim :CocInstall coc-pyright")
    print("vim :CocInstall coc-yaml")
