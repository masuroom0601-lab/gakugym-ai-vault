---
date: 2026-11-21
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(`select:mcp__Canva__autofill-design` でも見つからず)、
  フィールド流し込みができないため生成を行わなかった。2026-11-10から12日連続。
- 本日の対象台本:
  - ①: `02_departments/instagram_tiktok/drafts/task-2026-11-21-ig-*.md` は存在しない(feed-2026-11-21-001.md のみ)。処理対象なし。
  - ③: `task-2026-11-21-sumaho-001.md` はfrontmatterに `reel_format: canva_7rules` があるが、本文は
    「## リール台本(カード型・7秒)」形式(見出し3つ×各3項目=9項目)で、手順が想定する
    「## リール台本(〇選リスト型・Canva)」節および①〜⑦の7項目が存在しない。Autofillが使えたとしても
    項目数不一致(7個固定のルール)のため生成対象外。また校正で【要修正】(まとめの「9割の人は〜」の断定表現)が付いており status: draft のまま。
  - テンプレート `EAHZNFA_vrc` の想定形式と台本側の形式がずれているため、sumaho_habit側の台本フォーマットか本手順のどちらかを揃える必要あり。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
