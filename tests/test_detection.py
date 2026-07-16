import os
import cv2
from vision.detection import YuNetDetector, FaceCropper
from shared.logging.logger import setup_logger

logger = setup_logger()


def main():
    logger.info("Starting Face Detection test pipeline...")

    # Robust path resolution for the test image
    image_paths = ["assets/test.jpeg", "assests/test.jpeg", "tests/test.jpeg"]
    image_path = None
    for path in image_paths:
        if os.path.exists(path):
            image_path = path
            break

    if image_path is None:
        logger.error("Test image not found in assets or assests directory.")
        raise FileNotFoundError("Test image missing. Please ensure 'assests/test.jpeg' exists.")

    logger.info(f"Loading test image from: {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"Failed to read image at {image_path}")
        raise ValueError(f"Could not load image at {image_path}")

    # Initialize the YuNet detector
    detector = YuNetDetector()

    # Detect faces
    faces = detector.detect_faces(image)
    num_faces = 0 if faces is None else len(faces)
    logger.info(f"Number of faces detected: {num_faces}")

    # Crop and save faces
    save_dir = "reports/cropped_faces"
    cropped_faces = FaceCropper.crop_faces(image, faces, save_dir=save_dir)
    logger.info(f"Cropped and saved {len(cropped_faces)} face(s) to '{save_dir}'.")

    # Draw boxes and landmarks
    annotated_image = detector.draw_faces(image, faces)
    
    # Save the annotated output
    os.makedirs("reports", exist_ok=True)
    output_image_path = "reports/detection_output.jpg"
    cv2.imwrite(output_image_path, annotated_image)
    logger.info(f"Saved annotated detection output to: {output_image_path}")

    # Display window briefly to prevent blocking in non-interactive environments
    # but still allow visual verification.
    try:
        cv2.imshow("Detection", annotated_image)
        logger.info("Displaying detection window for 2 seconds. Press any key to close early.")
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
    except Exception as e:
        logger.warning(f"Could not display window: {e}. (Headless environment or lack of display)")

    logger.info("Face Detection test pipeline completed successfully.")


if __name__ == "__main__":
    main()