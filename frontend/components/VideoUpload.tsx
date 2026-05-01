"use client";

import { useCallback, useState } from "react";

interface VideoUploadProps {
  onFileSelected: (file: File) => void;
  isUploading: boolean;
}

export default function VideoUpload({
  onFileSelected,
  isUploading,
}: VideoUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      setFileName(file.name);
      onFileSelected(file);
    },
    [onFileSelected]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      className={`
        relative flex flex-col items-center justify-center
        w-full max-w-xl mx-auto p-10 rounded-2xl border-2 border-dashed
        transition-all duration-300 cursor-pointer
        ${
          isDragging
            ? "border-accent-blue bg-accent-blue/10 scale-[1.02]"
            : "border-card-border bg-card hover:border-accent-blue/50"
        }
        ${isUploading ? "animate-pulse-glow pointer-events-none opacity-70" : ""}
      `}
    >
      {/* Upload icon */}
      <svg
        className="w-14 h-14 mb-4 text-accent-blue"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
        />
      </svg>

      {isUploading ? (
        <div className="text-center">
          <p className="text-lg font-semibold text-accent-blue">
            Processing clip...
          </p>
          <p className="text-sm text-foreground/50 mt-1">
            Extracting frames from {fileName}
          </p>
        </div>
      ) : (
        <div className="text-center">
          <p className="text-lg font-semibold">
            Drop your soccer clip here
          </p>
          <p className="text-sm text-foreground/50 mt-1">
            or click to browse — MP4, MOV, AVI, MKV
          </p>
        </div>
      )}

      {/* Hidden file input */}
      <input
        type="file"
        accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska"
        onChange={onInputChange}
        disabled={isUploading}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
    </div>
  );
}
