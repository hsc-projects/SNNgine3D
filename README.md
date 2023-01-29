# SNNgine3D


Licensed under the terms of the [Apache License 2.0](https://spdx.org/licenses/Apache-2.0.html).
[New issues](https://github.com/hsc-projects/snngine3d/issues) and pull requests are welcome.

[//]: # (Please refer to the [contributing guide]&#40;https://github.com/hsc-projects/snngine3d/blob/main/CONTRIBUTING.md&#41;)
[//]: # (and [security policy]&#40;https://github.com/hsc-projects/snngine3d/blob/main/SECURITY.md&#41;.)


[![Created with Tyrannosaurus](https://img.shields.io/badge/Created_with-Tyrannosaurus-0000ff.svg)](https://github.com/dmyersturnbull/tyrannosaurus)
[![Build on vispy](https://img.shields.io/badge/Built_on-Vispy-black.svg)](https://vispy.org/)  

## Installation on Ubuntu 20.04

### Pre-requisites

* [PyTorch](https://pytorch.org/)
* [Nvidia CUDA](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#), preferably >=11.6
* "OpenGL-enabled"-[PyCUDA](https://wiki.tiker.net/PyCuda/Installation/Linux/). 
 
For example:  

    git clone https://github.com/inducer/pycuda.git
    cd pycuda
    git submodule update --init
    python ./configure.py --cuda-root=/usr/local/cuda --cuda-enable-gl
    su -c "make install"

### From Source
    
    git clone https://github.com/hsc-projects/snngine3D.git
    cd SNNgine3D
    pip install . 

## Docker
  
  docker run -d -p 4000:4000 --name nomachine0 --gpus all --cap-add=SYS_PTRACE hscprojects/snngine3d-nomachine:main
  (user & passw: snn)
