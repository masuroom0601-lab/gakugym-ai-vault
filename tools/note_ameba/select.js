#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 投稿時に「最適なハッシュタグ」と「見出し画像」を選ぶ(2026-10-17新設)。
 *
 * publish.jsと同じく、LLMを経由しない決定的ロジック(同じ入力なら必ず同じ結果)。
 * 選定の材料は次の3つだけ:
 *   1. 記事の中身(タイトル・subject・本文に含まれるキーワード)
 *   2. 下書き作成時にAIが提案した候補(frontmatterの hashtag_candidates / image_keywords)
 *   3. 過去の実績(04_analytics/note_ameba/performance.json。週次インサイト分析で自動更新)
 *
 * 人が明示的に指定した値は常に優先する:
 *   - frontmatterに hashtags: [...] があれば、それをそのまま使う(上限数で切るのみ)
 *   - frontmatterに header_image: <パス> があれば、その画像をそのまま使う
 *
 * 単体での確認(投稿はしない。選定結果を表示するだけ):
 *   node select.js ../../02_departments/note_ameba/drafts/task-2026-10-12-note-001.md
 */
const fs = require("fs");
const path = require("path");
const { parseFile, loadYaml, loadJson } = require("./lib/frontmatter");

const ROOT = path.join(__dirname, "..", "..");
const POOL_PATH = path.join(ROOT, "02_departments", "note_ameba", "hashtag-pool.yml");
const CATALOG_PATH = path.join(ROOT, "03_assets", "images", "note_ameba", "catalog.yml");
const PERF_PATH = path.join(ROOT, "04_analytics", "note_ameba", "performance.json");
const PUBLISHED_DIR = path.join(ROOT, "02_departments", "note_ameba", "published");

const DEFAULT_LIMITS = { note: 5, ameba: 5 }; // note公式ヘルプ「タグは5つぐらいが効果的」に合わせる
const MIN_SAMPLES = 2;   // 実績ボーナスを効かせる最低サンプル数(1件だけの偶然で偏らないように)
const RECENT_WINDOW = 3; // 直近この本数の記事で使った写真は避ける(同じ画像の連投防止)

function normalizeTag(t) {
  return String(t || "").trim().replace(/^[#＃]+/, "").replace(/\s+/g, "");
}

function countOccurrences(text, word) {
  if (!word) return 0;
  const hay = text.toLowerCase(), needle = String(word).toLowerCase();
  let n = 0, i = 0;
  while ((i = hay.indexOf(needle, i)) !== -1) { n++; i += needle.length; }
  return n;
}

// キーワードの出現箇所で重みを変える: タイトル > subject > 本文(本文は最大3回分まで)
function relevance(article, keywords) {
  const title = String(article.title || ""), subject = String(article.subject || (article.front && article.front.subject) || "");
  const body = String(article.body || "");
  let score = 0;
  for (const kw of keywords) {
    score += countOccurrences(title, kw) * 3;
    score += countOccurrences(subject, kw) * 2;
    score += Math.min(countOccurrences(body, kw), 3);
  }
  return score;
}

// performance.jsonのscoreは「その要素を使った記事の平均成績 ÷ 全体の典型値」(1.0=平均並み)。
// 平均より良ければ最大+3、悪ければ最大-2のボーナスにする。サンプル不足なら0。
function perfBonus(entry) {
  if (!entry || typeof entry.score !== "number" || (entry.samples || 0) < MIN_SAMPLES) return 0;
  return Math.max(-2, Math.min(3, (entry.score - 1) * 3));
}

function selectHashtags(article, platform, { pool, perf } = {}) {
  pool = pool || { tags: [] };
  perf = perf || {};
  const limit = (pool.limits && pool.limits[platform]) || DEFAULT_LIMITS[platform] || 5;
  const front = article.front || {};

  if (Array.isArray(front.hashtags) && front.hashtags.length) {
    const fixed = [...new Set(front.hashtags.map(normalizeTag).filter(Boolean))];
    return { tags: fixed.slice(0, limit), reason: "frontmatterのhashtags指定をそのまま使用", scored: [] };
  }

  const tagPerf = (perf.hashtags && perf.hashtags[platform]) || {};
  const candidates = new Map(); // tag -> {score, why[]}
  const add = (tag, pts, why) => {
    tag = normalizeTag(tag);
    if (!tag) return;
    const c = candidates.get(tag) || { tag, score: 0, why: [], relevant: false };
    c.score += pts; c.why.push(why);
    candidates.set(tag, c);
    return c;
  };

  for (const entry of pool.tags || []) {
    if (entry.platforms && !entry.platforms.map((p) => p.toLowerCase()).includes(platform)) continue;
    const kws = [entry.tag, ...(entry.keywords || [])];
    const rel = relevance(article, kws);
    const c = rel > 0 && add(entry.tag, rel, `本文との関連度${rel}`);
    if (c) c.relevant = true;
  }
  for (const t of front.hashtag_candidates || []) {
    const c = add(t, 5, "下書き作成時のAI提案");
    if (c) c.relevant = true;
  }
  for (const c of candidates.values()) {
    const b = perfBonus(tagPerf[c.tag]);
    if (b) { c.score += b; c.why.push(`過去実績${b > 0 ? "+" : ""}${b.toFixed(1)}`); }
  }

  const always = (pool.always || []).map(normalizeTag).filter(Boolean);
  const ranked = [...candidates.values()]
    .filter((c) => c.relevant && !always.includes(c.tag))
    // 同点ならタグ名順にして、実行ごとに結果がぶれないようにする
    .sort((a, b) => b.score - a.score || a.tag.localeCompare(b.tag, "ja"));

  const tags = [...always, ...ranked.map((c) => c.tag)].slice(0, limit);
  return { tags, reason: "記事内容・AI提案・過去実績からスコア順に選定", scored: ranked };
}

function recentlyUsedImages(publishedDir = PUBLISHED_DIR) {
  if (!fs.existsSync(publishedDir)) return [];
  const files = fs.readdirSync(publishedDir).filter((f) => f.endsWith(".md")).sort().slice(-RECENT_WINDOW);
  const used = [];
  for (const f of files) {
    const p = parseFile(path.join(publishedDir, f));
    if (p && p.front.image_source) used.push(p.front.image_source);
  }
  return used;
}

// 見出し画像の「背景写真」を選ぶ。実際の見出し画像は header-image.js が
// この写真+記事タイトルを固定テンプレートに流し込んで生成する。
// 写真が1枚も無い/関連する写真が無い場合は photo: null(テンプレートのグラデーション背景を使う)。
function selectImage(article, { catalog, perf, recent } = {}) {
  const front = article.front || {};
  if (front.header_image) {
    return { fixed: front.header_image, photo: null, reason: "frontmatterのheader_image指定をそのまま使用", scored: [] };
  }
  catalog = catalog || { images: [] };
  perf = perf || {};
  recent = recent || [];
  const imgPerf = perf.images || {};
  const extraKws = front.image_keywords || [];

  const scored = [];
  for (const img of catalog.images || []) {
    if (!img || !img.file) continue;
    if (!fs.existsSync(path.join(ROOT, img.file))) continue; // カタログにあってもファイルが無ければ対象外
    const kws = img.keywords || [];
    let score = relevance(article, kws);
    const why = [`本文との関連度${score}`];
    const hits = extraKws.filter((k) => kws.some((kw) => kw.includes(k) || k.includes(kw))).length;
    if (hits) { score += hits * 4; why.push(`AI提案キーワード一致${hits}件`); }
    if (score <= 0) continue;
    const b = perfBonus(imgPerf[img.file]);
    if (b) { score += b; why.push(`過去実績${b > 0 ? "+" : ""}${b.toFixed(1)}`); }
    if (recent.includes(img.file)) { score -= 5; why.push("直近の記事で使用済み"); }
    scored.push({ file: img.file, score, why });
  }
  scored.sort((a, b) => b.score - a.score || a.file.localeCompare(b.file));
  const best = scored.find((s) => s.score > 0);
  return best
    ? { fixed: null, photo: best.file, reason: "記事内容・AI提案・過去実績から最も合う写真を選定", scored }
    : { fixed: null, photo: null, reason: "合う写真が無いため、テンプレートの単色背景+タイトル文字で生成", scored };
}

function loadContext() {
  return {
    pool: loadYaml(POOL_PATH, { tags: [] }),
    catalog: loadYaml(CATALOG_PATH, { images: [] }),
    perf: loadJson(PERF_PATH, {}),
    recent: recentlyUsedImages(),
  };
}

function selectAll(article, ctx = loadContext()) {
  return {
    hashtags: {
      note: selectHashtags(article, "note", ctx),
      ameba: selectHashtags(article, "ameba", ctx),
    },
    image: selectImage(article, ctx),
  };
}

module.exports = { selectHashtags, selectImage, selectAll, loadContext, normalizeTag, perfBonus, ROOT };

if (require.main === module) {
  const file = process.argv[2];
  if (!file) { console.error("usage: node select.js <draft.md>"); process.exit(1); }
  const parsed = parseFile(file);
  if (!parsed) { console.error("frontmatterを読み取れませんでした"); process.exit(1); }
  const r = selectAll(parsed);
  console.log("note ハッシュタグ :", r.hashtags.note.tags.map((t) => "#" + t).join(" "), `(${r.hashtags.note.reason})`);
  console.log("Ameba ハッシュタグ:", r.hashtags.ameba.tags.map((t) => "#" + t).join(" "), `(${r.hashtags.ameba.reason})`);
  console.log("見出し画像       :", r.image.fixed || r.image.photo || "(写真なし・テンプレート背景)", `(${r.image.reason})`);
  for (const s of r.hashtags.note.scored.slice(0, 10)) console.log(`  [tag] ${s.tag}: ${s.score.toFixed(1)} … ${s.why.join(", ")}`);
  for (const s of r.image.scored.slice(0, 5)) console.log(`  [img] ${s.file}: ${s.score.toFixed(1)} … ${s.why.join(", ")}`);
}
