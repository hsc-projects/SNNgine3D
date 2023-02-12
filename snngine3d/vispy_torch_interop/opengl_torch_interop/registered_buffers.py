import numba.cuda
import numpy as np

# noinspection PyUnresolvedReferences
from pycuda.gl import (
    RegisteredBuffer,
    RegisteredImage,
    RegisteredMapping,
    graphics_map_flags
)
import torch
from typing import Optional, Union

from .registered_opengl_object import ExternalMemory, numpy_dtype_to_byte_size_dict, RegisteredOpenGLObject


class RegisteredOpenGLBuffer(RegisteredOpenGLObject):

    def __init__(self,
                 buffer_id,
                 shape: Optional[tuple] = None,
                 np_dtype: Optional[np.dtype] = None,
                 cpu_array: Optional[np.array] = None,
                 device: Union[torch.device, int] = 0,
                 stream: int = 0):
        if cpu_array is not None:
            assert shape is None
            assert np_dtype is None
            shape = cpu_array.shape
            strides: tuple = cpu_array.strides
            np_dtype: np.dtype = cpu_array.dtype
        else:
            assert cpu_array is None
            # noinspection PyTypeChecker
            nbytes = numpy_dtype_to_byte_size_dict[np_dtype]
            strides = (shape[1] * nbytes, nbytes)

        numba.cuda.select_device(device.index if not isinstance(device, int) else device)

        reg = RegisteredBuffer(buffer_id)
        mapping: RegisteredMapping = reg.map(None)
        # noinspection PyArgumentList
        ptr, size = mapping.device_ptr_and_size()
        gpu_data = ExternalMemory(ptr, size)
        # noinspection PyArgumentList
        mapping.unmap()

        super().__init__(shape=shape, strides=strides,
                         gpu_data=gpu_data,
                         register_buffer=reg,
                         mapping=mapping,
                         register_buffer_ptr=ptr,
                         opengl_id=buffer_id,
                         np_dtype=np_dtype,
                         device=device,
                         stream=stream)

        # noinspection PyUnresolvedReferences
        self._numba_device_array = numba.cuda.cudadrv.devicearray.DeviceNDArray(
            shape=self._shape,
            strides=self._strides,
            dtype=self._np_dtype,
            stream=self._stream,
            gpu_data=self._gpu_data)

        self.tensor = torch.as_tensor(self._numba_device_array, device=self._device)


class RegisteredVBO(RegisteredOpenGLBuffer):

    def __init__(self, buffer_id: int, shape: tuple, device: Union[torch.device, int]):

        # noinspection PyTypeChecker
        super().__init__(buffer_id=buffer_id, shape=shape, device=device, np_dtype=np.float32)


class RegisteredIBO(RegisteredOpenGLBuffer):

    def __init__(self, buffer_id: int, shape: tuple, device: Union[torch.device, int]):

        # noinspection PyTypeChecker
        super().__init__(buffer_id=buffer_id, shape=shape, device=device, np_dtype=np.int32)
