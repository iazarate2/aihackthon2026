"""Video frame extraction using OpenCV."""

import os
import cv2


def _sample_indices(total: int, count: int) -> list[int]:
    """Return evenly spaced frame indices across the playable clip."""
    count = min(count, total)
    if count <= 1:
        return [total // 2]

    step = (total - 1) / (count - 1)
    return [min(total - 1, int(round(i * step))) for i in range(count)]


def _frame_signature(frame) -> object:
    """Create a tiny grayscale signature for duplicate detection."""
    small = cv2.resize(frame, (24, 24))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return gray


def _signature_delta(sig_a, sig_b) -> float:
    return float(cv2.absdiff(sig_a, sig_b).mean())


def extract_frames(
    video_path: str,
    output_dir: str,
    num_frames: int = 12,
    candidate_frames: int = 36,
    min_visual_delta: float = 6.0,
) -> list[str]:
    """
    Extract diverse key frames from a video file.

    We previously tried selecting the largest motion spike as "contact", but
    broadcast clips often have camera cuts, crowd shots, and overlays that
    produce larger motion than the actual collision. This sampler keeps a
    broader, non-duplicate storyboard so the vision model can inspect the play
    progression instead of a repeated non-play moment.

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

    candidate_indices = _sample_indices(total, candidate_frames)

    os.makedirs(output_dir, exist_ok=True)
    saved: list[str] = []
    saved_signatures = []

    for fnum in candidate_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fnum)
        ok, frame = cap.read()
        if not ok:
            continue

        sig = _frame_signature(frame)
        if saved_signatures:
            nearest_delta = min(_signature_delta(sig, existing) for existing in saved_signatures)
            if nearest_delta < min_visual_delta:
                continue

        path = os.path.join(output_dir, f"frame_{len(saved):03d}_{fnum:06d}.jpg")
        cv2.imwrite(path, frame)
        saved.append(path)
        saved_signatures.append(sig)

        if len(saved) >= num_frames:
            break

    # If the clip has very little visual change, fill the remaining slots so the
    # AI still receives enough temporal context.
    if len(saved) < min(num_frames, total):
        saved_indices = {
            int(os.path.basename(path).split("_")[-1].split(".")[0])
            for path in saved
        }
        for fnum in candidate_indices:
            if fnum in saved_indices:
                continue
            cap.set(cv2.CAP_PROP_POS_FRAMES, fnum)
            ok, frame = cap.read()
            if not ok:
                continue
            path = os.path.join(output_dir, f"frame_{len(saved):03d}_{fnum:06d}.jpg")
            cv2.imwrite(path, frame)
            saved.append(path)
            if len(saved) >= min(num_frames, total):
                break

    cap.release()
    if not saved:
        raise ValueError("Failed to extract any frames.")
    return saved
