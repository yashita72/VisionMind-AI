import os
import cv2
import numpy as np
from typing import Optional, Tuple
from shared.logging.logger import setup_logger

logger = setup_logger()


class YuNetDetector:
    """
    YuNet Face Detector using OpenCV's FaceDetectorYN API.
    Provides robust detection of one or multiple faces, draws bounding boxes,
    and returns face detection outputs including bounding boxes and landmarks.
    """

    def __init__(
        self,
        model_path: str = "models/face_detection_yunet_2023mar.onnx",
        input_size: Tuple[int, int] = (320, 320),
        score_threshold: float = 0.6,
        nms_threshold: float = 0.3,
        top_k: int = 5000,
    ) -> None:
        """
        Initializes the YuNet Detector.

        Args:
            model_path: Path to the YuNet ONNX model file.
            input_size: Default input size (width, height) for the model.
            score_threshold: Filter out faces with score < score_threshold.
            nms_threshold: Suppress overlap boxes.
            top_k: Keep top K detections before NMS.
        """
        logger.info(f"Initializing YuNet detector with model: {model_path}")
        
        if not os.path.exists(model_path):
            logger.error(f"YuNet model file not found at: {model_path}")
            raise FileNotFoundError(f"YuNet model not found: {model_path}")

        try:
            self.detector = cv2.FaceDetectorYN.create(
                model=model_path,
                config="",
                input_size=input_size,
                score_threshold=score_threshold,
                nms_threshold=nms_threshold,
                top_k=top_k,
            )
            logger.info("YuNet detector initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to create FaceDetectorYN: {str(e)}")
            raise RuntimeError(f"Failed to initialize YuNet detector: {e}")

    def detect_faces(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Detects faces in the input image.

        Args:
            image: OpenCV image (BGR representation).

        Returns:
            A numpy array of shape (N, 15) representing detection results, 
            where N is the number of detected faces.
            Each row contains:
            - [0:4]: bounding box (x, y, width, height)
            - [4:14]: 5 landmarks (x, y) for right eye, left eye, nose tip, 
                      right mouth corner, left mouth corner.
            - [14]: face score (confidence).
            Returns None if no faces are detected or if image is invalid.
        """
        if image is None or not isinstance(image, np.ndarray):
            logger.error("Input image is invalid or missing.")
            raise ValueError("Input image must be a valid NumPy ndarray.")

        try:
            h, w = image.shape[:2]
            # Set input size dynamically matching the image shape (width, height)
            self.detector.setInputSize((w, h))
            
            retval, faces = self.detector.detect(image)
            
            if not retval or faces is None:
                logger.info("No faces detected in the image.")
                return None

            logger.info(f"Detected {len(faces)} face(s).")
            return faces
        except Exception as e:
            logger.error(f"Error during face detection: {str(e)}")
            raise RuntimeError(f"Face detection failed: {e}")

    def draw_faces(self, image: np.ndarray, faces: Optional[np.ndarray]) -> np.ndarray:
        """
        Draws bounding boxes and landmarks for all detected faces.

        Args:
            image: OpenCV BGR image to draw on.
            faces: Detection outputs from detect_faces.

        Returns:
            The image with drawings.
        """
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Input image must be a valid NumPy ndarray.")

        if faces is None:
            return image

        output_image = image.copy()
        for idx, face in enumerate(faces):
            # Coordinates
            x, y, w, h = face[:4].astype(int)
            score = face[14]

            # Draw bounding box
            cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Draw score
            text = f"Face {idx}: {score:.2f}"
            cv2.putText(
                output_image,
                text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

            # Draw 5 landmarks
            # Right eye, left eye, nose, right mouth corner, left mouth corner
            landmarks = face[4:14].reshape(5, 2).astype(int)
            colors = [
                (255, 0, 0),    # Right eye - Blue
                (0, 0, 255),    # Left eye - Red
                (0, 255, 0),    # Nose tip - Green
                (255, 0, 255),  # Right mouth corner - Magenta
                (0, 255, 255),  # Left mouth corner - Yellow
            ]
            for pt, color in zip(landmarks, colors):
                cv2.circle(output_image, tuple(pt), 2, color, -1)

        return output_image