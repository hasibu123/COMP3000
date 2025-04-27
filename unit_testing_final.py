import unittest
from phe import paillier
from haversine import haversine
from paillier import (trigonometric_values, alice_encrypt_values, server_compute_homomorphic_encryption, Bob_compute_distance)

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
            
            # Check if all values are encrypted(type of encrypted number)
            self.assertIsInstance(alice_data["enc_alpha_squared"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_neg_two_alpha_gamma"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_gamma_squared"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_zeta_eta_theta_lambda_squared"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_neg_two_zeta_mu_theta_lambda"], paillier.EncryptedNumber)
            self.assertIsInstance(alice_data["enc_zeta_mu"], paillier.EncryptedNumber)
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
            
            enc_a = server_compute_homomorphic_encryption(
                alice_data, beta, delta, nu, eta
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
            
            enc_a = server_compute_homomorphic_encryption(
                alice_data, beta, delta, nu, eta
            )
            
            distance = Bob_compute_distance(
                enc_a, self.private_key, self.geofence_radius
            )
            
            # Check if distance is reasonable (should be positive and less than Earth's circumference)
            self.assertTrue(0 <= distance <= 40075)  # Earth's circumference in km
            
            # Validate against standard haversine distance
            haversine_distance = haversine(
                (self.lat_A, self.lon_A), (self.lat_B, self.lon_B)
            )
            self.assertAlmostEqual(distance, haversine_distance, places=2) #assertAlmostEqual is used to check if the distance is almost equal to the haversine distance    
            print("test_bob_decryption: PASSED")
        except AssertionError:
            print("test_bob_decryption: FAILED")
            raise

    def test_geofence_accuracy(self):
        """Test if geofence detection is accurate"""
        try:
            # Test point inside geofence
            distance = Bob_compute_distance(
                self._compute_encrypted_distance(50.380000, -4.129000),
                self.private_key,
                self.geofence_radius
            )
            self.assertTrue(distance <= self.geofence_radius)
            
            # Test point outside geofence
            distance = Bob_compute_distance(
                self._compute_encrypted_distance(50.390000, -4.140000),
                self.private_key,
                self.geofence_radius
            )
            self.assertFalse(distance <= self.geofence_radius)
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
        
        return server_compute_homomorphic_encryption(
            alice_data, beta, delta, nu, eta
        )

if __name__ == '__main__':
    unittest.main() 