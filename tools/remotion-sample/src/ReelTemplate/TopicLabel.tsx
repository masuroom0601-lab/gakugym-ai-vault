import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const ACCENTS: Record<string, string> = {
  yellow: "#facc15",
  red: "#ef4444",
  blue: "#38bdf8",
  white: "#ffffff",
};

// The small pinned "topic tag" box (e.g. "①教室の場所確認") that stays
// visible for the whole beat, mimicking the reference reel's running header.
export const TopicLabel: React.FC<{ text: string; accent?: string }> = ({
  text,
  accent = "yellow",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200 } });
  const scale = interpolate(enter, [0, 1], [0.85, 1]);

  return (
    <div
      style={{
        position: "absolute",
        top: 260,
        left: "50%",
        transform: `translateX(-50%) scale(${scale})`,
        opacity: enter,
        backgroundColor: "white",
        borderRadius: 24,
        padding: "18px 32px",
        boxShadow: "0 8px 20px rgba(0,0,0,0.35)",
        maxWidth: "88%",
      }}
    >
      <span
        style={{
          fontFamily: "Arial, sans-serif",
          fontWeight: 800,
          fontSize: 40,
          color: "#111",
          textShadow: `1px 1px 0 ${ACCENTS[accent]}, -1px -1px 0 ${ACCENTS[accent]}`,
          whiteSpace: "nowrap",
        }}
      >
        {text}
      </span>
    </div>
  );
};
