#!/usr/bin/env python3
import os
import json
import click
from bootstrap.boot import boot


PREREQ = "Are all prequisites met? Fish is installed, is default shell, and a system python3 (NOT PYENV) is installed? If this is arch, is yay installed? Enter [t] if true or [f] for  false"


@click.command()
@click.option("--prereqs", prompt=PREREQ)
@click.option("--name", prompt="username", help="IE /users/??/")
# useful for "rebootstrapping"
@click.option(
    "--redovim", prompt="redo all of vim? [y] for yes, [n] for no", help="redo all vim plugins?"
)
@click.option("--systype", prompt="enter [mac] or [arch]", help="what system?")
@click.option("--loctype", prompt="enter [work] or [home]", help="use work or home dotfiles?")
def main(prereqs, name, redovim, systype, loctype):
    # TODO: we could obv get a lot fancier here
    assert prereqs == "t"
    assert systype in ["mac", "arch"]
    assert loctype in ["work", "private"]

    with open("config.json", "r") as f:
        cfg = json.loads(f.read())

    boot(cfg, name, redovim, systype, loctype)


if __name__ == "__main__":
    main()
