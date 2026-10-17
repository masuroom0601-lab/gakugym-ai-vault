---
department: note_ameba
role: note/Amebaの週次インサイトから得た改善指示
last_update: なし(2026-10-17新設、データ未収集)
---

# note/Amebaの改善指示(週次インサイト分析から自動更新)

毎週日曜05:00 JSTに `note-ameba-weekly-insights.yml` が note/Amebaの数値
(記事ごとのビュー・スキ/いいね・コメント)を収集・分析し、このファイルを更新します。
月曜の記事生成(`note-ameba-weekly-draft.yml`)は、記事を書く前に必ずこのファイルを読み、
「次回記事への改善指示(最新)」を反映します。
department.md・brand-guide.md と矛盾する場合は、そちらのルールを優先します。

数値の詳細: `04_analytics/note_ameba/weekly-report.md`(最新)、
`04_analytics/note_ameba/history/`(過去分)、`04_analytics/note_ameba/performance.json`(集計値)

## 次回記事への改善指示(最新)
(まだデータがありません。note/Amebaのログイン情報がGitHub Actions secretsに設定され、
公開記事の数値が集まり次第、ここに具体的な改善指示が書かれます。)

## 改善の履歴
- 2026-10-17: ファイル新設
