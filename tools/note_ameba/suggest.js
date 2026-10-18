#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 下書きに「おすすめのハッシュタグ・見出し画像」を添付する(2026-10-18新設)。
 *
 * 2026-10-18、自動投稿はやめて益田さんが手動投稿する運用に戻したため、
 * 投稿時に選んでいた画像・ハッシュタグを、下書きの段階で提案として書き込む形にした。
 * 選び方は select.js と同じ(記事内容・下書き時のAI提案・週次インサイト分析の実績)。
 *
 * 下書きのfrontmatterに書き込む項目:
 *   suggested_hashtags:      { note: [...], ameba: [...] }  … 投稿時にコピーして使う
 *   suggested_header_image:  02_departments/note_ameba/images/<下書き名>.jpg(1280x670、そのまま見出し画像に使える)
 *   suggested_image_source:  背景に使った写真(03_assets/images/note_ameba/...)。写真なしなら "template"
 * 投稿時に提案と違うタグ・画像を使った場合は、note_hashtags / ameba_hashtags / image_source に
 * 実際に使ったものを書いておくと、週次分析はそちらを優先して効果を測る。
 *
 * 使い方:
 *   node suggest.js            … 提案がまだ無い下書き(status: review / draft)すべてに添付
 *   node suggest.js --force    … 既に提案がある下書きも作り直す
 *   node suggest.js <ファイル名> … 指定した下書きだけ(既にあっても作り直す)
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { parseFile, writeFile } = require("./lib/frontmatter");
const { selectAll, loadContext, ROOT } = require("./select");
const { renderHeader, launchOptions } = require("./header-image");

const DRAFTS_DIR = path.join(ROOT, "02_departments", "note_ameba", "drafts");
const IMAGES_DIR = path.join(ROOT, "02_departments", "note_ameba", "images");

async function main() {
  const args = process.argv.slice(2);
  const force = args.includes("--force");
  const only = args.find((a) => !a.startsWith("--"));
  const files = fs.readdirSync(DRAFTS_DIR).filter((f) => f.endsWith(".md")).sort()
    .filter((f) => !only || f === path.basename(only));
  const ctx = loadContext();
  let browser = null;
  let done = 0;

  for (const file of files) {
    const filePath = path.join(DRAFTS_DIR, file);
    const parsed = parseFile(filePath);
    if (!parsed) continue;
    const { front, title, body } = parsed;
    if (!only && (front.status === "published" || (front.suggested_hashtags && !force))) continue;

    const sel = selectAll(parsed, ctx);
    let headerRel = null, source = null;
    if (sel.image.fixed) {
      headerRel = sel.image.fixed; source = sel.image.fixed;
    } else {
      browser = browser || await chromium.launch(launchOptions());
      const out = path.join(IMAGES_DIR, file.replace(/\.md$/, ".jpg"));
      await renderHeader({ title, subject: front.subject, photo: sel.image.photo, label: front.header_label }, out, browser);
      headerRel = path.relative(ROOT, out);
      source = sel.image.photo || "template";
    }
    front.suggested_hashtags = { note: sel.hashtags.note.tags, ameba: sel.hashtags.ameba.tags };
    front.suggested_header_image = headerRel;
    front.suggested_image_source = source;
    writeFile(filePath, front, title, body);
    done++;
    console.log(`${file}: note ${sel.hashtags.note.tags.map((t) => "#" + t).join(" ")} / Ameba ${sel.hashtags.ameba.tags.map((t) => "#" + t).join(" ")} / 画像 ${headerRel}(背景: ${source})`);
  }
  if (browser) await browser.close();
  console.log(`${done}件の下書きに提案を添付しました`);
}

main().catch((e) => { console.error(e); process.exit(1); });
