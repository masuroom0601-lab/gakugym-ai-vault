// note/Ameba下書きファイル(frontmatter付きMarkdown)の読み書き。
// publish.js / select.js / analyze.js で共通利用する。
const fs = require("fs");
const yaml = require("js-yaml");

function parseText(raw) {
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!m) return null;
  // CORE_SCHEMA: 日付(2026-10-05)をDate型に変換せず文字列のまま扱う
  // (DEFAULT_SCHEMAだと書き戻し時に 2026-10-05T00:00:00.000Z へ化けていた)
  const front = yaml.load(m[1], { schema: yaml.CORE_SCHEMA }) || {};
  const body = m[2];
  const titleMatch = body.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : (front.subject || "学ジム");
  const contentWithoutTitle = titleMatch ? body.replace(titleMatch[0], "").trim() : body.trim();
  return { front, body: contentWithoutTitle, title };
}

function parseFile(filePath) {
  return parseText(fs.readFileSync(filePath, "utf8"));
}

function writeFile(filePath, front, title, body) {
  const frontStr = yaml.dump(front, { lineWidth: -1, schema: yaml.CORE_SCHEMA }).trimEnd();
  const content = body ? `# ${title}\n\n${body}` : `# ${title}`;
  fs.writeFileSync(filePath, `---\n${frontStr}\n---\n\n${content}\n`, "utf8");
}

function loadYaml(filePath, fallback) {
  if (!fs.existsSync(filePath)) return fallback;
  return yaml.load(fs.readFileSync(filePath, "utf8")) || fallback;
}

function loadJson(filePath, fallback) {
  if (!fs.existsSync(filePath)) return fallback;
  try { return JSON.parse(fs.readFileSync(filePath, "utf8")); } catch { return fallback; }
}

module.exports = { parseText, parseFile, writeFile, loadYaml, loadJson };
