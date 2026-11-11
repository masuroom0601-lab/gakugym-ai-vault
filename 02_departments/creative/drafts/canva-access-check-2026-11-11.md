---
date: 2026-11-11
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(ToolSearchの
  完全名指定でも見つからず)、フィールド流し込みができないため、①(EAHXtgN-KXU)・③(EAHZNFA_vrc)とも
  生成を行わなかった。2026-11-10に続き2日連続。
- 本日の対象台本: ①の `task-2026-11-11-ig-*.md` は存在せず(対象なし)。
  ③の `task-2026-11-11-sumaho-001.md`(reel_format: canva_7rules)は存在するが未生成。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
