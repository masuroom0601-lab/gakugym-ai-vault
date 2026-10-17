// note.com / AmebaIDへのログイン処理(publish.js と insights.js で共通利用)。
// いずれも非公式のブラウザ操作。CAPTCHA・2段階認証が出た場合は自動突破せず中断する。
const { saveFailureScreenshot } = require("./screenshot");

function hasNoteCreds() { return !!(process.env.NOTE_EMAIL && process.env.NOTE_PASSWORD); }
function hasAmebaCreds() { return !!(process.env.AMEBA_ID && process.env.AMEBA_PASSWORD && process.env.AMEBA_BLOG_ID); }

async function detectCaptcha(page) {
  return page.locator('iframe[src*="recaptcha"], text=認証').count().catch(() => 0);
}

async function loginNote(page) {
  await page.goto("https://note.com/login", { waitUntil: "domcontentloaded" });
  const emailBox = page.locator('input[name="login_email"], input[type="email"]').first();
  if (!(await emailBox.count())) {
    await saveFailureScreenshot(page, "note-login-no-email-field");
    throw new Error("note.comログイン画面でメールアドレス入力欄が見つかりませんでした(UI変更の可能性)。");
  }
  await emailBox.fill(process.env.NOTE_EMAIL);
  await page.locator('input[name="password"], input[type="password"]').first().fill(process.env.NOTE_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(3000);
  if (await detectCaptcha(page)) {
    await saveFailureScreenshot(page, "note-login-captcha");
    throw new Error("note.comログイン時にCAPTCHA/認証画面が検出されました。自動処理を中断します(手動対応にフォールバックしてください)。");
  }
  if (page.url().includes("/login")) {
    await saveFailureScreenshot(page, "note-login-failed");
    throw new Error("note.comへのログインに失敗しました(URL確認: " + page.url() + ")。パスワード・メールアドレスを確認してください。");
  }
}

async function loginAmeba(page) {
  await page.goto("https://www.ameba.jp/login.html", { waitUntil: "domcontentloaded" });
  const idBox = page.locator('input[name="accountId"], input[type="text"]').first();
  if (!(await idBox.count())) {
    await saveFailureScreenshot(page, "ameba-login-no-id-field");
    throw new Error("AmebaIDログイン画面でID入力欄が見つかりませんでした(UI変更の可能性)。");
  }
  await idBox.fill(process.env.AMEBA_ID);
  await page.locator('input[name="password"], input[type="password"]').first().fill(process.env.AMEBA_PASSWORD);
  await page.click('button[type="submit"], input[type="submit"]');
  await page.waitForTimeout(3000);
  if (await detectCaptcha(page)) {
    await saveFailureScreenshot(page, "ameba-login-captcha");
    throw new Error("AmebaIDログイン時にCAPTCHA/認証画面が検出されました。自動処理を中断します(手動対応にフォールバックしてください)。");
  }
  if (page.url().includes("login")) {
    await saveFailureScreenshot(page, "ameba-login-failed");
    throw new Error("AmebaIDへのログインに失敗しました(URL確認: " + page.url() + ")。ID・パスワードを確認してください。");
  }
}

module.exports = { hasNoteCreds, hasAmebaCreds, loginNote, loginAmeba };
