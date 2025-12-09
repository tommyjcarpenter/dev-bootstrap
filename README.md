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
1. python3 (I am using 3.11) and `poetry` and `pyenv` (`curl https://pyenv.run | bash`)
2. if on mac, `homebrew`, and if on Arch, `yay`
3. If on mac, XCode command line tools (can't even build `gcc` from `homebrew` without this): `sudo xcode-select --install`
4. make a directory called `~/dotfiles/` with all of your dotfiles. I personally have a private github `dotfiles` repo. I simply clone that to use this.
5. Write `config.json`; see the next section

# Config.json
To use this package, you write a `config.json` to describe what you would like linked, installed, ran, etc.
That is the only input, other than a few cmd line parameters.

A sample (actually a copy of my real one!) config is included; see `sample_config.json`

My personal `config.json` is in my private `dotfiles` repo, and I clone it in step 4 above.

Please see the (evolving) jsonschema for `config.json` in `bootstrap/schema.py` for the full schema.
These are the major sections:

1. `comments`: this is a list of strings for your own sanity, since JSON has no native commenting mechanism.
2. `initial_mkdirs`: directories to be recursively made. For example, `~/.ssh/..`. You can specify whether to try deleting the directory first, which is helpful for "rebootstrapping"
3. `links`: this is a list of softlinked dotfiles, from you `~/dotfiles` directory, that can vary by "location" if you want. IE, if you have a `.gitconfig` that you use on "work" machines, and a seperate one you use on "private" machines, you can specify these seperately, and when you run the script, you specify the location. There is also a generic `all` key for specifying location-agnostic keys.
4. `commands`: a list of arbitrary commands to run, which can be specified as os-agnostic, or by OS type. Warning, whatever you put here will be executed! If the command needs sudo, it will pause and ask for your sudo password using a `STDIN` pipe, so privileged commands are fine.
5. `packages`: a list of packages to install, which can be specified as os-agnostic, or by OS type. You can also include "agnostic" installs in the os-specific sections, for example, "I only want this NPM package installed on my mac".

Supported package managers:
- `brew` / `brew_tap`: macOS Homebrew packages and taps
- `pacman` / `yay`: Arch Linux packages
- `ppa` / `apt` / `snap`: Ubuntu PPAs, apt packages, and snap packages
- `npm`: Node.js packages (cross-platform)
- `go_install`: Go packages via `go install` (cross-platform)
- `cargo`: Rust packages via `cargo install` (cross-platform)
- `fisher`: Fish shell plugins (cross-platform)

Note: For Ubuntu, `ppa` entries are automatically processed before `apt` regardless of order in the config.

6. `prereq_packages`: packages that provide language toolchains (rust/cargo, go, poetry) needed before other packages can be installed. These are installed before `packages`. Structure is the same as `packages` but keyed by OS only (no `all` section).

## Environment-Specific Configs

You can create separate config files for work vs private environments:
- `~/dotfiles/bootstrap_config.json` - main config (always loaded)
- `~/dotfiles/bootstrap_config_work.json` - loaded when `--loctype work`
- `~/dotfiles/bootstrap_config_private.json` - loaded when `--loctype private`

The extra config files are optional and use the same schema. They're processed after the main config, so you can put environment-specific packages (like kubernetes tools for work) in separate files.

# Prerequisites

1. You must have `homebrew` installed on mac, and `yay` installed on Arch linux.
2. You must have `~/dotfiles/` directory with your dotfiles in it.
3. You must have `config.json` file written.
4. You must have `python3` and `poetry` installed.

# Install and Running

    poetry install
    poetry run runboot [args]

You can also set CMD args on the command line:

    poetry run runboot --systype mac --loctype work
    poetry run runboot --systype arch --loctype private
    poetry run runboot --systype ubuntu --loctype work

The script is idempotent - it is safe to run repeatedly. You can add packages to `config.json` and re-run.

# Major TODOs:

1. User supplied functions
