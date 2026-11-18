---
date: 2026-11-18
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset、edit-design等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  "canva autofill design" 検索・`select:mcp__Canva__autofill-design` でも見つからず)、
  フィールド流し込みができないため生成を行わなかった。2026-11-10から9日連続。
- 本日の対象台本:
  - ①: `02_departments/instagram_tiktok/drafts/task-2026-11-18-ig-*.md` は存在しない。処理対象なし。
  - ③: `task-2026-11-18-sumaho-001.md` は `reel_format: checkup`(「スマホの定位置チェック」)で、
    `canva_7rules` ではないため本来も対象外。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
