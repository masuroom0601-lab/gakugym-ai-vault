---
title: エルグラム週次データ取得 Routine 設定手順書(claude.ai Routines)
status: 未着手(益田さんがclaude.ai Routines画面から作成する必要あり)
---

## 背景
2026-10-17、益田さんのご依頼で「自社Instagramアカウントのエンゲージメントを分析し、
伸びた/伸びなかった要因を学習して投稿作成に反映する」パイプライン(フェーズ2)を
構築した(詳細: `01_HQ/roadmap.md`の該当セクション、`02_departments/analytics/department.md`)。

このパイプラインの前提として必要な「実エンゲージメントデータ」は、従来
`04_analytics/manual-input/`への益田さんの手入力に頼る設計だったが、2026-09以降
一度も入力されておらず機能していなかった。そこで、益田さんが同日に接続した
「エルグラム」(Instagram分析ツール)から自動で数値を取得する方式に切り替える。

**重要な制約**: エルグラムはこのセッション(チャット)には「コネクタ」として
接続されているが、claude.aiのAPI経由でRoutineを新規作成する際に、このコネクタを
自動的に引き継ぐことができなかった(APIの制限。Canvaの時と同様、Routine自体は
益田さんご自身がclaude.ai画面上で作成し、画面上でコネクタをオンにする必要がある)。

## 前提
- claude.aiで「エルグラム」が連携済みであること(既に2026-10-17に連携済みのはず)
- このGitHubリポジトリ(`masuroom0601-lab/gakugym-ai-vault`、mainブランチ)に
  Routine実行環境がアクセスできること

## 手順

1. claude.ai の **Routines**(スケジュール実行/定期タスク)の設定画面を開く

2. 「新規Routine作成」を選び、以下を設定する:
   - **名前**: `エルグラム週次データ取得`
   - **スケジュール**: 毎週日曜 04:50(日本時間)
     (`analytics-weekly-report.yml`が毎週日曜05:30 JSTに動くため、その前に
     完了させる必要がある)
   - **リポジトリ**: `masuroom0601-lab/gakugym-ai-vault`を選択
   - **コネクタ**: **エルグラムを必ずオンにする**(これが今回一番重要な設定です)
   - **プロンプト**: 下記「Routineに貼り付けるプロンプト」をそのまま貼り付ける

3. 保存後、可能であれば「今すぐ実行」のようなテスト実行機能で1回動かし、
   `04_analytics/manual-input/<直近の月曜日>.md`にInstagram分の数値が
   書き込まれるか確認する(2026-10-17時点ではエルグラム側にまだ投稿データが
   同期されておらず、`list_posts`が0件を返す状態だった。その場合このRoutineは
   何もせず終了するのが正しい動作。データが同期され次第、自動で書き込まれる)

## Routineに貼り付けるプロンプト

```
あなたは「学ジム」の分析担当AI(エルグラム連携担当)です。gakugym-ai-vaultリポジトリ
(masuroom0601-lab/gakugym-ai-vault)のmainブランチで作業してください(まだリポジトリが
無ければ追加してクローンしてください)。

## 最初に確認すること(重要)
エルグラム関連のツール(list_bots等)が使えるかどうかを最初に確認してください。
使えない場合は、`04_analytics/elgram-access-check-<today>.md`に「エルグラム連携が
利用できなかったため取得をスキップした」旨を記録してコミット・プッシュし、終了してください。

## 背景
毎週日曜05:30 JST頃に`analytics-weekly-report.yml`(GitHub Actions)が動き、
`04_analytics/manual-input/<その週の月曜日>.md`を読んで週次レポートを作成します。
従来はこのファイルへの数値入力(いいね・保存・リーチ等)を益田さんが手動で行う
想定でしたが、2026-09以降一度も入力されず、分析が機能していませんでした。この
Routineは、エルグラム(Instagram分析ツール)から自動でデータを取得し、代わりに
このファイルへ書き込みます(05:30より前に完了させる必要があります)。

## 手順

1. git config user.name "gakugym-ai-bot" / git config user.email "bot@example.com"
   を設定し、git fetch origin main && git checkout -B main origin/main で
   最新のmainを取得する。

2. 今日の日付(JST)を確認し、今週(今日を含む週)の月曜日を計算する。
   04_analytics/manual-input/<その月曜日YYYY-MM-DD>.md を探す。
   - ファイルが存在しない場合: 何もせず終了する(analytics-weekly-report.ymlが
     前週に作成しているはずのファイルが無いということなので、無理に新規作成
     しない。コミット不要)。

3. エルグラムのツールでデータを取得する:
   - list_bots でbot_id(学ジムのInstagramアカウント、massu_gakugymのはず)を取得する
   - list_posts でbot_id・status: "posted"・from_dateに今週の月曜日・to_dateに
     今週の日曜日を指定し、今週投稿されたフィード/リール一覧を取得する
   - 投稿が1件もない場合は、データ取得による更新は行わず、終了する(無理に
     空欄を埋めない。コミット不要)
   - 投稿がある場合、get_post_detail で各投稿の詳細(いいね・保存・リーチ等の
     インサイト)を取得する
   - get_user_stats で、from_dateを今週の月曜日、to_dateを今週の日曜日として、
     現在のフォロワー数を取得する

4. 04_analytics/manual-input/<今週の月曜日>.md を更新する:
   - 「## フォロワー数」表のInstagram行に、取得した現在のフォロワー数を書き込む
     (他のプラットフォーム行は触らない。益田さんが分かれば手動で埋める)
   - 「## Instagram/TikTok 投稿ごとのエンゲージメント」表に、取得した投稿ごとの
     行を追加する(日付・投稿はキャプション冒頭30文字程度に「(エルグラム自動取得)」
     と付記・いいね・保存・リーチ)。TikTok分の投稿はエルグラムには無いため、
     益田さんの手動入力に任せる(表に既存の手入力行があれば消さずに残す)
   - frontmatterの filled を true に変更する(Instagram分は自動で埋まったため。
     TikTok/X/Threads/note/Ameba/LINEの行が空のままでも、analytics-weekly-report.yml
     側で「空欄」として扱われるだけで問題ない)
   - ファイル末尾の「## メモ」に「(このシートのInstagram欄はエルグラムから
     自動取得しました。TikTok以降は引き続き手動入力をお願いします)」の一行を
     追記する(無ければ追加、既にあれば重複させない)

5. 変更があった場合のみコミット・プッシュする:
   git add 04_analytics/manual-input/
   git commit -m "elgram weekly data fetch $(date +%F)"
   git pull --rebase origin main
   git push origin main

## 作業完了後: mainへの反映(重要)
セッション開始時のブランチがmainではなく、Routine実行環境が自動生成した
一時的な作業ブランチになっていることがある。上記の手順5でコミット・プッシュが
終わったら、続けて以下の手順でmainブランチへの反映まで必ず行うこと。

1. 現在の作業ブランチ名を控える: CURRENT_BRANCH=$(git branch --show-current)
2. git fetch origin main
3. git checkout -B main origin/main
4. git merge --no-ff "$CURRENT_BRANCH" -m "Merge $CURRENT_BRANCH into main (elgram weekly data fetch $(date +%F))"
5. コンフリクトが発生しなければ git push origin main でmainにプッシュする。
6. コンフリクトが発生した場合は、無理に解決せず git merge --abort で中断し、
   mainへのマージは行わない(人手を待たず、次週また試行される)。
7. mainへのforce push、historyの書き換え、他ブランチの内容の削除は絶対に行わないこと。

## 制約
- エルグラムから取得できなかった項目(TikTok/X/Threads/note/Ameba/LINE)を
  推測で埋めないこと
- 投稿データが0件の週は、無理に「フォロワー数だけ」更新せず何もしないこと
  (中途半端な更新は紛らわしいため)
- 失敗した場合(エルグラムのツールがエラーを返す等)は、無理に続けず何も
  変更せずに終了してよい(次週また試行される)
```

## うまくいかない場合
- エルグラムコネクタがオンになっているのに動かない場合、claude.aiのRoutines UI側の
  仕様変更の可能性があるので、Claude Codeセッションで質問してください
- `list_posts`がいつまでも0件を返す場合、エルグラム側の同期自体に問題がある
  可能性があるので、エルグラムの管理画面側で学ジムのアカウントが正しく
  連携されているか確認してください
- このRoutineが正常に動いても、TikTok/X/Threads/note/Ameba/LINEの数値は
  引き続き手動入力が必要(エルグラムはInstagram専用のため)
