import os
import numpy as np
from typing import List, Dict, Tuple
from vision.recognition.sface import SFaceRecognizer
from shared.logging.logger import setup_logger

logger = setup_logger()


class FaceSearcher:
    """
    Search module to compare a query face embedding against the database
    of registered face embeddings, returning Top-K matches.
    """

    def __init__(self, database_dir: str = "database", recognizer: SFaceRecognizer = None) -> None:
        """
        Initializes the FaceSearcher.

        Args:
            database_dir: Path to the registered faces database.
            recognizer: An instance of SFaceRecognizer. If None, instantiates one.
        """
        if os.environ.get("VERCEL"):
            database_dir = "/tmp/database"
        self.database_dir = database_dir
        self.recognizer = recognizer if recognizer is not None else SFaceRecognizer()
        self.database: Dict[str, np.ndarray] = {}
        self.load_database()

    def load_database(self) -> None:
        """
        Loads or reloads all registered .npy face embeddings from the database directory.
        """
        logger.info(f"Loading embeddings from database directory: '{self.database_dir}'")
        self.database.clear()

        if not os.path.exists(self.database_dir):
            logger.warning(f"Database directory '{self.database_dir}' does not exist.")
            return

        # Traverse the directory
        for person_name in os.listdir(self.database_dir):
            person_dir = os.path.join(self.database_dir, person_name)
            if not os.path.isdir(person_dir):
                continue

            embedding_path = os.path.join(person_dir, "embedding.npy")
            if os.path.exists(embedding_path):
                try:
                    embedding = np.load(embedding_path)
                    self.database[person_name] = embedding
                    logger.debug(f"Loaded embedding for: {person_name}")
                except Exception as e:
                    logger.error(f"Failed to load embedding for '{person_name}': {str(e)}")

        logger.info(f"Loaded {len(self.database)} registered identity/identities.")

    def search(
        self,
        query_embedding: np.ndarray,
        threshold: float = 0.363,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Searches the database for the query embedding and returns top matches.

        Args:
            query_embedding: 128-dimensional embedding of the unknown face (shape: 1, 128 or 128).
            threshold: Cosine similarity threshold below which matches are considered invalid/Unknown.
            top_k: Number of top matches to return.

        Returns:
            A sorted list of matches. Each match is a dict:
            {
                "name": str,
                "similarity_score": float,
                "confidence": float,
                "is_match": bool
            }
        """
        if not self.database:
            logger.warning("Search database is empty. No faces to match against.")
            return []

        if query_embedding is None:
            raise ValueError("Query embedding cannot be None.")

        # Ensure embedding shape matches the expected FaceRecognizerSF input
        if len(query_embedding.shape) == 1:
            query_embedding = np.expand_dims(query_embedding, axis=0)

        results = []

        for name, reg_embedding in self.database.items():
            try:
                # Calculate cosine similarity using the recognizer
                score = self.recognizer.compare_embeddings(
                    query_embedding, reg_embedding, dis_type=0
                )  # dis_type=0 is Cosine Similarity (cv2.FaceRecognizerSF_FR_COSINE)

                # Confidence score: Cosine similarity is in range [-1.0, 1.0].
                # Scale it to [0.0, 1.0] range: (score + 1.0) / 2.0
                confidence = float((score + 1.0) / 2.0)
                is_match = score >= threshold

                results.append({
                    "name": name,
                    "similarity_score": float(score),
                    "confidence": confidence,
                    "is_match": is_match
                })
            except Exception as e:
                logger.error(f"Failed to compare with '{name}': {str(e)}")
                continue

        # Sort results by similarity score in descending order
        results.sort(key=lambda x: x["similarity_score"], reverse=True)

        # Return top K results
        return results[:top_k]
