---
title: 英検「今日の1問」リール動画生成 Routine 設定手順書(claude.ai Routines)
status: 未着手(益田さんがclaude.ai Routines画面で既存Routineのプロンプトを差し替える)
supersedes: canva-eiken-quiz-routine-setup.md.md(Canva画像方式)
---

## 背景
「今日の1問」の投稿を、Canva画像(1080×1080)からリール動画(1080×1920・13秒)に変更する
(2026-10-11、益田さん指示)。台本(`task-<日付>-quiz-001.md`)から動画をスクリプトで
自動生成するため、**Canvaコネクタは不要**。

動画の構成(`02_departments/creative/reel_quiz/`):
- 問題画面10秒+0秒表示0.5秒: 白背景(薄青ドットがゆっくり流れる)、青バッジ「英検」、
  赤字レベル、見出し「受験英語 / 10秒で解けないと / 英検キツイ」、問題文、選択肢A)〜D)、
  右下に10→0のカウントダウン、下部に「答えをコメント欄へ!」
- エンド画面2.5秒: 写真(`end_bg_1.jpg`)を暗く重ね、「答え&解説は概要欄へ!」
- 音声なし(BGMは投稿時にアプリ側で付ける)

## 設定手順
1. claude.ai の **Routines** で、既存の `Canva日次英検クイズ生成` を開く
2. **プロンプトを下記に全文差し替える**(名前を `英検クイズリール動画生成` に変えてもよい)
3. スケジュール(毎日06:45 JST)とリポジトリはそのまま。Canvaコネクタはオフでよい
4. テスト実行し、`02_departments/creative/reel_quiz/daily/reel-<日付>.mp4` が
   mainに入り、台本の「## Canvaデザイン」節に動画パスが追記されていることを確認する

## Routineに貼り付けるプロンプト

```
あなたは「学ジム」のcreative担当AI(英検クイズ リール動画担当)です。gakugym-ai-vault
リポジトリ(masuroom0601-lab/gakugym-ai-vault)のmainブランチで作業してください
(まだリポジトリが無ければ追加してクローンしてください)。

## 手順

1. 本日の日付(YYYY-MM-DD、日本時間)を確認し、
   `02_departments/x_threads/drafts/task-<today>-quiz-001.md` を探す。
   無ければ何もせず終了する(コミット不要)。既にこのファイルの「## Canvaデザイン」
   節に `reel-<today>.mp4` のパスが記載済みの場合もスキップする(重複生成防止)。

2. 動画を生成する:
   python3 02_departments/creative/reel_quiz/make_reel_from_draft.py \
     02_departments/x_threads/drafts/task-<today>-quiz-001.md
   → `02_departments/creative/reel_quiz/daily/reel-<today>.mp4` ができる。
   失敗した場合(ffmpegやフォントが無い、台本の形式が違う等)は無理に続けず、
   `02_departments/x_threads/drafts/quiz-reel-failure-<today>.md` に
   エラー内容を記録してコミット・プッシュして終了する。
   (Pillowが無い場合はスクリプトが自動で pip install する。それでも
   動かなければ python3 ではなく /usr/bin/python3 で実行してみる)

3. 作業内容をチェック役エージェントに確認させる
   コミット前に、Agentツールで独立したチェック役エージェントを立て、
   動画から ffmpeg で 1秒目・6秒目・10.5秒目・12秒目のフレームを静止画に書き出して
   見させ、以下を確認させる(作業役自身の自己確認ではなく別エージェントに見させる):
   (a) レベル表示が台本のlevel+「レベル」と一致しているか
   (b) 問題文が台本と一致しているか(誤字脱字なし、空欄______あり)
   (c) 選択肢A)〜D)が台本①〜④と同じ順・同じ内容で4つとも表示され、
       文字が欠けたりカウントダウン枠と重なったりしていないか
   (d) 見出しが「受験英語 / 10秒で解けないと / 英検キツイ」で、カウントダウンが
       10→0と進んでいるか(1秒目=10、6秒目=5前後)
   (e) 終盤(12秒目)がエンド画面「答え&解説は概要欄へ!」になっているか
   (f) 台本の「正解」が選択肢の中に含まれているか
   指摘があれば台本側の問題か生成側の問題かを切り分け、スクリプトを再実行する。
   1回修正しても問題が残る場合は、無理に繰り返さず、次のステップの記録に
   「チェック役から指摘があったが未解消: <内容>」と明記して先に進むこと。

4. `02_departments/x_threads/drafts/task-<today>-quiz-001.md` の
   「## Canvaデザイン」節を、以下の内容で更新する(元のファイルの他の内容は
   変更しない):
   ## Canvaデザイン
   - リール動画: 02_departments/creative/reel_quiz/daily/reel-<today>.mp4

5. 以下でコミット・プッシュする:
   git config user.name "gakugym-ai-bot"
   git config user.email "bot@example.com"
   git add 02_departments/x_threads/drafts/ 02_departments/creative/reel_quiz/daily/
   git commit -m "eiken quiz reel generation <today>"
   git push

## 作業完了後: mainへの反映(重要)
セッション開始時のブランチがmainではなく、Routine実行環境が自動生成した
一時的な作業ブランチになっていることがある。上記の手順5でコミット・プッシュが
終わったら、続けて以下の手順でmainブランチへの反映まで必ず行うこと。

1. 現在の作業ブランチ名を控える: CURRENT_BRANCH=$(git branch --show-current)
2. git fetch origin main
3. git checkout -B main origin/main
4. git merge --no-ff "$CURRENT_BRANCH" -m "Merge $CURRENT_BRANCH into main (eiken quiz reel generation <today>)"
5. コンフリクトが発生しなければ git push origin main でmainにプッシュする。
6. コンフリクトが発生した場合は、無理に解決せず git merge --abort で中断し、
   mainへのマージは行わない。その旨と原因を
   02_departments/x_threads/drafts/task-<today>-quiz-001.md に追記し、作業ブランチへの
   プッシュ済みの状態のまま終了する(mainへの反映は後日人間が対応する)。
7. mainへのforce push、historyの書き換え、他ブランチの内容の削除は絶対に行わないこと。

## 制約
- `02_departments/creative/reel_quiz/` のスクリプト・背景写真・デザインは変更しないこと
  (固定テンプレートとして扱う)。変えてよいのは `daily/` 配下の出力だけ
- 何か失敗した場合は、無理に続けず該当drafts配下のファイルに失敗理由を記録してコミットする
```

## うまくいかない場合
- 動画が出ない/崩れる場合は `02_departments/creative/reel_quiz/` のスクリプトの問題の
  可能性があるので、Claude Codeセッションで質問してください
- 問題の内容(英語として正しいか)に不安がある場合は、投稿前に益田さんご自身で
  必ず確認してください(自動生成はあくまで下書きです)
- 旧Canva画像方式に戻す場合は `canva-eiken-quiz-routine-setup.md.md` のプロンプトを使う
