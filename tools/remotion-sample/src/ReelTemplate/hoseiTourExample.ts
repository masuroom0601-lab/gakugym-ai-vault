import type { Beat } from "./types";

// EXAMPLE content only — placeholder copy to demonstrate ReelTemplate with
// the Hosei campus footage in public/reels/hosei-tour/processed/. Swap in
// the real script before publishing. ~45s total, ending on the branded
// CAPS CTA card (clip-cta.mp4).
export const hoseiTourBeats: Beat[] = [
  {
    clipSrc: "reels/hosei-tour/processed/clip-1.mp4",
    durationInFrames: 165,
    captions: [
      { text: "法政大学のみんなへ", durationInFrames: 90 },
      { text: "CAPSが教える新歓Tips", durationInFrames: 75 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-2.mp4",
    durationInFrames: 180,
    label: "①SNSは絶対フォロー",
    labelAccent: "yellow",
    captions: [
      { text: "サークル情報や", durationInFrames: 60 },
      { text: "お得なイベント情報が", durationInFrames: 60 },
      { text: "届くよ", durationInFrames: 60 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-3.mp4",
    durationInFrames: 210,
    label: "②キャンパスまでの道",
    labelAccent: "blue",
    captions: [
      { text: "駅からキャンパスまで", durationInFrames: 70 },
      { text: "意外と迷いやすいから", durationInFrames: 70 },
      { text: "事前にチェックしておこう", durationInFrames: 70 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-4.mp4",
    durationInFrames: 405,
    label: "③学食は時間をずらす",
    labelAccent: "red",
    captions: [
      { text: "お昼のピークは", durationInFrames: 101 },
      { text: "激混みだから", durationInFrames: 101 },
      { text: "早め or 遅めが", durationInFrames: 101 },
      { text: "狙い目だよ", durationInFrames: 102 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-5.mp4",
    durationInFrames: 300,
    captions: [
      { text: "友達作りに迷ったら", durationInFrames: 150 },
      { text: "CAPSのイベントにおいで!", durationInFrames: 150 },
    ],
  },
  {
    // Branded closing card, self-contained (its own baked-in logo/text) —
    // no pinned label or caption overlay needed.
    clipSrc: "reels/hosei-tour/processed/clip-cta.mp4",
    durationInFrames: 151,
    captions: [],
  },
];
