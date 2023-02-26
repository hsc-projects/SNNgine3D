import numpy as np
import pandas as pd
import torch


class TorchCollection:

    def __init__(self, device, default_int_dtype, default_float_dtype, bprint_allocated_memory=False):
        self.device = torch.device(device)
        self.last_allocated_memory = 0
        self.bprint_allocated_memory = bprint_allocated_memory
        self.registered_buffers = []
        self._default_int_dtype = default_int_dtype
        self._default_float_dtype = default_float_dtype

    def izeros(self, shape) -> torch.Tensor:
        return torch.zeros(shape, dtype=self._default_int_dtype, device=self.device)

    def fzeros(self, shape) -> torch.Tensor:
        return torch.zeros(shape, dtype=self._default_float_dtype, device=self.device)

    def frand(self, shape) -> torch.Tensor:
        return torch.rand(shape, dtype=self._default_float_dtype, device=self.device)

    @staticmethod
    def to_dataframe(tensor: torch.Tensor):
        return pd.DataFrame(tensor.cpu().numpy())

    def print_allocated_memory(self, naming='', f=10**9):
        if self.bprint_allocated_memory:
            last = self.last_allocated_memory
            self.last_allocated_memory = now = torch.cuda.memory_allocated(0) / f
            diff = np.round((self.last_allocated_memory - last), 3)
            unit = 'GB'
            unit2 = 'GB'
            if self.last_allocated_memory < 0.1:
                now = now * 10 ** 3
                unit = 'MB'
            if diff < 0.1:
                diff = np.round((self.last_allocated_memory - last) * 10 ** 3, 1)
                unit2 = 'MB'
            now = np.round(now, 1)
            print(f"memory_allocated({naming}) = {now}{unit} ({'+' if diff >= 0 else ''}{diff}{unit2})")

    def unregister_registered_buffers(self):
        for rb in self.registered_buffers:
            rb.unregister()


class Torch32BitCollection(TorchCollection):

    def __init__(self, device, bprint_allocated_memory=False):

        super().__init__(device=device, default_int_dtype=torch.int32, default_float_dtype=torch.float32,
                         bprint_allocated_memory=bprint_allocated_memory)





