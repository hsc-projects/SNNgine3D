#include <snn_sim_demo.cuh>


LaunchParameters::LaunchParameters()
{
	block_size = 0;
	grid_size = 0;
	block3 = dim3(block_size);
	grid3 = dim3(grid_size);
}

LaunchParameters::LaunchParameters(const int n_threads_x, void*init_func)
{
	func = init_func;
	init_sizes(n_threads_x, init_func);
	block3 = dim3(block_size);
	grid3 = dim3(grid_size);
}


void LaunchParameters::init_sizes(const int n_threads_x, void* init_func)
{	
	cudaOccupancyMaxPotentialBlockSize(&min_grid_size, &block_size, func, 0, 64);
	grid_size = (n_threads_x + block_size - 1) / block_size;
	if (grid_size == 1) {
		block_size = std::min(block_size, n_threads_x);
	}
}



SynapticCurrentUpdater::SynapticCurrentUpdater(
    const int N_,
    const int S_,
    const int D_,
    const int T_,

    int* N_rep_, 
    int* N_delays_, 
    
    int* N_types_, 
    float* N_states_,
	float* N_weights_,
	
    float* fired_,
	float* firing_times_,
	int* firing_idcs_,
	int* firing_counts_
){
    
	N = N_;
	S = S_;
	D = D_;
    T = T_;

    N_rep = N_rep_;
    N_delays = N_delays_;

	N_types = N_types_;
    N_states = N_states_;
	N_weights = N_weights_;

	// Pointer initializations
	fired = fired_;	
	firing_times = firing_times_;
	firing_idcs = firing_idcs_;
	firing_counts = firing_counts_;

	// Initially, all pointers point to the start of the respective array.
	firing_times_write = firing_times;
	firing_times_read = firing_times;

	firing_idcs_write = firing_idcs;
	firing_idcs_read = firing_idcs;
	
	firing_counts_write = firing_counts;


	reset_firing_times_ptr_threshold = 13 * N;
	reset_firing_count_idx_threshold = 2 * T;

	// Cusparse Initialization (must only be done once)
	checkCusparseErrors(cusparseCreate(&fired_handle));
	checkCusparseErrors(cusparseCreateDnMat(&firing_times_dense,
		1, N, N,
		fired,
		CUDA_R_32F, CUSPARSE_ORDER_ROW));
	
	checkCusparseErrors(cusparseCreateCsr(&firing_times_sparse, 1, N, 0,
		firing_counts_write,
		firing_idcs_write,
		firing_times_write,
		CUSPARSE_INDEX_32I, CUSPARSE_INDEX_32I,
		CUSPARSE_INDEX_BASE_ZERO, CUDA_R_32F));

	checkCusparseErrors(cusparseDenseToSparse_bufferSize(
		fired_handle, firing_times_dense, firing_times_sparse,
		CUSPARSE_DENSETOSPARSE_ALG_DEFAULT,
		&fired_buffer_size));
	checkCudaErrors(cudaMalloc(&fired_buffer, fired_buffer_size));

}


__global__ void update_current_(
	const int N, const int S, const int D,
	const int* fired_idcs_read, const int* fired_idcs, 
	const float* firing_times_read, const float* firing_times,
	const int* N_flags, const int* N_rep, float* N_weights, float* N_states, const int* N_delays,
	const int n_fired_m1_to_end, const int n_fired,
	const int t
)
{
	const int fired_idx = blockIdx.x * blockDim.x + threadIdx.x;

	if (fired_idx < n_fired)
	{
		int n;  			// pre-synaptic neuron
		int firing_time;	// firing time of the pre-synaptic neuron

		if (fired_idx < n_fired_m1_to_end)
		{
			// global index of firing-array < len(fired-array) 
			// -> use the trailing pointer
			n = fired_idcs_read[fired_idx];
			firing_time = __float2int_rn(firing_times_read[fired_idx]);
		}
		else
		{
			// global index of firing-array >= len(fired-array) 
			// -> use the 'normal' pointer
			n = fired_idcs[fired_idx - n_fired_m1_to_end];
			firing_time = __float2int_rn(firing_times[fired_idx - n_fired_m1_to_end]);
		}

		int delay = t - firing_time;  // time passed since the neuron fired
		const int delay_idx = n + N * (delay);  

		int snk_N; 		// post-synaptic Neuron-ID
		int idx;		// synapse-index 
		
		// row-index of the first synapse with a delay d_next = delay + 1
		int s_end = N_delays[delay_idx + N];  

		float w;		// weight of the synapse

		// loop through all synapses with a delay d == delay
		for (int s = N_delays[delay_idx]; s < s_end; s++)
		{
			idx = n + N * s;		// synapse-index 
			snk_N = N_rep[idx];		// post-synaptic Neuron-ID

			if (snk_N >= 0)  // allows to delete synapses by placing -1
			{
				// add the weight of synapse to the current-value of the post-synaptic neuron
				w  =  N_weights[idx];			
				atomicAdd(&N_states[snk_N + 7 * N], w);		
			}
		}
	}
	
}


void SynapticCurrentUpdater::print_fired(){
	// TODO: rewrite the copying + printing
	printf("fired         = [");
	for (int i = 0; i < N; i++) {
		float fired_value;
		cudaMemcpy(&fired_value, fired + i, 
			sizeof(float), cudaMemcpyDeviceToHost);
		printf("%.0f", fired_value);
		if (i < N - 1){
			printf(", ");
		}

	}
	printf("].\n");
}


void SynapticCurrentUpdater::print_info(bool print_counts){
	
	if (print_counts){
		printf("t = %d,", t);
		printf("\nn_fired                      = %d, ", n_fired);
		if (n_fired < 10) printf(" ");
		printf("n_fired_m1_to_end            = %d,", n_fired_m1_to_end);
		printf("\nn_fired_0                    = %d, ", n_fired_0);
		if (n_fired_0 < 10) printf(" ");
		printf("n_fired_m1                   = %d,", n_fired_m1);
		printf("\nn_fired_total                = %d, ", n_fired_total);
		if (n_fired_total < 10) printf(" ");
		printf("n_fired_total_m1             = %d,", n_fired_total_m1);
		// printf("\nfiring_counts_write=%p", (void * )firing_counts_write);
		printf("\nfiring_counts_write (offset) = %ld,", firing_counts_write - firing_counts);
		printf("\nfiring_idcs_read    (offset) = %ld, ", firing_idcs_read - firing_idcs);
		if (firing_idcs_read - firing_idcs < 10) printf(" ");
		printf("firing_idcs_write  (offset)  = %ld,", firing_idcs_write - firing_idcs);
		printf("\nfiring_times_read   (offset) = %ld, ", firing_times_read - firing_times);
		if (firing_times_read - firing_times < 10) printf(" ");
		printf("firing_times_write (offset)  = %ld.", firing_times_write - firing_times);
		printf("\n");
	}
}


void SynapticCurrentUpdater::shift_sim_pointers(){

	checkCudaErrors(cudaMemcpy(
		&n_fired_0, firing_counts + firing_counts_idx, sizeof(int), cudaMemcpyDeviceToHost));

	n_fired_total += n_fired_0;
	n_fired += n_fired_0;
	firing_counts_idx += 2;

	if (n_fired_total > n_fired_total_m1) {
		n_fired_m1_to_end += n_fired_0;
	}


	if (t >= D)
	{
		cudaMemcpy(&n_fired_m1, firing_counts + firing_counts_idx_m1, 
                   sizeof(int), cudaMemcpyDeviceToHost);

		n_fired_total_m1 += n_fired_m1;
		n_fired -= n_fired_m1;
		n_fired_m1_to_end -= n_fired_m1;
		firing_counts_idx_m1 += 2;
	}

	if (n_fired_total <= reset_firing_times_ptr_threshold)
	{
		firing_times_write += n_fired_0;
		firing_idcs_write += n_fired_0;
	}
	else
	{
		firing_times_write = firing_times;
		firing_idcs_write = firing_idcs;
		n_fired_total = 0;
		resetting = true;
	}

	if (firing_counts_idx > reset_firing_count_idx_threshold){
		firing_counts_idx = 1;
		firing_counts_write = firing_counts;
	} else {
		firing_counts_write += 2;
	}
	
	if (firing_counts_idx_m1 > reset_firing_count_idx_threshold){
		firing_counts_idx_m1 = 1;	
	} 


	if (n_fired_total_m1 <= reset_firing_times_ptr_threshold)
	{
		firing_times_read += n_fired_m1;
		firing_idcs_read += n_fired_m1;
	}
	else
	{
		firing_times_read = firing_times;
		firing_idcs_read = firing_idcs;
		n_fired_m1_to_end = n_fired_total;
		n_fired_total_m1 = 0;
		resetting = false;
	}

	cusparseCsrSetPointers(firing_times_sparse,
		firing_counts_write,
		firing_idcs_write,
		firing_times_write);

	checkCudaErrors(cudaDeviceSynchronize());
}

void SynapticCurrentUpdater::dense_to_sparse_conversion(const bool verbose)
{	

	checkCudaErrors(cudaDeviceSynchronize());

	// 2. DenseToSparse Conversion (using "write"-pointers).
	checkCusparseErrors(cusparseDenseToSparse_analysis(
		fired_handle, firing_times_dense, firing_times_sparse,
		CUSPARSE_DENSETOSPARSE_ALG_DEFAULT, fired_buffer));
	
	checkCudaErrors(cudaDeviceSynchronize());

	checkCusparseErrors(cusparseDenseToSparse_convert(
		fired_handle, firing_times_dense, firing_times_sparse,
		CUSPARSE_DENSETOSPARSE_ALG_DEFAULT, fired_buffer));
	
	if (verbose) print_info(true);
	print_fired();
	
}

void SynapticCurrentUpdater::update_synaptic_current()
{	
	
	int block_dim_x = 32;
	int grid_dim_x = static_cast<int>(::ceilf(static_cast<float>(n_fired) 
									  / static_cast<float>(block_dim_x)));
	// 4. Synaptic current update (kernel; using "read"-pointers).
	update_current_ KERNEL_ARGS2(grid_dim_x, block_dim_x)(
		N, S, D,
		firing_idcs_read, firing_idcs,
		firing_times_read, firing_times,
		N_types, N_rep, N_weights, N_states, N_delays,
		n_fired_m1_to_end, n_fired, t
    );
	
	checkCudaErrors(cudaDeviceSynchronize());

	t++;
}
