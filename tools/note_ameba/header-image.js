#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 見出し画像(1280x670 PNG)を固定テンプレートから生成する(2026-10-17新設)。
 * テンプレート: 03_assets/creative-templates/note-header.html(CSSはAIが書き換えない)
 * 背景写真は select.js が選んだもの(無ければ紺のグラデーション背景)。
 *
 * 単体での確認: node header-image.js <draft.md> <出力PNGパス>
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.join(__dirname, "..", "..");
const TEMPLATE = path.join(ROOT, "03_assets", "creative-templates", "note-header.html");
const VIEWPORT = { width: 1280, height: 670 }; // noteの見出し画像の推奨比率

// 「暗記が苦手な子への声かけ ― 『覚えられない』は…」のようなタイトルを
// メイン見出しと補足に分ける(区切りが無ければ全体をメイン見出しにする)
function splitTitle(title) {
  const parts = String(title || "").split(/\s*[―—]\s*/);
  if (parts.length < 2) return { title: String(title || "").trim(), subtitle: "" };
  return { title: parts[0].trim(), subtitle: parts.slice(1).join(" ").trim() };
}

function launchOptions() {
  return process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE
    ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE }
    : {};
}

async function renderHeader({ title, subject, photo, label }, outPath, browser) {
  const own = !browser;
  if (own) browser = await chromium.launch(launchOptions());
  try {
    const page = await browser.newPage({ viewport: VIEWPORT });
    const { title: main, subtitle } = splitTitle(title);
    const payload = {
      title: main,
      subtitle,
      subject: subject || "",
      tagLabel: label || "保護者様へ",
      bg: photo ? "file://" + path.resolve(ROOT, photo) : null,
    };
    const b64 = Buffer.from(JSON.stringify(payload), "utf8").toString("base64");
    await page.goto("file://" + TEMPLATE + "?d=" + encodeURIComponent(b64));
    await page.waitForSelector('body[data-ready="true"]', { timeout: 15000 }).catch(() => {});
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    await page.screenshot({ path: outPath });
    await page.close();
    return outPath;
  } finally {
    if (own) await browser.close();
  }
}

module.exports = { renderHeader, splitTitle, launchOptions };

if (require.main === module) {
  const [draft, out] = process.argv.slice(2);
  if (!draft || !out) { console.error("usage: node header-image.js <draft.md> <out.png>"); process.exit(1); }
  const { parseFile } = require("./lib/frontmatter");
  const { selectImage, loadContext } = require("./select");
  const parsed = parseFile(draft);
  const img = selectImage(parsed, loadContext());
  renderHeader({ title: parsed.title, subject: parsed.front.subject, photo: img.photo, label: parsed.front.header_label }, out)
    .then((p) => console.log("生成しました:", p, "/ 背景:", img.photo || "グラデーション"))
    .catch((e) => { console.error(e); process.exit(1); });
}
