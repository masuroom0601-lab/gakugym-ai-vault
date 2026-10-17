// note.comの公開API(ログイン不要)で、アカウントの記事一覧・見出し画像・スキ数を取得する。
// ログインが通らない環境(GitHub Actions等)でも、公開情報だけは確実に取れるようにするため(2026-10-17新設)。
const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

const ROOT = path.join(__dirname, "..", "..", "..");
const ACCOUNTS_PATH = path.join(ROOT, "02_departments", "note_ameba", "accounts.yml");
const REF_DIR = path.join(ROOT, "03_assets", "images", "note_ameba", "reference");

function noteUrlname() {
  if (process.env.NOTE_URLNAME) return process.env.NOTE_URLNAME;
  if (!fs.existsSync(ACCOUNTS_PATH)) return null;
  const a = yaml.load(fs.readFileSync(ACCOUNTS_PATH, "utf8"), { schema: yaml.CORE_SCHEMA }) || {};
  return a.note_urlname || null;
}

const pick = (o, ...keys) => { for (const k of keys) if (o && o[k] !== undefined && o[k] !== null) return o[k]; return null; };

// APIの項目名は camelCase / snake_case の揺れがあるため両方に対応する
function normalizeNote(c, urlname) {
  const key = pick(c, "key");
  return {
    key,
    title: pick(c, "name", "title"),
    eyecatch: pick(c, "eyecatch", "eyecatchUrl", "eyecatch_url"),
    likes: pick(c, "likeCount", "like_count"),
    comments: pick(c, "commentCount", "comment_count"),
    published_at: pick(c, "publishAt", "publish_at", "createdAt", "created_at"),
    url: pick(c, "noteUrl", "note_url") || (key ? `https://note.com/${urlname}/n/${key}` : null),
  };
}

async function fetchPublicNotes(urlname, maxPages = 5) {
  const notes = [];
  for (let page = 1; page <= maxPages; page++) {
    const res = await fetch(`https://note.com/api/v2/creators/${encodeURIComponent(urlname)}/contents?kind=note&page=${page}`,
      { headers: { "User-Agent": "Mozilla/5.0 (gakugym-ai-vault insights)" } });
    if (!res.ok) throw new Error(`note公開API HTTP ${res.status}`);
    const data = ((await res.json()) || {}).data || {};
    const contents = data.contents || [];
    notes.push(...contents.map((c) => normalizeNote(c, urlname)));
    if (data.isLastPage !== false || !contents.length) break;
  }
  return notes;
}

// 既存記事の見出し画像を参考画像として保存する(保存済みは再取得しない)
async function saveReferenceImages(notes, limit = 12) {
  fs.mkdirSync(REF_DIR, { recursive: true });
  const indexPath = path.join(REF_DIR, "index.json");
  const index = fs.existsSync(indexPath) ? JSON.parse(fs.readFileSync(indexPath, "utf8")) : [];
  const saved = [];
  for (const n of notes.filter((n) => n.eyecatch && n.key).slice(0, limit)) {
    const ext = ((String(n.eyecatch).split("?")[0].match(/\.(png|jpe?g|webp|gif)$/i) || [])[1] || "png").toLowerCase();
    const file = `${n.key}.${ext}`;
    const dest = path.join(REF_DIR, file);
    if (!fs.existsSync(dest)) {
      const res = await fetch(n.eyecatch).catch(() => null);
      if (!res || !res.ok) continue;
      fs.writeFileSync(dest, Buffer.from(await res.arrayBuffer()));
    }
    const entry = { file: path.relative(ROOT, dest), key: n.key, title: n.title, likes: n.likes, published_at: n.published_at, url: n.url, eyecatch_url: n.eyecatch };
    const i = index.findIndex((e) => e.key === n.key);
    if (i >= 0) index[i] = entry; else index.push(entry);
    saved.push(entry.file);
  }
  fs.writeFileSync(indexPath, JSON.stringify(index, null, 2) + "\n", "utf8");
  return saved;
}

module.exports = { noteUrlname, fetchPublicNotes, saveReferenceImages, normalizeNote };

if (require.main === module) {
  (async () => {
    const urlname = noteUrlname();
    if (!urlname) { console.log("note_urlname が未設定です(02_departments/note_ameba/accounts.yml)"); return; }
    const notes = await fetchPublicNotes(urlname);
    console.log(`note公開記事: ${notes.length}件`);
    const saved = await saveReferenceImages(notes);
    console.log(`参考画像を保存/更新: ${saved.length}件`);
  })().catch((e) => { console.error(e.message); process.exit(1); });
}
