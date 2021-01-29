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

1. python3 (I am using 3.9)
2. if on mac, `homebrew`, and if on Arch, `yay`
3. If on mac, XCode command line tools (can't even build `gcc` from `homebrew` without this): `sudo xcode-select --install`
4. make a directory called `~/dotfiles/` with all of your dotfiles. I personally have a private github `dotfiles` repo. I simply clone that to use this.
5. Write `config.json`; see the next section

Optional:
- if you want `vim` installed, your `.vimrc` should be using vim-plug.

# Config.json
The idea here is that you write `config.json` to completely describe what you would like linked, installed, ran, etc.

My personal `config.json` is included in this repo, for now, but I may eventually remove it from here.

Please see the (evolving) jsonschema for `config.json` in `bootstrap/schema.py` for the full schema.
But for an overview, these are the major sections:

1. `comments`: this is just a list of strings for your own keeping since JSON has no native commenting mechanism. IE remind yourself why you install something etc.
2. `initial_mkdirs`: directories to be recursively made. For example, `~/.ssh/..`. You can specify whether to try deleting the directory first, which is sometimes helpful for "rebootstrapping"
3. `links`: this is a list of softlinked dotfiles, from you `~/dotfiles` directory, that can vary by "location" if you want. IE, if you have a `.gitconfig` that you use on "work" machines, and a seperate one you use on "private" machines, you can specify these seperately, and when you run the script, you specify the location. There is also a generic `all` key for specifying location-agnostic keys.
4. `commands`: a list of arbitrary commands to run, which can be specified as os-agnostic, or by OS type. Warning, whatever you put here will be executed!. While I havent tested this on mac yet, on linux, if the command needs sudo, it will pause and ask for your sudo password using a `STDIN` pipe, so privleged commands are fine.
5. `packages`: a list of packages to install, which can be specified as os-agnostic, or by OS type. Examples of agnostic installs include `npm` and `pip`. Examples of `mac` include `brew`. You can also include "agnostic" installs in the os-specific sections, for example, "I only want this NPM package installed on my mac".


# Major TODOs:

1. Ubuntu support
2. [IN PROGRESS] Have a JSON schema validator for `config.json`
3. User supplied functions, and `vim()` should move to this

# Install and Running

First, install, which puts a script called `runboot.py` into your `PATH`. (Note; on Arch, the default it seems to put this in, `/home/tommy/.local/bin`, wasn't in my path at the time; I had to add it. But on the Mac, it was `/usr/local/bin/` which was):

    pip install .

Then, from the root of this repo, or any repo with your `config.json`:

    runboot.py

You can also set CMD args on the command line:

    runboot.py --prereqs t --name tommycarpenter --redovim n --systype mac --loctype work
    runboot.py --prereqs t --name tommy --redovim n --systype arch --loctype private

It is normally safe to run this repeatedly in an additive manner; as in, you can add packages to `config.json` and re-run.
There is a TODO to fix `redovim` for this, since one of the packages `YCM` installs gets added without a writable flag, and removal fails without sudo.

# Dockerfiles

The goal here is to bootstrap my Arch based dev env completely in a Docker container.

I came across this article after I started this, but this person really has a similar idea: https://www.codeproject.com/Articles/1247038/Using-Docker-to-maintain-a-development-environment

## Arch Notes:
TODO: this Dockerfile is not currently user agnostic. It should take a param for the username during the build. The hardcoding of `tommy` below should be fixed.

TODO 2: Sometime in 2020, Docker for Mac changed to buildkit.
The below does not work unless I run the build like this:

    DOCKER_BUILDKIT=0 ...

Issue explained here: https://github.com/moby/buildkit/issues/1267

## Build
It is not possible to do a `COPY` in Docker from an arbitrary host path.
The files get transfered to a docker build context from the local directory.
So, we first need our dotfiles here, then we remove them later.

   cp -r ~/dotfiles dotfiles/

Now, build!

    DOCKER_BUILDKIT=0 docker build --no-cache -t devarch:latest . -f Dockerfiles/dev-arch/Dockerfile

Then to run:

    docker run -it -v /Users/$USER/Development:/home/tommy/workdir \
                   -v ~/.ssh:/home/$USER/.ssh \
                   -v /var/run/docker.sock:/var/run/docker.sock \
                   -h devarchwork \
                   devarchwork:latest

NOTE: the `docker.sock` innspiration came from https://itnext.io/docker-in-docker-521958d34efd
It is if you want to build docker images from within this, which is questionable..
(and what not to do came from https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/)

Finally,

    rm -rf dotfiles

Since the build is complete.

## Ubuntu CUDA Dev
EXPIRIMENTAL, IN PROGRESSM NOT DONE, PROBABLY IGNORE:

Note this requires https://github.com/NVIDIA/nvidia-docker to be on the host machine that will run the docker container
```
docker build -t devcudaub:0.0.1 . -f Dockerfiles/dev-ubuntu-cuda/Dockerfile
docker run --runtime=nvidia -it devcudaub:0.0.1
```
