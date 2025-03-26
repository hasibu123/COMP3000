# privacy-preserving geofencing algorithm using Paillier encryption

This project presents the development and implementation of a privacy-preserving geofencing system utilizing Paillier homomorphic encryption to protect user location data. Geofencing technology, which triggers actions when devices enter or exit predefined geographical boundaries, has become increasingly prevalent across sectors including retail, healthcare, and security. However, conventional implementations raise significant privacy concerns due to their reliance on continuous access to users' precise location data.

The research addresses these privacy challenges by implementing the Paillier cryptosystem, a homomorphic encryption technique that enables computations on encrypted data. This approach allows the geofencing system to determine whether a user is inside or outside a geofence boundary without decrypting their actual location coordinates. The implementation specifically focuses on circular geofencing using the PP-HS protocol derived from the Haversine formula, which accurately calculates distances between coordinates on a spherical surface.

Through comprehensive testing and validation, this project demonstrates that privacy-preserving geofencing is both feasible and effective for real-world applications. Performance evaluations confirm acceptable operational efficiency despite the computational overhead introduced by encryption. The proposed system successfully balances robust privacy protection with functional geofencing capabilities, offering a novel solution that aligns with data protection regulations such as UK-GDPR. This approach significantly mitigates the privacy risks traditionally associated with location-based services while maintaining their utility, establishing a foundation for more secure and compliant geofencing technologies in privacy-sensitive environments



