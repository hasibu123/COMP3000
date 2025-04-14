import pandas as pd
from phe import paillier
from haversine import haversine
from paillier import trigonometric_values, alice_encrypt_values, server_compute_homomorphic_encryption, Bob_compute_distance
import sys
from io import StringIO
import time  # Add time module

# Load the dataset
data = pd.read_csv("names.csv") 

center_lat = 50.375618
center_lon = -4.139433
geofence_radius = 0.5  # km

# Step 1: Key Generation 
public_key, private_key = paillier.generate_paillier_keypair()

# Define a function for privacy-preserving haversine distance
def is_within_geofence(center_lat, center_lon, geofence_radius, data_latitude, data_longtitude):
    # Get trigonometric values
    alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(
        center_lat, center_lon, data_latitude, data_longtitude
    )

    # Get encrypted values from Alice
    alice_data = alice_encrypt_values(public_key, alpha, gamma, zeta, eta, theta, lambda_, mu)

    # Server computes homomorphic encryption
    enc_a = server_compute_homomorphic_encryption(alice_data, beta, delta, mu, nu, eta)

    # Suppress output from Bob_compute_distance
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    distance = Bob_compute_distance(enc_a, private_key, geofence_radius)
    sys.stdout = old_stdout
    
    return distance <= geofence_radius, distance

# List to store results
results = []

# Iterate through the dataset
for _, row in data.iterrows():
    data_latitude = row['latitude']
    data_longtitude = row['longitude']

    # Measure time for each calculation
    start_time = time.time()
    inside, dist = is_within_geofence(center_lat, center_lon, geofence_radius, data_latitude, data_longtitude)
    calculation_time = time.time() - start_time

    # Validate using standard haversine library
    haversine_distance = haversine((center_lat, center_lon), (data_latitude, data_longtitude))

    results.append({
        "name": row["name"],
        "latitude": data_latitude,
        "longitude": data_longtitude,
        "haversine distance": round(haversine_distance, 2),
        "distance": round(dist, 2),
        "status": "INSIDE" if inside else "OUTSIDE",
        "time taken (s)": round(calculation_time, 4)  # Add time taken to results
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Print table
print(results_df)
