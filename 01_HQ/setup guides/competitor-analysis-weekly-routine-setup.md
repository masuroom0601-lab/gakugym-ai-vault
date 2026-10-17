---
title: 週次競合分析 Routine 設定手順書(claude.ai Routines)
status: 未着手(益田さんがclaude.ai Routines画面から作成する必要あり)
---

## 背景
2026-10-17、益田さんのご依頼で「Instagram/TikTokの競合分析を週1回自動で行い、
必要なら制作マニュアルの改善につなげる」仕組み(フェーズ3)を構築した。

同日、vidIQ連携ツールを使って手動で競合分析を1回実施し
(`02_departments/analytics/learned-patterns.md`「競合アカウント分析に基づく知見」節)、
対象アカウントを`02_departments/analytics/competitor-accounts.yml`に保存した。

**重要な制約**: vidIQはエルグラムと同様、このチャットセッション専用のMCPコネクタであり、
GitHub Actionsからは直接呼び出せない。また、claude.aiのRoutineをAPI経由で新規作成する際、
このセッションが持つコネクタの権限を自動的に引き継ぐことができない(エルグラム導入時に
判明した既知の制約)。

**2026-10-17追記**: 一度このセッションが`create_trigger`でRoutine本体を作成してみたが、
益田さんの画面の「スケジュール済みタスク」一覧に表示されず、コネクタのON/OFF操作も
できなかった(セッションに紐づく特殊な種類のRoutineになってしまったためと推測)。
このため削除し、エルグラムの時と同様、**益田さんご自身がclaude.ai画面上でRoutineを
新規作成し、画面上でvidIQコネクタを手動でオンにする**方式に統一する。

## 前提
- claude.aiで「vidIQ」が連携済みであること
- このGitHubリポジトリ(`masuroom0601-lab/gakugym-ai-vault`、mainブランチ)に
  Routine実行環境がアクセスできること
- vidIQの利用クレジット残高に余裕があること(1回の実行で40〜50クレジット程度消費する設計)

## 手順

1. claude.ai の **Routines**(スケジュール済みタスク)の設定画面を開く

2. 「新規Routine作成」を選び、以下を設定する:
   - **名前**: `週次競合分析`
   - **スケジュール**: 毎週日曜 02:53(日本時間)
     (03:00ちょうどだと他の処理と重なりやすいため、あえて7分早めてある。
     `analytics-weekly-report.yml`の05:30、エルグラムRoutineの04:50より前に完了する)
   - **リポジトリ**: `masuroom0601-lab/gakugym-ai-vault`を選択
   - **コネクタ**: **vidIQを必ずオンにする**(これが今回一番重要な設定です)
   - **プロンプト**: 下記「Routineに貼り付けるプロンプト」をそのまま貼り付ける

3. 保存後、可能であれば「今すぐ実行」で1回動かし、vidIQツールが使え、
   `learned-patterns.md`に新しい日付の段落が追記されるか確認する

## Routineに貼り付けるプロンプト

```
あなたは「学ジム」の分析担当AI(競合分析担当)です。gakugym-ai-vaultリポジトリ
(masuroom0601-lab/gakugym-ai-vault)のmainブランチで作業してください(まだリポジトリが
無ければ追加してクローンしてください)。

## 最初に確認すること(重要)
1. vidIQ関連のツール(vidiq_balance, vidiq_ig_profile_reels等)が使えるかどうかを
   最初に確認してください。使えない場合は、
   `02_departments/analytics/competitor-analysis-access-check-<today>.md`に
   「vidIQ連携が利用できなかったため分析をスキップした」旨を記録してコミット・プッシュし、
   終了してください。
2. vidiq_balance でクレジット残高を確認してください。50クレジット未満の場合、
   無理に実行せず、`02_departments/analytics/competitor-analysis-access-check-<today>.md`に
   「クレジット残高不足のためスキップした(残高: X)」と記録してコミット・プッシュし、
   終了してください。

## 背景
毎週日曜03:00 JST頃に実行し、Instagram/TikTokの教育系競合アカウントで伸びている
投稿の型を調べ、`02_departments/analytics/learned-patterns.md`の
「競合アカウント分析に基づく知見」節に知見を追記します。この結果は、月曜朝の
Instagram/TikTok・X/Threads台本生成(`instagram-tiktok-daily-draft.yml`等)が
自動で参照します。

## 手順

1. git config user.name "gakugym-ai-bot" / git config user.email "bot@example.com"
   を設定し、git fetch origin main && git checkout -B main origin/main で
   最新のmainを取得する。

2. `02_departments/analytics/competitor-accounts.yml` を読む。

3. チェック対象を選ぶ(クレジット節約のため、毎週全件は見ない):
   - `tier: high` のアカウントを最大6件選ぶ(7件以上ある場合は、前回のlearned-patterns.md
     の記録日時が古い順、または未記載のものを優先する)
   - `tier: normal` のアカウントから、ランダムまたはローテーションで2件選ぶ
     (全アカウントを数週間かけて一巡させるイメージ)

4. 選んだ各アカウント(最大8件)について `vidiq_ig_profile_reels` でhandleを指定し、
   直近のリール一覧(再生数・いいね数・キャプション)を取得する。

5. 加えて `vidiq_instagram_tiktok_outlier_search` を1回実行し、固定アカウントリストの
   外側で新しく伸びている投稿の型が無いか広く探る(query例:
   「高校生・大学受験生向けの勉強法・英検対策のリール/TikTok(教育系、学習アカウント)」、
   audienceQuery例:「Culture/Region: Japan/Japanese; Global: false; Demographics:
   高校生・大学受験生とその保護者、英検・大学受験対策に関心がある層;」)。

6. 取得した投稿群を分析し、以下の観点で「伸びている型」を言語化する:
   - フォーマット(手元撮影/顔出し/寸劇/インタビュー/リスト型/クイズ型 等)
   - フック(冒頭3秒で使われている訴求、ビフォーアフター数値、問いかけ等)
   - 学ジムの現行の完全自動生成パイプライン(Canva Autofill/スクリプト合成、
     出演者なし)で**再現可能かどうか**を必ず明記する(出演者が必要な型は
     「参考情報に留める」と明記し、無理に真似すべきとは書かないこと)

7. `02_departments/analytics/learned-patterns.md`の「競合アカウント分析に基づく知見」節に、
   以下のルールで追記する(既存の記述は消さず、日付付きの新しい段落として追加する。
   蓄積が目的なので上書きしないこと):
   - **調査日・チェックしたアカウント数(件数)を必ず明記する**
   - **断定しない**。「〜の傾向が見られる」「〜の可能性がある」といった慎重な書き方にする
   - 過去の知見と矛盾する結果が出た場合は、古い記述を消さずに「(2026-XX-XX時点の
     調査では逆の傾向も見られた。要継続観察)」と追記して両論併記する
   - 学ジムの既存ルール(department.md)を直接書き換えないこと(後述)

8. **複数週(目安3週以上)にわたって同じ傾向が繰り返し観察され、既存のdepartment.mdの
   ルールと矛盾する、または明確に改善すべき点が見つかった場合のみ**、
   `01_HQ/tasks/approval-pending.md`に「競合分析からの改善提案」として1件追記する
   (department.mdを直接編集しないこと。確定ルール化は益田さんの判断を仰ぐ)。
   1回だけの観察でここに書かないこと(誤検知・サンプル不足のリスクが高いため)。

9. 変更があった場合のみコミット・プッシュする:
   git add 02_departments/analytics/learned-patterns.md 01_HQ/tasks/approval-pending.md
   git commit -m "competitor analysis weekly $(date +%F)"
   git pull --rebase origin main
   git push origin main

## 作業完了後: mainへの反映(重要)
セッション開始時のブランチがmainではなく、Routine実行環境が自動生成した
一時的な作業ブランチになっていることがある。上記の手順9でコミット・プッシュが
終わったら、続けて以下の手順でmainブランチへの反映まで必ず行うこと。

1. 現在の作業ブランチ名を控える: CURRENT_BRANCH=$(git branch --show-current)
2. git fetch origin main
3. git checkout -B main origin/main
4. git merge --no-ff "$CURRENT_BRANCH" -m "Merge $CURRENT_BRANCH into main (competitor analysis weekly $(date +%F))"
5. コンフリクトが発生しなければ git push origin main でmainにプッシュする。
6. コンフリクトが発生した場合は、無理に解決せず git merge --abort で中断し、
   mainへのマージは行わない(人手を待たず、次週また試行される)。
7. mainへのforce push、historyの書き換え、他ブランチの内容の削除は絶対に行わないこと。

## 制約
- vidIQのクレジットを使い切らないよう、1回の実行で8アカウントのプロフィール取得+
  outlier検索1回(合計9回、約45クレジット)を超えないこと
- 競合アカウントが投稿を削除・非公開化していてデータが取れない場合は、無理に
  続けず該当アカウントだけスキップしてよい
- department.md・brand-guide.md等の確定ルールファイルは直接編集しないこと
  (改善提案は`01_HQ/tasks/approval-pending.md`経由で益田さんの判断を仰ぐ)
- 失敗した場合(vidIQのツールがエラーを返す等)は、無理に続けず何も変更せずに
  終了してよい(次週また試行される)
```

## うまくいかない場合
- vidIQコネクタがオンになっているのに動かない場合、claude.aiのRoutines UI側の
  仕様変更の可能性があるので、Claude Codeセッションで質問してください
- クレジット不足で毎週スキップされ続ける場合、vidIQのプラン・クレジット購入を
  検討するか、チェック対象アカウント数を減らす(手順3の「最大8件」を調整する)
  ことを検討してください
- `02_departments/analytics/competitor-accounts.yml`に新しい競合アカウントを
  追加したい場合は、このセッションに「このアカウントも競合分析に追加して」と
  伝えてください(YAMLに追記します)
