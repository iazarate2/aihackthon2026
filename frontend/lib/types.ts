/** Response from POST /upload */
export interface UploadResponse {
  video_id: string;
  frames: string[];
}

/** Response from POST /analyze/{video_id} */
export interface AnalysisResponse {
  video_id: string;
  frames: string[];
  verdict: "Fair Call" | "Foul" | "Dangerous Play" | "Inconclusive";
  confidence: number;
  rule_reference: string;
  explanation: string;
  key_frame: number;
  key_frame_reason?: string;
  key_observations: string[];
}
