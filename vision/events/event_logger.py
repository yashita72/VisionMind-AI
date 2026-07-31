import os
import sqlite3
import cv2
import numpy as np
from datetime import datetime
from typing import Optional
from shared.logging.logger import setup_logger

logger = setup_logger()


class EventLogger:
    """
    Logs face detection events to an SQLite database and saves screenshots,
    preventing duplicate entries for the same person within a 30-second window.
    """

    def __init__(self, db_path: str = "shared/database/events.db", screenshot_dir: str = "reports/screenshots") -> None:
        """
        Initializes the EventLogger.

        Args:
            db_path: Path to the SQLite database.
            screenshot_dir: Directory where event screenshots are saved.
        """
        if os.environ.get("VERCEL"):
            db_path = "/tmp/events.db"
            screenshot_dir = "/tmp/screenshots"
            logger.info("Vercel environment detected. Overriding database and screenshots path to /tmp.")

        self.db_path = db_path
        self.screenshot_dir = screenshot_dir

        # Ensure directories exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self._init_db()
        logger.info(f"EventLogger initialized. DB: '{self.db_path}', Screenshots: '{self.screenshot_dir}'")

    def _init_db(self) -> None:
        """
        Initializes the SQLite database schema if not already created.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        screenshot_path TEXT NOT NULL
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise RuntimeError(f"Database initialization failed: {e}")

    def log_detection(self, name: str, confidence: float, frame: np.ndarray) -> bool:
        """
        Logs a detection event for a known person if they haven't been logged in the last 30 seconds.

        Args:
            name: The name of the detected person.
            confidence: The matching confidence score (0.0 to 1.0).
            frame: The current video frame (NumPy BGR image) for saving a screenshot.

        Returns:
            True if the event was logged, False if it was skipped (duplicate or error).
        """
        if not name or frame is None or not isinstance(frame, np.ndarray):
            logger.warning("Invalid inputs provided to log_detection.")
            return False

        now = datetime.now()
        current_time_str = now.isoformat()

        # Check for duplicates within last 30 seconds
        if self._is_duplicate(name, now):
            logger.debug(f"Skipping log for '{name}' - detected within the last 30 seconds.")
            return False

        try:
            # Save screenshot
            timestamp_safe = now.strftime("%Y%m%d_%H%M%S_%f")
            screenshot_filename = f"{name}_{timestamp_safe}.jpg"
            screenshot_path = os.path.join(self.screenshot_dir, screenshot_filename)
            
            # Save the frame
            cv2.imwrite(screenshot_path, frame)

            # Insert into DB
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO events (name, timestamp, confidence, screenshot_path) VALUES (?, ?, ?, ?)",
                    (name, current_time_str, float(confidence), screenshot_path)
                )
                conn.commit()

            logger.info(f"Event Logged: {name} (Confidence: {confidence:.2f})")
            return True

        except Exception as e:
            logger.error(f"Failed to log event for '{name}': {str(e)}")
            return False

    def _is_duplicate(self, name: str, current_time: datetime) -> bool:
        """
        Checks if the person has already been logged within the last 30 seconds.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT timestamp FROM events WHERE name = ? ORDER BY id DESC LIMIT 1",
                    (name,)
                )
                row = cursor.fetchone()
                
                if row is None:
                    return False

                last_timestamp_str = row[0]
                last_time = datetime.fromisoformat(last_timestamp_str)
                
                # Check elapsed time
                elapsed_seconds = (current_time - last_time).total_seconds()
                return elapsed_seconds < 30.0

        except Exception as e:
            logger.error(f"Error checking duplicate status for '{name}': {str(e)}")
            # On error, we default to False to ensure we don't drop logs
            return False
