# Summary
This "package" allows you to specify a complete dev env setup, including packages to install (homebrew, yay, pacman, npm, etc etc).
You write a `config.json`, then run a python CLI tool.
I use this to keep multiple machines (work mac, home Arch, Docker based arch dev boxes) all up to date with my dev environment.

# Isn't there stuff already like this?
There are probably many. However, the well known ones; Puppet, Chef, Ansible, etc, are very heavyweight for my needs.

There are a lot of "dotfiles" repos on github; this depends on that --- it requires you to have a `~/dotfiles/` repo that can be symlinked against, but it goes a lot further (than dotfiles).

This was only a few hundred lines of python, and I've been using this to setup new computers (eg new Macs, new PC builds) and Dockerized development environments for years.

I am planning on making this more extensible so the user can provide functions that get run.

# Prerequisites

1. python3 (I am using 3.10) and `poetry` and `pyenv` (`curl https://pyenv.run | bash`)
2. if on mac, `homebrew`, and if on Arch, `yay`
3. If on mac, XCode command line tools (can't even build `gcc` from `homebrew` without this): `sudo xcode-select --install`
4. make a directory called `~/dotfiles/` with all of your dotfiles. I personally have a private github `dotfiles` repo. I simply clone that to use this.
5. Write `config.json`; see the next section

Optional:
- if you want `vim` installed, your `.vimrc` should be using vim-plug.

# Config.json
The idea here is that you write `config.json` to completely describe what you would like linked, installed, ran, etc.

My personal `config.json` is in a private repo (~/dotfiles/bootstrap_config.json)

Please see the (evolving) jsonschema for `config.json` in `bootstrap/schema.py` for the full schema.
But for an overview, these are the major sections:

1. `comments`: this is just a list of strings for your own keeping since JSON has no native commenting mechanism. IE remind yourself why you install something etc.
2. `initial_mkdirs`: directories to be recursively made. For example, `~/.ssh/..`. You can specify whether to try deleting the directory first, which is sometimes helpful for "rebootstrapping"
3. `links`: this is a list of softlinked dotfiles, from you `~/dotfiles` directory, that can vary by "location" if you want. IE, if you have a `.gitconfig` that you use on "work" machines, and a seperate one you use on "private" machines, you can specify these seperately, and when you run the script, you specify the location. There is also a generic `all` key for specifying location-agnostic keys.
4. `commands`: a list of arbitrary commands to run, which can be specified as os-agnostic, or by OS type. Warning, whatever you put here will be executed!. While I havent tested this on mac yet, on linux, if the command needs sudo, it will pause and ask for your sudo password using a `STDIN` pipe, so privleged commands are fine.
5. `packages`: a list of packages to install, which can be specified as os-agnostic, or by OS type. Examples of agnostic installs include `npm` and `pip`. Examples of `mac` include `brew`. You can also include "agnostic" installs in the os-specific sections, for example, "I only want this NPM package installed on my mac".


# Major TODOs:

1. User supplied functions, and `vim()` should move to this

# Install and Running

    poetry install
    poetry run runboot [args]

You can also set CMD args on the command line:

    poetry run runboot --prereqs t --name tommycarpenter --redovim n --systype mac --loctype work
    poetry run runboot --prereqs t --name tommy --redovim n --systype arch --loctype private
    /home/ubuntu/.local/bin/poetry run runboot --prereqs t --name ubuntu --redovim y --systype ubuntu --loctype work

It is normally safe to run this repeatedly in an additive manner; as in, you can add packages to `config.json` and re-run.
