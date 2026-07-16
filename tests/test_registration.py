import os
import shutil
import unittest
from vision.registration.register_face import FaceRegistrar


class TestRegistration(unittest.TestCase):
    def setUp(self):
        self.db_dir = "tests/test_database"
        self.registrar = FaceRegistrar(database_dir=self.db_dir)

        # Locate test image
        image_paths = ["assets/test.jpeg", "assests/test.jpeg", "tests/test.jpeg"]
        self.image_path = None
        for path in image_paths:
            if os.path.exists(path):
                self.image_path = path
                break

    def tearDown(self):
        # Clean up temporary test database directory
        if os.path.exists(self.db_dir):
            shutil.rmtree(self.db_dir)

    def test_registration_success(self):
        self.assertIsNotNone(self.image_path, "Test image not found in assets/assests")
        
        name = "Test_User"
        success = self.registrar.register(name, self.image_path)
        self.assertTrue(success, "Registration failed for a valid image with face.")

        # Verify directories and files
        person_dir = os.path.join(self.db_dir, name)
        self.assertTrue(os.path.exists(person_dir))
        self.assertTrue(os.path.exists(os.path.join(person_dir, "embedding.npy")))
        self.assertTrue(os.path.exists(os.path.join(person_dir, "original.jpg")))

    def test_duplicate_registration_fails(self):
        self.assertIsNotNone(self.image_path, "Test image not found in assets/assests")

        name = "Test_User"
        # First registration
        success1 = self.registrar.register(name, self.image_path)
        self.assertTrue(success1)

        # Duplicate registration
        success2 = self.registrar.register(name, self.image_path)
        self.assertFalse(success2, "Duplicate registration should fail.")

    def test_missing_image_fails(self):
        success = self.registrar.register("Nobody", "non_existent_file.jpg")
        self.assertFalse(success, "Registration should fail if image is missing.")


if __name__ == "__main__":
    unittest.main()
