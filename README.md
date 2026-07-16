# VisionMind-AI

A production-ready, modular computer vision system designed for Face Detection, Registration, Search, and Event/Attendance logging.

## Tech Stack
- **Backend**: Python 3.12, FastAPI, OpenCV (FaceDetectorYN & FaceRecognizerSF), SQLite
- **Frontend**: React 18, TailwindCSS, Vite, Lucide Icons
- **Deployment**: Docker, Docker Compose

## Repository Layout
- `vision/`: Central computer vision detection, embeddings, recognition, and search modules.
- `backend/`: FastAPI routers and app server configurations.
- `frontend/`: React components, hooks, styling, and dashboard assets.
- `shared/`: Config settings and SQLite database structures.
- `tests/`: End-to-end unittest suites for each system capability.

## Quick Start
To start the entire application including the FastAPI backend and React frontend with a single command:
```bash
docker compose up --build
```
Once initialized, visit:
- **Frontend Panel**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
