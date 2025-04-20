import pandas as pd
from phe import paillier
from haversine import haversine
from paillier import trigonometric_values, alice_encrypt_values, server_compute_homomorphic_encryption, Bob_compute_distance
import sys
from io import StringIO
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

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
        "time taken (s)": round(calculation_time, 4)
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Print table
print(results_df)

# Calculate delta_lat_km and delta_lon_km
results_df['delta_lat_km'] = (results_df['latitude'] - center_lat) * 111
results_df['delta_lon_km'] = (results_df['longitude'] - center_lon) * 111 * np.cos(np.radians(center_lat))

# Create figure and axis
fig, ax = plt.subplots(figsize=(8, 8))

# Plot the center
ax.plot(0, 0, 'bo', label='Center')

# Plot the geofence circle (radius 0.5 km)
circle = Circle((0, 0), 0.5, color='blue', fill=False, label='Geofence')
ax.add_patch(circle)

# Plot the points
inside_points = results_df[results_df['status'] == 'INSIDE']
outside_points = results_df[results_df['status'] == 'OUTSIDE']
ax.scatter(inside_points['delta_lon_km'], inside_points['delta_lat_km'], color='green', label='Inside')
ax.scatter(outside_points['delta_lon_km'], outside_points['delta_lat_km'], color='red', label='Outside')

# Set equal aspect ratio
ax.set_aspect('equal')

# Add labels and title
ax.set_xlabel('Δ Longitude (km)')
ax.set_ylabel('Δ Latitude (km)')
ax.set_title('Geofence Visualization')

# Add grid
ax.grid(True)

# Add legend
ax.legend()

# Save the plot
plt.savefig('geofence_plot.png')
print("Plot saved to geofence_plot.png")