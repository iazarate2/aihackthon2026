"use client";

import { AnalysisResponse } from "@/lib/types";

interface VerdictCardProps {
  result: AnalysisResponse;
}

/** Map verdict → colour classes */
function verdictColor(verdict: string) {
  switch (verdict) {
    case "Fair Call":
      return {
        text: "text-accent-green",
        bg: "bg-accent-green",
        border: "border-accent-green/30",
        glow: "shadow-[0_0_30px_rgba(34,197,94,0.25)]",
      };
    case "Foul":
      return {
        text: "text-accent-red",
        bg: "bg-accent-red",
        border: "border-accent-red/30",
        glow: "shadow-[0_0_30px_rgba(239,68,68,0.25)]",
      };
    case "Dangerous Play":
      return {
        text: "text-accent-orange",
        bg: "bg-accent-orange",
        border: "border-accent-orange/30",
        glow: "shadow-[0_0_30px_rgba(249,115,22,0.25)]",
      };
    case "Inconclusive":
    default:
      return {
        text: "text-accent-yellow",
        bg: "bg-accent-yellow",
        border: "border-accent-yellow/30",
        glow: "shadow-[0_0_30px_rgba(234,179,8,0.25)]",
      };
  }
}

export default function VerdictCard({ result }: VerdictCardProps) {
  const colors = verdictColor(result.verdict);
  const pct = Math.round(result.confidence * 100);

  return (
    <div
      className={`
        w-full max-w-2xl mx-auto rounded-2xl border
        bg-card p-8 animate-verdict-reveal
        ${colors.border} ${colors.glow}
      `}
    >
      {/* Verdict heading */}
      <div className="text-center mb-6">
        <p className="text-xs font-mono uppercase tracking-widest text-foreground/40 mb-2">
          VAR Decision
        </p>
        <h2 className={`text-5xl font-extrabold tracking-tight ${colors.text}`}>
          {result.verdict}
        </h2>
      </div>

      {/* Confidence bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs font-mono text-foreground/50 mb-1">
          <span>Confidence</span>
          <span>{pct}%</span>
        </div>
        <div className="w-full h-3 rounded-full bg-card-border overflow-hidden">
          <div
            className={`h-full rounded-full animate-fill-bar ${colors.bg}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Key frame callout */}
      {result.key_frame && (
        <div className={`mb-4 px-4 py-3 rounded-lg border ${colors.border} bg-background`}>
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs font-mono uppercase tracking-widest ${colors.text}`}>
              Decisive Moment — Frame {result.key_frame}
            </span>
          </div>
          {result.key_frame_reason && (
            <p className="text-sm text-foreground/70">{result.key_frame_reason}</p>
          )}
        </div>
      )}

      {/* Rule reference */}
      <div className="mb-4 px-4 py-2 rounded-lg bg-background border border-card-border">
        <p className="text-xs font-mono uppercase tracking-widest text-foreground/40 mb-0.5">
          Rule Reference
        </p>
        <p className="text-sm font-semibold">{result.rule_reference}</p>
      </div>

      {/* Explanation */}
      <div className="mb-6">
        <p className="text-xs font-mono uppercase tracking-widest text-foreground/40 mb-1">
          Explanation
        </p>
        <p className="text-sm leading-relaxed text-foreground/80">
          {result.explanation}
        </p>
      </div>

      {/* Key observations */}
      <div>
        <p className="text-xs font-mono uppercase tracking-widest text-foreground/40 mb-2">
          Key Observations
        </p>
        <ul className="space-y-1.5">
          {result.key_observations.map((obs, i) => (
            <li
              key={i}
              className="flex items-start gap-2 text-sm text-foreground/70"
            >
              <span className={`mt-1 w-1.5 h-1.5 rounded-full shrink-0 ${colors.bg}`} />
              {obs}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
