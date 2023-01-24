#include <pybind11/include/pybind11/pybind11.h>
#include <pybind11/include/pybind11/numpy.h>
#include <pybind11/include/pybind11/stl.h>

#include <snn_sim_demo.cuh>


namespace py = pybind11;


SynapticCurrentUpdater make_SynapticCurrentUpdater(
    const int N,
    const int S,
    const int D,
    const int T,

    const long N_rep_dp, 
    const long N_delays_dp, 
    
    const long N_types_dp,
    const long N_states_dp,
    const long N_weights_dp,
    
    const long fired_dp,
    const long firing_times_dp,
    const long firing_idcs_dp,
    const long firing_counts_dp

){
    int* N_rep = reinterpret_cast<int*> (N_rep_dp);
    int* N_delays = reinterpret_cast<int*> (N_delays_dp);

    int* N_types = reinterpret_cast<int*> (N_types_dp);
    float* N_states = reinterpret_cast<float*> (N_states_dp);
    float* N_weights = reinterpret_cast<float*> (N_weights_dp);

    float* fired = reinterpret_cast<float*> (fired_dp);
    float* firing_times = reinterpret_cast<float*> (firing_times_dp);
    int* firing_idcs = reinterpret_cast<int*> (firing_idcs_dp);
    int* firing_counts = reinterpret_cast<int*> (firing_counts_dp);

    
    return SynapticCurrentUpdater(
        N,
        S,
        D,
        T,

        N_rep, 
        N_delays, 
        
        N_types, 
        N_states,
        N_weights,
        
        fired,
        firing_times,
        firing_idcs,
        firing_counts
    );
}



PYBIND11_MODULE(snn_sim_demo_cpp, m)
    {    
    py::class_<SynapticCurrentUpdater, std::shared_ptr<SynapticCurrentUpdater>>(m, "SynapticCurrentUpdater_") //, py::dynamic_attr())
    .def_readonly("N", &SynapticCurrentUpdater::N)
    .def_readonly("S", &SynapticCurrentUpdater::S)
    .def_readonly("D", &SynapticCurrentUpdater::D)
    .def_readonly("T", &SynapticCurrentUpdater::T)
    .def_readonly("t", &SynapticCurrentUpdater::t)
    .def_readonly("n_fired", &SynapticCurrentUpdater::n_fired)
    .def_readonly("n_fired_total", &SynapticCurrentUpdater::n_fired_total)
    .def_readonly("n_fired_total_m1", &SynapticCurrentUpdater::n_fired_total_m1)
    .def_readonly("n_fired_0", &SynapticCurrentUpdater::n_fired_0)
    .def_readonly("n_fired_m1", &SynapticCurrentUpdater::n_fired_m1)
    .def_readonly("firing_counts_idx", &SynapticCurrentUpdater::firing_counts_idx)
    .def_readonly("firing_counts_idx_m1", &SynapticCurrentUpdater::firing_counts_idx_m1)
    .def_readonly("n_fired_m1_to_end", &SynapticCurrentUpdater::n_fired_m1_to_end)
    .def("dense_to_sparse_conversion", &SynapticCurrentUpdater::dense_to_sparse_conversion, py::arg("verbose"))
    .def("shift_sim_pointers", &SynapticCurrentUpdater::shift_sim_pointers)
    .def("update_synaptic_current", &SynapticCurrentUpdater::update_synaptic_current)
    .def("__repr__",
        [](const SynapticCurrentUpdater &sim) {
            return ("SynapticCurrentUpdater(N=" + std::to_string(sim.N) 
                    + ", S=" + std::to_string(sim.S) 
                    + ", D=" + std::to_string(sim.D) 
                    + ", T=" + std::to_string(sim.T) 
                    + ", t=" + std::to_string(sim.t) 
                    + ")");
        });
    m.def("SynapticCurrentUpdater", &make_SynapticCurrentUpdater,
        py::arg("N"),
        py::arg("S"),
        py::arg("D"),
        py::arg("T"),
        
        py::arg("N_rep"),
        py::arg("N_delays"),
        
        py::arg("N_types"),
        py::arg("N_states"),
        py::arg("N_weights"),
        
        py::arg("fired"),
        py::arg("firing_times"),
        py::arg("firing_idcs"),
        py::arg("firing_counts")
    );
}