import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router
from shared.logging.logger import setup_logger

logger = setup_logger()

app = FastAPI(
    title="VisionMind AI API",
    description="Production-ready FastAPI backend for face detection, registration, and recognition.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in a real production environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folders if not exist
os.makedirs("reports/screenshots", exist_ok=True)
os.makedirs("database", exist_ok=True)

# Mount static directories to serve original photos and screenshots to frontend
app.mount("/reports", StaticFiles(directory="reports"), name="reports")
app.mount("/database", StaticFiles(directory="database"), name="database")

# Include api routes
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "VisionMind AI FastAPI is running."}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
