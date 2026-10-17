#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 週次インサイト(記事ごとのビュー・スキ/いいね・コメント数)を
 * ブラウザ自動操作で収集する(2026-10-17新設)。
 *
 * 出力: 04_analytics/note_ameba/raw/<YYYY-MM-DD>.json
 *   { collected_at, note: {ok, source, articles:[{title,key,url,views,likes,comments}], error, raw_text},
 *     ameba: {ok, source, articles:[{title,url,entry_id,views,likes,comments}], error, raw_text} }
 * この後 analyze.js が数値を集計し、Claude(週次ワークフロー)が考察・改善案を書く。
 *
 * 取得方法(いずれも非公式。サイト側の仕様変更で取れなくなる可能性がある):
 *   - note: ログイン後、ダッシュボード「アクセス状況」が内部で使っている
 *           /api/v1/stats/pv を同じログイン状態で読む。失敗したら画面の文字をそのまま保存する
 *   - Ameba: ログイン後のアクセス解析画面と、公開の記事一覧から読み取る。
 *           表として読み取れなかった場合も画面の文字(raw_text)を保存し、
 *           Claudeの分析ステップが読み取れるようにする
 * 何も取れなくてもエラー終了はしない(取れた分だけ保存し、取れなかった理由を error に残す)。
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { hasNoteCreds, hasAmebaCreds, loginNote, loginAmeba } = require("./lib/auth");
const { launchOptions } = require("./header-image");

const ROOT = path.join(__dirname, "..", "..");
const OUT_DIR = path.join(ROOT, "04_analytics", "note_ameba", "raw");
const RAW_TEXT_LIMIT = 15000; // 画面テキストの保存上限(リポジトリを肥大化させない)

function toInt(v) {
  if (v === null || v === undefined || v === "") return null;
  const n = parseInt(String(v).replace(/[,\s]/g, ""), 10);
  return Number.isFinite(n) ? n : null;
}

async function pageText(page) {
  const t = await page.evaluate(() => document.body ? document.body.innerText : "").catch(() => "");
  return t.replace(/\n{3,}/g, "\n\n").slice(0, RAW_TEXT_LIMIT);
}

async function collectNote(page) {
  const out = { ok: false, source: null, articles: [], error: null, raw_text: null };
  if (!hasNoteCreds()) { out.error = "NOTE_EMAIL/NOTE_PASSWORDが未設定のためスキップ"; return out; }
  try {
    await loginNote(page);
    for (let p = 1; p <= 20; p++) {
      const res = await page.request.get(`https://note.com/api/v1/stats/pv?filter=all&page=${p}&sort=pv`);
      if (!res.ok()) throw new Error(`stats API HTTP ${res.status()}`);
      const json = await res.json();
      const data = json.data || {};
      for (const s of data.note_stats || []) {
        out.articles.push({
          title: s.name || null,
          key: s.key || null,
          url: s.key && s.user && s.user.urlname ? `https://note.com/${s.user.urlname}/n/${s.key}` : null,
          views: toInt(s.read_count),
          likes: toInt(s.like_count),
          comments: toInt(s.comment_count),
        });
      }
      if (data.last_page !== false || !(data.note_stats || []).length) break;
    }
    out.ok = true; out.source = "note stats api";
  } catch (e) {
    out.error = `stats API読み取り失敗: ${e.message}`;
    // フォールバック: ダッシュボード画面の文字をそのまま保存(Claudeが読み取る)
    try {
      await page.goto("https://note.com/sitesettings/stats", { waitUntil: "domcontentloaded" });
      await page.waitForTimeout(3000);
      out.raw_text = await pageText(page);
      out.source = "note stats page (raw_text)";
    } catch (e2) { out.error += ` / 画面取得も失敗: ${e2.message}`; }
  }
  return out;
}

// 記事リンク(entry-数字.html)を含む行から、タイトル・数値を読み取る汎用パーサ
async function extractAmebaRows(page) {
  return page.evaluate(() => {
    const rows = [];
    const seen = new Set();
    for (const a of document.querySelectorAll('a[href*="entry-"]')) {
      const m = a.href.match(/entry-(\d+)\.html/);
      if (!m || seen.has(m[1])) continue;
      const row = a.closest("tr, li, article, [class*=item], [class*=Item]") || a.parentElement;
      const text = (row ? row.innerText : a.innerText) || "";
      const title = (a.innerText || "").trim();
      if (!title) continue;
      seen.add(m[1]);
      const pick = (re) => { const mm = text.match(re); return mm ? mm[1] : null; };
      rows.push({
        entry_id: m[1],
        url: a.href,
        title,
        likes: pick(/いいね[!！]?\s*[(（]?\s*([\d,]+)/),
        comments: pick(/コメント\s*[(（]?\s*([\d,]+)/),
        views: pick(/([\d,]+)\s*(?:PV|アクセス|閲覧)/),
        row_text: text.slice(0, 300),
      });
    }
    return rows;
  });
}

async function collectAmeba(page) {
  const out = { ok: false, source: null, articles: [], error: null, raw_text: null };
  if (!hasAmebaCreds()) { out.error = "AMEBA_ID/AMEBA_PASSWORD/AMEBA_BLOG_IDが未設定のためスキップ"; return out; }
  const blogId = process.env.AMEBA_BLOG_ID;
  const byId = new Map();
  const merge = (rows, source) => {
    for (const r of rows) {
      const cur = byId.get(r.entry_id) || { entry_id: r.entry_id, url: r.url, title: r.title, views: null, likes: null, comments: null };
      for (const k of ["views", "likes", "comments"]) if (cur[k] === null && toInt(r[k]) !== null) cur[k] = toInt(r[k]);
      byId.set(r.entry_id, cur);
    }
    if (rows.length) out.source = out.source ? `${out.source} + ${source}` : source;
  };
  try {
    await loginAmeba(page);
    // アクセス解析画面(記事別アクセス数)。URLは変わりやすいので候補を順に試す
    const analysisUrls = [
      "https://blog.ameba.jp/ucs/analysis/analysis_entry.do",
      "https://blog.ameba.jp/ucs/analysis/analysis_page.do",
      "https://blog.ameba.jp/ucs/analysis/",
    ];
    for (const url of analysisUrls) {
      const res = await page.goto(url, { waitUntil: "domcontentloaded" }).catch(() => null);
      if (!res || !res.ok() || /login/.test(page.url())) continue;
      await page.waitForTimeout(2500);
      const rows = await extractAmebaRows(page);
      out.raw_text = await pageText(page);
      merge(rows, `analysis page (${url})`);
      break;
    }
    // 公開の記事一覧(タイトル・URL・いいね/コメント数)
    await page.goto(`https://ameblo.jp/${blogId}/entrylist.html`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(2000);
    merge(await extractAmebaRows(page), "entrylist");
    out.articles = [...byId.values()];
    out.ok = out.articles.length > 0;
    if (!out.ok) out.error = "記事を1件も読み取れませんでした(raw_textを確認してください)";
  } catch (e) {
    out.error = e.message;
    out.articles = [...byId.values()];
  }
  return out;
}

async function main() {
  if (!hasNoteCreds() && !hasAmebaCreds()) {
    console.log("note/Amebaのログイン情報(secrets)が未設定のため、インサイト収集をスキップします。");
    return;
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const today = new Date().toLocaleDateString("sv-SE", { timeZone: "Asia/Tokyo" });
  const result = { collected_at: new Date().toISOString(), note: null, ameba: null };

  const browser = await chromium.launch(launchOptions());
  try {
    for (const [key, fn] of [["note", collectNote], ["ameba", collectAmeba]]) {
      const context = await browser.newContext();
      const page = await context.newPage();
      result[key] = await fn(page);
      await context.close();
      const r = result[key];
      console.log(`${key}: ${r.ok ? "取得成功" : "取得できず"} - 記事${r.articles.length}件${r.error ? " / " + r.error : ""}`);
    }
  } finally {
    await browser.close();
  }

  const outPath = path.join(OUT_DIR, `${today}.json`);
  fs.writeFileSync(outPath, JSON.stringify(result, null, 2) + "\n", "utf8");
  console.log("保存しました:", path.relative(ROOT, outPath));
}

module.exports = { toInt };

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}
