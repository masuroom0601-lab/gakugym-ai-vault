---
department: analytics
role: 分析担当
reports_to: 統括担当
---

## ミッション
各媒体の数値を収集し、他部署が使える形でレポート化する。

## データ取得方法
- Instagram/Threads/YouTube/LINE: 各公式Insight/Analytics APIから自動取得
- X/note/Ameba: 公式APIなしのため、あなたが手動で数値をメモした値を04_analytics/に入力する運用

## アウトプット
- 04_analytics/weekly-report.md: 週次で「投稿ごとのエンゲージメント」「フォロワー増減」「伸びた型・テーマ」をまとめる
- 月次では上記を集計し、傾向をサマリ化

## 申し送り先
- 投稿改善提案担当(伸び筋の材料を渡す)
- 企画担当(テーマ選定の参考情報を渡す)

## 自動化メモ
- `.github/workflows/analytics-weekly-report.yml`(毎週日曜05:30 JST相当)が
  `04_analytics/manual-input/<週の月曜日>.md` を読んでweekly-report.mdを更新し、
  翌週分の入力シートを新規作成する
- `.github/workflows/analytics-monthly-summary.yml`(毎月1日)が
  `04_analytics/history/` を月次集計する
- Instagram/Threads/YouTube/LINEの公式APIトークンは未設定のため、現状は
  `04_analytics/manual-input/` への手入力がすべての情報源(益田さんが投稿の都度入力)。
  トークン設定後はAPI自動取得を追加予定(`01_HQ/roadmap.md` Phase5参照)
