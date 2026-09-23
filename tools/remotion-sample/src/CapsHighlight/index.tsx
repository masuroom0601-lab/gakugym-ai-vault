import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import type { Caption } from "@remotion/captions";
import { Clip } from "./Clip";
import { TitleCard } from "./TitleCard";
import { Captions } from "../Captions";

const SEGMENT_DURATION = 132;
const TRANSITION_DURATION = 15;
const TITLE_DURATION = 90;

const CLIPS = [
  "processed-clips/clip-1.mp4",
  "processed-clips/clip-2.mp4",
  "processed-clips/clip-3.mp4",
  "processed-clips/clip-4.mp4",
  "processed-clips/clip-5.mp4",
];

// `captions` is optional: pass Caption[] (e.g. via fromWhisperSegments) to
// burn in synced subtitles, or leave empty for the plain highlight reel.
export const CapsHighlight: React.FC<{ captions?: Caption[] }> = ({ captions = [] }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <TransitionSeries>
        {CLIPS.map((src, i) => (
          <React.Fragment key={src}>
            {i > 0 && (
              <TransitionSeries.Transition
                presentation={fade()}
                timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
              />
            )}
            <TransitionSeries.Sequence durationInFrames={SEGMENT_DURATION}>
              <Clip src={src} />
            </TransitionSeries.Sequence>
          </React.Fragment>
        ))}
      </TransitionSeries>

      <Sequence from={0} durationInFrames={TITLE_DURATION}>
        <TitleCard heading="CAPS" subheading="活動風景" durationInFrames={TITLE_DURATION} />
      </Sequence>

      {captions.length > 0 && <Captions captions={captions} />}
    </AbsoluteFill>
  );
};

export const capsHighlightDurationInFrames =
  CLIPS.length * SEGMENT_DURATION - (CLIPS.length - 1) * TRANSITION_DURATION;
