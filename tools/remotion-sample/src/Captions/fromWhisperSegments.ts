import type { Caption } from "@remotion/captions";

type WhisperSegment = { text: string; start: number; end: number };

// Converts OpenAI Whisper's verbose_json `segments` (seconds) into
// @remotion/captions' Caption[] (milliseconds).
export const fromWhisperSegments = (segments: WhisperSegment[]): Caption[] =>
  segments.map((s) => ({
    text: s.text.trim(),
    startMs: Math.round(s.start * 1000),
    endMs: Math.round(s.end * 1000),
    timestampMs: null,
    confidence: null,
  }));
