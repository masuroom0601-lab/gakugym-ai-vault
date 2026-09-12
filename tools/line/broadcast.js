#!/usr/bin/env node
// 学ジム LINE公式担当: 承認済み(status: approved)のドラフトをLINE Messaging APIで配信する。
//
// これは意図的にLLM(Claude)を経由させない決定的スクリプトです。
// 実際の生徒・保護者に一度送ると取り消せないメッセージを配信するステップなので、
// 「AIの解釈」ではなく「決まったルールで機械的に処理する」ことを優先しています。
//
// 使い方: node broadcast.js [--dry-run]
//   --dry-run: 実際には配信せず、何が送られるはずかをログに出すだけ(状態も変更しない)
//
// 必須環境変数: LINE_CHANNEL_ACCESS_TOKEN(未設定なら「まだ準備ができていない」として
// 何もせず正常終了する。設定手順は 01_HQ/setup guides/line-messaging-api-setup.md.md 参照)
// 任意環境変数: LINE_MONTHLY_QUOTA(既定200。フリープランの月間無料メッセージ数の目安)

const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

const REPO_ROOT = path.join(__dirname, "..", "..");
const DRAFTS_DIR = path.join(REPO_ROOT, "02_departments", "line", "drafts");
const PUBLISHED_DIR = path.join(REPO_ROOT, "02_departments", "line", "published");
const USAGE_FILE = path.join(REPO_ROOT, "04_analytics", "line-message-usage.json");

const DRY_RUN = process.argv.includes("--dry-run") || process.env.LINE_DRY_RUN === "true";
const CHANNEL_ACCESS_TOKEN = process.env.LINE_CHANNEL_ACCESS_TOKEN || "";
const MONTHLY_QUOTA = parseInt(process.env.LINE_MONTHLY_QUOTA || "200", 10);
const ASSUMED_FRIENDS_FALLBACK = parseInt(process.env.LINE_ASSUMED_FRIENDS || "50", 10);

function splitFrontmatter(content) {
  const m = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { frontmatter: {}, body: content };
  // JSON_SCHEMAを使い、date: 2026-09-14のような裸の日付をDateオブジェクトへ自動変換させない
  // (他部署のfrontmatterと同じ「plain文字列としてのYYYY-MM-DD」を保つため)
  const frontmatter = yaml.load(m[1], { schema: yaml.JSON_SCHEMA }) || {};
  return { frontmatter, body: m[2] };
}

function serialize(frontmatter, body) {
  const fm = yaml.dump(frontmatter, { lineWidth: -1 }).trimEnd();
  return `---\n${fm}\n---\n${body}`;
}

function extractBroadcastText(body) {
  const m = body.match(/##\s*配信本文\s*\n```[^\n]*\n([\s\S]*?)```/);
  if (!m) return null;
  return m[1].trim();
}

function loadUsage() {
  const month = new Date().toISOString().slice(0, 7); // YYYY-MM
  if (!fs.existsSync(USAGE_FILE)) return { month, sent: 0 };
  const data = JSON.parse(fs.readFileSync(USAGE_FILE, "utf8"));
  if (data.month !== month) return { month, sent: 0 }; // 月が変わったらリセット
  return data;
}

function saveUsage(usage) {
  fs.mkdirSync(path.dirname(USAGE_FILE), { recursive: true });
  fs.writeFileSync(USAGE_FILE, JSON.stringify(usage, null, 2) + "\n");
}

async function getFriendCount() {
  try {
    const d = new Date();
    d.setDate(d.getDate() - 1); // LINEのfollowers insightは前日分まで確定
    const dateStr =
      d.getFullYear().toString() +
      String(d.getMonth() + 1).padStart(2, "0") +
      String(d.getDate()).padStart(2, "0");
    const res = await fetch(
      `https://api.line.me/v2/bot/insight/followers?date=${dateStr}`,
      { headers: { Authorization: `Bearer ${CHANNEL_ACCESS_TOKEN}` } }
    );
    if (!res.ok) throw new Error(`insight API status ${res.status}`);
    const json = await res.json();
    if (typeof json.followers === "number") return json.followers;
    throw new Error("followers field missing");
  } catch (e) {
    console.warn(
      `[警告] 友だち数の取得に失敗したため、安全側の仮値(${ASSUMED_FRIENDS_FALLBACK}人)で判定します: ${e}`
    );
    return ASSUMED_FRIENDS_FALLBACK;
  }
}

async function sendBroadcast(text) {
  const res = await fetch("https://api.line.me/v2/bot/message/broadcast", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${CHANNEL_ACCESS_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages: [{ type: "text", text }] }),
  });
  const bodyText = await res.text();
  return { ok: res.ok, status: res.status, body: bodyText };
}

function appendComment(body, note) {
  return `${body.trimEnd()}\n\n## 配信担当コメント\n${note}\n`;
}

async function main() {
  if (!CHANNEL_ACCESS_TOKEN) {
    console.log(
      "LINE_CHANNEL_ACCESS_TOKEN が未設定のため、配信は行いません" +
        "(01_HQ/setup guides/line-messaging-api-setup.md.md を参照してセットアップしてください)。" +
        "それまでは published/ フォルダの内容を益田さんが手動で配信してください。"
    );
    process.exit(0);
  }

  if (!fs.existsSync(DRAFTS_DIR)) {
    console.log("line/drafts フォルダが見つかりません。");
    process.exit(0);
  }

  const files = fs
    .readdirSync(DRAFTS_DIR)
    .filter((f) => f.endsWith(".md"))
    .sort();

  const usage = loadUsage();
  let anyChange = false;

  for (const file of files) {
    const fullPath = path.join(DRAFTS_DIR, file);
    const raw = fs.readFileSync(fullPath, "utf8");
    const { frontmatter, body } = splitFrontmatter(raw);

    if (frontmatter.status !== "approved") continue;

    const text = extractBroadcastText(body);
    if (!text) {
      console.error(`[スキップ] ${file}: 「## 配信本文」のコードブロックが見つかりません`);
      const updated = serialize(
        frontmatter,
        appendComment(body, "配信スクリプトが本文を抽出できませんでした。フォーマットを確認してください。")
      );
      fs.writeFileSync(fullPath, updated);
      anyChange = true;
      continue;
    }

    const friendCount = await getFriendCount();
    if (usage.sent + friendCount > MONTHLY_QUOTA) {
      console.warn(
        `[見送り] ${file}: 今月の配信数(${usage.sent})+今回の想定送信数(${friendCount})が` +
          `月間上限(${MONTHLY_QUOTA})を超えるため配信しませんでした。LINE公式アカウントの` +
          `プラン確認・上限見直し・来月への持ち越しを検討してください。`
      );
      const updated = serialize(
        frontmatter,
        appendComment(
          body,
          `月間メッセージ上限(${MONTHLY_QUOTA})超過のため配信を見送りました` +
            `(今月の配信数: ${usage.sent}、今回の想定送信数: ${friendCount})。` +
            `承認は維持しているので、上限リセット後(翌月)またはプラン変更後に再実行してください。`
        )
      );
      fs.writeFileSync(fullPath, updated);
      anyChange = true;
      continue; // 他のファイルも同様に上限超過の可能性が高いため見送るが、処理自体は続行する
    }

    if (DRY_RUN) {
      console.log(`[DRY RUN] ${file} を ${friendCount}人に配信する想定です:\n---\n${text}\n---`);
      continue;
    }

    const result = await sendBroadcast(text);
    if (result.ok) {
      console.log(`[配信成功] ${file}(想定${friendCount}人)`);
      frontmatter.status = "published";
      frontmatter.sent_at = new Date().toISOString();
      frontmatter.sent_to_friends_estimate = friendCount;
      const updatedContent = serialize(frontmatter, body);
      fs.mkdirSync(PUBLISHED_DIR, { recursive: true });
      fs.writeFileSync(path.join(PUBLISHED_DIR, file), updatedContent);
      fs.unlinkSync(fullPath);
      usage.sent += friendCount;
      anyChange = true;
    } else {
      console.error(`[配信失敗] ${file}: HTTP ${result.status} ${result.body}`);
      const updated = serialize(
        frontmatter,
        appendComment(body, `配信に失敗しました(HTTP ${result.status}): ${result.body}`)
      );
      fs.writeFileSync(fullPath, updated);
      anyChange = true;
    }
  }

  if (!DRY_RUN && anyChange) saveUsage(usage);
  process.exit(0);
}

if (require.main === module) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}

module.exports = { splitFrontmatter, serialize, extractBroadcastText };
