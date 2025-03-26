import math
from phe import paillier
from haversine import haversine


#step 1: Convert degrees to radians and compute trigonometric values
def trigonometric_values(lat_A, lon_A, lat_B, lon_B):
# Convert degrees to radians
    latA = math.radians(lat_A)
    lonA = math.radians(lon_A)
    latB = math.radians(lat_B)
    lonB = math.radians(lon_B)

# Compute the trigonometric values as per the protocol
    alpha = math.cos(latA / 2)
    beta = math.sin(latB / 2)
    gamma = math.sin(latA / 2)
    delta = math.cos(latB / 2)
    zeta = math.cos(latA)
    eta = math.cos(latB)
    theta = math.sin(lonA / 2)
    lambda_ = math.cos(lonB / 2)
    mu = math.cos(lonA / 2)
    nu = math.sin(lonB / 2)
    return (alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu)
    
# Step 2: Alice computes encrypted values with her public key and sends them to ther server.
def alice_encrypt_values(public_key, alpha, gamma, zeta, eta, theta, lambda_, mu):
    # Compute
    alpha_squared = alpha**2
    neg_two_alpha_gamma = -2 * alpha * gamma
    gamma_squared = gamma**2
    zeta_eta_theta_lambda_squared = zeta * eta * (theta**2) * (lambda_**2)
    neg_two_zeta_eta_theta_lambda = -2 * zeta * eta * theta * lambda_
    zeta_mu = zeta * mu**2

    # Encrypt the values
    enc_alpha_squared = public_key.encrypt(alpha_squared)
    enc_neg_two_alpha_gamma = public_key.encrypt(neg_two_alpha_gamma)
    enc_gamma_squared = public_key.encrypt(gamma_squared)
    enc_zeta_eta_theta_lambda_squared = public_key.encrypt(zeta_eta_theta_lambda_squared)
    enc_neg_two_zeta_eta_theta_lambda = public_key.encrypt(neg_two_zeta_eta_theta_lambda)
    enc_zeta_mu = public_key.encrypt(zeta_mu)

# Alice sends encrypted values to the server
    return {
        "enc_alpha_squared": enc_alpha_squared,
        "enc_neg_two_alpha_gamma": enc_neg_two_alpha_gamma,
        "enc_gamma_squared": enc_gamma_squared,
        "enc_zeta_eta_theta_lambda_squared": enc_zeta_eta_theta_lambda_squared,
        "enc_neg_two_zeta_eta_theta_lambda": enc_neg_two_zeta_eta_theta_lambda,
        "enc_zeta_eta": enc_zeta_mu,
    }

# Step 3: The server computes alice encrypted values using homomorphic operations and send them to Bob
def Server_compute_homomorphic_ecnryption(alice_data, beta, delta, mu, nu, eta):
    beta_squared = beta**2
    delta_squared = delta**2
    mu_nu = mu * nu
    eta_nu_squared = eta * nu**2

    enc_a = (
        alice_data["enc_alpha_squared"] * beta_squared
        + alice_data["enc_neg_two_alpha_gamma"] * (beta * delta)
        + alice_data["enc_gamma_squared"] * delta_squared
        + alice_data["enc_zeta_eta_theta_lambda_squared"]
        + alice_data["enc_neg_two_zeta_eta_theta_lambda"] * mu_nu
        + alice_data["enc_zeta_eta"] * eta_nu_squared
    )

    return enc_a

# Step 4: Bob decrypts enc_a with Alice private key and computes the distance
def Bob_compute_distance(enc_a,private_key, geofence_radius):
    a = private_key.decrypt(enc_a)
    R = 6371.0 # Earth's radius in kilometers
    distance = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)) # Compute haversine distance

    # Determine if Alice's point is inside or outside Bob geofence
    if distance <= geofence_radius:
        print(f"ALice's location is INSIDE the geofence (distance: {distance:.2f} km).")
    else:
        print(f"Alice's location is OUTSIDE the geofence (distance: {distance:.2f} km).")
        
    return distance

def main():
    public_key, private_key = paillier.generate_paillier_keypair()
    lat_A, lon_A = 50.379320, -4.131244  # Alice's coordinates
    lat_B, lon_B = 50.381813, -4.127100  # Bob's coordinates
    geofence_radius = 0.39  # Radius in kilometers

    # Step 1: Convert degrees to radians and compute trigonometric values
    alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(lat_A, lon_A, lat_B, lon_B)

    # Step 2: Alice computes encrypted values and sends them to the server
    alice_data = alice_encrypt_values(public_key, alpha, gamma, zeta, eta, theta, lambda_, mu)

    # Step 3: The server computes alice encrypted values using homomorphic operations
    enc_a = Server_compute_homomorphic_ecnryption(alice_data, beta, delta, mu, nu, eta)

    # Step 4: Bob decrypts enc_a and computes the distance
    distance = Bob_compute_distance(enc_a, private_key, geofence_radius)

    # Validate using standard haversine library to prove validaty
    haversine_distance = haversine((lat_A, lon_A), (lat_B, lon_B))
    print(f"Distance between Alice and Bob (using haversine library): {haversine_distance:.2f} km")

if __name__ == "__main__":
    main()