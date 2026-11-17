---
date: 2026-11-17
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset、edit-design等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  "canva autofill design brand template" 検索・`select:mcp__Canva__autofill-design` でも見つからず)、
  フィールド流し込みができないため生成を行わなかった。2026-11-10から8日連続。
- 本日の対象台本:
  - ①: `02_departments/instagram_tiktok/drafts/task-2026-11-17-ig-*.md` は存在しない。処理対象なし。
  - ③: `task-2026-11-17-sumaho-001.md` は `reel_format: canva_7rules`(「受験生の親が黙ってやってる7つのこと❤️」)で
    **本来は生成対象だった**。Autofillが使えれば生成していた。
  - 参考(台本側の書式): この台本は「## リール台本(カード型・7秒)」節・「- 」箇条書き7項目の形式で、
    手順書が想定する「## リール台本(〇選リスト型・Canva)」節・「①〜⑦」行の形式とは異なる。項目数は7個で一致。
    Autofill復旧後に読み取り手順の見直しが必要になる可能性あり。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
