"""
RefCheck AI — Backend API
FastAPI server for soccer officiating analysis.
"""

import os
import uuid
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from services.video_processing import extract_frames
from services.ai_analysis import analyze_frames

# ---------------------------------------------------------------------------
# Rate Limiting — prevents API abuse when hosted publicly
# Limits are per IP address.
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FRAMES_DIR = os.path.join(BASE_DIR, "extracted_frames")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="RefCheck AI",
    description="AI-powered soccer officiating analysis",
    version="0.1.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow the frontend (Next.js dev server) to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve extracted frames as static files so the frontend can display them
# e.g. http://localhost:8000/frames/{video_id}/frame_000.jpg
app.mount("/frames", StaticFiles(directory=FRAMES_DIR), name="frames")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Quick check that the server is running."""
    return {"status": "running"}


ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


@app.post("/upload")
@limiter.limit("10/minute")  # max 10 uploads per minute per IP
async def upload_video(request: Request, file: UploadFile = File(...)):
    """
    Accept a video upload, save it, extract frames, and return metadata.
    """
    # --- Validate file type ---
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # --- Generate unique video ID and save the upload ---
    video_id = uuid.uuid4().hex[:12]
    video_filename = f"{video_id}{ext}"
    video_path = os.path.join(UPLOAD_DIR, video_filename)

    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")

    # --- Extract frames ---
    output_dir = os.path.join(FRAMES_DIR, video_id)

    try:
        saved_paths = extract_frames(video_path, output_dir, num_frames=16)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Build URLs the frontend can use to display frames
    frame_urls = [
        f"/frames/{video_id}/{os.path.basename(p)}" for p in saved_paths
    ]

    return {
        "video_id": video_id,
        "frames": frame_urls,
    }


@app.post("/analyze/{video_id}")
@limiter.limit("5/minute")  # max 5 analyses per minute per IP (protects API costs)
async def analyze_video(request: Request, video_id: str):
    """
    Run AI analysis on previously extracted frames for a given video.
    """
    # Check that frames exist for this video
    frames_dir = os.path.join(FRAMES_DIR, video_id)
    if not os.path.isdir(frames_dir):
        raise HTTPException(
            status_code=404,
            detail=f"No extracted frames found for video_id '{video_id}'.",
        )

    # Gather frame file paths (sorted so order is consistent)
    frame_files = sorted(
        os.path.join(frames_dir, f)
        for f in os.listdir(frames_dir)
        if f.endswith(".jpg")
    )

    if not frame_files:
        raise HTTPException(
            status_code=404,
            detail="Frames directory exists but contains no images.",
        )

    # Run analysis
    result = await analyze_frames(video_id, frame_files)

    # Include frame URLs so the frontend can display them alongside the verdict
    frame_urls = [
        f"/frames/{video_id}/{os.path.basename(p)}" for p in frame_files
    ]

    return {
        "video_id": video_id,
        "frames": frame_urls,
        **result,
    }
