---
title: 英検「今日の1問」画像生成 Routine 設定手順書(claude.ai Routines)
status: 未着手(益田さんがclaude.ai Routines画面から設定)
---

## 背景
X/Threadsの投稿方針を、2026-09-22付けで従来のテキスト型3種から「今日の1問」
(英検クイズ画像)に全面切り替えした(詳細: `02_departments/x_threads/department.md`)。
問題文・選択肢・正解は`x-threads-daily-draft.yml`(GitHub Actions)が毎朝作成するが、
画像化にはCanva連携が必要なため、リール・フィードと同じくclaude.aiのRoutine機能を使う。

マスターテンプレート: `DAHV4YSYYb8`(1080×1080、白背景+青バッジ「英検」+
赤字レベル表示+黒太字の問題文・選択肢。詳細: `02_departments/creative/department.md`参照)

## 前提
- claude.aiでCanvaが連携済みであること
- リール/フィード用Routineが既に動いていること(同じ仕組みをもう1つ作る)

## 手順

1. claude.ai の **Routines** 設定画面を開く

2. 「新規Routine作成」を選び、以下を設定する:
   - **名前**: `Canva日次英検クイズ生成`
   - **スケジュール**: 毎日 06:25(日本時間)(リール06:15・フィード06:20と
     重ならないようにずらす)
   - **リポジトリ**: `masuroom0601-lab/gakugym-ai-vault`を選択
   - **コネクタ**: **Canva を必ずオンにする**
   - **プロンプト**: 下記「Routineに貼り付けるプロンプト」をそのまま貼り付ける

3. 保存後、テスト実行機能で1回動かし、`02_departments/x_threads/drafts/` の
   該当ファイルに Canva編集URL が追記されているか確認する

## Routineに貼り付けるプロンプト

```
あなたは「学ジム」のcreative担当AI(英検クイズ画像担当)です。gakugym-ai-vault
リポジトリ(masuroom0601-lab/gakugym-ai-vault)のmainブランチで作業してください
(まだリポジトリが無ければ追加してクローンしてください)。

## 最初に確認すること(重要)
Canva関連のツール(read-design, copy-design, edit-design等)が使えるかどうかを
最初に確認してください。使えない場合は、以下の手順を実行せず、
`02_departments/x_threads/drafts/quiz-canva-access-check-<today>.md` に
「Canva連携が利用できなかったため生成をスキップした」旨を記録してコミット・プッシュし、
終了してください。

## 手順

1. 本日の日付(YYYY-MM-DD)を確認し、
   `02_departments/x_threads/drafts/task-<today>-quiz-001.md` を探す。
   無ければ何もせず終了する(コミット不要)。既にこのファイルの「## Canvaデザイン」
   節にCanva編集URLが記載済みの場合もスキップする(重複生成防止)。

2. そのファイルから以下を読み取る:
   - level(準2級/準2級プラス/2級/準1級のいずれか)
   - 問題文(空欄を______で示す英文)
   - 選択肢①〜④

3. マスターテンプレート DAHV4YSYYb8 を copy-design で複製する(背景の色・
   バッジの位置やデザインは一切変更しない。変えるのはテキストのみ)。
   複製後、read-design(open_transaction: true)でテキスト要素を確認し、
   以下を差し替える:
   - レベル文字(赤字、例:「準2級レベル」): 台本のlevelに「レベル」を
     付けた文字列に差し替える
   - 問題文(黒太字): 台本の問題文にそのまま差し替える。文字数が長く
     明らかにはみ出す場合は、意味を変えない範囲でフォントサイズを
     やや小さくしてよい(format_textで調整。ただし極端な縮小は避ける)
   - 選択肢(黒太字、①〜④の4行): 台本の4択にそのまま差し替える
   - バッジの「英検」文字・バッジの色・位置は変更しないこと
   問題なければ finalize: "commit" で確定する。

4. 作業内容をチェック役エージェントに確認させる
   コミット前に、Agentツールで独立したチェック役エージェントを立て、以下を
   確認させること(作業役自身の自己確認ではなく、別エージェントに見させることで
   見落としを減らす):
   (a) read-designのサムネイルで見て、レベル・問題文・選択肢が台本の内容と
       一致しているか(誤字脱字含む)
   (b) 選択肢が①②③④の4つとも表示されているか、文字が欠けたりはみ出したり
       していないか
   (c) 台本の「正解」が実際にその選択肢の中に含まれているか(選択肢の転記ミスで
       正解が消えていないか)
   チェック役から指摘があれば該当箇所を修正し、finalize: "commit" で確定し直す。
   1回修正しても問題が残る場合は、無理に繰り返さず、次のステップの記録に
   「チェック役から指摘があったが未解消: <内容>」と明記して先に進むこと。

5. `02_departments/x_threads/drafts/task-<today>-quiz-001.md` の
   「## Canvaデザイン」節を、以下の内容で更新する(元のファイルの他の内容は
   変更しない):
   ## Canvaデザイン
   - <copy-designで作った新デザインのedit_url>

6. 以下でコミット・プッシュする:
   git config user.name "gakugym-ai-bot"
   git config user.email "bot@example.com"
   git add 02_departments/x_threads/drafts/
   git commit -m "canva eiken quiz generation <today>"
   git push

## 作業完了後: mainへの反映(重要)
セッション開始時のブランチがmainではなく、Routine実行環境が自動生成した
一時的な作業ブランチになっていることがある。上記の手順6でコミット・プッシュが
終わったら、続けて以下の手順でmainブランチへの反映まで必ず行うこと。

1. 現在の作業ブランチ名を控える: CURRENT_BRANCH=$(git branch --show-current)
2. git fetch origin main
3. git checkout -B main origin/main
4. git merge --no-ff "$CURRENT_BRANCH" -m "Merge $CURRENT_BRANCH into main (canva eiken quiz generation <today>)"
5. コンフリクトが発生しなければ git push origin main でmainにプッシュする。
6. コンフリクトが発生した場合は、無理に解決せず git merge --abort で中断し、
   mainへのマージは行わない。その旨と原因を
   02_departments/x_threads/drafts/task-<today>-quiz-001.md に追記し、作業ブランチへの
   プッシュ済みの状態のまま終了する(mainへの反映は後日人間が対応する)。
7. mainへのforce push、historyの書き換え、他ブランチの内容の削除は絶対に行わないこと。

## 制約
- マスターテンプレート(DAHV4YSYYb8)の背景色・バッジの位置やデザイン・フォントは
  変更しないこと(固定テンプレートとして扱う)
- 何か失敗した場合(台本が無い、Canvaでの編集に失敗した等)は、無理に続けず
  該当drafts配下のファイルに失敗理由を記録してコミットする
```

## うまくいかない場合
- リール・フィード用Routineと同様、Canvaコネクタがオンになっているのに
  動かない場合はUIの仕様変更の可能性があるのでClaude Codeセッションで質問してください
- 問題の内容(英語として正しいか)に不安がある場合は、益田さんが投稿前に必ず
  ご自身で確認してください(自動生成はあくまで下書きです)
