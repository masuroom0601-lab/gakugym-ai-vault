import React from "react";
import { AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Beat } from "./Beat";
import type { ReelTemplateProps } from "./types";

const DEFAULT_TRANSITION_DURATION = 12;

// Reusable "tips reel" template: a sequence of Beats (B-roll clip + pinned
// topic label + cycling bold captions), crossfaded together. Feed it new
// `beats` for each future CAPS reel instead of writing a new composition.
export const ReelTemplate: React.FC<ReelTemplateProps> = ({
  beats,
  transitionDurationInFrames = DEFAULT_TRANSITION_DURATION,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <TransitionSeries>
        {beats.map((beat, i) => (
          <React.Fragment key={i}>
            {i > 0 && (
              <TransitionSeries.Transition
                presentation={fade()}
                timing={linearTiming({ durationInFrames: transitionDurationInFrames })}
              />
            )}
            <TransitionSeries.Sequence durationInFrames={beat.durationInFrames}>
              <Beat {...beat} />
            </TransitionSeries.Sequence>
          </React.Fragment>
        ))}
      </TransitionSeries>
    </AbsoluteFill>
  );
};

export const reelTemplateDurationInFrames = (
  beats: ReelTemplateProps["beats"],
  transitionDurationInFrames = DEFAULT_TRANSITION_DURATION,
) =>
  beats.reduce((sum, b) => sum + b.durationInFrames, 0) -
  (beats.length - 1) * transitionDurationInFrames;
