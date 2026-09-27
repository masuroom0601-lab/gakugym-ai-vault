import { AbsoluteFill, Series, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { wrapJapanese } from "../Captions/wrapJapanese";
import type { CaptionFragment } from "./types";

const MAX_CHARS_PER_LINE = 14;

const FragmentText: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200 } });
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const translateY = interpolate(enter, [0, 1], [20, 0]);
  const lines = wrapJapanese(text, MAX_CHARS_PER_LINE);

  return (
    // Series.Sequence positions its child absolutely without re-establishing
    // flex centering, so each fragment centers itself rather than relying on
    // a shared wrapper.
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingTop: 120 }}>
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px)`,
          fontFamily: "Arial, sans-serif",
          fontWeight: 900,
          fontSize: 58,
          color: "white",
          textAlign: "center",
          lineHeight: 1.35,
          textShadow:
            "-3px -3px 0 #111, 3px -3px 0 #111, -3px 3px 0 #111, 3px 3px 0 #111, 0 6px 16px rgba(0,0,0,0.5)",
          maxWidth: "90%",
        }}
      >
        {lines.map((line, i) => (
          <div key={i}>{line}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// Plays a beat's caption fragments one after another (e.g. one voiceover
// phrase at a time), positioned where the reference reel's big bold
// subtitles sit — below the pinned topic label.
export const BeatCaptions: React.FC<{ captions: CaptionFragment[] }> = ({ captions }) => {
  if (captions.length === 0) return null;

  return (
    <Series>
      {captions.map((c, i) => (
        <Series.Sequence key={i} durationInFrames={c.durationInFrames}>
          <FragmentText text={c.text} />
        </Series.Sequence>
      ))}
    </Series>
  );
};
