# NOTES:
1) This requires: https://github.com/NVIDIA/nvidia-docker
2) Must do a `runtime` argument. Here is an example run command of the strait nvidia container:
```
docker run --runtime nvidia -it nvidia/cuda:10.0-devel /bin/bash
```
