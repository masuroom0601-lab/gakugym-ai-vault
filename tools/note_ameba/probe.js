#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 画面構成の診断(2026-10-17新設)。**投稿・保存は一切しない**。
 * ログインして、note/Amebaの投稿画面・統計APIの「形」(入力欄・ボタン・JSONのキー)をログに出す。
 * サイト側のUI変更で自動投稿が失敗したとき、セレクタを直すための調査用。
 * 実行: .github/workflows/note-ameba-probe.yml(手動実行のみ)
 */
const { chromium } = require("playwright");
const { hasNoteCreds, hasAmebaCreds, loginNote, loginAmeba } = require("./lib/auth");
const { newSessionContext } = require("./lib/session");
const { dumpPageStructure } = require("./lib/screenshot");
const { launchOptions } = require("./header-image");

// JSONの中身(値)ではなく構造(キーと型)だけを出す
function shape(v, depth = 0) {
  if (Array.isArray(v)) return v.length ? [`len=${v.length}`, shape(v[0], depth + 1)] : [];
  if (v && typeof v === "object") {
    if (depth > 3) return "{…}";
    return Object.fromEntries(Object.entries(v).slice(0, 40).map(([k, x]) => [k, shape(x, depth + 1)]));
  }
  return typeof v;
}

async function probeApi(page, url) {
  try {
    const res = await page.request.get(url);
    let body = null;
    try { body = shape(await res.json()); } catch { body = "(JSONではない)"; }
    console.log(`[API] ${url} -> HTTP ${res.status()} ${JSON.stringify(body)}`);
  } catch (e) { console.log(`[API] ${url} -> 失敗 ${e.message}`); }
}

async function probeNote(browser) {
  if (!hasNoteCreds()) return console.log("note: secrets未設定");
  const page = await (await newSessionContext(browser)).newPage();
  try {
    await loginNote(page);
    console.log("note: ログイン成功 URL=" + page.url());
    await probeApi(page, "https://note.com/api/v2/current_user");
    await probeApi(page, "https://note.com/api/v1/stats/pv?filter=all&page=1&sort=pv");
    await probeApi(page, "https://note.com/api/v1/stats/pv?filter=weekly&page=1&sort=pv");
    // プロフィールへのリンクからユーザー名(urlname)を推定する
    const links = await page.evaluate(() => [...document.querySelectorAll("a[href]")].map((a) => a.getAttribute("href"))
      .filter((h) => /^\/[A-Za-z0-9_]+\/?$/.test(h || "")).slice(0, 20));
    console.log("note: トップページの /<名前> 形式リンク: " + JSON.stringify(links));
    await page.goto("https://note.com/notes/new", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(6000);
    await dumpPageStructure(page, "note-editor-6s");
    await page.waitForTimeout(6000);
    await dumpPageStructure(page, "note-editor-12s");
  } catch (e) {
    console.log("note: " + e.message);
  }
}

async function probeAmeba(browser) {
  if (!hasAmebaCreds()) return console.log("Ameba: secrets未設定");
  const page = await (await newSessionContext(browser)).newPage();
  try {
    await page.goto("https://www.ameba.jp/login.html", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(4000);
    await dumpPageStructure(page, "ameba-login-step1");
    await loginAmeba(page);
    console.log("Ameba: ログイン成功 URL=" + page.url());
    await page.goto("https://blog.ameba.jp/ucs/entry/srventryinsertinput.do", { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(6000);
    await dumpPageStructure(page, "ameba-editor");
  } catch (e) {
    console.log("Ameba: " + e.message);
  }
}

(async () => {
  const browser = await chromium.launch(launchOptions());
  try {
    await probeNote(browser);
    await probeAmeba(browser);
  } finally {
    await browser.close();
  }
})().catch((e) => { console.error(e); process.exit(1); });
