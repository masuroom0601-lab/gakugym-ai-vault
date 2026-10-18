#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 週次インサイトの数値集計(2026-10-17新設)。LLMを使わない決定的処理。
 *
 * 入力:
 *   - 04_analytics/note_ameba/raw/*.json の最新ファイル(insights.js が収集)
 *   - 02_departments/note_ameba/published/*.md(投稿時に記録した URL・ハッシュタグ・画像)
 * 出力:
 *   - 04_analytics/note_ameba/performance.json
 *     select.js が次回投稿時に「実績の良いタグ・画像」を優先するために読む
 *
 * 成績の測り方:
 *   公開からの日数が長い記事ほどビューが多くなるため、「1日あたりビュー」
 *   (公開7日未満は7日として計算)で比べる。プラットフォームごとに中央値を1.0として
 *   各記事の相対成績(index)を出し、スキ/いいねがあれば同様に計算して平均する。
 *   タグ・画像の score は、それを使った記事の index の平均を、サンプルが少ないうちは
 *   1.0(平均並み)に寄せて計算する(1〜2件の偶然で極端な評価にならないように)。
 */
const fs = require("fs");
const path = require("path");
const { parseFile } = require("./lib/frontmatter");

const ROOT = path.join(__dirname, "..", "..");
const RAW_DIR = path.join(ROOT, "04_analytics", "note_ameba", "raw");
const PERF_PATH = path.join(ROOT, "04_analytics", "note_ameba", "performance.json");
const PUBLISHED_DIR = path.join(ROOT, "02_departments", "note_ameba", "published");
const DRAFTS_DIR = path.join(ROOT, "02_departments", "note_ameba", "drafts");
const PRIOR_WEIGHT = 2; // 1.0に寄せる強さ(仮想的に「平均並みの記事2本分」を混ぜる)
const MIN_DAYS = 7;

const norm = (s) => String(s || "").replace(/\s+/g, "").replace(/[「」『』―—:：!！?？、。]/g, "").toLowerCase();

function median(xs) {
  const a = xs.filter((x) => typeof x === "number" && x > 0).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

function latestRaw(rawDir = RAW_DIR) {
  if (!fs.existsSync(rawDir)) return null;
  const files = fs.readdirSync(rawDir).filter((f) => /^\d{4}-\d{2}-\d{2}\.json$/.test(f)).sort();
  if (!files.length) return null;
  const file = files[files.length - 1];
  return { file, data: JSON.parse(fs.readFileSync(path.join(rawDir, file), "utf8")) };
}

// 2026-10-18〜は益田さんの手動投稿のため、記事ファイルは drafts/ に残ったままになる。
// published/ と drafts/ の両方を読み、実際に投稿されたもの(=統計データにタイトル等が一致したもの)だけが集計に入る。
function loadPublished(dirs = [PUBLISHED_DIR, DRAFTS_DIR]) {
  const out = [];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".md")).sort()) {
      const p = parseFile(path.join(dir, f));
      if (p) out.push({ file: f, ...p });
    }
  }
  return out;
}

function matchStat(article, stats, platform) {
  const front = article.front;
  const url = platform === "note" ? front.note_url : front.ameba_url;
  if (url) {
    if (platform === "note") {
      const key = (String(url).match(/\/n\/([A-Za-z0-9]+)/) || [])[1];
      const hit = key && stats.find((s) => s.key === key);
      if (hit) return hit;
    } else {
      const id = (String(url).match(/entry-(\d+)/) || [])[1];
      const hit = id && stats.find((s) => s.entry_id === id);
      if (hit) return hit;
    }
  }
  const t = norm(article.title);
  return stats.find((s) => s.title && (norm(s.title) === t || (norm(s.title).length >= 8 && t.startsWith(norm(s.title))))) || null;
}

function daysSince(dateStr, now) {
  const d = new Date(dateStr);
  if (isNaN(d)) return MIN_DAYS;
  return Math.max(MIN_DAYS, (now - d) / 86400000);
}

function aggregate(entries) {
  // entries: [{key, index}] -> {key: {samples, score, mean}}
  const by = {};
  for (const { key, index } of entries) (by[key] = by[key] || []).push(index);
  const out = {};
  for (const [k, xs] of Object.entries(by)) {
    const sum = xs.reduce((a, b) => a + b, 0);
    out[k] = {
      samples: xs.length,
      mean: +(sum / xs.length).toFixed(3),
      score: +((sum + PRIOR_WEIGHT * 1.0) / (xs.length + PRIOR_WEIGHT)).toFixed(3),
    };
  }
  return out;
}

function analyze({ raw, published, now = new Date() }) {
  const result = {
    generated_at: now.toISOString(),
    source: raw ? raw.file : null,
    method: "1日あたりビュー(とスキ/いいね)をプラットフォーム内の中央値=1.0で相対化。タグ・画像のscoreはサンプルが少ないほど1.0に寄せた平均",
    articles: [],
    hashtags: { note: {}, ameba: {} },
    images: {},
    unmatched: { note: [], ameba: [] },
  };
  if (!raw) return result;

  const rows = published.map((a) => ({
    file: a.file, title: a.title,
    published_at: a.front.published_at || a.front.date || null,
    // 実際に使った画像・タグ(手入力)があればそれを、無ければ下書きに添付した提案を使ったものとみなす
    image_source: a.front.image_source || a.front.suggested_image_source || null,
    hashtags: {
      note: a.front.note_hashtags || (a.front.suggested_hashtags && a.front.suggested_hashtags.note) || [],
      ameba: a.front.ameba_hashtags || (a.front.suggested_hashtags && a.front.suggested_hashtags.ameba) || [],
    },
    note: null, ameba: null, index: {},
  }));

  for (const platform of ["note", "ameba"]) {
    const block = raw.data[platform];
    const stats = (block && block.articles) || [];
    const matchedStats = new Set();
    rows.forEach((row, i) => {
      const s = matchStat(published[i], stats, platform);
      if (!s) return;
      matchedStats.add(s);
      if (s.published_at) row.published_at = s.published_at; // 統計側に公開日があればそちらが正確
      const days = daysSince(row.published_at, now);
      row[platform] = {
        views: s.views, likes: s.likes, comments: s.comments,
        views_per_day: s.views != null ? s.views / days : null,
        likes_per_day: s.likes != null ? s.likes / days : null,
      };
    });
    result.unmatched[platform] = stats.filter((s) => !matchedStats.has(s)).map((s) => s.title).slice(0, 30);

    const mv = median(rows.map((r) => r[platform] && r[platform].views_per_day));
    const ml = median(rows.map((r) => r[platform] && r[platform].likes_per_day));
    for (const r of rows) {
      const m = r[platform];
      if (!m) continue;
      const parts = [];
      if (mv && m.views_per_day != null) parts.push(m.views_per_day / mv);
      if (ml && m.likes_per_day != null) parts.push(m.likes_per_day / ml);
      if (parts.length) r.index[platform] = +(parts.reduce((a, b) => a + b, 0) / parts.length).toFixed(3);
      // 表示用に丸める(相対化の計算は丸める前の値で行う)
      if (m.views_per_day != null) m.views_per_day = +m.views_per_day.toFixed(2);
      if (m.likes_per_day != null) m.likes_per_day = +m.likes_per_day.toFixed(3);
    }

    result.hashtags[platform] = aggregate(rows.flatMap((r) =>
      r.index[platform] == null ? [] : r.hashtags[platform].map((t) => ({ key: t, index: r.index[platform] }))));
  }

  // 画像はnote/Amebaの平均成績で評価する(同じ画像を両方に使うため)
  result.images = aggregate(rows.flatMap((r) => {
    const xs = Object.values(r.index);
    if (!r.image_source || !xs.length) return [];
    return [{ key: r.image_source, index: xs.reduce((a, b) => a + b, 0) / xs.length }];
  }));

  result.articles = rows;
  return result;
}

module.exports = { analyze, median, matchStat, aggregate };

if (require.main === module) {
  const raw = latestRaw();
  if (!raw) { console.log("04_analytics/note_ameba/raw/ に収集データが無いため、集計をスキップします。"); process.exit(0); }
  const result = analyze({ raw, published: loadPublished() });
  fs.mkdirSync(path.dirname(PERF_PATH), { recursive: true });
  fs.writeFileSync(PERF_PATH, JSON.stringify(result, null, 2) + "\n", "utf8");
  const n = result.articles.filter((a) => Object.keys(a.index).length).length;
  console.log(`集計しました: 数値と紐づいた記事 ${n}/${result.articles.length}件 → ${path.relative(ROOT, PERF_PATH)}`);
}
