import os
import cv2
import numpy as np
from vision.detection import YuNetDetector
from vision.recognition import SFaceRecognizer
from shared.logging.logger import setup_logger

logger = setup_logger()


def main():
    logger.info("Starting Face Recognition test pipeline...")

    # Load test image
    image_paths = ["assets/test.jpeg", "assests/test.jpeg", "tests/test.jpeg"]
    image_path = None
    for path in image_paths:
        if os.path.exists(path):
            image_path = path
            break

    if image_path is None:
        raise FileNotFoundError("Test image missing. Please ensure 'assests/test.jpeg' exists.")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image at {image_path}")

    # Step 1: Detect faces using YuNet
    detector = YuNetDetector()
    faces = detector.detect_faces(image)

    if faces is None or len(faces) == 0:
        logger.error("No faces detected in the test image, cannot proceed with recognition tests.")
        return

    logger.info(f"Detected {len(faces)} face(s) for recognition tests.")

    # Step 2: Initialize SFace Recognizer
    recognizer = SFaceRecognizer()

    # Step 3: Align faces and compute embeddings
    embeddings = []
    for idx, face in enumerate(faces):
        logger.info(f"Processing face {idx}...")
        aligned_face = recognizer.align_face(image, face)
        
        # Save aligned face to reports for inspection
        os.makedirs("reports/aligned_faces", exist_ok=True)
        aligned_path = f"reports/aligned_faces/aligned_face_{idx}.jpg"
        cv2.imwrite(aligned_path, aligned_face)
        logger.info(f"Saved aligned face {idx} to {aligned_path}")

        # Compute 128-d embedding
        embedding = recognizer.compute_embedding(aligned_face)
        embeddings.append(embedding)
        logger.info(f"Embedding shape for face {idx}: {embedding.shape}")
        assert embedding.shape == (1, 128), f"Expected embedding shape (1, 128), got {embedding.shape}"

    # Step 4: Compare embeddings
    # Test 1: Self-similarity (should match perfectly)
    logger.info("Running Self-Similarity Test (Cosine Similarity)...")
    is_match, score = recognizer.verify(embeddings[0], embeddings[0], cv2.FaceRecognizerSF_FR_COSINE)
    logger.info(f"Self-similarity match result: {is_match}, score: {score:.6f}")
    assert is_match, "Self-similarity verification failed!"
    assert np.isclose(score, 1.0, atol=1e-4), f"Expected cosine similarity close to 1.0, got {score}"

    logger.info("Running Self-Distance Test (L2 Distance)...")
    is_match_l2, score_l2 = recognizer.verify(embeddings[0], embeddings[0], cv2.FaceRecognizerSF_FR_NORM_L2)
    logger.info(f"Self-L2 distance match result: {is_match_l2}, distance score: {score_l2:.6f}")
    assert is_match_l2, "Self L2 distance verification failed!"
    assert np.isclose(score_l2, 0.0, atol=1e-4), f"Expected L2 distance close to 0.0, got {score_l2}"

    # Test 2: Compare different faces if multiple faces are detected
    if len(embeddings) > 1:
        logger.info("Running Cross-Face Verification...")
        is_match_cross, score_cross = recognizer.verify(embeddings[0], embeddings[1], cv2.FaceRecognizerSF_FR_COSINE)
        logger.info(f"Cross-face match result (Face 0 vs Face 1): {is_match_cross}, score: {score_cross:.6f}")
        
        is_match_cross_l2, score_cross_l2 = recognizer.verify(embeddings[0], embeddings[1], cv2.FaceRecognizerSF_FR_NORM_L2)
        logger.info(f"Cross-face L2 distance (Face 0 vs Face 1): {is_match_cross_l2}, distance score: {score_cross_l2:.6f}")
    else:
        logger.info("Skipping cross-face comparison as only 1 face was detected.")

    logger.info("Face Recognition test pipeline completed successfully.")


if __name__ == "__main__":
    main()
