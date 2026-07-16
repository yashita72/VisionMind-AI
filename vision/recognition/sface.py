import os
import cv2
import numpy as np
from typing import Tuple, Optional
from shared.logging.logger import setup_logger

logger = setup_logger()


class SFaceRecognizer:
    """
    SFace Face Recognition model wrapper using OpenCV's FaceRecognizerSF API.
    Provides face alignment, embedding extraction, and verification.
    """

    def __init__(
        self,
        model_path: str = "models/face_recognition_sface_2021dec.onnx",
        cosine_threshold: float = 0.363,
        l2_threshold: float = 1.128,
    ) -> None:
        """
        Initializes the SFace Recognizer.

        Args:
            model_path: Path to the SFace ONNX model file.
            cosine_threshold: Cosine similarity threshold for verification (default: 0.363).
            l2_threshold: L2 distance threshold for verification (default: 1.128).
        """
        logger.info(f"Initializing SFace recognizer with model: {model_path}")
        
        if not os.path.exists(model_path):
            logger.error(f"SFace model file not found at: {model_path}")
            raise FileNotFoundError(f"SFace model file not found: {model_path}")

        self.cosine_threshold = cosine_threshold
        self.l2_threshold = l2_threshold

        try:
            self.recognizer = cv2.FaceRecognizerSF.create(model=model_path, config="")
            logger.info("SFace recognizer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to create FaceRecognizerSF: {str(e)}")
            raise RuntimeError(f"Failed to initialize SFace recognizer: {e}")

    def align_face(self, image: np.ndarray, face: np.ndarray) -> np.ndarray:
        """
        Aligns and crops the face from the source image.

        Args:
            image: BGR source image.
            face: A single face detection result from YuNet (15-element array).

        Returns:
            An aligned and cropped BGR face image.
        """
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Input image must be a valid NumPy ndarray.")
        if face is None or not isinstance(face, np.ndarray) or face.size < 15:
            raise ValueError("Face detection array must contain 15 elements (bounding box + landmarks + score).")

        try:
            # Ensure the face detection structure matches expected format
            # FaceRecognizerSF expects a 2D array or a properly formatted face vector.
            face_formatted = face.astype(np.float32)
            if len(face_formatted.shape) == 1:
                face_formatted = np.expand_dims(face_formatted, axis=0)

            # alignCrop aligns and crops the face
            aligned_face = self.recognizer.alignCrop(image, face_formatted)
            return aligned_face
        except Exception as e:
            logger.error(f"Failed to align face: {str(e)}")
            raise RuntimeError(f"Face alignment failed: {e}")

    def compute_embedding(self, aligned_face: np.ndarray) -> np.ndarray:
        """
        Computes 128-dimensional embedding from the aligned face.

        Args:
            aligned_face: Aligned BGR face image.

        Returns:
            A 128-dimensional feature embedding as a NumPy array of shape (1, 128).
        """
        if aligned_face is None or not isinstance(aligned_face, np.ndarray):
            raise ValueError("Aligned face image must be a valid NumPy ndarray.")

        try:
            embedding = self.recognizer.feature(aligned_face)
            return embedding
        except Exception as e:
            logger.error(f"Failed to compute embedding: {str(e)}")
            raise RuntimeError(f"Embedding computation failed: {e}")

    def compare_embeddings(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        dis_type: int = cv2.FaceRecognizerSF_FR_COSINE
    ) -> float:
        """
        Compares two face embeddings.

        Args:
            embedding1: First 128-dimensional embedding.
            embedding2: Second 128-dimensional embedding.
            dis_type: Similarity measure (cv2.FaceRecognizerSF_FR_COSINE or cv2.FaceRecognizerSF_FR_NORM_L2).

        Returns:
            A float representing the comparison score (similarity or distance).
        """
        if embedding1 is None or embedding2 is None:
            raise ValueError("Embeddings cannot be None.")

        try:
            score = self.recognizer.match(embedding1, embedding2, dis_type)
            return float(score)
        except Exception as e:
            logger.error(f"Failed to compare embeddings: {str(e)}")
            raise RuntimeError(f"Embedding comparison failed: {e}")

    def verify(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        dis_type: int = cv2.FaceRecognizerSF_FR_COSINE
    ) -> Tuple[bool, float]:
        """
        Verifies if two embeddings belong to the same person based on a threshold.

        Args:
            embedding1: First 128-dimensional embedding.
            embedding2: Second 128-dimensional embedding.
            dis_type: Distance/Similarity measure.

        Returns:
            A tuple (is_match, score).
        """
        score = self.compare_embeddings(embedding1, embedding2, dis_type)
        
        if dis_type == cv2.FaceRecognizerSF_FR_COSINE:
            # For Cosine Similarity, higher score is more similar.
            is_match = score >= self.cosine_threshold
        elif dis_type == cv2.FaceRecognizerSF_FR_NORM_L2:
            # For L2 Norm distance, lower score is more similar.
            is_match = score <= self.l2_threshold
        else:
            raise ValueError("Unsupported distance type.")

        logger.info(f"Verification completed. Match: {is_match}, Score: {score:.4f} (Type: {dis_type})")
        return is_match, score
