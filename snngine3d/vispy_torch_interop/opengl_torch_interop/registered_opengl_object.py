import ctypes
import numba.cuda
import numpy as np
import pandas as pd

import pycuda.driver
import pycuda.gpuarray
import pycuda.gpuarray
# noinspection PyUnresolvedReferences
from pycuda.gl import (
    RegisteredBuffer,
    RegisteredImage,
    RegisteredMapping,
    graphics_map_flags
)
import torch
from typing import Optional, Union


numpy_to_torch_dtype_dict = {
    np.int32: torch.int32,
    np.float32: torch.float32,
}

numpy_dtype_to_byte_size_dict = {
    np.int32: 4,
    np.float32: 4,
}


class ExternalMemory(object):
    """
    Provide an externally managed memory.
    Interface requirement: __cuda_memory__, device_ctypes_pointer, _cuda_memsize_
    """
    __cuda_memory__ = True

    def __init__(self, ptr, size):
        self.device_ctypes_pointer = ctypes.c_void_p(ptr)
        self._cuda_memsize_ = size


class RegisteredOpenGLObject:

    def __init__(self,
                 shape: tuple,
                 strides: tuple,
                 np_dtype: np.dtype,
                 gpu_data: Union[ExternalMemory, pycuda.driver.Array],
                 register_buffer: RegisteredBuffer,
                 mapping: RegisteredMapping,
                 register_buffer_ptr: int,
                 opengl_id: Optional[int],
                 device: Union[torch.device, int] = 0,
                 stream: int = 0):

        self._shape = shape
        self._strides = strides
        self._np_dtype = np_dtype
        self._stream = stream
        self._device = device

        self._registered_buffer: RegisteredBuffer = register_buffer
        self._mapping: RegisteredMapping = mapping
        self._register_buffer_ptr: int = register_buffer_ptr

        self._gpu_data: Union[ExternalMemory, pycuda.driver.Array] = gpu_data

        self._opengl_id = opengl_id

        self.tensor: Optional[torch.Tensor] = None
        # noinspection PyUnresolvedReferences
        self._numba_device_array: Optional[numba.cuda.cudadrv.devicearray.DeviceNDArray] = None

    @property
    def ctype_ptr(self):
        return self._gpu_data.device_ctypes_pointer

    @property
    def size(self):
        # noinspection PyProtectedMember
        return self._gpu_data._cuda_memsize_

    def map(self):
        self._registered_buffer.map(None)

    def unmap(self):
        # noinspection PyArgumentList
        self._mapping.unmap()

    # @property
    # def tensor(self) -> torch.Tensor:
    #     self.map()
    #     if self._tensor is None:
    #         self._tensor = torch.as_tensor(self.device_array, device=self.conf.device)
    #     return self._tensor

    def data_ptr(self) -> int:
        return self.tensor.data_ptr()

    @property
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.tensor.cpu().numpy())

    def unregister(self):
        # noinspection PyArgumentList
        self._registered_buffer.unregister()

    def copy_to_host(self):
        return self._numba_device_array.copy_to_host()
