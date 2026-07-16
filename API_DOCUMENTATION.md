# API Documentation

All API endpoints are prefixed with `/api`. Auto-generated Swagger UI docs can be accessed at `http://localhost:8000/docs`.

## Endpoints

### 1. `POST /detect`
Detects faces in the uploaded image.
- **Request**: Multipart Form Data
  - `file`: Image file
- **Response**:
```json
{
  "faces_detected": 1,
  "faces": [
    {
      "box": [401, 308, 511, 623],
      "landmarks": [[434, 534], [672, 534], [489, 725], [447, 841], [651, 842]],
      "score": 0.689
    }
  ]
}
```

### 2. `POST /recognize`
Generates SFace embeddings for an aligned face.
- **Request**: Multipart Form Data
  - `file`: Aligned face image file
- **Response**:
```json
{
  "embedding": [0.012, -0.045, ...]
}
```

### 3. `POST /register`
Registers a face by creating embedding files and saving the portrait.
- **Request**: Multipart Form Data
  - `name`: Profile Name (e.g. `Jane_Doe`)
  - `file`: Portrait image file
- **Response**:
```json
{
  "status": "success",
  "message": "Successfully registered 'Jane_Doe'."
}
```

### 4. `POST /verify`
Verifies whether two uploaded images are of the same person.
- **Request**: Multipart Form Data
  - `file1`: Image file A
  - `file2`: Image file B
- **Response**:
```json
{
  "verified": true,
  "similarity_score": 0.852,
  "confidence": 0.926
}
```

### 5. `POST /search`
Searches the database for matching profiles.
- **Request**: Multipart Form Data
  - `file`: Image file to search
  - `threshold`: Query parameter (Float, e.g. `0.363`)
- **Response**:
```json
{
  "matches": [
    {
      "name": "Jane_Doe",
      "similarity_score": 0.852,
      "confidence": 0.926,
      "is_match": true
    }
  ]
}
```

### 6. `GET /attendance`
Retrieves detection and login events.
- **Response**:
```json
[
  {
    "id": 1,
    "name": "Jane_Doe",
    "timestamp": "2026-07-16T18:05:42.756000",
    "confidence": 0.92,
    "screenshot_path": "reports/screenshots/Jane_Doe_20260716_180542_756000.jpg"
  }
]
```
