#pragma once

#include <iostream>

#include <cuda/helper_cuda.h>

#include <cuda_runtime.h>

#include "cublas_v2.h"
#include <cusparse.h>

#ifdef __INTELLISENSE__

#define KERNEL_ARGS2(grid, block)
#define KERNEL_ARGS3(grid, block, sh_mem)
#define KERNEL_ARGS4(grid, block, sh_mem, stream)

#else

#define KERNEL_ARGS2(grid, block) <<< grid, block >>>
#define KERNEL_ARGS3(grid, block, sh_mem) <<< grid, block, sh_mem >>>
#define KERNEL_ARGS4(grid, block, sh_mem, stream) <<< grid, block, sh_mem, stream >>>

#endif

#define WRAP(x) do {x} while (0)
#define checkCusparseErrors(x) WRAP(									\
  cusparseStatus_t err = (x);											\
  if (err != CUSPARSE_STATUS_SUCCESS) {									\
    std::cerr << "\nCusparse Error " << int(err) << " ("                \
        << cusparseGetErrorString(err) <<") at Line "                   \
        << __LINE__ << " of " << __FILE__ << ": " << #x << std::endl;   \
    exit(1);															\
  }																		\
)



struct LaunchParameters
{
	dim3 block3;
	dim3 grid3;

	int block_size;			
	int min_grid_size;		
	
	int grid_size;			

	void* func;

	LaunchParameters();

	LaunchParameters(
		int n_threads_x,
		void* init_func
	);

	void init_sizes(
		int n_threads_x,
		void* init_func
	);

};

struct SynapticCurrentUpdater
{
    int N;
    int S;
    int D;
    int T;

    int* N_rep;
    int* N_delays;

    int* N_types;
    float* N_states;
    float* N_weights;

    float* fired;               // during each step we collect firing times as floats 
                                // i.e. a neuron n fired at time t, then fired[n] = t 

    // read (meaning): the "current_update_"-kernel will be applied on all 
    //                 firing indices between firing_idcs_read and firing_idcs_write - 1

    // write (meaning): the cusparseDenseToSparse conversion will be executed as if
    //                  the respective arrays would start where the "write"-pointers point

    float* firing_times_write;  // pointer (used by the cusparseDenseToSparse conversion)
    float* firing_times_read;   // pointer (used by the current-update kernel)
    float* firing_times;        // pointer to the start of array

    int* firing_idcs_write;   // pointer (used by the cusparseDenseToSparse conversion)
    int* firing_idcs_read;    // pointer (used by the current-update kernel)
    int* firing_idcs;         // pointer to the start of array

    int* firing_counts_write;  // pointer (used by the cusparseDenseToSparse conversion)
    int* firing_counts;        // pointer (used by the current-update kernel)


    LaunchParameters lp_update_state;

    cusparseHandle_t fired_handle;

    cusparseSpMatDescr_t firing_times_sparse;
    cusparseDnMatDescr_t firing_times_dense;

    void* fired_buffer{nullptr};
    size_t fired_buffer_size = 0;

    int n_fired = 0;
    int n_fired_total = 0;
    int n_fired_total_m1 = 0;
    int n_fired_0 = 0;
    int n_fired_m1 = 0;

    int firing_counts_idx = 1;
    int firing_counts_idx_m1 = 1;

    int reset_firing_times_ptr_threshold;
    int reset_firing_count_idx_threshold;
    int n_fired_m1_to_end = 0;

    int t = 0;
    bool resetting = false;

    SynapticCurrentUpdater(
      int N_,
      int S_,
      int D_,
      int T_,

      int* N_rep_,
      int* N_delays_,

      int* N_types_,
      float* N_states_,
      float* N_weights_,

      float* fired_,
      float* firing_times_,
      int* firing_idcs_,
      int* firing_counts_
    );


    void print_fired();
    void print_info(bool print_fired = false);
    void dense_to_sparse_conversion(bool verbose);
    void shift_sim_pointers();
    void update_synaptic_current();

};