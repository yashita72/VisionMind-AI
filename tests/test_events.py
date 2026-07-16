import os
import shutil
import unittest
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from vision.events.event_logger import EventLogger


class TestEvents(unittest.TestCase):
    def setUp(self):
        self.db_path = "tests/test_events.db"
        self.screenshot_dir = "tests/test_screenshots"
        
        # Clean up database if it exists from a previous aborted run
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass
                
        self.logger = EventLogger(db_path=self.db_path, screenshot_dir=self.screenshot_dir)
        self.dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    def tearDown(self):
        # Force garbage collection to release SQLite connection handles on Windows
        import gc
        gc.collect()
        
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except Exception:
            pass

        try:
            if os.path.exists(self.screenshot_dir):
                shutil.rmtree(self.screenshot_dir)
        except Exception:
            pass

    def test_log_detection(self):
        name = "Jane_Doe"
        confidence = 0.92

        # 1. Log event
        success = self.logger.log_detection(name, confidence, self.dummy_frame)
        self.assertTrue(success)

        # 2. Check DB entry
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, confidence, screenshot_path FROM events WHERE name = ?", (name,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], name)
            self.assertAlmostEqual(row[1], confidence)
            self.assertTrue(os.path.exists(row[2]))

    def test_deduplication_30s(self):
        name = "John_Doe"
        
        # Log first time
        success1 = self.logger.log_detection(name, 0.85, self.dummy_frame)
        self.assertTrue(success1)

        # Log second time immediately (should be skipped)
        success2 = self.logger.log_detection(name, 0.88, self.dummy_frame)
        self.assertFalse(success2, "Immediate duplicate detection log should have been skipped.")

    def test_deduplication_expired(self):
        name = "Alice"
        
        # Log first time
        success1 = self.logger.log_detection(name, 0.90, self.dummy_frame)
        self.assertTrue(success1)

        # Manually alter the timestamp in the database to simulate passage of time (> 30s ago)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            past_time = (datetime.now() - timedelta(seconds=35)).isoformat()
            cursor.execute("UPDATE events SET timestamp = ? WHERE name = ?", (past_time, name))
            conn.commit()

        # Log second time (should succeed)
        success2 = self.logger.log_detection(name, 0.95, self.dummy_frame)
        self.assertTrue(success2, "Duplicate check should allow logging after 30 seconds.")


if __name__ == "__main__":
    unittest.main()
