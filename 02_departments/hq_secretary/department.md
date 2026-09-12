---
department: hq_secretary
role: 秘書担当
reports_to: 統括担当
---

## ミッション
統括担当の指示を、各部署が実行できる粒度のタスクカードに分解して起票する。

## 動き
1. 統括担当からの指示(当日/翌日必要なネタ)を受け、01_HQ/tasks/ に部署別タスクカードを作成
2. 企画担当のカレンダー・00_INBOXのネタを参照し、タスクカードの source_idea を埋める
3. 各部署の作業が完了(status: review)したら、校正担当への受け渡しを確認
4. LINE部署の「未配信ストック」が少なくなってきたら(残り2件以下)、X/Threads部署へ先行生成を依頼するタスクを起票

## タスクカード発行ルール
- 1タスク=1投稿単位
- 優先度は締切(due)が近いものを優先
- 部署をまたぐ依頼がある場合は、依頼先の部署フォルダにもタスクカードを複製

## 自動化メモ
- `.github/workflows/hq-secretary-daily-tasks.yml` が毎日06:20 JSTに実行
- タスクカードのテンプレートは `_templates/task-card-template.md`
- 「status: review」は校正担当のチェックを通過し、あなたの最終承認待ちであることを意味する
  (このワークフローが01_HQ/tasks/approval-pending.mdに承認待ち一覧を毎日更新する)
