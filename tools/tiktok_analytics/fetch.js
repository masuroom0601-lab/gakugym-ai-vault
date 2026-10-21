#!/usr/bin/env node
// 学ジム TikTok担当: TikTok公式Display APIから自社アカウント(massu_gakugym)の
// フォロワー数・プロフィール文・動画ごとの再生数等を取得し、
// 04_analytics/manual-input/<週の月曜日>.md のTikTok欄に自動で書き込む。
//
// これはInstagramの「エルグラム」連携(claude.aiのRoutine経由)とは別方式で、
// TikTok公式APIのトークンだけで動くため、GitHub Actionsのスケジュール実行で
// そのまま完結する(claude.aiのコネクタ連携は不要)。
//
// 使い方: node fetch.js
//
// 必須環境変数: TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET / TIKTOK_REFRESH_TOKEN
// (いずれか未設定なら「まだ準備ができていない」として何もせず正常終了する。
// 設定手順は 01_HQ/setup guides/tiktok-api-setup.md 参照)

const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

const REPO_ROOT = path.join(__dirname, "..", "..");
const MANUAL_INPUT_DIR = path.join(REPO_ROOT, "04_analytics", "manual-input");

const CLIENT_KEY = process.env.TIKTOK_CLIENT_KEY || "";
const CLIENT_SECRET = process.env.TIKTOK_CLIENT_SECRET || "";
const REFRESH_TOKEN = process.env.TIKTOK_REFRESH_TOKEN || "";

const AUTO_NOTE =
  "このシートのTikTok欄(フォロワー数・投稿ごとの再生数)はTikTok公式API経由で自動取得しました。";

function splitFrontmatter(content) {
  const m = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { frontmatter: {}, body: content };
  const frontmatter = yaml.load(m[1], { schema: yaml.JSON_SCHEMA }) || {};
  return { frontmatter, body: m[2] };
}

function serialize(frontmatter, body) {
  const fm = yaml.dump(frontmatter, { lineWidth: -1 }).trimEnd();
  return `---\n${fm}\n---\n${body}`;
}

// JSTで「今日を含む週」の月曜日・日曜日を YYYY-MM-DD で返す
function currentWeekRangeJST() {
  const now = new Date();
  const jstMs = now.getTime() + 9 * 60 * 60 * 1000;
  const jst = new Date(jstMs);
  const dow = jst.getUTCDay(); // 0=日
  const diffToMonday = dow === 0 ? 6 : dow - 1;
  const monday = new Date(jst);
  monday.setUTCDate(jst.getUTCDate() - diffToMonday);
  const sunday = new Date(monday);
  sunday.setUTCDate(monday.getUTCDate() + 6);
  const fmt = (d) => d.toISOString().slice(0, 10);
  return { weekStart: fmt(monday), weekEnd: fmt(sunday) };
}

async function refreshAccessToken() {
  const res = await fetch("https://open.tiktokapis.com/v2/oauth/token/", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_key: CLIENT_KEY,
      client_secret: CLIENT_SECRET,
      grant_type: "refresh_token",
      refresh_token: REFRESH_TOKEN,
    }),
  });
  const json = await res.json();
  if (!res.ok || !json.access_token) {
    throw new Error(`アクセストークンの更新に失敗: HTTP ${res.status} ${JSON.stringify(json)}`);
  }
  return json.access_token;
}

async function getUserInfo(accessToken) {
  const fields = "display_name,bio_description,follower_count,likes_count,video_count";
  const res = await fetch(`https://open.tiktokapis.com/v2/user/info/?fields=${fields}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const json = await res.json();
  if (!res.ok || json.error?.code !== "ok") {
    throw new Error(`user/info取得に失敗: HTTP ${res.status} ${JSON.stringify(json)}`);
  }
  return json.data.user;
}

// 直近の動画を新しい順に最大40件取得(週次フィルタはこの後に行う)
async function listRecentVideos(accessToken) {
  const fields = "id,create_time,title,view_count,like_count,comment_count,share_count";
  const videos = [];
  let cursor = 0;
  for (let page = 0; page < 2; page++) {
    const res = await fetch(
      `https://open.tiktokapis.com/v2/video/list/?fields=${fields}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ max_count: 20, cursor }),
      }
    );
    const json = await res.json();
    if (!res.ok || json.error?.code !== "ok") {
      throw new Error(`video/list取得に失敗: HTTP ${res.status} ${JSON.stringify(json)}`);
    }
    videos.push(...(json.data.videos || []));
    if (!json.data.has_more) break;
    cursor = json.data.cursor;
  }
  return videos;
}

function updateFollowerRow(body, followerCount) {
  const re = /^\|\s*TikTok\s*\|[^|\n]*\|$/m;
  if (!re.test(body)) return body;
  return body.replace(re, `| TikTok | ${followerCount}人 |`);
}

function appendVideoRows(body, videos) {
  const sectionRe = /(## Instagram\/TikTok 投稿ごとのエンゲージメント\n\|[^\n]*\|\n\|[^\n]*\|\n)([\s\S]*?)(\n##|\n$|$)/;
  const m = body.match(sectionRe);
  if (!m) return body;

  const existingBlock = m[2];
  const existingLines = existingBlock
    .split("\n")
    .filter((l) => l.trim().length > 0);
  // 初期状態の空プレースホルダー行(| | | | | |)は捨てる。手入力済みの行は残す
  const keptLines = existingLines.filter((l) => !/^\|\s*\|\s*\|\s*\|\s*\|\s*\|$/.test(l));

  const newLines = videos
    .filter((v) => !existingBlock.includes(`id:${v.id}`))
    .map((v) => {
      const dateJst = new Date((v.create_time + 9 * 3600) * 1000)
        .toISOString()
        .slice(0, 10);
      const titleSnippet = (v.title || "(無題)").slice(0, 30);
      const label = `${titleSnippet}(TikTok公式API自動取得・id:${v.id})`;
      return `| ${dateJst} | ${label} | ${v.like_count ?? ""} | ー | ${v.view_count ?? ""} |`;
    });

  if (newLines.length === 0) return body;

  const rebuilt = [...keptLines, ...newLines].join("\n") + "\n";
  return body.replace(sectionRe, `$1${rebuilt}$3`);
}

function addMemoNote(body) {
  if (body.includes(AUTO_NOTE)) return body;
  const memoRe = /(## メモ\(数値以外で気づいたこと\)\n)([\s\S]*)$/;
  const m = body.match(memoRe);
  if (!m) return body;
  const rest = m[2].replace(/^-\s*$/m, "").trimEnd();
  const newBody = `${m[1]}- ${AUTO_NOTE}\n${rest ? rest + "\n" : ""}`;
  return body.replace(memoRe, newBody);
}

async function main() {
  if (!CLIENT_KEY || !CLIENT_SECRET || !REFRESH_TOKEN) {
    console.log(
      "TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET / TIKTOK_REFRESH_TOKEN が未設定のため、" +
        "TikTok分析データの取得は行いません(01_HQ/setup guides/tiktok-api-setup.md を参照して" +
        "セットアップしてください)。それまではTikTok欄は益田さんの手動入力のままで構いません。"
    );
    process.exit(0);
  }

  const { weekStart } = currentWeekRangeJST();
  const manualInputPath = path.join(MANUAL_INPUT_DIR, `${weekStart}.md`);
  if (!fs.existsSync(manualInputPath)) {
    console.log(
      `${manualInputPath} が見つからないため何もしません` +
        "(analytics-weekly-report.ymlが作成するはずのファイルが無い週は、無理に新規作成しません)。"
    );
    process.exit(0);
  }

  const accessToken = await refreshAccessToken();
  const user = await getUserInfo(accessToken);
  const allVideos = await listRecentVideos(accessToken);

  const weekStartSec = Math.floor(new Date(`${weekStart}T00:00:00+09:00`).getTime() / 1000);
  const weekEndSec = weekStartSec + 7 * 24 * 3600;
  const thisWeekVideos = allVideos.filter(
    (v) => v.create_time >= weekStartSec && v.create_time < weekEndSec
  );

  const raw = fs.readFileSync(manualInputPath, "utf8");
  const { body } = splitFrontmatter(raw);

  let newBody = updateFollowerRow(body, user.follower_count);
  newBody = appendVideoRows(newBody, thisWeekVideos);
  newBody = addMemoNote(newBody);

  if (newBody === body) {
    console.log("更新すべき内容がありませんでした(フォロワー数欄が見つからない、または今週の新規動画なし)。");
    process.exit(0);
  }

  // frontmatterはyaml.dumpで再出力せず、filled行だけを正規表現で書き換える
  // (他部署のfrontmatterの素のYYYY-MM-DD表記が、再dump時に引用符付き文字列に
  // 変換されてしまい、手書きフォーマットと差分が出るのを避けるため)
  let newRaw = raw.replace(body, newBody);
  newRaw = newRaw.replace(/^filled:\s*false\s*$/m, "filled: true");
  fs.writeFileSync(manualInputPath, newRaw);
  console.log(
    `${manualInputPath} を更新しました` +
      `(フォロワー数: ${user.follower_count}人、プロフィール文: ${user.bio_description || "(未設定)"}、` +
      `今週の動画件数: ${thisWeekVideos.length}件)。`
  );
}

if (require.main === module) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}

module.exports = {
  splitFrontmatter,
  serialize,
  currentWeekRangeJST,
  updateFollowerRow,
  appendVideoRows,
  addMemoNote,
};
