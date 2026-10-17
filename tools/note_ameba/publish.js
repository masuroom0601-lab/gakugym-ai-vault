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
const { newSessionContext } = require("./lib/session");
const { saveFailureScreenshot, dumpPageStructure } = require("./lib/screenshot");
const { selectAll, loadContext, ROOT } = require("./select");
const { renderHeader, launchOptions } = require("./header-image");

const DRAFTS_DIR = path.join(ROOT, "02_departments", "note_ameba", "drafts");
const PUBLISHED_DIR = path.join(ROOT, "02_departments", "note_ameba", "published");
const IMAGES_DIR = path.join(ROOT, "02_departments", "note_ameba", "images");
const DRY_RUN = process.env.PUBLISH_DRY_RUN === "1";
// リハーサル: 指定した下書き1本について、ログイン→入力→公開設定画面まで進め、
// 最後の「投稿する」だけ押さずに止める(画面構成をログに出す)。ファイルの書き換えもしない。
// 例: PUBLISH_REHEARSAL=task-2026-10-05-note-001.md node publish.js
// ※ noteは入力内容が自動で下書き保存されるため、リハーサル後にnote側の下書きを削除すること
const REHEARSAL = process.env.PUBLISH_REHEARSAL || "";

// note.comのエディタはリッチテキストなので、Markdownの見出し記号(##)・強調(**)を
// 簡易的に取り除いたプレーンテキストとして段落ごとに扱う(文字数チェック・貼り付け失敗時の手入力用)。
function toPlainParagraphs(md) {
  return md
    .replace(/<!--[\s\S]*?-->/g, "") // 内部メモ用のHTMLコメントは投稿しない
    .split(/\n\s*\n/)
    .map((p) => p.replace(/^#{1,6}\s*/gm, "").replace(/\*\*(.+?)\*\*/g, "$1").trim())
    .filter(Boolean);
}

const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const inline = (t) => esc(t).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

// 下書きのMarkdownを、エディタに貼り付けるための簡易HTMLに変換する(2026-10-17)。
// 見出し(##/###)・太字・箇条書き・引用・表(1行ずつの段落に変換)に対応。
// note/Amebaのエディタとも、貼り付けたHTMLの見出し・太字をそのまま書式として扱える。
function markdownToHtml(md) {
  const lines = md.replace(/<!--[\s\S]*?-->/g, "").split("\n");
  const out = [];
  let list = null, para = [];
  const flushPara = () => { if (para.length) { out.push(`<p>${para.map(inline).join("<br>")}</p>`); para = []; } };
  const flushList = () => { if (list) { out.push(`<ul>${list.map((i) => `<li>${inline(i)}</li>`).join("")}</ul>`); list = null; } };
  for (const raw of lines) {
    const line = raw.trimEnd();
    let m;
    if (!line.trim()) { flushPara(); flushList(); continue; }
    if ((m = line.match(/^(#{1,6})\s+(.*)$/))) {
      flushPara(); flushList();
      const level = m[1].length <= 2 ? 2 : 3; // noteは大見出し(h2)・小見出し(h3)の2段階
      out.push(`<h${level}>${inline(m[2])}</h${level}>`);
    } else if ((m = line.match(/^\s*[-*・]\s+(.*)$/)) || (m = line.match(/^\s*\d+[.)]\s+(.*)$/))) {
      flushPara(); (list = list || []).push(m[1]);
    } else if ((m = line.match(/^>\s?(.*)$/))) {
      flushPara(); flushList(); out.push(`<blockquote><p>${inline(m[1])}</p></blockquote>`);
    } else if (/^\s*\|/.test(line)) {
      flushPara(); flushList();
      if (/^\s*\|?\s*:?-{2,}/.test(line)) continue; // 表の区切り行
      const cells = line.split("|").map((c) => c.trim()).filter(Boolean);
      out.push(`<p>${cells.map(inline).join(" → ")}</p>`);
    } else {
      flushList(); para.push(line.trim());
    }
  }
  flushPara(); flushList();
  return out.join("\n");
}

// 投稿前チェック用: 本文の文字数(空白・記号の差は許容するため、比較は6割以上あればOKとする)
function expectedLength(md) {
  return toPlainParagraphs(md).join("").replace(/\s/g, "").length;
}

// ボタン等をクリックしてファイル選択ダイアログを開き、画像を渡す。
// ダイアログが出ない場合は、ページ内の input[type=file] に直接渡す。
async function uploadViaChooser(page, triggers, filePath, fileInputSelector = 'input[type="file"]') {
  for (const sel of triggers) {
    const el = page.locator(sel).first();
    if (!(await el.isVisible().catch(() => false))) continue;
    try {
      const [chooser] = await Promise.all([
        page.waitForEvent("filechooser", { timeout: 5000 }),
        el.click({ timeout: 5000 }),
      ]);
      await chooser.setFiles(filePath);
      return true;
    } catch { /* 次の候補へ */ }
  }
  const input = page.locator(fileInputSelector).first();
  if (await input.count().catch(() => 0)) {
    await input.setInputFiles(filePath);
    return true;
  }
  return false;
}

async function clickIfPresent(page, names, wait = 1500) {
  for (const name of names) {
    const btn = page.getByRole("button", { name, exact: true }).first();
    if (await btn.isVisible().catch(() => false)) {
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
    if (!(await box.isVisible().catch(() => false))) continue;
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

// 画面の「N 文字」「文字数: N」表示を読む(読めなければnull)
async function readCharCount(page, re) {
  const text = await page.evaluate(() => document.body.innerText).catch(() => "");
  const m = text.match(re);
  return m ? parseInt(m[1].replace(/,/g, ""), 10) : null;
}

function checkLength(platform, actual, expected, warnings) {
  if (actual === null) { warnings.push(`${platform}: 本文の文字数表示を読めませんでした(本文が入ったかは目視で確認してください)`); return; }
  if (actual < expected * 0.6) {
    throw new Error(`${platform}: 本文が正しく入力されていません(入力 ${actual}文字 / 想定 約${expected}文字)。投稿を中止しました(下書きとして残っている場合は削除してください)。`);
  }
}

// noteの見出し画像: タイトル欄より上にある、文字の無いアイコンボタン(画像追加)を押し、
// 出てきたメニューの「画像をアップロード」からファイルを渡す。トリミング画面が出たら「保存」。
async function setNoteEyecatch(page, titleBox, headerPath, rehearsal) {
  const titleTop = (await titleBox.boundingBox().catch(() => null))?.y ?? 400;
  const candidates = page.locator("button");
  const n = await candidates.count();
  for (let i = 0; i < n; i++) {
    const b = candidates.nth(i);
    const box = await b.boundingBox().catch(() => null);
    if (!box || box.y >= titleTop) continue;
    const text = ((await b.innerText().catch(() => "")) || "").trim();
    const label = (await b.getAttribute("aria-label").catch(() => "")) || "";
    if (text || /AI|目次|ヒント|ガイド|その他|閉じる/.test(label)) continue;
    // ボタンを押すと直接ファイル選択が開く場合と、メニューが出る場合の両方に対応する
    const chooserP = page.waitForEvent("filechooser", { timeout: 4000 }).catch(() => null);
    await b.click({ timeout: 3000 }).catch(() => {});
    let chooser = await chooserP;
    if (!chooser) {
      if (rehearsal) await dumpPageStructure(page, "note-eyecatch-menu(rehearsal)");
      const item = page.getByText(/画像をアップロード|アップロード/).first();
      if (await item.isVisible().catch(() => false)) {
        const p2 = page.waitForEvent("filechooser", { timeout: 5000 }).catch(() => null);
        await item.click().catch(() => {});
        chooser = await p2;
      }
    }
    if (!chooser) { await page.keyboard.press("Escape").catch(() => {}); continue; }
    await chooser.setFiles(headerPath);
    await page.waitForTimeout(4000);
    if (rehearsal) await dumpPageStructure(page, "note-eyecatch-crop(rehearsal)");
    await clickIfPresent(page, ["保存", "適用", "完了", "この画像を使う", "決定"], 3000);
    return true;
  }
  return false;
}

// Amebaのハッシュタグ: 「#」ボタンを押すと入力欄が開くので、1つずつ入力してEnter、最後に決定する
async function setAmebaHashtags(page, tags, rehearsal) {
  const opener = page.locator("#js-hashtag-button").first();
  if (!(await opener.isVisible().catch(() => false))) return false;
  await opener.click().catch(() => {});
  await page.waitForTimeout(1500);
  if (rehearsal) await dumpPageStructure(page, "ameba-hashtag-editor(rehearsal)");
  const input = page.locator('#js-hashtag-input, [class*="hashtag"] input[type="text"]').first();
  if (!(await input.isVisible().catch(() => false))) return false;
  for (const t of tags) {
    await input.fill(t);
    await page.keyboard.press("Enter");
    await page.waitForTimeout(500);
  }
  await clickIfPresent(page, ["OK", "決定", "完了", "設定する", "保存"], 1000);
  return true;
}

async function publishToNote(page, { title, body, headerPath, hashtags, rehearsal }) {
  if (!hasNoteCreds()) return { skipped: true, reason: "NOTEのログイン情報(NOTE_SESSION)が未設定" };
  const warnings = [];
  await loginNote(page);

  // notes/new は editor.note.com/notes/<記事キー>/edit/ に転送される(2026-10-17確認)
  await page.goto("https://note.com/notes/new", { waitUntil: "domcontentloaded" });
  const titleBox = page.locator('textarea[placeholder*="タイトル"]').first();
  await titleBox.waitFor({ state: "visible", timeout: 30000 }).catch(() => {});
  if (!(await titleBox.isVisible().catch(() => false))) {
    await saveFailureScreenshot(page, "note-editor-no-title-field");
    throw new Error("note.comの新規投稿画面でタイトル欄が見つかりませんでした(UI変更の可能性)。");
  }
  const noteKey = (page.url().match(/notes\/(n[a-z0-9]+)/i) || [])[1] || null;

  // 見出し画像(タイトル上の画像追加ボタン)。失敗しても本文の投稿は続ける
  let imageOk = false;
  if (headerPath) {
    try {
      imageOk = await setNoteEyecatch(page, titleBox, headerPath, rehearsal);
      if (!imageOk) warnings.push("note: 見出し画像のアップロード欄が見つかりませんでした");
    } catch (e) { imageOk = false; warnings.push(`note: 見出し画像の設定に失敗(${e.message})`); }
  }

  await titleBox.click({ timeout: 10000 });
  await titleBox.fill(title);

  // 本文: HTMLとして貼り付ける(見出し・太字を保つ)。貼り付けが効かなければ1段落ずつ手入力する
  const bodyBox = page.locator(".ProseMirror[contenteditable='true'], [role='textbox'][contenteditable='true']").first();
  await bodyBox.click({ timeout: 10000 });
  const html = markdownToHtml(body);
  await page.evaluate(({ html, text }) => {
    const el = document.querySelector(".ProseMirror[contenteditable='true']") || document.activeElement;
    el.focus();
    const dt = new DataTransfer();
    dt.setData("text/html", html);
    dt.setData("text/plain", text);
    el.dispatchEvent(new ClipboardEvent("paste", { clipboardData: dt, bubbles: true, cancelable: true }));
  }, { html, text: toPlainParagraphs(body).join("\n\n") });
  await page.waitForTimeout(2000);
  const expected = expectedLength(body);
  let count = await readCharCount(page, /([\d,]+)\s*文字/);
  if (count !== null && count < expected * 0.6) {
    warnings.push("note: 本文の貼り付けが効かなかったため、書式なしで手入力しました");
    await bodyBox.click();
    for (const para of toPlainParagraphs(body)) { await page.keyboard.type(para); await page.keyboard.press("Enter"); }
    count = await readCharCount(page, /([\d,]+)\s*文字/);
  }
  checkLength("note", count, expected, warnings);

  // 「公開に進む」→ 公開設定画面(ハッシュタグ入力)→「投稿する」
  // 見出し画像の保存直後などは押しても進まないことがあるため、公開設定画面(/publish/)に移るまで数回押し直す
  let proceeded = false;
  for (let i = 0; i < 6 && !proceeded; i++) {
    await clickIfPresent(page, ["公開に進む"], 3000);
    proceeded = /\/publish\/?/.test(page.url()) ||
      await page.locator('input[placeholder*="ハッシュタグ"]').first().isVisible().catch(() => false);
    if (!proceeded) await page.waitForTimeout(2000);
  }
  if (!proceeded) {
    await saveFailureScreenshot(page, "note-no-proceed-button");
    throw new Error("note.comで「公開に進む」を押しても公開設定画面に進めませんでした(UI変更の可能性。下書きとして残っている場合は削除してください)。");
  }
  let tagsOk = false;
  if (hashtags.length) {
    tagsOk = await typeHashtags(page, ['input[placeholder*="ハッシュタグ"]'], hashtags)
      .catch((e) => { warnings.push(`note: ハッシュタグ入力でエラー(${e.message})`); return false; });
    if (!tagsOk && !warnings.some((w) => w.includes("ハッシュタグ"))) warnings.push("note: ハッシュタグ入力欄が見つかりませんでした");
  }

  if (rehearsal) {
    await dumpPageStructure(page, "note-publish-settings(rehearsal)");
    return { skipped: false, rehearsal: true, url: page.url(), noteKey, imageOk, tagsOk, warnings, charCount: count, expected };
  }

  if (!(await clickIfPresent(page, ["投稿する", "公開する"], 4000))) {
    await saveFailureScreenshot(page, "note-no-publish-button");
    throw new Error("note.comの公開設定画面で「投稿する」ボタンが見つかりませんでした(UI変更の可能性。下書きとして残っている場合は確認してください)。");
  }

  // 公開できたかは、画面遷移ではなく記事情報(API)の status で確認する
  let url = null;
  for (let i = 0; i < 10 && noteKey; i++) {
    const res = await page.request.get(`https://note.com/api/v3/notes/${noteKey}`).catch(() => null);
    const d = res && res.ok() ? ((await res.json().catch(() => ({}))).data || {}) : {};
    if (d.status === "published") { url = d.note_url || d.noteUrl || page.url(); break; }
    await page.waitForTimeout(2000);
  }
  if (!url && /note\.com\/[^/]+\/n\/[a-z0-9]+/i.test(page.url())) url = page.url();
  if (!url) {
    await saveFailureScreenshot(page, "note-publish-not-confirmed");
    throw new Error(`note.comで「投稿する」を押しましたが、公開済みになったことを確認できませんでした(記事キー: ${noteKey}, URL: ${page.url()})。実際に公開されたか手動で確認してください。`);
  }
  if (warnings.length) await saveFailureScreenshot(page, "note-media-warning");
  return { skipped: false, url, imageOk, tagsOk, warnings };
}

async function publishToAmeba(page, { title, body, headerPath, hashtags, rehearsal }) {
  if (!hasAmebaCreds()) return { skipped: true, reason: "Amebaのログイン情報(AMEBA_SESSION)またはAMEBA_BLOG_IDが未設定" };
  const warnings = [];
  await loginAmeba(page);

  // 新規投稿画面(ameblo.jp/<ID>/entry-edit.html は404になる。2026-10-17確認)
  await page.goto("https://blog.ameba.jp/ucs/entry/srventryinsertinput.do", { waitUntil: "domcontentloaded" });
  const titleBox = page.locator('input[name="entry_title"], input[placeholder*="タイトル"]').first();
  await titleBox.waitFor({ state: "visible", timeout: 30000 }).catch(() => {});
  if (!(await titleBox.isVisible().catch(() => false))) {
    await saveFailureScreenshot(page, "ameba-editor-no-title-field");
    throw new Error("Amebaの新規投稿画面でタイトル欄が見つかりませんでした(UI変更の可能性)。");
  }
  await titleBox.fill(title);

  // 本文: エディタ(CKEditor)の機能でHTMLを流し込む(見出し・太字を保つ)
  await page.waitForFunction(() => window.CKEDITOR && Object.keys(window.CKEDITOR.instances).length > 0, null, { timeout: 30000 }).catch(() => {});
  const html = markdownToHtml(body);
  const setOk = await page.evaluate((h) => {
    const ed = window.CKEDITOR && Object.values(window.CKEDITOR.instances)[0];
    if (!ed) return false;
    ed.setData(h);
    return true;
  }, html).catch(() => false);
  if (!setOk) {
    await saveFailureScreenshot(page, "ameba-editor-no-body-field");
    throw new Error("Amebaの本文エディタを操作できませんでした(UI変更の可能性)。");
  }
  await page.waitForTimeout(2000);
  const expected = expectedLength(body);
  checkLength("Ameba", await readCharCount(page, /文字数[:：]\s*([\d,]+)/), expected, warnings);

  // 見出し画像: 画像一覧にアップロードし、一覧に増えた画像をクリックして本文に挿入→本文の先頭へ移動する
  // (Amebaは本文の先頭画像が記事のサムネイルになる)
  let imageOk = false;
  if (headerPath) {
    try {
      await page.locator("#sidepanel-accessoryTab-photos").click({ timeout: 5000 }).catch(() => {});
      // 画像一覧は「アップロード」ボタン(#js-file-trigger)と同じリストに並ぶ
      const itemsSel = 'xpath=//*[@id="js-file-trigger"]/ancestor::ul[1]/li[not(.//*[@id="js-file-trigger"])]';
      const before = await page.locator(itemsSel).count().catch(() => 0);
      const uploaded = await uploadViaChooser(page, ["#js-file-trigger"], headerPath, "#js-input-files");
      if (uploaded) {
        let added = false;
        for (let i = 0; i < 20 && !added; i++) {
          await page.waitForTimeout(1500);
          added = (await page.locator(itemsSel).count().catch(() => 0)) > before;
        }
        if (rehearsal) {
          const html = await page.evaluate(() => {
            const ul = document.getElementById("js-file-trigger")?.closest("ul");
            return ul ? ul.outerHTML.replace(/\s+/g, " ").slice(0, 2500) : "(ulなし)";
          }).catch(() => "");
          console.log(`[画像一覧(rehearsal)] before=${before} added=${added} ${html}`);
        }
        if (added) {
          const htmlBefore = await page.evaluate(() => Object.values(window.CKEDITOR.instances)[0].getData()).catch(() => "");
          await page.evaluate(() => { const ed = Object.values(window.CKEDITOR.instances)[0]; ed.focus(); const r = ed.createRange(); r.moveToElementEditStart(ed.editable()); r.select(); }).catch(() => {});
          // 新しい画像は一覧の先頭(アップロードボタンの次)に入る想定。中の画像/ボタンをクリックすると本文に挿入される
          const item = page.locator(itemsSel).first();
          const clickable = item.locator("img, button, a").first();
          await ((await clickable.count()) ? clickable : item).click({ timeout: 5000 }).catch(() => {});
          await page.waitForTimeout(2500);
          // 挿入された<img>を本文の先頭に置き直す(カーソル位置に入らなかった場合の保険)
          imageOk = await page.evaluate((prev) => {
            const ed = Object.values(window.CKEDITOR.instances)[0];
            const now = ed.getData();
            if (now === prev) return false;
            const doc = new DOMParser().parseFromString(`<div id="r">${now}</div>`, "text/html");
            const root = doc.getElementById("r");
            const img = root.querySelector("img");
            if (!img) return false;
            const block = img.closest("p, div:not(#r)") || img;
            root.insertBefore(block, root.firstChild);
            ed.setData(root.innerHTML);
            return true;
          }, htmlBefore).catch(() => false);
        }
        if (!imageOk) warnings.push("Ameba: 画像はアップロードしましたが、本文への挿入を確認できませんでした");
      } else warnings.push("Ameba: 画像のアップロード欄が見つかりませんでした");
    } catch (e) { imageOk = false; warnings.push(`Ameba: 画像の挿入に失敗(${e.message})`); }
  }

  let tagsOk = false;
  if (hashtags.length) {
    tagsOk = await setAmebaHashtags(page, hashtags, rehearsal).catch((e) => { warnings.push(`Ameba: ハッシュタグ入力でエラー(${e.message})`); return false; });
    if (!tagsOk && !warnings.some((w) => w.includes("ハッシュタグ"))) warnings.push("Ameba: ハッシュタグ入力欄が見つかりませんでした");
  }

  if (rehearsal) {
    await dumpPageStructure(page, "ameba-editor-filled(rehearsal)");
    return { skipped: false, rehearsal: true, url: page.url(), imageOk, tagsOk, warnings };
  }

  const publishBtn = page.locator('button, input[type="submit"], a[role="button"]').filter({ hasText: /^\s*(投稿する|公開する)\s*$/ }).first();
  if (!(await publishBtn.isVisible().catch(() => false))) {
    await saveFailureScreenshot(page, "ameba-no-publish-button");
    throw new Error("Amebaで「投稿する」ボタンが見つかりませんでした(UI変更の可能性)。");
  }
  await publishBtn.click({ timeout: 10000 });
  await page.waitForLoadState("domcontentloaded").catch(() => {});
  await page.waitForTimeout(4000);

  // 公開後は記事ページ(ameblo.jp/<ID>/entry-<数字>.html)か、投稿完了画面(記事へのリンクあり)になる
  let url = /ameblo\.jp\/[^/]+\/entry-\d+/i.test(page.url()) ? page.url() : null;
  if (!url) {
    url = await page.evaluate(() => {
      const a = [...document.querySelectorAll('a[href*="ameblo.jp/"]')].find((x) => /\/entry-\d+\.html/.test(x.href));
      return a ? a.href : null;
    }).catch(() => null);
  }
  if (!url) {
    await saveFailureScreenshot(page, "ameba-publish-not-confirmed");
    throw new Error(`Amebaで「投稿する」を押しましたが、公開された記事のURLを確認できませんでした(現在のURL: ${page.url()})。実際に公開されたか手動で確認してください。`);
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
  if (REHEARSAL && !files.includes(path.basename(REHEARSAL))) { console.log(`リハーサル対象 ${REHEARSAL} が drafts/ にありません`); return; }
  const targets = files.map((f) => ({ file: f, parsed: parseFile(path.join(DRAFTS_DIR, f)) }))
    .filter((t) => t.parsed && (REHEARSAL ? t.file === path.basename(REHEARSAL) : (DRY_RUN || t.parsed.front.status === "approved")));
  if (!targets.length) { console.log("投稿対象(status: approved)の下書きはありません"); return; }

  const ctx = loadContext();
  const browser = await chromium.launch({ headless: true, ...launchOptions() });

  for (const { file, parsed } of targets) {
    const filePath = path.join(DRAFTS_DIR, file);
    const { front, body, title } = parsed;
    console.log(`--- ${file} (status: ${front.status}) を処理します ---`);
    const media = await prepareMedia(file, parsed, ctx, browser);
    if (DRY_RUN) continue;

    if (REHEARSAL) {
      const context = await newSessionContext(browser);
      const page = await context.newPage();
      for (const [name, fn, tags] of [["note", publishToNote, media.sel.hashtags.note.tags], ["Ameba", publishToAmeba, media.sel.hashtags.ameba.tags]]) {
        try {
          const r = await fn(page, { title, body, headerPath: media.headerPath, hashtags: tags, rehearsal: true });
          console.log(`[リハーサル] ${name}: ` + JSON.stringify(r));
        } catch (e) { console.error(`[リハーサル] ${name}: 失敗 - ${e.message}`); }
      }
      await context.close();
      continue;
    }

    const context = await newSessionContext(browser);
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

module.exports = { toPlainParagraphs, markdownToHtml, expectedLength };

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}
