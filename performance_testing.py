from phe import paillier
import time
import statistics
from paillier import trigonometric_values, alice_encrypt_values, Server_compute_homomorphic_ecnryption, Bob_compute_distance
import sys
import io

def run_performance_test(num_iterations=5):
    # Lists to store timing results for each iteration
    timings_per_iteration = {
        'key_generation': [],
        'encryption': [],
        'server_computation': [],
        'decryption': [],
        'total': []
    }
    
    print(f"Running {num_iterations} iterations of the protocol...\n")
    
    # Create a string buffer to capture output
    output_buffer = io.StringIO()
    
    for i in range(num_iterations):
        iteration_timings = {}
        total_start_time = time.time()
        
        # Time key generation
        start_time = time.time()
        public_key, private_key = paillier.generate_paillier_keypair()
        iteration_timings['key_generation'] = time.time() - start_time

        # Test coordinates
        lat_A, lon_A = 50.379320, -4.131244  # Alice's coordinates
        lat_B, lon_B = 50.381813, -4.127100  # Bob's coordinates
        geofence_radius = 0.39  # Radius in kilometers

        # Step 1: Convert degrees to radians and compute trigonometric values
        alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(lat_A, lon_A, lat_B, lon_B)

        # Step 2: Time Alice's encryption
        start_time = time.time()
        alice_data = alice_encrypt_values(public_key, alpha, gamma, zeta, eta, theta, lambda_, mu)
        iteration_timings['encryption'] = time.time() - start_time

        # Step 3: Time server computation
        start_time = time.time()
        enc_a = Server_compute_homomorphic_ecnryption(alice_data, beta, delta, mu, nu, eta)
        iteration_timings['server_computation'] = time.time() - start_time

        # Step 4: Time Bob's decryption and distance computation
        start_time = time.time()
        # Redirect stdout to capture output
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        distance = Bob_compute_distance(enc_a, private_key, geofence_radius)
        sys.stdout = old_stdout
        iteration_timings['decryption'] = time.time() - start_time

        # Calculate total time for this iteration
        iteration_timings['total'] = time.time() - total_start_time

        # Store timings for this iteration
        for key in iteration_timings:
            timings_per_iteration[key].append(iteration_timings[key])

        print(f"Iteration {i+1}/{num_iterations} completed")

    # Calculate statistics
    stats = {}
    for operation in timings_per_iteration:
        times = timings_per_iteration[operation]
        stats[operation] = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times)
        }

    # Print detailed performance report
    print("\nDetailed Performance Report")
    print("=" * 60)
    
    for operation in stats:
        print(f"\n{operation.replace('_', ' ').title()} Statistics:")
        print("-" * 40)
        print(f"Mean time:     {stats[operation]['mean']:.4f} seconds")
        print(f"Median time:   {stats[operation]['median']:.4f} seconds")
        print(f"Std deviation: {stats[operation]['std_dev']:.4f} seconds")
        print(f"Min time:      {stats[operation]['min']:.4f} seconds")
        print(f"Max time:      {stats[operation]['max']:.4f} seconds")

if __name__ == "__main__":
    run_performance_test() 