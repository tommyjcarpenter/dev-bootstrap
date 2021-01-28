# Summary
This "package" allows you to specify a complete dev env setup, including packages to install (homebrew, yay, pacman, npm, etc etc).
You write a `config.json`, then run a python CLI tool.

# Isn't there stuff already like this?
There are probably many. However, the well known ones; Puppet, Chef, Ansible, etc, are very heavyweight for my needs.

This was only a few hundred lines of python, and I've been using this to setup new computers (eg new Macs, new PC builds) and Dockerized development environments for years.

I am planning on making this more extensible so the user can provide functions that get run.

# Prerequisites

1. python3 (I am using 3.9)
2. if on mac, `homebrew`, and if on Arch, `yay`
3. If on mac, XCode command line tools (can't even build `gcc` from `homebrew` without this): `sudo xcode-select --install`
3. fish shell. TODO: make this configurable! This project is not geared towards `bash` at the moment.
4. make a directory called `~/dotfiles/` with all of your dotfiles. I personally have a private github `dotfiles` repo. I simply clone that to use this.
5. Write `config.json`; see the next section

# Config.json

TODO: (write this section)

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

# Arch
## Building

TOMMY WARNING: Sometime in 2020, Docker for Mac changed to buildkit.
The below does not work unless I run the build like this:

    DOCKER_BUILDKIT=0 ...

These seem relevent:
1. https://unix.stackexchange.com/questions/631177/arch-linux-in-docker-on-a-free-system-is-running-out-of-space/631178#631178
2. https://github.com/moby/buildkit/issues/1267
3. https://stackoverflow.com/questions/63652551/docker-build-vs-docker-run-dont-behave-the-same

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
