---
date: 2026-11-13
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、edit-design等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  "autofill-design" / "+Canva autofill" 検索でも見つからず)、フィールド流し込みができないため生成を行わなかった。
  2026-11-10から4日連続。
- 本日の対象台本: ①の `task-2026-11-13-ig-*.md` は存在せず(対象なし)。
  ③の `task-2026-11-13-sumaho-001.md` は `reel_format: canva_7rules`(タイトル「朝スマホをやめる受験生の7ルール」)で
  **生成対象だったが未生成**。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
