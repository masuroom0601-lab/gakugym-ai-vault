---
date: 2026-11-23
status: skipped
---
## Canva連携チェック結果
- Canva連携が利用できなかったため生成をスキップした。
- 詳細: Canva MCPのツール群(read-design、create-design-from-brand-template、get-brand-template-dataset等)は接続されていたが、
  必須の `autofill-design`(ブランドテンプレートAutofill)がツール一覧に存在せず(キーワード検索 `autofill-design canva` でも見つからず)、
  フィールド流し込みができないため生成を行わなかった。2026-11-10以降、継続して同じ状態。
- 本日の対象台本:
  - ①: `02_departments/instagram_tiktok/drafts/task-2026-11-23-ig-*.md` は存在しない。処理対象なし。
  - ③: `task-2026-11-23-sumaho-001.md` はfrontmatterに `reel_format: canva_7rules` があり項目は7個だが、本文は
    「## リール台本(カード型・7秒)」形式で、手順が想定する「## リール台本(〇選リスト型・Canva)」節や
    ①〜⑦の番号付き行の形式ではない(箇条書き「- ビリ:…→1位:…」)。Autofillが使える場合も節名・番号形式の整合確認が必要。
- 対応: Canva連携側でautofill系ツール(autofill-design)が有効になっているか確認してください
  (コネクタの再接続でスコープが付与される可能性あり)。
