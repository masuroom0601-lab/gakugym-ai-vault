---
date: 2026-11-20
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset、edit-design等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(`select:mcp__Canva__autofill-design` でも見つからず)、
  フィールド流し込みができないため生成を行わなかった。2026-11-10から11日連続。
- 本日の対象台本:
  - ①: `02_departments/instagram_tiktok/drafts/task-2026-11-20-ig-*.md` は存在しない(feed-2026-11-20-001.md のみ)。処理対象なし。
  - ③: `task-2026-11-20-sumaho-001.md` は `reel_format: checkup`(「三日坊主脳チェック」)のため対象外。
  - したがって本日はAutofillが使えたとしても生成対象はなかった。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
