import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { Caption } from "@remotion/captions";
import { wrapJapanese } from "./wrapJapanese";

const MAX_CHARS_PER_LINE = 14;

// Renders a Whisper-style caption list (segment text + startMs/endMs) as
// burned-in Japanese subtitles, wrapping at natural phrase boundaries via BudouX.
export const Captions: React.FC<{ captions: Caption[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const timeMs = (frame / fps) * 1000;

  const active = captions.find((c) => timeMs >= c.startMs && timeMs < c.endMs);
  if (!active) return null;

  const lines = wrapJapanese(active.text, MAX_CHARS_PER_LINE);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 160,
      }}
    >
      <div
        style={{
          fontFamily: "Arial, sans-serif",
          fontSize: 52,
          fontWeight: 700,
          color: "white",
          textAlign: "center",
          lineHeight: 1.4,
          textShadow:
            "0 0 12px rgba(0,0,0,0.85), 0 2px 6px rgba(0,0,0,0.85), 0 -2px 6px rgba(0,0,0,0.85)",
          maxWidth: "85%",
        }}
      >
        {lines.map((line, i) => (
          <div key={i}>{line}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
