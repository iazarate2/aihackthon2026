"""Video frame extraction using OpenCV."""

import os
import cv2


def extract_frames(
    video_path: str,
    output_dir: str,
    num_frames: int = 5,
) -> list[str]:
    """
    Extract evenly-spaced frames from a video file.

    Returns list of saved frame file paths.
    Raises ValueError on bad input.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        raise ValueError("Video has no frames.")

    num_frames = min(num_frames, total)

    if num_frames == 1:
        indices = [total // 2]
    else:
        step = total / (num_frames - 1)
        indices = [int(round(i * step)) for i in range(num_frames)]
        indices[-1] = min(indices[-1], total - 1)

    os.makedirs(output_dir, exist_ok=True)
    saved: list[str] = []

    for idx, fnum in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fnum)
        ok, frame = cap.read()
        if not ok:
            continue
        path = os.path.join(output_dir, f"frame_{idx:03d}.jpg")
        cv2.imwrite(path, frame)
        saved.append(path)

    cap.release()
    if not saved:
        raise ValueError("Failed to extract any frames.")
    return saved
