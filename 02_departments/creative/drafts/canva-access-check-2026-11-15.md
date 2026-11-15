---
date: 2026-11-15
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  "autofill-design" 検索・`select:mcp__Canva__autofill-design` でも見つからず)、フィールド流し込みができないため生成を行わなかった。
  2026-11-10から6日連続。
- 本日の対象台本:
  - ①: `task-2026-11-15-ig-001.md` は存在するが、`type: 今週の1問まとめ`(`feed_type: weekly`、フィード用スライドJSON)で、
    リール本編「10選」形式の台本ではない。Canva連携が使えた場合も①のリール生成対象外だった可能性が高い。
  - ③: `task-2026-11-15-sumaho-001.md` は `reel_format: canva_7rules`(タイトル「直前期のスマホの誘惑に勝つ7ルール」)で
    **本来は生成対象**。Autofill不可のため未生成。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
