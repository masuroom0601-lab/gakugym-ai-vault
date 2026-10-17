#!/usr/bin/env node
/*
 * 【益田さんのPCで実行するスクリプト】note/Amebaのログイン状態を保存する(2026-10-17新設、方式A)。
 *
 * 使い方(詳しくは 01_HQ/setup guides/note-ameba-auto-publish-setup.md):
 *   node save-session.js note    … noteのログイン状態を note-session.txt に保存
 *   node save-session.js ameba   … Amebaのログイン状態を ameba-session.txt に保存
 *
 * ブラウザが開くので、いつも通り手でログインしてください(ロボット判定も手で通せます)。
 * ログインできたら、このウィンドウ(ターミナル)に戻って Enter を押すと保存されます。
 * 保存されたファイルの中身を、GitHubのsecrets(NOTE_SESSION / AMEBA_SESSION)に貼り付けてください。
 *
 * 【注意】保存ファイルはログイン済みの状態そのものです(パスワードと同じくらい大切)。
 *   secretsに貼り付けたら、PCからファイルを削除してください。人に送らないでください。
 */
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const { chromium } = require("playwright");
const { filterState, encodeState } = require("./lib/session");

const SITES = {
  note: { login: "https://note.com/login", secret: "NOTE_SESSION",
    check: async (page) => (await page.request.get("https://note.com/api/v2/current_user")).status() === 200 },
  ameba: { login: "https://www.ameba.jp/", secret: "AMEBA_SESSION",
    check: async (page) => {
      await page.goto("https://blog.ameba.jp/ucs/top.do", { waitUntil: "domcontentloaded" }).catch(() => {});
      await page.waitForTimeout(2000);
      return /blog\.ameba\.jp\/ucs/.test(page.url());
    } },
};

const ask = (q) => new Promise((resolve) => {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  rl.question(q, (a) => { rl.close(); resolve(a); });
});

async function launch() {
  // Playwright付属のChromiumが無ければ、PCにインストール済みのGoogle Chromeを使う
  try { return await chromium.launch({ headless: false }); }
  catch { return chromium.launch({ headless: false, channel: "chrome" }); }
}

(async () => {
  const platform = (process.argv[2] || "").toLowerCase();
  const site = SITES[platform];
  if (!site) { console.log("使い方: node save-session.js note  または  node save-session.js ameba"); process.exit(1); }

  const browser = await launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(site.login);
  console.log(`\nブラウザで${platform === "note" ? "note" : "Ameba(右上の「ログイン」から)"}にログインしてください。`);
  await ask("ログインが終わったら、ここで Enter を押してください > ");

  if (!(await site.check(page).catch(() => false))) {
    console.log("\n⚠ ログイン状態を自動で確認できませんでした(サイトの仕様変更の可能性もあります)。");
    const yes = await ask("ブラウザで確かにログインできている場合は y を、やり直す場合は Enter を押してください > ");
    if (!/^y/i.test(yes.trim())) { await browser.close(); process.exit(1); }
  }

  const state = filterState(await context.storageState(), platform);
  const encoded = encodeState(state);
  const out = path.resolve(`${platform}-session.txt`);
  fs.writeFileSync(out, encoded, "utf8");
  await browser.close();

  console.log(`\n✅ 保存しました: ${out}(${Math.round(encoded.length / 1024)}KB)`);
  if (encoded.length > 48 * 1024) console.log("⚠ 48KBを超えているためGitHubのsecretsに入りません。このセッションに相談してください。");
  console.log(`このファイルをメモ帳等で開き、中身をすべてコピーして、GitHubのsecrets「${site.secret}」に貼り付けてください。`);
  console.log("貼り付けたら、このファイルは削除してください。");
})().catch((e) => { console.error(e); process.exit(1); });
