---
date: 2026-11-16
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset、edit-design等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  "autofill" 検索・`select:mcp__Canva__autofill-design` でも見つからず)、フィールド流し込みができないため生成を行わなかった。
  2026-11-10から7日連続。
- 本日の対象台本:
  - ①: `02_departments/instagram_tiktok/drafts/task-2026-11-16-ig-*.md` は存在しない(`feed-2026-11-16-001.md` のみ)。
    Canva連携が使えた場合も①は処理対象なし。
  - ③: `task-2026-11-16-sumaho-001.md` は `reel_format: checkup`(「ご褒美依存度チェック」)で、canva_7rules形式ではないため対象外。
  - つまり本日はAutofillが使えた場合でも生成対象はなかった。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
