import { AbsoluteFill, OffthreadVideo, staticFile, useVideoConfig } from "remotion";
import { TopicLabel } from "./TopicLabel";
import { BeatCaptions } from "./BeatCaptions";
import type { Beat as BeatType } from "./types";

export const Beat: React.FC<BeatType> = ({
  clipSrc,
  clipTrimStartSec = 0,
  label,
  labelAccent,
  captions,
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <OffthreadVideo
        src={staticFile(clipSrc)}
        muted
        startFrom={Math.round(clipTrimStartSec * fps)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.45) 100%)",
        }}
      />
      {label && <TopicLabel text={label} accent={labelAccent} />}
      <BeatCaptions captions={captions} />
    </AbsoluteFill>
  );
};
