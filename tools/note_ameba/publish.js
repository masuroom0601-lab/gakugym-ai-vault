#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 承認済みドラフトをブラウザ自動操作で投稿する。
 *
 * note.com・Amebaブログには投稿用の公式APIが無いため、Playwrightで実際の
 * ログイン画面・投稿画面を操作して代行する(2026-10-17新設)。
 *
 * ##【重要】初回は必ず人の監視下で動かすこと
 * note.com/Amebaとも非公式のブラウザ操作であり、以下の理由で壊れる可能性が高い:
 *   - サイト側のUI変更でセレクタが合わなくなる
 *   - ログイン時にCAPTCHA・2段階認証が表示されると自動突破できず失敗する
 *   - note.comのエディタはリッチテキスト(ProseMirror等)のため、Markdownの
 *     見出し(##)・太字(**)が完全な書式として反映されない可能性がある
 *     (本スクリプトは見出し行を改行+テキストとして貼り付けるのみで、
 *     装飾の再現は保証しない。体裁の最終確認は益田さんにお願いする)
 * 失敗しても下書きファイルは消えず、status: approved のまま残るので、
 * いつでも手動投稿にフォールバックできる(自動投稿前提で下書きを消す設計にはしていない)。
 *
 * 承認フロー(department.md参照):
 *   drafts(status: review)→ 益田さんが最終確認・編集してstatus: approved に変更
 *   → このスクリプトが自動投稿 → 成功したら status: published にして published/ へ移動
 *
 * 必要な環境変数(GitHub Actions secrets):
 *   NOTE_EMAIL / NOTE_PASSWORD        … note.comのログイン情報
 *   AMEBA_ID / AMEBA_PASSWORD         … AmebaIDのログイン情報
 *   AMEBA_BLOG_ID                     … ameblo.jp/<ここ> のブログID
 * いずれかが未設定の場合、該当プラットフォームへの投稿はスキップする
 * (両方未設定なら何もせず終了する。段階的に導入できるようにしている)。
 */
const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");
const { chromium } = require("playwright");

const HERE = __dirname;
const DRAFTS_DIR = path.join(HERE, "..", "..", "02_departments", "note_ameba", "drafts");
const PUBLISHED_DIR = path.join(HERE, "..", "..", "02_departments", "note_ameba", "published");
const SCREENSHOT_DIR = path.join(HERE, "failure-screenshots");

async function saveFailureScreenshot(page, label) {
  try {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    const p = path.join(SCREENSHOT_DIR, `${label}-${Date.now()}.png`);
    await page.screenshot({ path: p, fullPage: true });
    console.log(`失敗時のスクリーンショットを保存しました: ${p}(ワークフローのartifactとして確認可能)`);
  } catch (e) {
    console.log("スクリーンショット保存にも失敗:", e.message);
  }
}

function parseFile(filePath) {
  const raw = fs.readFileSync(filePath, "utf8");
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) return null;
  const front = yaml.load(m[1]) || {};
  const body = m[2];
  const titleMatch = body.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : (front.subject || "学ジム");
  const contentWithoutTitle = titleMatch ? body.replace(titleMatch[0], "").trim() : body.trim();
  return { front, body: contentWithoutTitle, title, raw, frontRaw: m[1] };
}

function writeFile(filePath, front, body) {
  const frontStr = yaml.dump(front, { lineWidth: -1 }).trimEnd();
  fs.writeFileSync(filePath, `---\n${frontStr}\n---\n\n${body}\n`, "utf8");
}

// note.comのエディタはリッチテキストなので、Markdownの見出し記号(##)・強調(**)を
// 簡易的に取り除いたプレーンテキストとして段落ごとに貼り付ける(装飾は失われる前提)。
function toPlainParagraphs(md) {
  return md
    .split(/\n\s*\n/)
    .map((p) => p.replace(/^#{1,6}\s*/gm, "").replace(/\*\*(.+?)\*\*/g, "$1").trim())
    .filter(Boolean);
}

async function publishToNote(page, title, bodyMd) {
  const email = process.env.NOTE_EMAIL, password = process.env.NOTE_PASSWORD;
  if (!email || !password) return { skipped: true, reason: "NOTE_EMAIL/NOTE_PASSWORDが未設定" };

  await page.goto("https://note.com/login", { waitUntil: "domcontentloaded" });
  const emailBox = page.locator('input[name="login_email"], input[type="email"]').first();
  if (!(await emailBox.count())) {
    await saveFailureScreenshot(page, "note-login-no-email-field");
    throw new Error("note.comログイン画面でメールアドレス入力欄が見つかりませんでした(UI変更の可能性)。");
  }
  await emailBox.fill(email);
  const passBox = page.locator('input[name="password"], input[type="password"]').first();
  await passBox.fill(password);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);

  const captcha = await page.locator('iframe[src*="recaptcha"], text=認証').count().catch(() => 0);
  if (captcha > 0) {
    await saveFailureScreenshot(page, "note-login-captcha");
    throw new Error("note.comログイン時にCAPTCHA/認証画面が検出されました。自動投稿を中断します(手動投稿にフォールバックしてください)。");
  }
  if (page.url().includes("/login")) {
    await saveFailureScreenshot(page, "note-login-failed");
    throw new Error("note.comへのログインに失敗しました(URL確認: " + page.url() + ")。パスワード・メールアドレスを確認してください。");
  }

  await page.goto("https://note.com/notes/new", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2000);

  const titleBox = page.locator('textarea[placeholder*="タイトル"], [contenteditable][aria-label*="タイトル"]').first();
  if (!(await titleBox.count())) {
    await saveFailureScreenshot(page, "note-editor-no-title-field");
    throw new Error("note.comの新規投稿画面でタイトル欄が見つかりませんでした(UI変更の可能性)。");
  }
  await titleBox.click({ timeout: 10000 });
  await titleBox.fill(title).catch(async () => { await page.keyboard.type(title); });

  await page.keyboard.press("Tab");
  const bodyBox = page.locator('[contenteditable="true"]').last();
  await bodyBox.click({ timeout: 10000 });
  for (const para of toPlainParagraphs(bodyMd)) {
    await page.keyboard.type(para);
    await page.keyboard.press("Enter");
    await page.keyboard.press("Enter");
  }

  // 「公開に進む」→「投稿する」のような2段階公開フローが一般的なため、それらしいボタンを順に試す
  const publishButtons = ["公開に進む", "投稿する", "公開する"];
  let clickedAny = false;
  for (const label of publishButtons) {
    const btn = page.getByRole("button", { name: label }).first();
    if (await btn.count()) {
      await btn.click({ timeout: 10000 });
      clickedAny = true;
      await page.waitForTimeout(2000);
    }
  }
  if (!clickedAny) {
    await saveFailureScreenshot(page, "note-no-publish-button");
    throw new Error("note.comで「公開する」系のボタンが見つからず、クリックできませんでした(UI変更の可能性。本文は入力済みの可能性があるため要確認)。");
  }

  await page.waitForTimeout(2000);
  const url = page.url();
  // 公開後のnote.com記事URLは note.com/<ユーザー名>/n/<記事ID> の形になる。
  // それ以外(エディタ画面のままなど)は「クリックはしたが実際には公開されていない」可能性が高いため失敗扱いにする。
  if (!/note\.com\/[^/]+\/n\/[a-z0-9]+/i.test(url)) {
    await saveFailureScreenshot(page, "note-publish-not-confirmed");
    throw new Error(`note.comで公開ボタンはクリックしましたが、公開後の記事URLに遷移しませんでした(現在のURL: ${url})。実際に公開されたか手動で確認してください。`);
  }

  return { skipped: false, url };
}

async function publishToAmeba(page, title, bodyMd) {
  const id = process.env.AMEBA_ID, password = process.env.AMEBA_PASSWORD, blogId = process.env.AMEBA_BLOG_ID;
  if (!id || !password || !blogId) return { skipped: true, reason: "AMEBA_ID/AMEBA_PASSWORD/AMEBA_BLOG_IDが未設定" };

  await page.goto("https://www.ameba.jp/login.html", { waitUntil: "domcontentloaded" });
  const idBox = page.locator('input[name="accountId"], input[type="text"]').first();
  if (!(await idBox.count())) {
    await saveFailureScreenshot(page, "ameba-login-no-id-field");
    throw new Error("AmebaIDログイン画面でID入力欄が見つかりませんでした(UI変更の可能性)。");
  }
  await idBox.fill(id);
  const passBox = page.locator('input[name="password"], input[type="password"]').first();
  await passBox.fill(password);
  await page.click('button[type="submit"], input[type="submit"]');
  await page.waitForTimeout(3000);

  const captcha = await page.locator('iframe[src*="recaptcha"], text=認証').count().catch(() => 0);
  if (captcha > 0) {
    await saveFailureScreenshot(page, "ameba-login-captcha");
    throw new Error("AmebaIDログイン時にCAPTCHA/認証画面が検出されました。自動投稿を中断します(手動投稿にフォールバックしてください)。");
  }
  if (page.url().includes("login")) {
    await saveFailureScreenshot(page, "ameba-login-failed");
    throw new Error("AmebaIDへのログインに失敗しました(URL確認: " + page.url() + ")。ID・パスワードを確認してください。");
  }

  await page.goto(`https://ameblo.jp/${blogId}/entry-edit.html`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2000);

  const titleBox = page.locator('input[placeholder*="タイトル"], input[name*="title"]').first();
  if (!(await titleBox.count())) {
    await saveFailureScreenshot(page, "ameba-editor-no-title-field");
    throw new Error("Amebaの新規投稿画面でタイトル欄が見つかりませんでした(UI変更の可能性)。");
  }
  await titleBox.click({ timeout: 10000 });
  await titleBox.fill(title).catch(async () => { await page.keyboard.type(title); });

  const bodyBox = page.locator('[contenteditable="true"], textarea[name*="body"]').first();
  if (!(await bodyBox.count())) {
    await saveFailureScreenshot(page, "ameba-editor-no-body-field");
    throw new Error("Amebaの新規投稿画面で本文欄が見つかりませんでした(UI変更の可能性)。");
  }
  await bodyBox.click({ timeout: 10000 });
  for (const para of toPlainParagraphs(bodyMd)) {
    await page.keyboard.type(para);
    await page.keyboard.press("Enter");
    await page.keyboard.press("Enter");
  }

  const publishBtn = page.getByRole("button", { name: /公開する|投稿する/ }).first();
  if (!(await publishBtn.count())) {
    await saveFailureScreenshot(page, "ameba-no-publish-button");
    throw new Error("Amebaで「公開する」系のボタンが見つからず、クリックできませんでした(UI変更の可能性。本文は入力済みの可能性があるため要確認)。");
  }
  await publishBtn.click({ timeout: 10000 });
  await page.waitForTimeout(3000);

  const url = page.url();
  // 公開後のAmeba記事URLは ameblo.jp/<ブログID>/entry-<ID>.html の形になる。
  // entry-edit.htmlのままの場合は「クリックはしたが実際には公開されていない」可能性が高いため失敗扱いにする。
  if (!/ameblo\.jp\/[^/]+\/entry-\d+/i.test(url)) {
    await saveFailureScreenshot(page, "ameba-publish-not-confirmed");
    throw new Error(`Amebaで公開ボタンはクリックしましたが、公開後の記事URLに遷移しませんでした(現在のURL: ${url})。実際に公開されたか手動で確認してください。`);
  }

  return { skipped: false, url };
}

async function main() {
  if (!fs.existsSync(DRAFTS_DIR)) { console.log("drafts/が存在しません"); return; }
  fs.mkdirSync(PUBLISHED_DIR, { recursive: true });

  const files = fs.readdirSync(DRAFTS_DIR).filter((f) => f.endsWith(".md"));
  const browser = await chromium.launch({ headless: true });

  for (const file of files) {
    const filePath = path.join(DRAFTS_DIR, file);
    const parsed = parseFile(filePath);
    if (!parsed) continue;
    const { front, body, title } = parsed;
    if (front.status !== "approved") continue;

    console.log(`--- ${file} (status: approved) を処理します ---`);
    const context = await browser.newContext();
    const page = await context.newPage();
    const errors = [];

    if (!front.note_published) {
      try {
        const r = await publishToNote(page, title, body);
        if (r.skipped) { console.log("note: スキップ -", r.reason); }
        else { front.note_published = true; front.note_url = r.url; console.log("note: 投稿成功 -", r.url); }
      } catch (e) {
        errors.push(`note: ${e.message}`);
        console.error("note: 失敗 -", e.message);
      }
    }

    if (!front.ameba_published) {
      try {
        const r = await publishToAmeba(page, title, body);
        if (r.skipped) { console.log("Ameba: スキップ -", r.reason); }
        else { front.ameba_published = true; front.ameba_url = r.url; console.log("Ameba: 投稿成功 -", r.url); }
      } catch (e) {
        errors.push(`Ameba: ${e.message}`);
        console.error("Ameba: 失敗 -", e.message);
      }
    }

    await context.close();

    const platforms = Array.isArray(front.platform) ? front.platform : [];
    const wantsNote = platforms.some((p) => /note/i.test(p));
    const wantsAmeba = platforms.some((p) => /ameba/i.test(p));
    const noteDone = !wantsNote || front.note_published;
    const amebaDone = !wantsAmeba || front.ameba_published;

    if (errors.length) {
      front.publish_error = `${new Date().toISOString()}: ${errors.join(" / ")}`;
    } else {
      delete front.publish_error;
    }

    if (noteDone && amebaDone && (wantsNote || wantsAmeba)) {
      front.status = "published";
      front.published_at = new Date().toISOString().slice(0, 10);
      const destPath = path.join(PUBLISHED_DIR, file);
      writeFile(destPath, front, body ? `# ${title}\n\n${body}` : `# ${title}`);
      fs.unlinkSync(filePath);
      console.log(`${file}: 全プラットフォームへの投稿が完了したためpublished/へ移動しました`);
    } else {
      writeFile(filePath, front, body ? `# ${title}\n\n${body}` : `# ${title}`);
      console.log(`${file}: 未完了のプラットフォームが残っているため drafts/ にstatus: approvedのまま残します`);
    }
  }

  await browser.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
