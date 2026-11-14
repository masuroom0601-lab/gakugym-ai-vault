---
date: 2026-11-14
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  "autofill-design" 検索でも見つからず)、フィールド流し込みができないため生成を行わなかった。
  2026-11-10から5日連続。
- 本日の対象台本: ①の `task-2026-11-14-ig-*.md` は存在せず(対象なし)。
  ③の `task-2026-11-14-sumaho-001.md` は `reel_format: checkup`(タイトル「LINE気にしすぎ度チェック」)のため
  対象外。したがって本日はCanva連携が使えたとしても生成対象はなかった。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
