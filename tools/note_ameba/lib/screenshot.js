// 失敗時のスクリーンショット保存(ワークフローのartifactとして確認できる)
const fs = require("fs");
const path = require("path");

const SCREENSHOT_DIR = path.join(__dirname, "..", "failure-screenshots");

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

module.exports = { saveFailureScreenshot, SCREENSHOT_DIR };
