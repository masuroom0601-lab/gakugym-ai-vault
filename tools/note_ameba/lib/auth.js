// note.com / AmebaIDへのログイン処理(publish.js と insights.js で共通利用)。
// いずれも非公式のブラウザ操作。CAPTCHA・2段階認証が出た場合は自動突破せず中断する。
const { saveFailureScreenshot } = require("./screenshot");

function hasNoteCreds() { return !!(process.env.NOTE_EMAIL && process.env.NOTE_PASSWORD); }
function hasAmebaCreds() { return !!(process.env.AMEBA_ID && process.env.AMEBA_PASSWORD && process.env.AMEBA_BLOG_ID); }

async function detectCaptcha(page) {
  return page.locator('iframe[src*="recaptcha"], text=認証').count().catch(() => 0);
}

// 最初に見つかった「表示されている」入力欄を返す(SPAの描画完了も待つ)
async function findVisible(page, selectors, timeout = 15000) {
  const sel = selectors.join(", ");
  await page.locator(sel).first().waitFor({ state: "visible", timeout }).catch(() => {});
  const all = page.locator(sel);
  const n = await all.count().catch(() => 0);
  for (let i = 0; i < n; i++) {
    const el = all.nth(i);
    if (await el.isVisible().catch(() => false)) return el;
  }
  return null;
}

async function clickSubmit(page, names) {
  for (const name of names) {
    const btn = page.getByRole("button", { name, exact: false }).first();
    if (await btn.isVisible().catch(() => false)) { await btn.click(); return true; }
  }
  const fallback = page.locator('button[type="submit"], input[type="submit"]').first();
  if (await fallback.isVisible().catch(() => false)) { await fallback.click(); return true; }
  await page.keyboard.press("Enter");
  return false;
}

const NOTE_ID_FIELDS = ['#email', 'input[name="login_email"]', 'input[type="email"]', 'input[autocomplete="username"]',
  'input[placeholder*="mail"]', 'input[placeholder*="メール"]', 'input[placeholder*="note ID"]'];
const PASSWORD_FIELDS = ['#password', 'input[name="password"]', 'input[type="password"]'];

async function loginNote(page) {
  await page.goto("https://note.com/login", { waitUntil: "domcontentloaded" });
  // note.comのログイン画面はJSで描画されるため、入力欄が出るまで待つ
  // (2026-10-17の初回テストでは描画前に探して「入力欄が見つからない」で失敗した)
  const emailBox = await findVisible(page, NOTE_ID_FIELDS);
  if (!emailBox) {
    await saveFailureScreenshot(page, "note-login-no-email-field");
    throw new Error("note.comログイン画面でメールアドレス入力欄が見つかりませんでした(UI変更の可能性)。");
  }
  await emailBox.fill(process.env.NOTE_EMAIL);
  const passBox = await findVisible(page, PASSWORD_FIELDS, 5000);
  if (!passBox) {
    await saveFailureScreenshot(page, "note-login-no-password-field");
    throw new Error("note.comログイン画面でパスワード入力欄が見つかりませんでした(UI変更の可能性)。");
  }
  await passBox.fill(process.env.NOTE_PASSWORD);
  await clickSubmit(page, ["ログイン"]);
  await page.waitForURL((u) => !String(u).includes("/login"), { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(1500);
  if (await detectCaptcha(page)) {
    await saveFailureScreenshot(page, "note-login-captcha");
    throw new Error("note.comログイン時にCAPTCHA/認証画面が検出されました。自動処理を中断します(手動対応にフォールバックしてください)。");
  }
  if (page.url().includes("/login")) {
    await saveFailureScreenshot(page, "note-login-failed");
    throw new Error("note.comへのログインに失敗しました(URL確認: " + page.url() + ")。パスワード・メールアドレスを確認してください。");
  }
}

const AMEBA_ID_FIELDS = ['input[name="accountId"]', 'input[name="amebaId"]', 'input[autocomplete="username"]',
  'input[type="email"]', 'input[type="text"]'];

async function loginAmeba(page) {
  await page.goto("https://www.ameba.jp/login.html", { waitUntil: "domcontentloaded" });
  const idBox = await findVisible(page, AMEBA_ID_FIELDS);
  if (!idBox) {
    await saveFailureScreenshot(page, "ameba-login-no-id-field");
    throw new Error("AmebaIDログイン画面でID入力欄が見つかりませんでした(UI変更の可能性)。");
  }
  await idBox.fill(process.env.AMEBA_ID);
  // AmebaIDは「ID入力→次へ→パスワード入力」の2段階画面のことがある
  // (2026-10-17の初回テストでは1画面目でパスワード欄を待ち続けてタイムアウトした)
  let passBox = await findVisible(page, PASSWORD_FIELDS, 2000);
  if (!passBox) {
    await clickSubmit(page, ["次へ", "続ける", "ログイン"]);
    passBox = await findVisible(page, PASSWORD_FIELDS, 15000);
  }
  if (!passBox) {
    await saveFailureScreenshot(page, "ameba-login-no-password-field");
    throw new Error("AmebaIDログインでパスワード入力欄が見つかりませんでした(UI変更、またはID誤りの可能性)。");
  }
  await passBox.fill(process.env.AMEBA_PASSWORD);
  await clickSubmit(page, ["ログイン"]);
  await page.waitForURL((u) => !/login|accounts\.ameba/.test(String(u)), { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(1500);
  if (await detectCaptcha(page)) {
    await saveFailureScreenshot(page, "ameba-login-captcha");
    throw new Error("AmebaIDログイン時にCAPTCHA/認証画面が検出されました。自動処理を中断します(手動対応にフォールバックしてください)。");
  }
  if (/login/.test(page.url())) {
    await saveFailureScreenshot(page, "ameba-login-failed");
    throw new Error("AmebaIDへのログインに失敗しました(URL確認: " + page.url() + ")。ID・パスワードを確認してください。");
  }
}

module.exports = { hasNoteCreds, hasAmebaCreds, loginNote, loginAmeba };
