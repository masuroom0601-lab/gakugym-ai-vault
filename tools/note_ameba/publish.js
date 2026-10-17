#!/usr/bin/env node
/*
 * 学ジム note/Ameba担当: 承認済みドラフトをブラウザ自動操作で投稿する。
 *
 * note.com・Amebaブログには投稿用の公式APIが無いため、Playwrightで実際の
 * ログイン画面・投稿画面を操作して代行する(2026-10-17新設)。
 *
 * 2026-10-17追加: 投稿のたびに select.js で「最適なハッシュタグ」と「見出し画像の背景写真」を選び、
 * header-image.js で見出し画像(1280x670)を生成して、記事と一緒に設定する。
 *   - 選定は記事内容・下書き時のAI提案・過去実績(週次インサイト分析)に基づく決定的ロジック
 *   - 画像・ハッシュタグの設定に失敗しても記事の投稿自体は続行する
 *     (失敗内容は frontmatter の publish_warnings に残す)
 *   - 実際に使ったタグ・画像は frontmatter(note_hashtags / ameba_hashtags / image_source)に
 *     記録し、翌週以降の分析(analyze.js)で効果を測る
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
 *
 * 投稿せずに選定結果と見出し画像だけ確認したい場合:
 *   PUBLISH_DRY_RUN=1 node publish.js
 *   (status: approved に限らず drafts/ の全記事について、選ばれるタグ・画像を表示し、
 *    02_departments/note_ameba/images/ に見出し画像を生成する。ファイルの書き換え・投稿はしない)
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const { parseFile, writeFile } = require("./lib/frontmatter");
const { hasNoteCreds, hasAmebaCreds, loginNote, loginAmeba } = require("./lib/auth");
const { saveFailureScreenshot } = require("./lib/screenshot");
const { selectAll, loadContext, ROOT } = require("./select");
const { renderHeader, launchOptions } = require("./header-image");

const DRAFTS_DIR = path.join(ROOT, "02_departments", "note_ameba", "drafts");
const PUBLISHED_DIR = path.join(ROOT, "02_departments", "note_ameba", "published");
const IMAGES_DIR = path.join(ROOT, "02_departments", "note_ameba", "images");
const DRY_RUN = process.env.PUBLISH_DRY_RUN === "1";

// note.comのエディタはリッチテキストなので、Markdownの見出し記号(##)・強調(**)を
// 簡易的に取り除いたプレーンテキストとして段落ごとに貼り付ける(装飾は失われる前提)。
function toPlainParagraphs(md) {
  return md
    .replace(/<!--[\s\S]*?-->/g, "") // 内部メモ用のHTMLコメントは投稿しない
    .split(/\n\s*\n/)
    .map((p) => p.replace(/^#{1,6}\s*/gm, "").replace(/\*\*(.+?)\*\*/g, "$1").trim())
    .filter(Boolean);
}

// ボタン等をクリックしてファイル選択ダイアログを開き、画像を渡す。
// ダイアログが出ない場合は、ページ内の input[type=file] に直接渡す。
async function uploadViaChooser(page, triggers, filePath) {
  for (const sel of triggers) {
    const el = page.locator(sel).first();
    if (!(await el.count().catch(() => 0))) continue;
    try {
      const [chooser] = await Promise.all([
        page.waitForEvent("filechooser", { timeout: 5000 }),
        el.click({ timeout: 5000 }),
      ]);
      await chooser.setFiles(filePath);
      return true;
    } catch { /* 次の候補へ */ }
  }
  const input = page.locator('input[type="file"]').first();
  if (await input.count().catch(() => 0)) {
    await input.setInputFiles(filePath);
    return true;
  }
  return false;
}

async function clickIfPresent(page, names, wait = 1500) {
  for (const name of names) {
    const btn = page.getByRole("button", { name }).first();
    if (await btn.count().catch(() => 0)) {
      await btn.click({ timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(wait);
      return true;
    }
  }
  return false;
}

// ハッシュタグ入力欄に1つずつ入力してEnterで確定する
async function typeHashtags(page, selectors, tags) {
  for (const sel of selectors) {
    const box = page.locator(sel).first();
    if (!(await box.count().catch(() => 0))) continue;
    for (const tag of tags) {
      await box.click({ timeout: 5000 });
      await box.fill(tag).catch(async () => { await page.keyboard.type(tag); });
      await page.keyboard.press("Enter");
      await page.waitForTimeout(400);
    }
    return true;
  }
  return false;
}

async function publishToNote(page, { title, body, headerPath, hashtags }) {
  if (!hasNoteCreds()) return { skipped: true, reason: "NOTE_EMAIL/NOTE_PASSWORDが未設定" };
  const warnings = [];
  await loginNote(page);

  await page.goto("https://note.com/notes/new", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2000);

  // 見出し画像(タイトル上の「画像を追加」)。失敗しても本文の投稿は続ける
  let imageOk = false;
  if (headerPath) {
    try {
      imageOk = await uploadViaChooser(page, [
        'button[aria-label*="見出し画像"]', 'button[aria-label*="画像を追加"]',
        'button:has-text("見出し画像")', '[class*="eyecatch"] button', '[class*="Eyecatch"] button',
      ], headerPath);
      if (imageOk) {
        await page.waitForTimeout(2500);
        await clickIfPresent(page, ["保存", "適用", "完了"]); // トリミング確認ダイアログ
      } else warnings.push("note: 見出し画像のアップロード欄が見つかりませんでした");
    } catch (e) { imageOk = false; warnings.push(`note: 見出し画像の設定に失敗(${e.message})`); }
  }

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
  for (const para of toPlainParagraphs(body)) {
    await page.keyboard.type(para);
    await page.keyboard.press("Enter");
    await page.keyboard.press("Enter");
  }

  // 「公開に進む」→(公開設定画面でハッシュタグ入力)→「投稿する」の2段階
  const proceeded = await clickIfPresent(page, ["公開に進む"], 2500);
  let tagsOk = false;
  if (hashtags.length) {
    tagsOk = await typeHashtags(page, [
      'input[placeholder*="ハッシュタグ"]', 'input[aria-label*="ハッシュタグ"]', 'input[placeholder*="タグ"]',
    ], hashtags).catch((e) => { warnings.push(`note: ハッシュタグ入力でエラー(${e.message})`); return false; });
    if (!tagsOk && !warnings.some((w) => w.includes("ハッシュタグ"))) warnings.push("note: ハッシュタグ入力欄が見つかりませんでした");
  }
  const clickedFinal = await clickIfPresent(page, ["投稿する", "公開する"], 3000);
  if (!proceeded && !clickedFinal) {
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
  if (warnings.length) await saveFailureScreenshot(page, "note-media-warning");
  return { skipped: false, url, imageOk, tagsOk, warnings };
}

async function publishToAmeba(page, { title, body, headerPath, hashtags }) {
  if (!hasAmebaCreds()) return { skipped: true, reason: "AMEBA_ID/AMEBA_PASSWORD/AMEBA_BLOG_IDが未設定" };
  const warnings = [];
  await loginAmeba(page);

  await page.goto(`https://ameblo.jp/${process.env.AMEBA_BLOG_ID}/entry-edit.html`, { waitUntil: "domcontentloaded" });
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

  // Amebaは本文の先頭画像が記事のサムネイルになるため、本文より先に見出し画像を挿入する
  let imageOk = false;
  if (headerPath) {
    try {
      imageOk = await uploadViaChooser(page, [
        'button[aria-label*="画像"]', 'button:has-text("画像")', '[title*="画像"]',
      ], headerPath);
      if (imageOk) {
        await page.waitForTimeout(3000);
        await clickIfPresent(page, ["挿入", "貼り付け", "決定"]); // 画像挿入モーダル
        await bodyBox.click({ timeout: 5000 }).catch(() => {});
        await page.keyboard.press("Control+End").catch(() => {});
        await page.keyboard.press("Enter");
      } else warnings.push("Ameba: 画像のアップロード欄が見つかりませんでした");
    } catch (e) { imageOk = false; warnings.push(`Ameba: 画像の挿入に失敗(${e.message})`); }
  }

  for (const para of toPlainParagraphs(body)) {
    await page.keyboard.type(para);
    await page.keyboard.press("Enter");
    await page.keyboard.press("Enter");
  }

  let tagsOk = false;
  if (hashtags.length) {
    tagsOk = await typeHashtags(page, [
      'input[placeholder*="ハッシュタグ"]', 'input[aria-label*="ハッシュタグ"]', 'input[name*="hashtag"]',
    ], hashtags).catch((e) => { warnings.push(`Ameba: ハッシュタグ入力でエラー(${e.message})`); return false; });
    if (!tagsOk && !warnings.some((w) => w.includes("ハッシュタグ"))) warnings.push("Ameba: ハッシュタグ入力欄が見つかりませんでした");
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
  if (warnings.length) await saveFailureScreenshot(page, "ameba-media-warning");
  return { skipped: false, url, imageOk, tagsOk, warnings };
}

// 記事ごとに画像・ハッシュタグを選び、見出し画像を生成する
async function prepareMedia(file, parsed, ctx, browser) {
  const sel = selectAll(parsed, ctx);
  let headerPath = null, imageSource = null;
  if (sel.image.fixed) {
    headerPath = path.resolve(ROOT, sel.image.fixed);
    imageSource = sel.image.fixed;
    if (!fs.existsSync(headerPath)) { headerPath = null; imageSource = null; }
  } else {
    headerPath = path.join(IMAGES_DIR, file.replace(/\.md$/, ".png"));
    try {
      await renderHeader({ title: parsed.title, subject: parsed.front.subject, photo: sel.image.photo, label: parsed.front.header_label }, headerPath, browser);
      imageSource = sel.image.photo || "template";
    } catch (e) {
      console.error("見出し画像の生成に失敗(画像なしで投稿を続行):", e.message);
      headerPath = null;
    }
  }
  console.log(`  ハッシュタグ(note) : ${sel.hashtags.note.tags.map((t) => "#" + t).join(" ") || "(なし)"}`);
  console.log(`  ハッシュタグ(Ameba): ${sel.hashtags.ameba.tags.map((t) => "#" + t).join(" ") || "(なし)"}`);
  console.log(`  見出し画像         : ${headerPath ? path.relative(ROOT, headerPath) : "(なし)"} / 背景: ${imageSource || "-"}(${sel.image.reason})`);
  return { sel, headerPath, imageSource };
}

async function main() {
  if (!fs.existsSync(DRAFTS_DIR)) { console.log("drafts/が存在しません"); return; }
  fs.mkdirSync(PUBLISHED_DIR, { recursive: true });

  const files = fs.readdirSync(DRAFTS_DIR).filter((f) => f.endsWith(".md")).sort();
  const targets = files.map((f) => ({ file: f, parsed: parseFile(path.join(DRAFTS_DIR, f)) }))
    .filter((t) => t.parsed && (DRY_RUN || t.parsed.front.status === "approved"));
  if (!targets.length) { console.log("投稿対象(status: approved)の下書きはありません"); return; }

  const ctx = loadContext();
  const browser = await chromium.launch({ headless: true, ...launchOptions() });

  for (const { file, parsed } of targets) {
    const filePath = path.join(DRAFTS_DIR, file);
    const { front, body, title } = parsed;
    console.log(`--- ${file} (status: ${front.status}) を処理します ---`);
    const media = await prepareMedia(file, parsed, ctx, browser);
    if (DRY_RUN) continue;

    const context = await browser.newContext();
    const page = await context.newPage();
    const errors = [], warnings = [];
    const record = (platform, r, tags) => {
      warnings.push(...(r.warnings || []));
      if (r.tagsOk) front[`${platform}_hashtags`] = tags; // 実際に設定できたタグだけを分析対象として記録
      if (r.imageOk) front.image_source = media.imageSource;
    };

    if (!front.note_published) {
      try {
        const tags = media.sel.hashtags.note.tags;
        const r = await publishToNote(page, { title, body, headerPath: media.headerPath, hashtags: tags });
        if (r.skipped) { console.log("note: スキップ -", r.reason); }
        else { front.note_published = true; front.note_url = r.url; record("note", r, tags); console.log("note: 投稿成功 -", r.url); }
      } catch (e) {
        errors.push(`note: ${e.message}`);
        console.error("note: 失敗 -", e.message);
      }
    }

    if (!front.ameba_published) {
      try {
        const tags = media.sel.hashtags.ameba.tags;
        const r = await publishToAmeba(page, { title, body, headerPath: media.headerPath, hashtags: tags });
        if (r.skipped) { console.log("Ameba: スキップ -", r.reason); }
        else { front.ameba_published = true; front.ameba_url = r.url; record("ameba", r, tags); console.log("Ameba: 投稿成功 -", r.url); }
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

    if (errors.length) front.publish_error = `${new Date().toISOString()}: ${errors.join(" / ")}`;
    else delete front.publish_error;
    if (warnings.length) {
      front.publish_warnings = warnings;
      warnings.forEach((w) => console.warn("警告:", w));
    }

    if (noteDone && amebaDone && (wantsNote || wantsAmeba)) {
      front.status = "published";
      front.published_at = new Date().toISOString().slice(0, 10);
      writeFile(path.join(PUBLISHED_DIR, file), front, title, body);
      fs.unlinkSync(filePath);
      console.log(`${file}: 全プラットフォームへの投稿が完了したためpublished/へ移動しました`);
    } else {
      writeFile(filePath, front, title, body);
      console.log(`${file}: 未完了のプラットフォームが残っているため drafts/ にstatus: approvedのまま残します`);
    }
  }

  await browser.close();
}

module.exports = { toPlainParagraphs };

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}
