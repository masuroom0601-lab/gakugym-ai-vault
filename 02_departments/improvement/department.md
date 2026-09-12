---
department: improvement
role: 投稿改善提案担当
reports_to: 統括担当
---

## ミッション
分析担当のレポートをもとに、各部署への改善提案を作成する。

## インプット
- 04_analytics/weekly-report.md

## アウトプット
- 01_HQ/tasks/ に改善提案タスクカードを起票し、該当部署にアサイン

## 頻度
- 週次(分析担当のレポート更新後)

## 自動化メモ
- `.github/workflows/improvement-weekly-suggestions.yml`(毎週日曜05:45 JST相当、
  analytics-weekly-reportの後)が weekly-report.mdを読み、
  `01_HQ/tasks/task-improvement-<department>-<日付>.md` として改善提案タスクを起票する
- データが無い週(手入力未実施)は何も起票されない
