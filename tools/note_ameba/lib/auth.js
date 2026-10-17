// note.com / AmebaIDへのログイン処理(publish.js と insights.js で共通利用)。
// いずれも非公式のブラウザ操作。CAPTCHA・2段階認証が出た場合は自動突破せず中断する。

function hasNoteCreds() { return !!(process.env.NOTE_EMAIL && process.env.NOTE_PASSWORD); }
function hasAmebaCreds() { return !!(process.env.AMEBA_ID && process.env.AMEBA_PASSWORD && process.env.AMEBA_BLOG_ID); }

async function detectCaptcha(page) {
  return page.locator('iframe[src*="recaptcha"], text=認証').count().catch(() => 0);
}

async function loginNote(page) {
  await page.goto("https://note.com/login", { waitUntil: "domcontentloaded" });
  await page.fill('input[name="login_email"], input[type="email"]', process.env.NOTE_EMAIL).catch(() => {});
  await page.fill('input[name="password"], input[type="password"]', process.env.NOTE_PASSWORD).catch(() => {});
  await page.click('button[type="submit"]').catch(() => {});
  await page.waitForTimeout(3000);
  if (await detectCaptcha(page)) {
    throw new Error("note.comログイン時にCAPTCHA/認証画面が検出されました。自動処理を中断します(手動対応にフォールバックしてください)。");
  }
  if (page.url().includes("/login")) {
    throw new Error("note.comへのログインに失敗しました(URL確認: " + page.url() + ")。パスワード・メールアドレスを確認してください。");
  }
}

async function loginAmeba(page) {
  await page.goto("https://www.ameba.jp/login.html", { waitUntil: "domcontentloaded" });
  await page.fill('input[name="accountId"], input[type="text"]', process.env.AMEBA_ID).catch(() => {});
  await page.fill('input[name="password"], input[type="password"]', process.env.AMEBA_PASSWORD).catch(() => {});
  await page.click('button[type="submit"], input[type="submit"]').catch(() => {});
  await page.waitForTimeout(3000);
  if (await detectCaptcha(page)) {
    throw new Error("AmebaIDログイン時にCAPTCHA/認証画面が検出されました。自動処理を中断します(手動対応にフォールバックしてください)。");
  }
}

module.exports = { hasNoteCreds, hasAmebaCreds, loginNote, loginAmeba };
