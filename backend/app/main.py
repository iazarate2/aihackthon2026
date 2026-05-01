"""
RefCheck AI — Basketball Coach Challenge Review Assistant
FastAPI backend server.
"""

import os
import uuid
import shutil
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.rules_engine import get_sample_cases, get_sample_case
from app.analyzer import analyze_sample_case, analyze_video_upload
from app.video_processor import extract_frames

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FRAMES_DIR = os.path.join(BASE_DIR, "extracted_frames")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RefCheck AI",
    description="Basketball Coach Challenge Review Assistant",
    version="1.0.0",
)

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

extra_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEFAULT_CORS_ORIGINS + extra_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve extracted frames as static files
app.mount("/frames", StaticFiles(directory=FRAMES_DIR), name="frames")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "RefCheck AI basketball backend running",
    }


@app.get("/sample-cases")
def list_sample_cases():
    """Return all available sample cases for the frontend selector."""
    cases = get_sample_cases()
    return {
        "cases": [
            {
                "id": c["id"],
                "title": c["title"],
                "description": c["description"],
                "original_call": c["original_call"],
            }
            for c in cases
        ]
    }


VALID_CALLS = {"Charge", "Blocking Foul", "No Call"}
ALLOWED_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


@app.post("/review")
async def review(
    original_call: str = Form(...),
    sample_case_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Run a charge-vs-block review.

    Supports two modes:
      A) sample_case_id provided → return pre-built analysis
      B) video file uploaded    → extract frames + mock analysis
    """
    # Validate original_call
    if original_call not in VALID_CALLS:
        raise HTTPException(
            status_code=400,
            detail=f"original_call must be one of: {', '.join(VALID_CALLS)}",
        )

    # --- Mode A: sample case ---
    if sample_case_id:
        case = get_sample_case(sample_case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Sample case not found.")
        return analyze_sample_case(case, original_call)

    # --- Mode B: video upload ---
    if file:
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXT:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXT)}",
            )

        video_id = uuid.uuid4().hex[:12]
        video_path = os.path.join(UPLOAD_DIR, f"{video_id}{ext}")

        try:
            with open(video_path, "wb") as buf:
                shutil.copyfileobj(file.file, buf)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")

        try:
            saved = extract_frames(
                video_path,
                os.path.join(FRAMES_DIR, video_id),
                num_frames=12,
                candidate_frames=36,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        frame_urls = [f"/frames/{video_id}/{os.path.basename(p)}" for p in saved]
        try:
            return analyze_video_upload(
                original_call, frame_urls,
                frame_paths=saved,
                filename=file.filename,
            )
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))

    # Neither provided
    raise HTTPException(
        status_code=400,
        detail="Provide either sample_case_id or upload a video file.",
    )
