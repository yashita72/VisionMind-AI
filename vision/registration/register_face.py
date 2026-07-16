import os
import cv2
import numpy as np
from typing import Optional
from vision.detection.yunet_detector import YuNetDetector
from vision.recognition.sface import SFaceRecognizer
from shared.logging.logger import setup_logger

logger = setup_logger()


class FaceRegistrar:
    """
    Handles face registration by detecting a face, aligning it, 
    generating SFace embeddings, and saving it to the database.
    """

    def __init__(self, database_dir: str = "database") -> None:
        """
        Initializes the FaceRegistrar.

        Args:
            database_dir: Directory where face records are stored.
        """
        self.database_dir = database_dir
        os.makedirs(self.database_dir, exist_ok=True)
        self.detector = YuNetDetector()
        self.recognizer = SFaceRecognizer()
        logger.info(f"FaceRegistrar initialized. Database directory: '{self.database_dir}'")

    def register(self, person_name: str, image_path: str) -> bool:
        """
        Registers a person's face into the database.

        Args:
            person_name: Name of the person to register.
            image_path: Path to the image containing the person's face.

        Returns:
            True if registration was successful, False otherwise.
        """
        # 1. Input Validation
        if not person_name or not isinstance(person_name, str):
            logger.error("Invalid person name provided.")
            return False

        # Clean name for directory usage
        person_name = person_name.strip().replace(" ", "_")
        person_dir = os.path.join(self.database_dir, person_name)

        # Prevent duplicate registration
        if os.path.exists(person_dir):
            logger.warning(f"Person '{person_name}' is already registered.")
            return False

        if not os.path.exists(image_path):
            logger.error(f"Image not found at path: '{image_path}'")
            return False

        try:
            # 2. Load Image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image at '{image_path}'")
                return False

            # 3. Detect Face
            faces = self.detector.detect_faces(image)
            if faces is None or len(faces) == 0:
                logger.error(f"No face detected in the image '{image_path}'. Cannot register.")
                return False

            if len(faces) > 1:
                logger.warning(f"Multiple faces ({len(faces)}) detected in '{image_path}'. Registering the first one.")

            # Get the first face
            face = faces[0]

            # 4. Align Face
            aligned_face = self.recognizer.align_face(image, face)

            # 5. Generate Embedding
            embedding = self.recognizer.compute_embedding(aligned_face)

            # 6. Save data
            os.makedirs(person_dir, exist_ok=True)
            
            # Save embedding
            embedding_path = os.path.join(person_dir, "embedding.npy")
            np.save(embedding_path, embedding)

            # Save original image
            original_img_path = os.path.join(person_dir, "original.jpg")
            cv2.imwrite(original_img_path, image)

            logger.info(f"Successfully registered '{person_name}'. Data saved to '{person_dir}'.")
            return True

        except Exception as e:
            logger.exception(f"An error occurred while registering '{person_name}': {str(e)}")
            # Cleanup directory if creation failed midway
            if os.path.exists(person_dir) and not os.listdir(person_dir):
                try:
                    os.rmdir(person_dir)
                except Exception:
                    pass
            return False
