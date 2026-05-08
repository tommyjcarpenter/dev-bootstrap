import json
import os
import sys

import click

from bootstrap import log, utils
from bootstrap.boot import boot
from bootstrap.schema import config_validate


def detect_systype():
    """Auto-detect the system type from the current platform."""
    if sys.platform == "darwin":
        return "mac"
    if sys.platform == "win32":
        return "windows"
    if sys.platform == "linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro_id = line.strip().split("=", 1)[1].strip('"')
                        if distro_id == "arch":
                            return "arch"
                        if distro_id == "ubuntu":
                            return "ubuntu"
        except FileNotFoundError:
            pass
    raise RuntimeError(
        f"Could not auto-detect systype (platform={sys.platform!r}). Please specify --systype explicitly."
    )


def load_config(path):
    """Load and validate a config file, returns None if file doesn't exist."""
    full_path = utils._replace_home(path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r") as f:
        cfg = json.loads(f.read())
    config_validate(cfg)
    return cfg


@click.command()
@click.option("--loctype", prompt="enter [work] or [private]", help="use work or private dotfiles?")
def main(loctype):
    systype = detect_systype()
    log.info(f"Detected systype: {systype}")
    assert loctype in ["work", "private"]
    name = os.environ.get("USER")

    # Load main config
    cfg = load_config("~/dotfiles/bootstrap_config.json")
    if cfg is None:
        raise FileNotFoundError("Main config ~/dotfiles/bootstrap_config.json not found!")

    # Try to load environment-specific config (e.g., bootstrap_config_work.json)
    extra_config_path = f"~/dotfiles/bootstrap_config_{loctype}.json"
    extra_cfg = load_config(extra_config_path)
    if extra_cfg:
        log.info(f"Found extra config: {extra_config_path}")
    else:
        log.skip(f"No extra config found at {extra_config_path}")

    # go!
    boot(cfg, name, systype, loctype, extra_cfg)


if __name__ == "__main__":
    main()
