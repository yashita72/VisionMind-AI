import os
import shutil
import unittest
import numpy as np
import cv2
from vision.detection import YuNetDetector
from vision.recognition import SFaceRecognizer, FaceSearcher
from vision.registration.register_face import FaceRegistrar


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.db_dir = "tests/test_search_database"
        self.registrar = FaceRegistrar(database_dir=self.db_dir)
        self.detector = YuNetDetector()
        self.recognizer = SFaceRecognizer()
        
        # Locate test image
        image_paths = ["assets/test.jpeg", "assests/test.jpeg", "tests/test.jpeg"]
        self.image_path = None
        for path in image_paths:
            if os.path.exists(path):
                self.image_path = path
                break

    def tearDown(self):
        if os.path.exists(self.db_dir):
            shutil.rmtree(self.db_dir)

    def test_search_pipeline(self):
        self.assertIsNotNone(self.image_path)

        # 1. Register a test user
        name = "Searchable_Person"
        register_success = self.registrar.register(name, self.image_path)
        self.assertTrue(register_success)

        # 2. Instantiate Searcher
        searcher = FaceSearcher(database_dir=self.db_dir, recognizer=self.recognizer)

        # 3. Create query embedding from same image
        image = cv2.imread(self.image_path)
        faces = self.detector.detect_faces(image)
        self.assertIsNotNone(faces)
        
        aligned_face = self.recognizer.align_face(image, faces[0])
        query_embedding = self.recognizer.compute_embedding(aligned_face)

        # 4. Search
        results = searcher.search(query_embedding, threshold=0.363, top_k=5)
        self.assertTrue(len(results) > 0)
        
        top_match = results[0]
        self.assertEqual(top_match["name"], name)
        self.assertTrue(top_match["is_match"])
        self.assertGreaterEqual(top_match["similarity_score"], 0.363)
        self.assertGreaterEqual(top_match["confidence"], 0.5)


if __name__ == "__main__":
    unittest.main()
