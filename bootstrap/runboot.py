import json

import click

from bootstrap import utils
from bootstrap.boot import boot
from bootstrap.schema import config_validate

PREREQ = "Are all prequisites met? See README"


@click.command()
@click.option("--prereqs", prompt=PREREQ)
@click.option("--name", prompt="username", help="IE /users/??/")
# useful for "rebootstrapping"
@click.option(
    "--redovim",
    prompt="redo all of vim? [y] for yes, [n] for no",
    help="redo all vim plugins?",
)
@click.option("--systype", prompt="enter [mac] or [arch] or [ubuntu]", help="what system?")
@click.option("--loctype", prompt="enter [work] or [home]", help="use work or home dotfiles?")
def main(prereqs, name, redovim, systype, loctype):
    # TODO: we could obv get a lot fancier here
    assert prereqs == "t"
    assert systype in ["mac", "arch", "ubuntu"]
    assert loctype in ["work", "private"]

    with open(utils._replace_home("~/dotfiles/bootstrap_config.json"), "r") as f:
        cfg = json.loads(f.read())

    # validate schema
    config_validate(cfg)

    # go!
    boot(cfg, name, redovim, systype, loctype)


if __name__ == "__main__":
    main()
