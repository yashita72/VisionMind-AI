import os
import cv2
import numpy as np
from typing import List, Optional
from shared.logging.logger import setup_logger

logger = setup_logger()


class FaceCropper:
    """
    Utility class for cropping detected faces and saving them if requested.
    """

    @staticmethod
    def crop_faces(
        image: np.ndarray,
        faces: Optional[np.ndarray],
        save_dir: Optional[str] = None
    ) -> List[np.ndarray]:
        """
        Crops each detected face from the image with boundary clamping to avoid errors.

        Args:
            image: The original input BGR image.
            faces: Detection results from YuNetDetector.
            save_dir: Path to save the cropped faces. If provided, saves each cropped face.

        Returns:
            A list of cropped face images as NumPy ndarrays.
        """
        if image is None or not isinstance(image, np.ndarray):
            logger.error("Input image is invalid or missing.")
            raise ValueError("Input image must be a valid NumPy ndarray.")

        cropped_images: List[np.ndarray] = []

        if faces is None or len(faces) == 0:
            logger.warning("No faces provided to crop.")
            return cropped_images

        img_h, img_w = image.shape[:2]

        for idx, face in enumerate(faces):
            try:
                # Bounding box coordinates: x, y, w, h
                x, y, w, h = face[:4].astype(int)

                # Clamp coordinates to ensure they fall within image boundaries
                x1 = max(0, min(x, img_w - 1))
                y1 = max(0, min(y, img_h - 1))
                x2 = max(0, min(x + w, img_w))
                y2 = max(0, min(y + h, img_h))

                if (x2 - x1) <= 0 or (y2 - y1) <= 0:
                    logger.warning(f"Face bounding box {idx} has invalid clamped dimensions: {x2-x1}x{y2-y1}. Skipping.")
                    continue

                face_img = image[y1:y2, x1:x2]
                cropped_images.append(face_img)

                # Save face image if save_dir is specified
                if save_dir:
                    os.makedirs(save_dir, exist_ok=True)
                    output_path = os.path.join(save_dir, f"face_{idx}.jpg")
                    cv2.imwrite(output_path, face_img)
                    logger.info(f"Saved cropped face {idx} to: {output_path}")

            except Exception as e:
                logger.error(f"Error cropping face at index {idx}: {str(e)}")
                continue

        logger.info(f"Successfully cropped {len(cropped_images)} face(s).")
        return cropped_images
