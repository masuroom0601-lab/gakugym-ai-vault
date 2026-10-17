// 失敗時のスクリーンショット保存(ワークフローのartifactとして確認できる)と、
// 画面の入力欄・ボタン構成のログ出力(artifactを開けない環境からも原因を調べられるように)。
const fs = require("fs");
const path = require("path");

const SCREENSHOT_DIR = path.join(__dirname, "..", "failure-screenshots");

// 画面上の入力欄・編集領域・ボタンの一覧をログに出す(値は出さない。パスワード等が漏れないように)
async function dumpPageStructure(page, label) {
  try {
    const info = await page.evaluate(() => {
      const vis = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
      const attrs = (el) => {
        const o = { tag: el.tagName.toLowerCase() };
        for (const a of ["type", "name", "id", "placeholder", "aria-label", "role", "data-placeholder", "contenteditable", "autocomplete"]) {
          const v = el.getAttribute(a);
          if (v !== null && v !== "") o[a] = v.slice(0, 60);
        }
        if (el.className && typeof el.className === "string") o.class = el.className.slice(0, 80);
        o.visible = vis(el);
        return o;
      };
      const fields = [...document.querySelectorAll("input, textarea, [contenteditable], [role=textbox]")].slice(0, 40).map(attrs);
      const buttons = [...document.querySelectorAll("button, [role=button], input[type=submit], a[href*=login]")]
        .filter(vis).slice(0, 40).map((b) => ({ ...attrs(b), text: (b.innerText || b.value || "").trim().slice(0, 30) }));
      const iframes = [...document.querySelectorAll("iframe")].map((f) => (f.src || "").slice(0, 100));
      return { url: location.href, title: document.title, fields, buttons, iframes };
    });
    console.log(`[画面構成:${label}] ` + JSON.stringify(info));
  } catch (e) {
    console.log(`[画面構成:${label}] 取得失敗: ${e.message}`);
  }
}

async function saveFailureScreenshot(page, label) {
  await dumpPageStructure(page, label);
  try {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
    const p = path.join(SCREENSHOT_DIR, `${label}-${Date.now()}.png`);
    await page.screenshot({ path: p, fullPage: true });
    console.log(`失敗時のスクリーンショットを保存しました: ${p}(ワークフローのartifactとして確認可能)`);
  } catch (e) {
    console.log("スクリーンショット保存にも失敗:", e.message);
  }
}

module.exports = { saveFailureScreenshot, dumpPageStructure, SCREENSHOT_DIR };
