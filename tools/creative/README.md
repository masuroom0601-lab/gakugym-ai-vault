# creative部署 画像レンダラー

`02_departments/creative/department.md` の「技術方式(最重要ルール)」を実装したツールです。
HTML/CSSテンプレート(`03_assets/creative-templates/`)は固定で、
このスクリプトは「テキストの中身」と「科目別配色パラメータ」だけを差し込んで
Playwright(ヘッドレスChromium)でPNG化します。AIはCSS自体を書き換えません。

## 使い方
```bash
cd tools/creative
npm install
npx playwright install --with-deps chromium   # 初回のみ
node render.js <spec.jsonのパス> <出力先ディレクトリ>
```

## spec.json のスキーマ
Instagram/TikTok担当の下書き(`02_departments/instagram_tiktok/drafts/task-*.md`)を、
creative担当(Claude)がこの形式のJSONに変換して
`02_departments/creative/drafts/<task_id>.spec.json` として保存する運用です。

```jsonc
{
  "task_id": "2026-09-11-ig-001",
  "subject": "総合型選抜対策",          // 科目カテゴリ。配色判定に使う
  "thumbnail": {
    "hype": "これ聞かれたら詰む",        // 煽り文句
    "headline": "面接で聞かれること",     // インパクト大文字
    "number": "5",                       // 本編の箇条書き数と必ず一致させる
    "swipe": "SWIPE >>>",                // 省略可
    "bg": null                            // 03_assets/images/backgrounds/ 内の相対パス。無ければグラデーション代替
  },
  "feed": {
    "template": "C",                      // "A"(和紙×手書き) | "B"(グラデーション) | "C"(紺×白アイコン)
    "slides": [
      { "role": "cover", "title": "総合型選抜\n面接直前にやるべきこと", "catch": "付け焼き刃の対策で、後悔しないために。" },
      { "role": "content", "title": "志望理由を「一言」で言えるか確認する", "body": "きみの言葉で30秒にまとめられないなら、\nまだ理解が浅いサイン。", "checklist": true },
      { "role": "closing", "title": "まとめ", "body": "①志望理由は一言で\n②経験は数字で語る\n③逆質問は3つ準備" }
    ]
  }
}
```

すべてのテンプレート共通で `page_number`/`total_pages` はrender.js側が
slides配列の位置から自動で埋め込む(spec.json側で指定する必要はない)。

### テンプレート固有のフィールド(2026-09-12: 過去の実投稿デザインに寄せて拡張)
- **A(和紙×手書き)**: `highlights`(bodyの中でマーカー風にハイライトしたいフレーズの配列。
  文字列の配列、または`{text, color}`。colorは red/yellow/green/purple)、`icon`(絵文字)
- **B(グラデーション)**: cover用の `number`(大きく出す数字、例:"5")、
  `category`(数字の右のピル文言、例:"教科別")。`catch`があれば下部に白いカードで表示、
  無ければ通常のicon+body表示になる
- **C(紺×白アイコン)**: cover用の `grid`(`{icon, label}`の配列、3〜9個。
  指定すると3x3のアイコンカードグリッドになる)、`eyebrow`(タイトル上の小さい前置き文言)、
  `accent`(titleの中で1色だけ変えたい部分文字列、例:"70")

## 出力
`<出力先>/<task_id>-thumbnail.png`、`<出力先>/<task_id>-feed-01.png` ...、
`<出力先>/<task_id>-render-report.json`(生成成功/失敗の一覧)。

## 文字数ルール
`validate.js` が縦4行まで/横17文字までを検証します(hp/department.mdのバナールールと同基準)。
超過したフィールドはレンダリングをスキップし、render-report.json の errors に理由が記録されます
(ワークフロー自体は失敗させず、校正担当・秘書担当が report を見て気づける形にしています)。

## 日本語フォントについて
テンプレートはGoogle Fonts(Noto Sans JP等)をCDN経由で読み込みますが、
CI環境でネットワークが使えない場合の文字化け(tofu)対策として、
`fonts-noto-cjk` をシステムフォントとしてインストールしておくことを前提にしています
(`.github/workflows/creative-pipeline.yml` 参照)。
