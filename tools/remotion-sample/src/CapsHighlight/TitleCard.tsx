import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const TitleCard: React.FC<{
  heading: string;
  subheading: string;
  durationInFrames: number;
}> = ({ heading, subheading, durationInFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enter = spring({ frame, fps, config: { damping: 200 } });
  const exit = interpolate(
    frame,
    [durationInFrames - 15, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  const opacity = enter * exit;
  const translateY = interpolate(enter, [0, 1], [30, 0]);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        background:
          "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.15) 40%, rgba(0,0,0,0.15) 60%, rgba(0,0,0,0.55) 100%)",
      }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px)`,
          textAlign: "center",
          fontFamily: "Arial, sans-serif",
          color: "white",
        }}
      >
        <div
          style={{
            fontSize: 96,
            fontWeight: 800,
            letterSpacing: 4,
            textShadow: "0 4px 24px rgba(0,0,0,0.6)",
          }}
        >
          {heading}
        </div>
        <div
          style={{
            marginTop: 20,
            fontSize: 40,
            fontWeight: 500,
            textShadow: "0 2px 12px rgba(0,0,0,0.6)",
          }}
        >
          {subheading}
        </div>
      </div>
    </AbsoluteFill>
  );
};
