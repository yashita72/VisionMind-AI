import os
import cv2
import sys
from vision.detection import YuNetDetector
from vision.recognition import SFaceRecognizer, FaceSearcher
from vision.events import EventLogger
from shared.logging.logger import setup_logger

logger = setup_logger()


class RealTimeRecognitionApp:
    """
    Main application orchestrating face detection, recognition, searching,
    event logging, and webcam visualization.
    """

    def __init__(
        self,
        database_dir: str = "database",
        threshold: float = 0.363,
        webcam_id: int = 0
    ) -> None:
        """
        Initializes the RealTimeRecognitionApp.

        Args:
            database_dir: Directory containing registered faces.
            threshold: Cosine similarity threshold for verification.
            webcam_id: ID of the webcam source.
        """
        self.threshold = threshold
        self.webcam_id = webcam_id
        
        logger.info("Initializing Real-Time Face Recognition App...")
        self.detector = YuNetDetector()
        self.recognizer = SFaceRecognizer()
        self.searcher = FaceSearcher(database_dir=database_dir, recognizer=self.recognizer)
        self.event_logger = EventLogger()

    def run(self) -> None:
        """
        Runs the main webcam face recognition loop.
        """
        logger.info(f"Opening webcam source {self.webcam_id}...")
        cap = cv2.VideoCapture(self.webcam_id)

        if not cap.isOpened():
            logger.error(f"Cannot open webcam source {self.webcam_id}.")
            print(f"Error: Webcam source {self.webcam_id} could not be opened.")
            return

        print("\n=== Real-Time Face Recognition App ===")
        print("Press 'q' in the window to quit.\n")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.warning("Failed to grab frame from webcam.")
                    break

                # Work on a copy for display
                display_frame = frame.copy()

                # 1. Detect faces
                faces = self.detector.detect_faces(frame)

                if faces is not None:
                    for face in faces:
                        # 2. Extract bounding box coordinates
                        x, y, w, h = face[:4].astype(int)

                        # Draw bounding box
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # 3. Align face and generate SFace embedding
                        try:
                            aligned_face = self.recognizer.align_face(frame, face)
                            query_emb = self.recognizer.compute_embedding(aligned_face)

                            # 4. Search database
                            matches = self.searcher.search(query_emb, threshold=self.threshold, top_k=1)

                            if matches and matches[0]["is_match"]:
                                match = matches[0]
                                name = match["name"]
                                score = match["similarity_score"]
                                confidence = match["confidence"]
                                label = f"{name} ({confidence:.2%})"

                                # Log the event
                                self.event_logger.log_detection(name, confidence, frame)
                            else:
                                label = "Unknown"

                        except Exception as e:
                            logger.error(f"Recognition pipeline error: {str(e)}")
                            label = "Error"

                        # Draw the label text
                        cv2.putText(
                            display_frame,
                            label,
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0) if label not in ["Unknown", "Error"] else (0, 0, 255),
                            2,
                            cv2.LINE_AA,
                        )

                # Show visual feedback
                cv2.imshow("VisionMind Real-Time Face Recognition", display_frame)

                # Break loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Quit key 'q' pressed. Exiting...")
                    break

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt. Exiting...")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            logger.info("Resources released successfully.")


def main():
    # If database is empty, log a warning
    if not os.path.exists("database") or not os.listdir("database"):
        print("Warning: The 'database' directory is empty. Run registration tests first to add faces.")
    
    app = RealTimeRecognitionApp()
    app.run()


if __name__ == "__main__":
    main()