import json
import os

import click

from bootstrap import utils
from bootstrap.boot import boot
from bootstrap.schema import config_validate

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
@click.option("--systype", prompt="enter [mac] or [arch] or [ubuntu]", help="what system?")
@click.option("--loctype", prompt="enter [work] or [private]", help="use work or private dotfiles?")
def main(systype, loctype):
    assert systype in ["mac", "arch", "ubuntu"]
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
        print(f"Found extra config: {extra_config_path}")
    else:
        print(f"No extra config found at {extra_config_path}, skipping")

    # go!
    boot(cfg, name, systype, loctype, extra_cfg)


if __name__ == "__main__":
    main()
