import type { Beat } from "./types";

// EXAMPLE content only — placeholder copy to demonstrate ReelTemplate with
// the Hosei campus footage in public/reels/hosei-tour/processed/. Swap in
// the real script before publishing.
export const hoseiTourBeats: Beat[] = [
  {
    clipSrc: "reels/hosei-tour/processed/clip-1.mp4",
    durationInFrames: 150,
    captions: [
      { text: "法政大学のみんなへ", durationInFrames: 90 },
      { text: "CAPSが教える新歓Tips", durationInFrames: 60 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-2.mp4",
    durationInFrames: 180,
    label: "①SNSは絶対フォロー",
    labelAccent: "yellow",
    captions: [
      { text: "サークル情報や", durationInFrames: 90 },
      { text: "お得なイベント情報が届くよ", durationInFrames: 90 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-3.mp4",
    durationInFrames: 150,
    label: "②キャンパスまでの道",
    labelAccent: "blue",
    captions: [
      { text: "駅からキャンパスまで", durationInFrames: 75 },
      { text: "意外と迷いやすいから要注意", durationInFrames: 75 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-4.mp4",
    durationInFrames: 180,
    label: "③学食は時間をずらす",
    labelAccent: "red",
    captions: [
      { text: "お昼のピークは激混み", durationInFrames: 90 },
      { text: "早め or 遅めが狙い目", durationInFrames: 90 },
    ],
  },
  {
    clipSrc: "reels/hosei-tour/processed/clip-5.mp4",
    durationInFrames: 180,
    captions: [
      { text: "友達作りに迷ったら", durationInFrames: 90 },
      { text: "CAPSのイベントにおいで!", durationInFrames: 90 },
    ],
  },
];
