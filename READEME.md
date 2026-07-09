# VisionMind AI

VisionMind AI is an intelligent vision system that combines computer vision, face recognition, event logging, and AI reasoning into a single platform. Instead of simply detecting faces or recording attendance, the system continuously observes camera feeds, stores meaningful events, and allows users to retrieve information through natural language queries.

The project is designed as a modular platform where different vision capabilities can be integrated over time without changing the overall architecture.

---

## Motivation

Most surveillance systems only record video. Finding a specific event often requires manually reviewing hours of footage.

VisionMind AI aims to solve this by converting video streams into structured information that can be searched, analyzed, and queried naturally.

For example:

- Who entered after 6 PM?
- Did Rahul visit today?
- Show all unknown visitors from yesterday.
- Generate today's security summary.

---

## Features

Current

- Real-time face detection
- Face recognition using facial embeddings
- Face registration
- Known and unknown person identification

Planned

- Person tracking
- Event logging
- Memory engine
- Natural language search
- AI agent
- Automated report generation
- Multi-camera support

---

## System Architecture

```
Camera
    │
Frame Capture
    │
Face Detection
    │
Face Alignment
    │
Face Recognition
    │
Person Tracking
    │
Event Generation
    │
SQLite + FAISS
    │
Memory Engine
    │
LLM Agent
    │
Dashboard
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Computer Vision | OpenCV |
| Face Detection | YuNet |
| Face Recognition | SFace |
| Tracking | ByteTrack |
| Object Detection | YOLO |
| Vector Database | FAISS |
| Database | SQLite |
| Backend | FastAPI |
| Frontend | Streamlit |
| AI Framework | LangGraph |
| LLM | Gemini |

---

## Project Structure

```
VisionMind-AI/

backend/
vision/
ai_agent/
database/
frontend/
reports/
models/
docs/
tests/

app.py
```

---

## Development Roadmap

### Phase 1

- Face Detection
- Face Recognition
- Face Registration

### Phase 2

- Person Tracking
- Event Logging
- SQLite Integration

### Phase 3

- AI Memory Engine
- Natural Language Queries
- Dashboard

### Phase 4

- Multi-camera Support
- Scene Understanding
- Plugin Architecture

---

## Future Work

- Liveness detection
- Emotion recognition
- OCR
- Fire and smoke detection
- PPE detection
- License plate recognition
- Voice interaction
- Cloud deployment

---

## License

MIT License