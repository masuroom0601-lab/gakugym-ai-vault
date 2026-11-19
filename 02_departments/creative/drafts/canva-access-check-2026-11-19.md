---
date: 2026-11-19
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset、edit-design等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  "+Canva autofill" 検索・`select:mcp__Canva__autofill-design` でも見つからず)、
  フィールド流し込みができないため生成を行わなかった。2026-11-10から10日連続。
- 本日の対象台本:
  - ①: `02_departments/instagram_tiktok/drafts/task-2026-11-19-ig-*.md` は存在しない。処理対象なし。
  - ③: `task-2026-11-19-sumaho-001.md` は `reel_format: canva_7rules`(「学年1位が守ってる帰宅後ルール7選」)で本来は対象。
    ただし台本の書式がRoutine手順の想定と異なる点に注意: 節名が「## リール台本(〇選リスト型・Canva)」ではなく
    「## リール台本(カード型・7秒)」、項目も「①〜⑦」で始まる行ではなく「- 」箇条書き7行(項目数は7個で正しい)。
    Autofill再開時は、この書式差をどう扱うか(①〜⑦を付番して流し込む等)を手順側で明確化しておくとよい。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
