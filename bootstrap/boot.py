from bootstrap import log
from bootstrap.utils import cmds, mkdirs, packages, prereq_packages, softlinks
from bootstrap.windows import install_file_associations


def boot_config(cfg: dict, systype, loctype, run_prereqs=False):
    """
    Process a single config file.
    CURRENT ORDER (TODO, make this specifiable??)
     1. generic mkdirs (initial_mkdirs.all)
     2. os-specific mkdirs (initial_mkdirs.mac/arch/ubuntu/windows)
     3. generic softlinks (links.all)
     4. os-specific softlinks (links.mac/arch/ubuntu/windows)
     5. generic commands
     6. system specific commands
     7. prereq packages (rust/cargo, go, poetry) - only on first config
     8. system specific packages (installs npm, go, etc via pacman/brew/apt/winget)
     9. generic packages (uses pip, npm, go_install, cargo, fisher)
    10. file associations (windows-only, runs after packages so target apps exist)
    """
    mkdirs(cfg, "all")
    mkdirs(cfg, systype)
    softlinks(cfg, "all")
    softlinks(cfg, systype)
    cmds(cfg, "all")
    cmds(cfg, systype)
    if run_prereqs:
        prereq_packages(cfg, systype)
    # systype packages first (installs npm, go, etc via pacman/brew/apt)
    # then "all" packages (uses npm, go_install, etc)
    packages(cfg, systype)
    packages(cfg, "all")
    install_file_associations(cfg)


def boot(cfg: dict, name, systype, loctype, extra_cfg: dict = None):
    """
    Run the main config, then optionally run an extra config (e.g., work or private specific).
    """
    log.header("Processing main config")
    boot_config(cfg, systype, loctype, run_prereqs=True)

    if extra_cfg:
        log.header(f"Processing extra config for {loctype}")
        boot_config(extra_cfg, systype, loctype, run_prereqs=False)
