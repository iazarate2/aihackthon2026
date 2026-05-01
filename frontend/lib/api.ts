import { UploadResponse, AnalysisResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Upload a video file to the backend.
 * Returns the video_id and extracted frame URLs.
 */
export async function uploadVideo(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || `Upload failed (${res.status})`);
  }

  return res.json();
}

/**
 * Request AI analysis for a previously uploaded video.
 */
export async function analyzeVideo(
  videoId: string
): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyze/${videoId}`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail || `Analysis failed (${res.status})`);
  }

  return res.json();
}

/** Build a full URL for a frame path returned by the API. */
export function frameUrl(path: string): string {
  return `${API_BASE}${path}`;
}
