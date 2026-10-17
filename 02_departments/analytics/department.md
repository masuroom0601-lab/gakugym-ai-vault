---
department: analytics
role: 分析担当
reports_to: 統括担当
---

## ミッション
各媒体の数値を収集し、他部署が使える形でレポート化する。さらに、蓄積したデータから
「何が伸び/伸び悩みの要因だったか」を分析・学習し、各部署の投稿作成が自己改善して
いくための知見としてフィードバックする(2026-10-17、ミッション拡張)。

## データ取得方法
- Instagram/Threads/YouTube/LINE: 各公式Insight/Analytics APIから自動取得(予定。
  現時点ではAPIトークン未設定のため未稼働)
- X/note/Ameba: 公式APIなしのため、あなたが手動で数値をメモした値を04_analytics/に入力する運用
- **【2026-10-17時点の重要な注記】** 上記いずれも、`04_analytics/manual-input/`への
  週次手入力が2026-09以降一度も行われていないため、**実エンゲージメントデータは
  現状まだ存在しない**。この状態が続く限り、下記「学習済みパターン」の
  エンゲージメントベースの知見は空のまま。益田さんの入力が再開/継続されない限り、
  このミッションの後半(分析・学習)は実質的に機能しない点を認識しておくこと

## アウトプット
- 04_analytics/weekly-report.md: 週次で「投稿ごとのエンゲージメント」「フォロワー増減」「伸びた型・テーマ」をまとめる
- 月次では上記を集計し、傾向をサマリ化
- **02_departments/analytics/learned-patterns.md**(2026-10-17新設): 週次レポート・
  過去履歴から「伸びる型・テーマ」の知見を蓄積するファイル。各部署の台本生成
  ワークフローが参照する。データ不足時は断定的な結論を書かないこと(詳細は
  `.github/workflows/analytics-pattern-learning.yml`参照)

## 申し送り先
- 投稿改善提案担当(伸び筋の材料を渡す)
- 企画担当(テーマ選定の参考情報を渡す)
- Instagram/TikTok部署・X/Threads部署(learned-patterns.md経由で、台本生成時に
  自動で参照される)

## 自動化メモ
- `.github/workflows/analytics-weekly-report.yml`(毎週日曜05:30 JST相当)が
  `04_analytics/manual-input/<週の月曜日>.md` を読んでweekly-report.mdを更新し、
  翌週分の入力シートを新規作成する
- `.github/workflows/analytics-monthly-summary.yml`(毎月1日)が
  `04_analytics/history/` を月次集計する
- **`.github/workflows/analytics-pattern-learning.yml`(2026-10-17新設)**: 
  `analytics-weekly-report`の完了を検知して自動実行(`workflow_run`トリガー)。
  週次レポート・履歴から傾向を分析し、`learned-patterns.md`に知見を追記する。
  実データの合計投稿件数が一定数(目安10件)に満たない場合は分析をスキップし、
  ファイルを荒らさない設計にしている
- Instagram/Threads/YouTube/LINEの公式APIトークンは未設定のため、現状は
  `04_analytics/manual-input/` への手入力がすべての情報源(益田さんが投稿の都度入力)。
  トークン設定後はAPI自動取得を追加予定(`01_HQ/roadmap.md` Phase5参照。
  これが整えば`manual-input`依存を解消でき、学習パイプラインが本格稼働する)
