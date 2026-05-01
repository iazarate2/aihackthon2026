"""
Video Processing Service
Extracts evenly-spaced frames from uploaded soccer clips using OpenCV.
"""

import os
import cv2


def extract_frames(
    video_path: str,
    output_dir: str,
    num_frames: int = 16,
) -> list[str]:
    """
    Extract evenly-spaced frames from a video file.

    Args:
        video_path:  Path to the uploaded video file.
        output_dir:  Directory to save extracted frame images.
        num_frames:  How many frames to extract (default 8).

    Returns:
        List of saved frame file paths (relative to backend/).

    Raises:
        ValueError: If the video can't be opened or has no frames.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        raise ValueError("Video has no frames or is empty.")

    # Don't try to extract more frames than the video has
    num_frames = min(num_frames, total_frames)

    # Calculate evenly-spaced frame indices
    if num_frames == 1:
        frame_indices = [total_frames // 2]
    else:
        step = total_frames / (num_frames - 1)
        frame_indices = [int(round(i * step)) for i in range(num_frames)]
        # Clamp last index so we don't go out of bounds
        frame_indices[-1] = min(frame_indices[-1], total_frames - 1)

    os.makedirs(output_dir, exist_ok=True)

    saved_paths: list[str] = []

    for idx, frame_num in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        success, frame = cap.read()

        if not success:
            continue  # skip unreadable frames

        filename = f"frame_{idx:03d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame)
        saved_paths.append(filepath)

    cap.release()

    if not saved_paths:
        raise ValueError("Failed to extract any frames from the video.")

    return saved_paths
