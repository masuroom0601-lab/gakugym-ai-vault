#!/usr/bin/env node
// Fish Audio (https://fish.audio) text-to-speech CLI.
// Sends text to the Fish Audio TTS API and saves the resulting audio file.
//
// Usage:
//   FISH_AUDIO_API_KEY=xxx node tts.js "読み上げたいテキスト" out.mp3 [referenceId]
//
// Docs: https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech
const fs = require("fs");

const API_URL = "https://api.fish.audio/v1/tts";
const DEFAULT_MODEL = "s1"; // see Fish Audio docs for available model headers (e.g. "s1", "s2.1-pro")

async function main() {
  const [text, outPath, referenceId] = process.argv.slice(2);
  const apiKey = process.env.FISH_AUDIO_API_KEY;

  if (!text || !outPath) {
    console.error(
      "usage: FISH_AUDIO_API_KEY=xxx node tts.js <text> <outPath.mp3> [referenceId]",
    );
    process.exit(1);
  }
  if (!apiKey) {
    console.error("環境変数 FISH_AUDIO_API_KEY が未設定です。APIキーをここに直接書かないこと。");
    process.exit(1);
  }

  const body = { text, format: "mp3" };
  if (referenceId) body.reference_id = referenceId;

  const res = await fetch(API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
      model: DEFAULT_MODEL,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => "");
    console.error(`Fish Audio API error: ${res.status} ${res.statusText}\n${errText}`);
    process.exit(1);
  }

  const buffer = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(outPath, buffer);
  console.log(`saved: ${outPath} (${buffer.length} bytes)`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
