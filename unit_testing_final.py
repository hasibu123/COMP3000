import unittest
import math
from phe import paillier
from haversine import haversine

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

def alice_encrypt_values(public_key, alpha, gamma, zeta, eta, theta, lambda_, mu):
    alpha_squared = alpha**2
    neg_two_alpha_gamma = -2 * alpha * gamma
    gamma_squared = gamma**2
    zeta_eta_theta_lambda_squared = zeta * eta * (theta**2) * (lambda_**2)
    neg_two_zeta_eta_theta_lambda = -2 * zeta * eta * theta * lambda_
    zeta_mu = zeta * mu**2

    enc_alpha_squared = public_key.encrypt(alpha_squared)
    enc_neg_two_alpha_gamma = public_key.encrypt(neg_two_alpha_gamma)
    enc_gamma_squared = public_key.encrypt(gamma_squared)
    enc_zeta_eta_theta_lambda_squared = public_key.encrypt(zeta_eta_theta_lambda_squared)
    enc_neg_two_zeta_eta_theta_lambda = public_key.encrypt(neg_two_zeta_eta_theta_lambda)
    enc_zeta_mu = public_key.encrypt(zeta_mu)

    return {
        "enc_alpha_squared": enc_alpha_squared,
        "enc_neg_two_alpha_gamma": enc_neg_two_alpha_gamma,
        "enc_gamma_squared": enc_gamma_squared,
        "enc_zeta_eta_theta_lambda_squared": enc_zeta_eta_theta_lambda_squared,
        "enc_neg_two_zeta_eta_theta_lambda": enc_neg_two_zeta_eta_theta_lambda,
        "enc_zeta_eta": enc_zeta_mu,
    }

def Server_compute_homomorphic_encryption(alice_data, beta, delta, mu, nu, eta):
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

def Bob_compute_distance(enc_a, private_key, geofence_radius):
    a = private_key.decrypt(enc_a)
    R = 6371.0  # Earth's radius in kilometers
    distance = 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return distance <= geofence_radius, distance

class TestPaillierGeofence(unittest.TestCase):
    def setUp(self):
        # Generate a public/private key pair for testing
        self.public_key, self.private_key = paillier.generate_paillier_keypair()
        # Sample coordinates for testing
        self.lat_A, self.lon_A = 50.379320, -4.131244  # Alice's coordinates
        self.lat_B, self.lon_B = 50.381813, -4.127100  # Bob's coordinates
        self.geofence_radius = 0.39  # Radius in kilometers

    def test_trigonometric_values(self):
        """Test if trigonometric values are computed correctly"""
        try:
            alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(
                self.lat_A, self.lon_A, self.lat_B, self.lon_B
            )
            
            # Check if all values are within valid ranges
            self.assertTrue(-1 <= alpha <= 1)
            self.assertTrue(-1 <= beta <= 1)
            self.assertTrue(-1 <= gamma <= 1)
            self.assertTrue(-1 <= delta <= 1)
            self.assertTrue(-1 <= zeta <= 1)
            self.assertTrue(-1 <= eta <= 1)
            self.assertTrue(-1 <= theta <= 1)
            self.assertTrue(-1 <= lambda_ <= 1)
            self.assertTrue(-1 <= mu <= 1)
            self.assertTrue(-1 <= nu <= 1)
            print("test_trigonometric_values: PASSED")
        except AssertionError:
            print("test_trigonometric_values: FAILED")
            raise

    def test_alice_encryption(self):
        """Test if Alice's encryption produces valid encrypted values"""
        try:
            alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(
                self.lat_A, self.lon_A, self.lat_B, self.lon_B
            )
            
            alice_data = alice_encrypt_values(
                self.public_key, alpha, gamma, zeta, eta, theta, lambda_, mu
            )
            
            # Check if all values are encrypted
            self.assertIsInstance(alice_data["enc_alpha_squared"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_neg_two_alpha_gamma"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_gamma_squared"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_zeta_eta_theta_lambda_squared"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_neg_two_zeta_eta_theta_lambda"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_zeta_eta"], paillier.EncryptedNumber)
            print("test_alice_encryption: PASSED")
        except AssertionError:
            print("test_alice_encryption: FAILED")
            raise

    def test_server_computation(self):
        """Test if server's homomorphic computation works correctly"""
        try:
            alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(
                self.lat_A, self.lon_A, self.lat_B, self.lon_B
            )
            
            alice_data = alice_encrypt_values(
                self.public_key, alpha, gamma, zeta, eta, theta, lambda_, mu
            )
            
            enc_a = Server_compute_homomorphic_encryption(
                alice_data, beta, delta, mu, nu, eta
            )
            
            self.assertIsInstance(enc_a, paillier.EncryptedNumber)
            print("test_server_computation: PASSED")
        except AssertionError:
            print("test_server_computation: FAILED")
            raise

    def test_bob_decryption(self):
        """Test if Bob's decryption and distance computation work correctly"""
        try:
            alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(
                self.lat_A, self.lon_A, self.lat_B, self.lon_B
            )
            
            alice_data = alice_encrypt_values(
                self.public_key, alpha, gamma, zeta, eta, theta, lambda_, mu
            )
            
            enc_a = Server_compute_homomorphic_encryption(
                alice_data, beta, delta, mu, nu, eta
            )
            
            inside, distance = Bob_compute_distance(
                enc_a, self.private_key, self.geofence_radius
            )
            
            # Check if distance is reasonable (should be positive and less than Earth's circumference)
            self.assertTrue(0 <= distance <= 40075)  # Earth's circumference in km
            
            # Validate against standard haversine distance
            haversine_distance = haversine(
                (self.lat_A, self.lon_A), (self.lat_B, self.lon_B)
            )
            self.assertAlmostEqual(distance, haversine_distance, places=2)
            print("test_bob_decryption: PASSED")
        except AssertionError:
            print("test_bob_decryption: FAILED")
            raise

    def test_geofence_accuracy(self):
        """Test if geofence detection is accurate"""
        try:
            # Test point inside geofence
            inside, distance = Bob_compute_distance(
                self._compute_encrypted_distance(50.380000, -4.129000),
                self.private_key,
                self.geofence_radius
            )
            self.assertTrue(inside)
            
            # Test point outside geofence
            inside, distance = Bob_compute_distance(
                self._compute_encrypted_distance(50.390000, -4.140000),
                self.private_key,
                self.geofence_radius
            )
            self.assertFalse(inside)
            print("test_geofence_accuracy: PASSED")
        except AssertionError:
            print("test_geofence_accuracy: FAILED")
            raise

    def _compute_encrypted_distance(self, lat_A, lon_A):
        """Helper method to compute encrypted distance"""
        alpha, beta, gamma, delta, zeta, eta, theta, lambda_, mu, nu = trigonometric_values(
            lat_A, lon_A, self.lat_B, self.lon_B
        )
        
        alice_data = alice_encrypt_values(
            self.public_key, alpha, gamma, zeta, eta, theta, lambda_, mu
        )
        
        return Server_compute_homomorphic_encryption(
            alice_data, beta, delta, mu, nu, eta
        )

if __name__ == '__main__':
    unittest.main() 