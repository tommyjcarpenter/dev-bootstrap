FROM nvidia/cuda:10.0-devel

#install essentials
RUN apt-get update &&  apt-get install -y \
      software-properties-common \
      vim \
      git-core

#install fish
RUN apt-add-repository ppa:fish-shell/release-2 && apt-get update && apt-get install -y fish

CMD fish
