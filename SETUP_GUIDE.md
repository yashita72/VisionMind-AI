# Setup and Deployment Guide

Follow these steps to run VisionMind-AI locally or inside a Docker environment.

## 1. Docker Deployment (Recommended)

Ensure Docker and Docker Compose are installed.

```bash
# Build and start services
docker compose up --build
```
- The frontend will be accessible at: `http://localhost:3000`
- The backend API docs will be at: `http://localhost:8000/docs`

## 2. Local Manual Setup

If you prefer to run the services outside Docker:

### Prerequisites
- Python 3.12+
- Node.js 18+

### Step A: Setup Backend
1. Create and activate a python virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI development server:
   ```bash
   python -m backend.main
   ```

### Step B: Setup Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your web browser.
