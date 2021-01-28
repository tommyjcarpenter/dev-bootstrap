FROM archlinux/base
MAINTAINER tommyjcarpenter@gmail.com

# Update keyring first; on feb 5 2020 the next line was blowing up due to invalid sig
RUN pacman -Sy archlinux-keyring --noconfirm

# we need sudo in order to create a "normal non root user" but who can still install stuff
RUN pacman -Syyu sudo fish --noconfirm

ENV USER tommy
ENV HOME /home/$USER
ENV SHELL /usr/bin/fish

RUN useradd --shell=$SHELL $USER -d $HOME
RUN usermod -L $USER
RUN echo "$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "$USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN mkdir $HOME; chown -R $USER:$USER $HOME
# The below is questionable. If doing any development that does "make install" puts headers in /usr/local/include, it will fail without this
RUN chown -R $USER:$USER  /usr/local

# switch users
USER $USER
WORKDIR $HOME

# Install prequisites
# base-devel needed for yay: https://github.com/Jguer/yay#installation
# pkgconf and libffi is needed for python3.8 to work correctly https://stackoverflow.com/questions/27022373/python3-importerror-no-module-named-ctypes-when-using-value-from-module-mul
#     see a comment deeper into the thread about pkgconf being needed on arch!
# gvim: even though we dont need vim gui gvim enables clipboard support
# go and fakeroot are needed for yay, and go is needed for go development
# go-tools is for go development
# gawk and procps-ng are needed for fisherman
# powerline powerline-fonts rxvt-unicode are all for font stuff
# openssh is for being able to ssh into other servers using the key on the host (it gets mounted)
RUN sudo pacman -Syyu \
        base-devel \
        pkgconf \
        libffi \
        python \
        python-pip \
        git \
        gawk \
        procps-ng \
        clang \
        make \
        sudo \
        fakeroot \
    --noconfirm

# get yay, AUR package manager,  mkpkg isn't allowed to run as root
# http://allanmcrae.com/2015/01/replacing-makepkg-asroot/
# https://bbs.archlinux.org/viewtopic.php?id=229027
RUN git clone https://aur.archlinux.org/yay.git
WORKDIR $HOME/yay
RUN makepkg -si --noconfirm
RUN rm -rf yay

WORKDIR $HOME

# Install bootstrap
COPY dotfiles/ dotfiles/
COPY config.json .
RUN mkdir py
COPY bin/ py/bin/
COPY bootstrap/ py/bootstrap/
COPY setup.py py/
# We do this in Arch only, since a later package in bootstrap will complain about a conflict here. Arch wants python packages installed via pacman moreso than pip.
RUN sudo pacman -S python-click --noconfirm
# we use sudo since this would install into /home/tommy/.local/bin/runbootstrap.py otherwise and thats not yet in PATH (alternatively, we could add that to PATH)
RUN sudo pip3 install py/

# run it!
RUN runboot.py --prereqs t --name tommy --redovim y --systype arch --loctype work

# Cleanup
RUN sudo pip3 uninstall -y bootstrap
RUN sudo rm -rf py/
RUN rm config.json
# (clear pac cache)
RUN sudo pacman -Sc --noconfirm

# vim setup/plugins
# this TERM is set in the fish config, but 256 colors didnt work until I set it in here as well.. requires investigation..
ENV TERM xterm-256color

# Set timezone; exa will complain otherwise
# https://wiki.archlinux.org/index.php/System_time
# https://github.com/ogham/exa/issues/453
RUN sudo ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

# Enter
WORKDIR $HOME/workdir
CMD tmux
