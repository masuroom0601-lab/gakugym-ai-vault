import { z } from "zod";

// Mirrors types.ts, but as a Zod schema so Remotion Studio renders an
// editable form (in the browser, no code) for every field below.
export const captionFragmentSchema = z.object({
  text: z.string(),
  durationInFrames: z.number(),
});

export const beatSchema = z.object({
  clipSrc: z.string(),
  clipTrimStartSec: z.number().optional(),
  durationInFrames: z.number(),
  label: z.string().optional(),
  labelAccent: z.enum(["yellow", "red", "blue", "white"]).optional(),
  captions: z.array(captionFragmentSchema),
});

export const reelTemplateSchema = z.object({
  beats: z.array(beatSchema),
  transitionDurationInFrames: z.number().optional(),
});
