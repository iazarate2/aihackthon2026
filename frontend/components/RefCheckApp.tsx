"use client";

import { useState } from "react";
import { uploadVideo, analyzeVideo } from "@/lib/api";
import { AnalysisResponse } from "@/lib/types";
import VideoUpload from "./VideoUpload";
import FrameGallery from "./FrameGallery";
import VerdictCard from "./VerdictCard";

type AppState = "idle" | "uploading" | "analyzing" | "done" | "error";

export default function RefCheckApp() {
  const [state, setState] = useState<AppState>("idle");
  const [frames, setFrames] = useState<string[]>([]);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleFileSelected(file: File) {
    setError(null);
    setResult(null);
    setFrames([]);

    try {
      // Step 1: Upload and extract frames
      setState("uploading");
      const uploadRes = await uploadVideo(file);
      setFrames(uploadRes.frames);

      // Step 2: Run AI analysis
      setState("analyzing");
      const analysisRes = await analyzeVideo(uploadRes.video_id);
      setResult(analysisRes);
      setState("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setState("error");
    }
  }

  function handleReset() {
    setState("idle");
    setFrames([]);
    setResult(null);
    setError(null);
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <header className="w-full border-b border-card-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-extrabold tracking-tight">
              Ref<span className="text-accent-blue">Check</span> AI
            </h1>
            <p className="text-xs text-foreground/40 font-mono">
              AI-Powered Officiating Analysis
            </p>
          </div>
          {state !== "idle" && (
            <button
              onClick={handleReset}
              className="text-xs font-mono px-3 py-1.5 rounded-lg border border-card-border
                         hover:bg-card-border/50 transition-colors"
            >
              New Analysis
            </button>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center px-6 py-12 gap-10">
        {/* Landing / Upload */}
        {(state === "idle" || state === "uploading") && (
          <div className="flex flex-col items-center gap-6 max-w-xl text-center">
            <h2 className="text-4xl font-extrabold tracking-tight">
              Upload a soccer clip.
              <br />
              <span className="text-accent-blue">Get a referee-style verdict.</span>
            </h2>
            <p className="text-foreground/50 text-sm max-w-md">
              Our AI extracts key frames, analyzes the play against IFAB Law 12,
              and delivers a VAR-style decision with confidence scoring.
            </p>
            <VideoUpload
              onFileSelected={handleFileSelected}
              isUploading={state === "uploading"}
            />
          </div>
        )}

        {/* Analyzing state */}
        {state === "analyzing" && (
          <div className="flex flex-col items-center gap-8">
            {frames.length > 0 && <FrameGallery frames={frames} />}
            <div className="flex flex-col items-center gap-4 animate-pulse-glow rounded-2xl border border-accent-blue/30 bg-card px-12 py-8">
              <div className="w-10 h-10 border-3 border-accent-blue border-t-transparent rounded-full animate-spin" />
              <p className="text-sm font-mono text-accent-blue">
                Analyzing play...
              </p>
              <p className="text-xs text-foreground/40">
                Comparing against IFAB Law 12 rules
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {state === "done" && result && (
          <div className="flex flex-col items-center gap-10 w-full">
            <VerdictCard result={result} />
            <FrameGallery frames={frames} keyFrame={result.key_frame} />
          </div>
        )}

        {/* Error */}
        {state === "error" && (
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="px-6 py-4 rounded-xl border border-accent-red/30 bg-accent-red/5">
              <p className="text-accent-red font-semibold">Analysis Failed</p>
              <p className="text-sm text-foreground/60 mt-1">{error}</p>
            </div>
            <button
              onClick={handleReset}
              className="text-sm font-mono px-4 py-2 rounded-lg border border-card-border
                         hover:bg-card-border/50 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-card-border py-4 text-center">
        <p className="text-xs text-foreground/30 font-mono">
          RefCheck AI — Hackathon 2026 · Powered by Multimodal AI
        </p>
      </footer>
    </div>
  );
}
