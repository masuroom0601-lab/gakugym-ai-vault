import { AbsoluteFill, OffthreadVideo, staticFile } from "remotion";

export const Clip: React.FC<{ src: string }> = ({ src }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <OffthreadVideo
        src={staticFile(src)}
        muted
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    </AbsoluteFill>
  );
};
