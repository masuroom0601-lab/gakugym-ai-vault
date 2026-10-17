// 選定(select.js)・集計(analyze.js)の決定的ロジックのテスト。
// ブラウザ操作(publish/insights)はサイト依存のためここでは扱わない。
// 実行: npm test
const test = require("node:test");
const assert = require("node:assert/strict");
const { selectHashtags, selectImage, normalizeTag, perfBonus } = require("../select");
const { analyze, median } = require("../analyze");
const { splitTitle } = require("../header-image");
const { toPlainParagraphs } = require("../publish");
const { parseText } = require("../lib/frontmatter");

const pool = {
  limits: { note: 3, ameba: 2 },
  always: ["学ジム"],
  tags: [
    { tag: "声かけ", keywords: ["声かけ", "NG例"] },
    { tag: "暗記", keywords: ["暗記", "覚えられない"] },
    { tag: "英語学習", keywords: ["英語"] },
    { tag: "スマホ依存", keywords: ["スマホ"], platforms: ["ameba"] },
  ],
};
const article = (front = {}, title = "暗記が苦手な子への声かけ", body = "暗記のコツ。声かけのNG例。") =>
  ({ front: { subject: "暗記と声かけ", ...front }, title, body });

test("記事に関連するタグをスコア順に選び、毎回付けるタグを先頭にして上限で切る", () => {
  const r = selectHashtags(article(), "note", { pool });
  assert.deepEqual(r.tags, ["学ジム", "声かけ", "暗記"]);
  assert.ok(!r.tags.includes("英語学習"), "本文に無いタグは選ばない");
});

test("Amebaは上限2個、platforms指定のタグはそのプラットフォームでのみ候補になる", () => {
  const a = article({ subject: "スマホ" }, "スマホばかりの子", "スマホ スマホ スマホ");
  assert.deepEqual(selectHashtags(a, "ameba", { pool }).tags, ["学ジム", "スマホ依存"]);
  assert.deepEqual(selectHashtags(a, "note", { pool }).tags, ["学ジム"]);
});

test("frontmatterのhashtags指定は最優先(#や重複を取り除いてそのまま使う)", () => {
  const r = selectHashtags(article({ hashtags: ["#受験", "受験", "親子"] }), "note", { pool });
  assert.deepEqual(r.tags, ["受験", "親子"]);
});

test("下書き時のAI提案候補はプールに無いタグでも候補になる", () => {
  const r = selectHashtags(article({ hashtag_candidates: ["記憶術"] }), "note", { pool: { ...pool, limits: { note: 5 } } });
  assert.ok(r.tags.includes("記憶術"));
});

test("過去実績の良いタグが、関連度が同程度のタグより上に来る", () => {
  const a = article({}, "声かけと暗記", "");
  const base = selectHashtags(a, "note", { pool }).tags;
  assert.deepEqual(base, ["学ジム", "暗記", "声かけ"]); // 同点はタグ名順
  const perf = { hashtags: { note: { 声かけ: { samples: 4, score: 1.8 } } } };
  assert.deepEqual(selectHashtags(a, "note", { pool, perf }).tags, ["学ジム", "声かけ", "暗記"]);
});

test("実績ボーナスはサンプル2件未満なら効かず、上下限がある", () => {
  assert.equal(perfBonus({ samples: 1, score: 5 }), 0);
  assert.equal(perfBonus({ samples: 3, score: 5 }), 3);
  assert.equal(perfBonus({ samples: 3, score: 0 }), -2);
  assert.equal(normalizeTag(" ＃子育て "), "子育て");
});

test("画像: 指定があればそれを使い、カタログが空ならテンプレート背景(photo: null)", () => {
  assert.equal(selectImage(article({ header_image: "x.png" })).fixed, "x.png");
  const r = selectImage(article(), { catalog: { images: [] } });
  assert.equal(r.photo, null);
});

test("画像: 関連する写真を選び、直近で使った写真は避ける・存在しないファイルは除外", () => {
  const catalog = { images: [
    { file: "03_assets/creative-templates/note-header.html", keywords: ["暗記"] },
    { file: "03_assets/creative-templates/reel-thumbnail.html", keywords: ["声かけ"] },
    { file: "03_assets/images/note_ameba/does-not-exist.jpg", keywords: ["暗記", "声かけ"] },
  ] };
  const a = article({}, "暗記と声かけ", "暗記");
  assert.equal(selectImage(a, { catalog }).photo, "03_assets/creative-templates/note-header.html");
  const r = selectImage(a, { catalog, recent: ["03_assets/creative-templates/note-header.html"] });
  assert.equal(r.photo, "03_assets/creative-templates/reel-thumbnail.html");
});

test("集計: URLのキー/タイトルで記事と数値を紐づけ、中央値=1.0で相対化する", () => {
  const now = new Date("2026-10-31T00:00:00Z");
  const mk = (file, title, extra) => ({ file, title, body: "", front: { published_at: "2026-10-01", ...extra } });
  const published = [
    mk("a.md", "記事A", { note_url: "https://note.com/x/n/nAAA", note_hashtags: ["声かけ"], image_source: "template" }),
    mk("b.md", "記事B", { note_hashtags: ["声かけ", "暗記"], image_source: "template" }),
    mk("c.md", "記事C", { note_hashtags: ["暗記"] }),
  ];
  const raw = { file: "2026-10-31.json", data: {
    note: { articles: [
      { key: "nAAA", title: "別タイトル", views: 300, likes: 30 },
      { key: "nBBB", title: "記事B", views: 100, likes: 10 },
      { key: "nCCC", title: "記事C", views: 200, likes: 20 },
      { key: "nZZZ", title: "無関係", views: 5, likes: 0 },
    ] },
    ameba: { articles: [] },
  } };
  const r = analyze({ raw, published, now });
  const idx = Object.fromEntries(r.articles.map((a) => [a.file, a.index.note]));
  assert.equal(idx["a.md"], 1.5);
  assert.equal(idx["b.md"], 0.5);
  assert.equal(idx["c.md"], 1);
  assert.deepEqual(r.unmatched.note, ["無関係"]);
  // 声かけ: (1.5+0.5+2)/(2+2)=1.0 / 暗記: (0.5+1+2)/(2+2)=0.875
  assert.equal(r.hashtags.note["声かけ"].score, 1);
  assert.equal(r.hashtags.note["暗記"].score, 0.875);
  assert.equal(r.images.template.samples, 2);
});

test("ユーティリティ", () => {
  assert.equal(median([3, 1, 2]), 2);
  assert.equal(median([0, null]), null);
  assert.deepEqual(splitTitle("見出し ― 補足です"), { title: "見出し", subtitle: "補足です" });
  assert.deepEqual(splitTitle("区切りなし"), { title: "区切りなし", subtitle: "" });
  assert.deepEqual(toPlainParagraphs("## 見出し\n\n**太字**です"), ["見出し", "太字です"]);
  const p = parseText("---\nstatus: review\n---\n\n# タイトル\n\n本文");
  assert.equal(p.title, "タイトル");
  assert.equal(p.body, "本文");
});

test("frontmatterの日付は文字列のまま書き戻す(2026-10-05T00:00:00.000Zに化けない)", () => {
  const os = require("os"), fs = require("fs"), path = require("path");
  const { writeFile, parseFile } = require("../lib/frontmatter");
  const p = parseText("---\ndate: 2026-10-05\napproved_by:\n---\n\n# T\n\nB");
  assert.equal(p.front.date, "2026-10-05");
  const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "fm-")), "x.md");
  writeFile(tmp, p.front, p.title, p.body);
  assert.match(fs.readFileSync(tmp, "utf8"), /^date: '?2026-10-05'?$/m);
  assert.equal(parseFile(tmp).front.date, "2026-10-05");
});

test("HTMLコメント(内部メモ)は投稿本文に含めない", () => {
  assert.deepEqual(toPlainParagraphs("<!-- 内部メモ\n複数行 -->\n\n本文"), ["本文"]);
});

test("ログイン状態: 対象サイトのCookieだけを残し、gzip+base64で往復できる", () => {
  const { filterState, encodeState, decodeState } = require("../lib/session");
  const state = { cookies: [
    { name: "a", domain: ".note.com" }, { name: "b", domain: "google.com" },
    { name: "c", domain: ".ameba.jp" }, { name: "d", domain: "ameblo.jp" },
  ], origins: [{ origin: "https://note.com", localStorage: [] }, { origin: "https://evil-note.com", localStorage: [] }] };
  const note = filterState(state, "note");
  assert.deepEqual(note.cookies.map((c) => c.name), ["a"]);
  assert.deepEqual(note.origins.map((o) => o.origin), ["https://note.com"]);
  assert.deepEqual(filterState(state, "ameba").cookies.map((c) => c.name), ["c", "d"]);
  assert.deepEqual(decodeState(encodeState(note)), note);
});

test("note公開APIの項目名の揺れ(camelCase/snake_case)を吸収する", () => {
  const { normalizeNote } = require("../lib/note-public");
  const a = normalizeNote({ key: "n1", name: "T", eyecatch: "https://x/y.png", likeCount: 3 }, "u");
  assert.equal(a.url, "https://note.com/u/n/n1");
  assert.equal(a.likes, 3);
  assert.equal(normalizeNote({ key: "n2", like_count: 5 }, "u").likes, 5);
});
