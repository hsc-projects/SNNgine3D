# noinspection PyPackageRequirements
from IPython.display import display_html
from itertools import chain, cycle
import numpy as np
import pandas as pd
from pycuda.compiler import SourceModule
import pycuda.driver as cuda
import torch


update_N_state_mod = SourceModule(
    """
__global__ void update_N_state(
    const int N,
    const float t,
    const float* r,
    const float* rt,
    float* N_states,
    const int* N_type,
    float* fired,
    const float thalamic_inh_input_current = 1.f,
    const float thalamic_exc_input_current = 1.f
)
{
    const int n = blockIdx.x * blockDim.x + threadIdx.x;

    if (n < N)
    {
        fired[n] = 0.f;

        float pt = N_states[n];
        float u = N_states[n + N];
        float v = N_states[n + 2 * N];
        const float a = N_states[n + 3 * N];
        const float b = N_states[n + 4 * N];
        const float c = N_states[n + 5 * N];
        const float d = N_states[n + 6 * N];
        float i = N_states[n + 7 * N];

        if (r[n] < pt)
        {
            const int ntype = N_type[n];
            i += (thalamic_exc_input_current * ntype + thalamic_exc_input_current * (1 - ntype)) * rt[n];
        }

        if (v > 30.f)
        {
            v = c;
            u = u + d;
            fired[n] = t;
        }

        v = v + 0.5f * (0.04f * v * v + 5 * v + 140 - u + i);
        v = v + 0.5f * (0.04f * v * v + 5 * v + 140 - u + i);
        u = u + a * (b * v - u);

        N_states[n + N] = u;
        N_states[n + 2 * N] = v;
        N_states[n + 7 * N] = 0.f;
    }
}
"""
)

update_N_state_kernel = update_N_state_mod.get_function("update_N_state")


class TorchHolder(cuda.PointerHolderBase):

    """
    from: https://gist.github.com/szagoruyko/440c561f7fce5f1b20e6154d801e6033
    """

    # noinspection PyArgumentList
    def __init__(self, tensor):
        super(TorchHolder, self).__init__()
        assert tensor.device != torch.device('cpu')
        self.tensor: torch.Tensor = tensor
        self.gpudata = tensor.data_ptr()

    def get_pointer(self, **kwargs):
        return self.tensor.data_ptr()

    @property
    def as_array(self):
        return self.tensor.cpu().flatten().numpy().round(2)

    def print_as_list(self, *prefixes):
        print(*prefixes, list(self.as_array))

    def print_col_as_list(self, col, *prefixes):
        print(*prefixes, list(self.tensor[:, col].cpu().numpy().round(2)))

    def print_row_as_list(self, row, *prefixes):
        print(*prefixes, list(self.tensor[row].cpu().numpy().round(2)))

    @property
    def shape(self):
        return self.tensor.shape

    def __repr__(self):
        return self.tensor.__repr__()


def display_side_by_side(*args, titles=cycle([''])):
    """
    from: https://stackoverflow.com/questions/38783027/jupyter-notebook-display-two-pandas-tables-side-by-side
    """
    html_str = ''
    for df, title in zip(args, chain(titles, cycle(['</br>']))):
        if not isinstance(df, pd.DataFrame):
            if isinstance(df, TorchHolder):
                df = df.tensor
            if isinstance(df, np.ndarray):
                df = pd.DataFrame(df)
            elif isinstance(df, torch.Tensor):
                transpose = (df.ndim == 1)
                df = pd.DataFrame(df.cpu().numpy())
                if transpose is True:
                    df = df.T
        html_str += '<th style="text-align:center"><td style="vertical-align:top">'
        html_str += f'<h2 style="text-align: center;">{title}</h2>'
        html_str += df.to_html(float_format=lambda x: '%.2f' % x).replace('table', 'table style="display:inline"')
        html_str += '</td></th>'

    display_html(html_str, raw=True)


def print_neuron_info(n, n_state):
    print(f"\tN{n}: pt={n_state[0]:.2f}, u={n_state[1]:.2f}, v={n_state[2]:.2f}, a={n_state[2]:.2f}, "
          f"b={n_state[4]:.2f}, c={n_state[5]:.2f}, d={n_state[6]:.2f}, i={n_state[7]:.2f}")


# noinspection PyPep8Naming
def make_neurons_states(N, N_types_):
    r = torch.round(torch.rand(N).cuda() * 100) / 100

    Neuron_states = torch.zeros((8, N)).cuda()  # Neurons States (float) [rows: pt, u, v, a, b, c, d, i]
    # pt := probability of thalamic current injection
    Neuron_states[0] = torch.rand(N).cuda()  # probability thalamic input current injection
    Neuron_states[2] = -65.  # v
    Neuron_states[3] = .02 + .08 * r * N_types_  # a
    Neuron_states[4] = .2 + .05 * (1. - r) * N_types_  # b
    Neuron_states[5] = -65 + 15 * (r ** 2) * ~N_types_  # c
    Neuron_states[6] = 2 * N_types_ + (8 - 6 * (r ** 2)) * ~N_types_  # d
    Neuron_states[1] = Neuron_states[3] * Neuron_states[1]  # u  = b * v
    Neuron_states[7] = 0  # i

    print("neuron states:")
    for n in range(N):
        print_neuron_info(n, Neuron_states[:, n])
    print()
    return TorchHolder(Neuron_states)


def print_n_rep(N_rep: TorchHolder):
    print("\nsynapses:\n\tpre-synaptic neuron -> [post-synaptic neuron0, post-synaptic neuron1, ....]")
    for n in range(N_rep.shape[1]):
        N_rep.print_col_as_list(n, f'\t{n} -> ')
    return N_rep


# noinspection PyPep8Naming
def make_n_rep(S, N):
    N_rep_ = np.zeros((S, N), dtype=np.int32)
    for n in range(N):
        N_rep_[:, n] = np.random.choice(N, size=S, replace=False)
    N_rep_ = TorchHolder(torch.Tensor(N_rep_).type(torch.int32).cuda())
    print_n_rep(N_rep_)
    return N_rep_


def print_n_delays(N_delays: TorchHolder):
    print("\ndelays: neuron, [first synapse index with delay 0, first synapse index with delay 1, ...]")
    for n in range(N_delays.tensor.shape[1]):
        N_delays.print_col_as_list(n, f'\tN{n}: ')
    return N_delays


# noinspection PyPep8Naming
def make_n_delays(D, N, S):
    N_delays_ = TorchHolder(torch.zeros((D + 1, N)).type(torch.int32).cuda())
    for d in range(D):
        N_delays_.tensor[d + 1] = N_delays_.tensor[d] + (torch.rand(N).cuda() < .5).type(torch.int32)
    N_delays_.tensor[D, N_delays_.tensor[D] < S] = S
    print_n_delays(N_delays_)
    return N_delays_


# noinspection PyPep8Naming
def make_n_weights(N_types, N_rep):
    N_weights_ = torch.rand(size=N_rep.tensor.shape).cuda()
    inh_mask = ~N_types.tensor.type(torch.bool)
    N_weights_[:, inh_mask] = -N_weights_[:, inh_mask]
    N_weights_[N_weights_ > 0] = N_weights_[N_weights_ > 0] + 5
    N_weights_ = TorchHolder(N_weights_)
    print("\nweights:")
    for n in range(N_weights_.shape[1]):
        N_weights_.print_col_as_list(n, f'\tN{n}: ')
    return N_weights_
