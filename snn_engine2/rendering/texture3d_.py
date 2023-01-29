import numpy as np
import numpy.linalg as la

import pycuda.driver as drv
from pycuda.compiler import SourceModule


from contextlib import contextmanager

import torch
from torch import Tensor, ByteTensor
import torch.nn.functional as F
from torch.autograd import Variable
import pycuda.driver
from pycuda.gl import graphics_map_flags
from glumpy import app, gloo, gl


# noinspection PyArgumentList
def test_3d_texture():
    # adapted from code by Nicolas Pinto
    w = 2
    h = 2
    d = 2
    shape = (w, h, d)

    a = np.asarray(np.random.randint(0, 50, shape), dtype=np.int32)
    a = np.asarray(np.random.rand(*shape), dtype=np.float32)

    descr = drv.ArrayDescriptor3D()
    descr.width = w
    descr.height = h
    descr.depth = d
    descr.format = drv.dtype_to_array_format(a.dtype)
    descr.num_channels = 1
    descr.flags = 0

    ary = drv.Array(descr)

    copy = drv.Memcpy3D()
    copy.set_src_host(a)
    copy.set_dst_array(ary)
    copy.width_in_bytes = copy.src_pitch = 8
    copy.src_height = copy.height = h
    copy.depth = d

    copy()

    a2 = np.asarray(np.zeros(shape, dtype=np.float32), dtype=np.float32)
    b1 = torch.zeros(shape, dtype=torch.float32, device='cuda')
    copy2 = drv.Memcpy3D()
    copy2.set_src_array(ary)
    # copy2.set_dst_host(a2)
    copy2.set_dst_device(b1.data_ptr())
    copy2.width_in_bytes = copy2.src_pitch = 8
    copy2.src_height = copy2.height = h
    copy2.depth = d

    copy2()

    copy2.set_dst_host(a2)
    copy2()

    mod = SourceModule(
        """
    texture<float, 3, cudaReadModeElementType> mtx_tex;
    __global__ void copy_texture(float *dest)
    {
      int x = threadIdx.x;
      int y = threadIdx.y;
      int z = threadIdx.z;
      int dx = blockDim.x;
      int dy = blockDim.y;
      int i = (z*dy + y)*dx + x;
      dest[i] = tex3D(mtx_tex, x, y, z);
      //dest[i] = x;
    }
    """
    )

    copy_texture = mod.get_function("copy_texture")
    mtx_tex = mod.get_texref("mtx_tex")

    mtx_tex.set_array(ary)

    dest = np.zeros(shape, dtype=np.float32, order="F")
    copy_texture(drv.Out(dest), block=shape, texrefs=[mtx_tex])
    res = la.norm(dest - a)
    print(dest, a, res)
    assert res == 0


@contextmanager
def cuda_activate(img):
    """Context manager simplifying use of pycuda.gl.RegisteredImage"""
    mapping = img.map()
    yield mapping.array(0,0)
    mapping.unmap()


def create_shared_texture(w, h, c=4,
                          map_flags=graphics_map_flags.WRITE_DISCARD,
                          dtype=np.uint8):
    """Create and return a Texture2D with gloo and pycuda views."""
    tex = np.zeros((h, w, c), dtype).view(gloo.Texture2D)
    tex.activate()  # force gloo to create on GPU
    tex.deactivate()
    cuda_buffer = pycuda.gl.RegisteredImage(
        int(tex.handle), tex.target, map_flags)
    return tex, cuda_buffer


def setup():
    global screen, cuda_buffer, state
    w, h = window.get_size()
    # setup pycuda and torch
    import pycuda.gl.autoinit
    import pycuda.gl
    assert torch.cuda.is_available()
    print('using GPU {}'.format(torch.cuda.current_device()))
    # torch.nn layers expect batch_size, channels, height, width
    state = torch.cuda.FloatTensor(1, 3, h, w)
    state.uniform_()
    state = Variable(state, volatile=True)
    # create a buffer with pycuda and gloo views
    tex, cuda_buffer = create_shared_texture(w, h, 4)
    # create a shader to program to draw to the screen
    vertex = """
    uniform float scale;
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        v_texcoord = texcoord;
        gl_Position = vec4(scale*position, 0.0, 1.0);
    } """
    fragment = """
    uniform sampler2D tex;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(tex, v_texcoord);
    } """
    # Build the program and corresponding buffers (with 4 vertices)
    screen = gloo.Program(vertex, fragment, count=4)
    # Upload data into GPU
    screen['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
    screen['texcoord'] = [(0, 0), (0, 1), (1, 0), (1, 1)]
    screen['scale'] = 1.0
    screen['tex'] = tex


def torch_process(state):
    """Random convolutions."""
    fs = 11
    filters, sgns = (
        Variable(init(torch.cuda.FloatTensor(3, 3, fs, fs)), volatile=True)
        for init in (
            lambda x: x.normal_(),
            lambda x: x.bernoulli_(0.52)
        ))
    filters = F.softmax(filters)*(sgns*2-1)
    state = F.conv2d(state, filters, padding=fs//2)
    state = state-state.mean().expand(state.size())
    state = state/state.std().expand(state.size())
    return state


# create window with OpenGL context
app.use('glfw')
window = app.Window(512, 512, fullscreen=False)


@window.event
def on_draw(dt):
    global state
    window.set_title(
        # str(window.fps).encode("ascii")
        str(window.fps)
    )
    tex = screen['tex']
    h,w = tex.shape[:2]
    # mutate state in torch
    state = torch_process(state).detach() # prevent autograd from filling memory
    img = F.tanh(state).abs()
    # convert into proper format
    tensor = img.squeeze().transpose(0,2).transpose(0,1).data # put in texture order
    tensor = torch.cat((tensor, tensor[:, :, 0].reshape(512, 512, 1)), 2) # add the alpha channel
    tensor[:,:,3] = 1 # set alpha
    # check that tensor order matches texture:
    # img[:,:,2] = 1 # set blue
    # img[100,:,:] = 1 # horizontal white line
    # img[:,200,0] = 1 # vertical magenta line
    tensor = (255*tensor).byte().contiguous() # convert to ByteTensor
    # copy from torch into buffer
    assert tex.nbytes == tensor.numel()*tensor.element_size()
    with cuda_activate(cuda_buffer) as ary:
        cpy = pycuda.driver.Memcpy2D()
        cpy.set_src_device(tensor.data_ptr())
        cpy.set_dst_array(ary)
        cpy.width_in_bytes = cpy.src_pitch = cpy.dst_pitch = tex.nbytes//h
        # cpy.width = w
        cpy.height = h
        cpy(aligned=False)
        torch.cuda.synchronize()
    # draw to screen
    window.clear()
    screen.draw(gl.GL_TRIANGLE_STRIP)


# not sure why this doesn't work right
@window.event
def on_close():
    pycuda.gl.autoinit.context.pop()


def test_3d_fp_surfaces():

    import pycuda.gpuarray as gpuarray
    from pycuda.tools import mark_cuda_test, dtype_to_ctype

    orden = "C"
    npoints = 32

    for prec in [np.int16, np.float32, np.float64, np.complex64, np.complex128]:

        print(prec)

        prec_str = dtype_to_ctype(prec)
        if prec == np.complex64:
            fpName_str = "fp_tex_cfloat"
            A_cpu = np.zeros([npoints, npoints, npoints], order=orden, dtype=prec)
            A_cpu[:].real = np.random.rand(npoints, npoints, npoints)[:]
            A_cpu[:].imag = np.random.rand(npoints, npoints, npoints)[:]
        elif prec == np.complex128:
            fpName_str = "fp_tex_cdouble"
            A_cpu = np.zeros([npoints, npoints, npoints], order=orden, dtype=prec)
            A_cpu[:].real = np.random.rand(npoints, npoints, npoints)[:]
            A_cpu[:].imag = np.random.rand(npoints, npoints, npoints)[:]
        elif prec == np.float64:
            fpName_str = "fp_tex_double"
            A_cpu = np.zeros([npoints, npoints, npoints], order=orden, dtype=prec)
            A_cpu[:] = np.random.rand(npoints, npoints, npoints)[:]
        else:
            fpName_str = prec_str
            A_cpu = np.zeros([npoints, npoints, npoints], order=orden, dtype=prec)
            A_cpu[:] = np.random.rand(npoints, npoints, npoints)[:] * 100.0

        A_gpu = gpuarray.to_gpu(A_cpu)  # Array randomized

        myKernRW = """
        #include <pycuda-helpers.hpp>

        surface<void, cudaSurfaceType3D> mtx_tex;

        __global__ void copy_texture(cuPres *dest, int rw)
        {
          int row   = blockIdx.x*blockDim.x + threadIdx.x;
          int col   = blockIdx.y*blockDim.y + threadIdx.y;
          int slice = blockIdx.z*blockDim.z + threadIdx.z;
          int tid = row + col*blockDim.x*gridDim.x + slice*blockDim.x*gridDim.x*blockDim.y*gridDim.y;
          if (rw==0){
             cuPres aux = dest[tid];
             fp_surf3Dwrite(aux, mtx_tex, row, col, slice,cudaBoundaryModeClamp);}
          else {
             cuPres aux = 0;
             fp_surf3Dread(&aux, mtx_tex, slice, col, row, cudaBoundaryModeClamp);
          dest[tid] = aux;
          }
        }
        """
        myKernRW = myKernRW.replace("fpName", fpName_str)
        myKernRW = myKernRW.replace("cuPres", prec_str)
        modW = SourceModule(myKernRW)

        copy_texture = modW.get_function("copy_texture")
        mtx_tex = modW.get_surfref("mtx_tex")
        cuBlock = (8, 8, 8)
        if cuBlock[0] > npoints:
            cuBlock = (npoints, npoints, npoints)
        cuGrid = (
            npoints // cuBlock[0] + 1 * (npoints % cuBlock[0] != 0),
            npoints // cuBlock[1] + 1 * (npoints % cuBlock[1] != 0),
            npoints // cuBlock[2] + 1 * (npoints % cuBlock[1] != 0),
        )
        copy_texture.prepare("Pi")  # ,texrefs=[mtx_tex])
        A_gpu2 = gpuarray.zeros_like(A_gpu)  # To initialize surface with zeros
        cudaArray = drv.gpuarray_to_array(A_gpu2, orden, allowSurfaceBind=True)
        A_cpu = A_gpu.get()  # To remember original array
        mtx_tex.set_array(cudaArray)
        copy_texture.prepared_call(
            cuGrid, cuBlock, A_gpu.gpudata, np.int32(0)
        )  # Write random array
        copy_texture.prepared_call(
            cuGrid, cuBlock, A_gpu.gpudata, np.int32(1)
        )  # Read, but transposed
        assert np.sum(np.abs(A_gpu.get() - np.transpose(A_cpu))) == np.array(
            0, dtype=prec
        )

        A_gpu.gpudata.free()


if __name__ == '__main__':
    # setup()
    # app.run()

    import pycuda.autoinit
    test_3d_fp_surfaces()
