"use client";

import { useState, useCallback, useEffect } from "react";
import { frameUrl } from "@/lib/api";

interface FrameGalleryProps {
  frames: string[];
  /** 1-based index of the decisive frame (highlighted if set) */
  keyFrame?: number;
}

export default function FrameGallery({ frames, keyFrame }: FrameGalleryProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  // Close on Escape key
  useEffect(() => {
    if (expandedIndex === null) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setExpandedIndex(null);
      if (e.key === "ArrowRight" && expandedIndex < frames.length - 1)
        setExpandedIndex(expandedIndex + 1);
      if (e.key === "ArrowLeft" && expandedIndex > 0)
        setExpandedIndex(expandedIndex - 1);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [expandedIndex, frames.length]);

  const close = useCallback(() => setExpandedIndex(null), []);

  if (frames.length === 0) return null;

  return (
    <>
      <div className="w-full max-w-4xl mx-auto">
        <h2 className="text-sm font-mono uppercase tracking-widest text-foreground/50 mb-3">
          Extracted Frames
          <span className="text-foreground/30 ml-2">— click to expand</span>
        </h2>
        <div className="grid grid-cols-4 gap-2">
          {frames.map((frame, i) => {
            const isKey = keyFrame !== undefined && i + 1 === keyFrame;
            return (
              <button
                key={frame}
                onClick={() => setExpandedIndex(i)}
                className={`relative aspect-video rounded-lg overflow-hidden border-2 bg-card transition-all cursor-pointer
                  hover:scale-[1.04] hover:z-10 hover:shadow-lg ${
                  isKey
                    ? "border-accent-blue shadow-[0_0_12px_rgba(59,130,246,0.4)] scale-[1.03] z-10"
                    : "border-card-border"
                }`}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={frameUrl(frame)}
                  alt={`Frame ${i + 1}`}
                  className="w-full h-full object-cover"
                />
                <span
                  className={`absolute bottom-1 right-1 text-[10px] font-mono px-1.5 py-0.5 rounded ${
                    isKey
                      ? "bg-accent-blue text-white"
                      : "bg-black/70 text-white"
                  }`}
                >
                  {isKey ? "★ KEY" : `F${i + 1}`}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Lightbox modal */}
      {expandedIndex !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
          onClick={close}
        >
          <div
            className="relative max-w-4xl w-full mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={close}
              className="absolute -top-10 right-0 text-white/70 hover:text-white text-sm font-mono"
            >
              ESC to close
            </button>

            {/* Frame image */}
            <div className="relative rounded-xl overflow-hidden border-2 border-card-border">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={frameUrl(frames[expandedIndex])}
                alt={`Frame ${expandedIndex + 1}`}
                className="w-full h-auto"
              />
              {/* Frame label */}
              <div className="absolute bottom-3 left-3 flex items-center gap-2">
                <span
                  className={`text-sm font-mono px-2 py-1 rounded ${
                    keyFrame !== undefined && expandedIndex + 1 === keyFrame
                      ? "bg-accent-blue text-white"
                      : "bg-black/70 text-white"
                  }`}
                >
                  {keyFrame !== undefined && expandedIndex + 1 === keyFrame
                    ? `★ KEY FRAME ${expandedIndex + 1}`
                    : `Frame ${expandedIndex + 1} of ${frames.length}`}
                </span>
              </div>
            </div>

            {/* Navigation arrows */}
            <div className="flex justify-between mt-3">
              <button
                onClick={() =>
                  setExpandedIndex(Math.max(0, expandedIndex - 1))
                }
                disabled={expandedIndex === 0}
                className="text-sm font-mono text-white/70 hover:text-white disabled:text-white/20 disabled:cursor-not-allowed"
              >
                ← Previous
              </button>
              <button
                onClick={() =>
                  setExpandedIndex(
                    Math.min(frames.length - 1, expandedIndex + 1)
                  )
                }
                disabled={expandedIndex === frames.length - 1}
                className="text-sm font-mono text-white/70 hover:text-white disabled:text-white/20 disabled:cursor-not-allowed"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
