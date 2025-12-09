from bootstrap.utils import cmds, mkdirs, packages, prereq_packages, softlinks


def boot_config(cfg: dict, systype, loctype, run_prereqs=False):
    """
    Process a single config file.
    CURRENT ORDER (TODO, make this specifiable??)
    1. generic mkdirs (initial_mkdirs.all)
    2. os-specific mkdirs (initial_mkdirs.mac/arch/ubuntu)
    3. generic softlinks (links.all)
    4. os-specific softlinks (links.mac/arch/ubuntu)
    5. generic commands
    6. system specific commands
    7. prereq packages (rust/cargo, go, poetry) - only on first config
    8. generic packages
    9. system specific packages
    """
    mkdirs(cfg, "all")
    mkdirs(cfg, systype)
    softlinks(cfg, "all")
    softlinks(cfg, systype)
    cmds(cfg, "all")
    cmds(cfg, systype)
    if run_prereqs:
        prereq_packages(cfg, systype)
    packages(cfg, "all")
    packages(cfg, systype)


def boot(cfg: dict, name, systype, loctype, extra_cfg: dict = None):
    """
    Run the main config, then optionally run an extra config (e.g., work or private specific).
    """
    print("=== Processing main config ===")
    boot_config(cfg, systype, loctype, run_prereqs=True)

    if extra_cfg:
        print(f"\n=== Processing extra config for {loctype} ===")
        boot_config(extra_cfg, systype, loctype, run_prereqs=False)
