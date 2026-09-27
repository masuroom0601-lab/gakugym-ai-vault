// A single caption fragment shown for part of a beat, e.g. one spoken phrase.
export type CaptionFragment = {
  text: string;
  durationInFrames: number;
};

// One "beat" of the reel: a B-roll clip with an optional persistent topic
// label (the small pinned box, e.g. "①教室の場所確認") and a sequence of
// bigger caption fragments that change underneath it while the clip plays.
export type Beat = {
  clipSrc: string; // path relative to public/, passed to staticFile()
  clipTrimStartSec?: number; // where to start reading the source clip
  durationInFrames: number; // total time this beat occupies in the reel
  label?: string;
  labelAccent?: "yellow" | "red" | "blue" | "white";
  captions: CaptionFragment[]; // fragments' durations should sum to durationInFrames
};

export type ReelTemplateProps = {
  beats: Beat[];
  transitionDurationInFrames?: number;
};
