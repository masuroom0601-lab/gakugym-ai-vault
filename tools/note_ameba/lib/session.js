// ログイン状態(Cookie)の保存・復元(2026-10-17新設、方式A)。
// GitHub Actionsからのフォームログインは、noteはロボット判定(reCAPTCHA)、Amebaは
// ログインサーバーのアクセス拒否で通らなかったため、益田さんのPCで一度ログインした状態を
// secrets(NOTE_SESSION / AMEBA_SESSION)に保存し、自動処理はログイン画面を通らずに使う。
// 形式: Playwrightの storageState(JSON)を gzip → base64 にした文字列。
const zlib = require("zlib");

const DESKTOP_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36";

const DOMAINS = {
  note: [/(^|\.)note\.com$/],
  ameba: [/(^|\.)ameba\.jp$/, /(^|\.)ameblo\.jp$/],
};

function filterState(state, platform) {
  const ok = (host) => DOMAINS[platform].some((re) => re.test(String(host).replace(/^\./, "")));
  return {
    cookies: (state.cookies || []).filter((c) => ok(c.domain)),
    origins: (state.origins || []).filter((o) => { try { return ok(new URL(o.origin).hostname); } catch { return false; } }),
  };
}

function encodeState(state) {
  return zlib.gzipSync(Buffer.from(JSON.stringify(state), "utf8")).toString("base64");
}

function decodeState(text) {
  return JSON.parse(zlib.gunzipSync(Buffer.from(String(text).trim(), "base64")).toString("utf8"));
}

function sessionEnv(platform) {
  return platform === "note" ? process.env.NOTE_SESSION : process.env.AMEBA_SESSION;
}

function hasSession(platform) { return !!sessionEnv(platform); }

// secretsに保存されたログイン状態(あれば)を読み込んだブラウザコンテキストを作る。
// note/Ameba両方を同じコンテキストで扱えるよう、2つの状態を結合する。
async function newSessionContext(browser) {
  const merged = { cookies: [], origins: [] };
  for (const platform of ["note", "ameba"]) {
    const raw = sessionEnv(platform);
    if (!raw) continue;
    try {
      const st = filterState(decodeState(raw), platform);
      merged.cookies.push(...st.cookies);
      merged.origins.push(...st.origins);
    } catch (e) {
      console.warn(`${platform}: 保存されたログイン状態(${platform === "note" ? "NOTE_SESSION" : "AMEBA_SESSION"})を読み込めませんでした: ${e.message}`);
    }
  }
  // 自動操作ブラウザ(HeadlessChrome)と判定されると画面が表示されないことがあるため、
  // 通常のChromeと同じユーザーエージェント・言語・画面サイズにする(2026-10-17、noteエディタが真っ白だった件)
  const base = { userAgent: DESKTOP_UA, locale: "ja-JP", timezoneId: "Asia/Tokyo", viewport: { width: 1366, height: 900 } };
  return browser.newContext(merged.cookies.length || merged.origins.length ? { ...base, storageState: merged } : base);
}

module.exports = { filterState, encodeState, decodeState, hasSession, newSessionContext };
