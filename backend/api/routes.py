import os
import sqlite3
import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from typing import List, Dict, Any
from vision.detection import YuNetDetector, FaceCropper
from vision.recognition import SFaceRecognizer, FaceSearcher
from vision.registration import FaceRegistrar
from vision.events import EventLogger
from shared.logging.logger import setup_logger

logger = setup_logger()
router = APIRouter()

# Instantiate modules
detector = YuNetDetector()
recognizer = SFaceRecognizer()
registrar = FaceRegistrar()
searcher = FaceSearcher(recognizer=recognizer)
event_logger = EventLogger()


def decode_image(file_bytes: bytes) -> np.ndarray:
    """Decodes uploaded file bytes into an OpenCV BGR image."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    return image


@router.post("/detect")
async def detect_faces_api(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Detects faces in the uploaded image, returning bounding boxes and landmarks."""
    try:
        contents = await file.read()
        image = decode_image(contents)
        faces = detector.detect_faces(image)
        
        if faces is None:
            return {"faces_detected": 0, "faces": []}

        faces_list = []
        for face in faces:
            bbox = face[:4].tolist()  # [x, y, w, h]
            landmarks = face[4:14].reshape(5, 2).tolist()  # [[x, y], ...]
            score = float(face[14])
            faces_list.append({
                "box": bbox,
                "landmarks": landmarks,
                "score": score
            })

        return {"faces_detected": len(faces_list), "faces": faces_list}
    except Exception as e:
        logger.error(f"Error in /detect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recognize")
async def recognize_face_api(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Generates a 128-dimensional SFace embedding for an ALIGNED face image."""
    try:
        contents = await file.read()
        image = decode_image(contents)
        embedding = recognizer.compute_embedding(image)
        return {"embedding": embedding.flatten().tolist()}
    except Exception as e:
        logger.error(f"Error in /recognize: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
async def register_face_api(
    name: str = Form(...),
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Registers a person's face. Saves the embedding and original image."""
    try:
        contents = await file.read()
        
        # Temp save uploaded file to register it
        temp_dir = "reports/temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"temp_{name}.jpg")
        with open(temp_path, "wb") as f:
            f.write(contents)

        success = registrar.register(name, temp_path)

        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        if not success:
            raise HTTPException(status_code=400, detail="Registration failed (e.g. user already exists or no face detected).")

        # Reload database in Searcher
        searcher.load_database()

        return {"status": "success", "message": f"Successfully registered '{name}'."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in /register: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify")
async def verify_faces_api(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
) -> Dict[str, Any]:
    """Verifies whether two uploaded face images belong to the same person."""
    try:
        contents1 = await file1.read()
        contents2 = await file2.read()

        img1 = decode_image(contents1)
        img2 = decode_image(contents2)

        # Detect face in image 1
        faces1 = detector.detect_faces(img1)
        if faces1 is None:
            raise HTTPException(status_code=400, detail="No face detected in image 1.")

        # Detect face in image 2
        faces2 = detector.detect_faces(img2)
        if faces2 is None:
            raise HTTPException(status_code=400, detail="No face detected in image 2.")

        aligned1 = recognizer.align_face(img1, faces1[0])
        aligned2 = recognizer.align_face(img2, faces2[0])

        emb1 = recognizer.compute_embedding(aligned1)
        emb2 = recognizer.compute_embedding(aligned2)

        is_match, score = recognizer.verify(emb1, emb2)

        return {
            "verified": bool(is_match),
            "similarity_score": float(score),
            "confidence": float((score + 1.0) / 2.0)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in /verify: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_face_api(
    file: UploadFile = File(...),
    threshold: float = Query(0.363, description="Similarity threshold for a match.")
) -> Dict[str, Any]:
    """Searches the registered database for the face in the uploaded image, returning Top-5 matches."""
    try:
        contents = await file.read()
        image = decode_image(contents)

        faces = detector.detect_faces(image)
        if faces is None:
            raise HTTPException(status_code=400, detail="No face detected in the query image.")

        aligned = recognizer.align_face(image, faces[0])
        embedding = recognizer.compute_embedding(aligned)

        # Search the database
        results = searcher.search(embedding, threshold=threshold, top_k=5)
        
        # Log event if a known person is found
        if results and results[0]["is_match"]:
            match = results[0]
            event_logger.log_detection(match["name"], match["confidence"], image)

        return {"matches": results}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in /search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/attendance")
async def get_attendance_api() -> List[Dict[str, Any]]:
    """Retrieves list of face detection attendance events from the SQLite database."""
    try:
        events = []
        if not os.path.exists(event_logger.db_path):
            return events

        with sqlite3.connect(event_logger.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, timestamp, confidence, screenshot_path FROM events ORDER BY id DESC")
            rows = cursor.fetchall()
            for row in rows:
                events.append({
                    "id": row["id"],
                    "name": row["name"],
                    "timestamp": row["timestamp"],
                    "confidence": float(row["confidence"]),
                    "screenshot_path": row["screenshot_path"]
                })
        return events
    except Exception as e:
        logger.error(f"Error in /attendance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
