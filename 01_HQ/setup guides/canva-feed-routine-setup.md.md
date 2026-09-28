---
title: Canva日次フィード生成 Routine 設定手順書(claude.ai Routines)
status: 稼働中
---

## 背景
フィード(カルーセル)投稿も、リールと同じくCanva上で1から構築したマスターテンプレートを
複製・編集する方式に統一した(2026-09-12確定。詳細: `02_departments/creative/department.md`)。

**【2026-09-27更新】テンプレートは【通常版】のみ**: マスターデザイン `DAHWhf0nHMY`
(全6ページ、ベージュ背景+手書き風ドードル+太字丸ゴシック)。以前は「図解で覚える
シリーズ」(`DAHCqMT3jhw`)と日付の奇偶で交互選択していたが、益田さんの指示により
図解シリーズは廃止し、今後は常に通常版のみを使う。

リールのRoutine(`canva-routine-setup.md.md`)と同様、GitHub Actionsからは
Canva連携をスケジュール実行できないため、claude.aiのRoutines機能を使う。

## 前提
- claude.aiでCanvaが連携済みであること
- リール用Routine「Canva日次クリエイティブ生成」が既に動いていること
  (同じ仕組みをフィード用にもう1つ作る)

## 手順

1. claude.ai の **Routines** 設定画面を開く

2. 「新規Routine作成」を選び、以下を設定する:
   - **名前**: `Canva日次フィード生成`
   - **スケジュール**: 毎日 06:20(日本時間)
     (リール用Routineの06:15と時間をずらし、Canva操作が重ならないようにする)
   - **環境/リポジトリ**: リール用Routineと同じ環境
   - **コネクタ**: **Canva を必ずオンにする**
   - **プロンプト**: 下記「Routineに貼り付けるプロンプト」をそのまま貼り付ける

3. 保存後、テスト実行機能で1回動かし、`02_departments/creative/drafts/` に
   `<today>-feed-canva.md` とPNGファイルが増えているか確認する

## Routineに貼り付けるプロンプト

```
あなたは「学ジム」のcreative担当AI(フィード担当)です。gakugym-ai-vaultリポジトリ
(masuroom0601-lab/gakugym-ai-vault)のmainブランチで作業してください
(まだリポジトリが無ければ追加してクローンしてください)。

## 最初に確認すること(重要)
Canva関連のツール(read-design, copy-design, edit-design, export-design等)が
使えるかどうかを最初に確認してください。使えない場合は、以下の手順を実行せず、
`02_departments/creative/drafts/feed-canva-access-check-<today>.md` に
「Canva連携が利用できなかったため生成をスキップした」旨を記録してコミット・プッシュし、
終了してください。

## 手順

1. 本日の日付(YYYY-MM-DD)を確認し、
   `02_departments/instagram_tiktok/drafts/task-<today>-ig-*.md` を探す。
   無ければ何もせず終了する(コミット不要)。
   既に `02_departments/creative/drafts/<today>-feed-canva.md` が存在する場合も
   スキップする(重複生成防止)。

2. そのファイルの「## フィード下書き(カルーセル)」セクションを読み取る:
   表紙(title/catch)、中面各枚(title/body)、締め(title/body)。

3. `DAHWhf0nHMY` を copy-design で複製する(page_numbersを指定しなければ全6ページ複製される)。
   台本のスライド数が6枚(表紙+中面4+締め)と異なる場合は、`add_page`で不足分を追加、
   または`delete_element`は使わずページごと削除できないため、余ったページはテキストだけ
   「(このページは今回未使用)」等にせず、中面の`add_page`テンプレート(下記4参照)を
   台本のスライド数に合わせて過不足なく作ること。

   **(2026-09-18追加、重要)**: `copy-design`または`read-design`が
   `design_not_found`エラーを返した場合(2026-09-17に実際に発生。原因不明。
   マスターテンプレート自体がCanvaアカウントから消失していた)、無理に代替
   デザインを推測で使わない(過去にAI生成画像混入のインシデントがあったため、
   確証のないデザインを流用しない)。代わりに`search-designs`で
   `query: "受験F・全編"`のように検索し、`DAHWhf0nHMY`という完全一致のIDが
   見つからないことを確認した上で、`02_departments/creative/drafts/<today>-feed-canva.md`
   に「通常版マスターテンプレート(DAHWhf0nHMY)が見つからず生成できなかった。
   益田さんによる復旧または新マスター作成が必要」と明記してコミット・プッシュし、
   終了すること。

3.5. **(2026-09-27追加、重要)デザインのタイトル(名前)を必ず変更すること**
   `copy-design`で複製した直後のデザインは、元テンプレのタイトル(デザイン名)が
   そのまま引き継がれる(`update_title`しない限り変わらない)。益田さんのCanva
   ダッシュボードで日々の投稿を区別できなくなるため、複製直後(テキスト差し替えと
   同じ編集トランザクション内でよい)に`update_title`操作で
   「<today> フィード <科目/テーマ>」のような、今日の内容が分かるタイトルに
   必ず変更すること(例:「2026-09-27 フィード 古文」)。

4. 複製したデザインを `read-design(open_transaction: true)` で開き、以下のレイアウト
   ルールを**必ず守って**テキストを差し替える(2026-09-12にDAHU-f_gDOU本体で検証済みの値。
   **2026-09-15更新**: マスターテンプレート自体からAI生成の背景・ドードル画像を削除し、
   手描きベクター図形に置き換えたため、以下も合わせて更新した。**2026-09-28追記**:
   旧マスター`DAHU-f_gDOU`はCanva側で原因不明の理由により消失(`design_not_found`)
   したため、同じレイアウトルールのまま新マスター`DAHWhf0nHMY`として再構築した
   (詳細は`01_HQ/roadmap.md`参照)。台本のページ数が6枚と一致していれば、複製した
   6ページはそのまま手描きベクター版になっているのでこの節の背景・角装飾の指定は
   無視してよい。台本のページ数が6枚と異なり`add_page`でページを追加する場合のみ、
   以下の指定に従うこと):
   - 背景色: 全ページ共通でページ自体の背景色を`#f3e7ce`にする(`add_page`の
     `background_color`パラメータで指定。**AI生成画像は一切使わないこと**。
     `insert_fill`でmediaIdを挿入する旧方式は廃止)
   - 角の装飾: `insert_shape`で以下の2種類の図形を手描きする(色は共通で`#a8763f`、
     塗りつぶし・線ともにこの色)
     - 輪っか(ストロークのみ、塗りなし): `path: "M0 55 A55 55 0 0 1 110 55 A55 55 0 0 1 0 55 Z"`,
       `view_box_width/height: 110`, `stroke_color: "#a8763f"`, `stroke_weight: 6`
     - キラキラ(塗りつぶし): `path: "M22.5 0 L28 17 L45 22.5 L28 28 L22.5 45 L17 28 L0 22.5 L17 17 Z"`,
       `view_box_width/height: 45`, `color: "#a8763f"`
     配置は top-right に輪っか(top:50, left:860, width/height:110)+キラキラ(top:25,
     left:955, width/height:45)、bottom-left に輪っか(top:1155, left:45,
     width/height:110)+キラキラ(top:1245, left:140, width/height:45)
   - **表紙**: 見出し上の小さいアイキャッチ文(top:515, width:880, left:100,
     font_size:34, color:#7d390c, text_align:center) → その下にタイトル
     (top:650, width:880, left:100, font_size:78, bold, color:#4a2c12,
     text_align:center, line_height:1.3)。この2つで縦方向のかたまりがページ中央
     (縦1350のうち515〜850あたり)に来るようにする。**上に偏らせないこと**
     (2026-09-12の益田さんフィードバックにより確定したルール)
   - **中面(チェックリスト型)**: 絵文字アイコン1つ(top:430, left:100, width:100,
     font_size:64) → タイトル(top:540, left:100, width:880, font_size:54, bold,
     color:#4a2c12, line_height:1.4) → 本文(top:760, left:100, width:880,
     font_size:38, color:#6b4423, line_height:1.75)
   - **締め**: アイコン(top:350) → 「まとめ」等の見出し(top:460, font_size:58, bold,
     color:#4a2c12) → 番号付きリスト(top:600, font_size:46, bold, color:#4a2c12,
     line_height:1.6。番号は本文の文字列に埋め込むこと。別要素にしない。
     **項目数は台本の「締め」に書かれている項目をそのまま全部使うこと
     (中面ページ数と一致しているか必ず確認する。2026-09-16に中面4項目に対し
     締めが3項目しかない不整合が発生したため、勝手に3点等に丸めないこと)**) →
     締めの一言(top:880, font_size:34, color:#6b4423, line_height:1.7)
   - 各ページ左下に "n/総ページ数"(top:1270, left:70, width:100, font_size:24, bold,
     color:#a8763f)、右下に "学ジム"(top:1270, left:850, width:160, font_size:24,
     bold, color:#a8763f, text_align:end)
   - 絵文字アイコンは "☐" 等の記号ではなく実際の絵文字(✏️📊❓🤔📌など)を使うこと
     (記号だと文字化けして四角い枠(tofu)になることがある。2026-09-12に実際に発生し、
     絵文字に置き換えて解決した不具合)
   - 問題なければ `finalize: "commit"` で確定する

## 共通の後処理

5. **(2026-09-16変更: エクスポート・ダウンロードの手順は廃止)** 以前はここで
   export-design → curlでダウンロード → リポジトリに保存、という手順だったが、
   実行環境の送信(egress)ポリシー上、Canvaのエクスポート用ダウンロードURLに
   アクセスできないことが判明した(`connect_rejected`)。ファイルのダウンロードは
   行わず、次のステップでCanvaの編集URLのみを記録すること。

6. **作業内容をチェック役エージェントに確認させる(2026-09-21更新: 従来の自己チェックを、
   独立したチェック役エージェントによる確認に変更)**
   コミット前に、Agentツールで独立したチェック役エージェントを立て、以下を確認させること
   (作業役自身の自己確認ではなく、別エージェントに見させることで見落としを減らす):
   (a) 締めのまとめ項目数が、中面のページ数と一致しているか
       (2026-09-16に不一致が発生した既知の不具合)
   (b) 台本のスライド数と、実際に作成したページ数が過不足なく一致しているか
   (c) 各ページを `read-design` のサムネイルで見て、**表紙(1ページ目)が空白になって
       いないか**(テキストがデータ上正しく入っていても実際には空白で表示される
       不具合が2026-09-16に実際に発生した。原因不明。該当のテキスト要素を
       `delete_element`で一度削除し、`add_text`で作り直したら解決した)
   (d) 絵文字アイコンが文字化け(tofu)していないか
   チェック役から指摘があれば該当ページを修正し、`finalize: "commit"` で確定し直す。
   1回修正しても問題が残る場合は、無理に繰り返さず、次の記録ファイルに
   「チェック役から指摘があったが未解消: <内容>」と明記して先に進むこと。

7. `02_departments/creative/drafts/<today>-feed-canva.md` というファイルを作成し、
   以下を記録する:
   ---
   date: <today>
   status: draft
   template: 通常版
   source_draft: 02_departments/instagram_tiktok/drafts/task-<today>-ig-*.md
   ---
   ## Canvaデザイン
   - <copy-designで作った新デザインのedit_url>

   (ファイルはダウンロードせず、上記のCanva編集URLから直接確認・投稿する運用とする)

8. 以下でコミット・プッシュする:
   git config user.name "gakugym-ai-bot"
   git config user.email "bot@example.com"
   git add 02_departments/creative/drafts/
   git commit -m "canva feed generation <today>"
   git push

## 作業完了後: mainへの反映(2026-09-20追加、重要)
セッション開始時のブランチがmainではなく、Routine実行環境が自動生成した
一時的な作業ブランチになっていることがある。実際に2026-09-18・19分の生成結果が
mainへ届かず、`claude/quirky-mendel-*`のような一時ブランチにしか存在しておらず
益田さんが見つけられない、という不具合が発生した。上記の手順8でコミット・
プッシュが終わったら、続けて以下の手順でmainブランチへの反映まで必ず行うこと。

1. 現在の作業ブランチ名を控える: `CURRENT_BRANCH=$(git branch --show-current)`
2. `git fetch origin main`
3. `git checkout -B main origin/main`
4. `git merge --no-ff "$CURRENT_BRANCH" -m "Merge $CURRENT_BRANCH into main (canva feed generation <today>)"`
5. コンフリクトが発生しなければ `git push origin main` でmainにプッシュする。
6. コンフリクトが発生した場合は、無理に解決せず `git merge --abort` で中断し、
   mainへのマージは行わない。その旨と原因を
   `02_departments/creative/drafts/<today>-feed-canva.md` に追記し、作業ブランチへの
   プッシュ済みの状態のまま終了する(mainへの反映は後日人間が対応する)。
7. mainへのforce push、historyの書き換え、他ブランチの内容の削除は絶対に行わないこと。

## 制約
- 通常版のマスターテンプレート(DAHWhf0nHMY)のレイアウト数値は上記の通り厳守すること。
  独自の位置・サイズに変更しない(過去に「文字が上に偏っている」という差し戻しが
  発生したため、中央配置のルールは特に重要)
- テキストが長すぎて明らかにはみ出す場合は、要点を保ったまま短く要約してよい
- 何か失敗した場合は、無理に続けず `02_departments/creative/drafts/<today>-feed-canva.md`
  に失敗理由を記録してコミットする
```

## 【2026-09-27廃止】「図解で覚えるシリーズ」について
以前はマスターテンプレート`DAHCqMT3jhw`を使う「図解で覚えるシリーズ」と、日付の
奇偶で交互選択していたが、益田さんの指示により廃止した。今後のフィード生成では
一切使用しない(`DAHCqMT3jhw`自体はCanva上に残しているが参照しない)。

## テスト済みの実績(参考)
- 通常版: `DAHWhf0nHMY`(全6ページ、古文単語の実データ)で上記レイアウトルールを検証済み
  (2026-09-28に旧マスター`DAHU-f_gDOU`消失を受けて再構築したもの。詳細は
  `01_HQ/roadmap.md`参照)

## うまくいかない場合
- リール用Routineと同様、Canvaコネクタがオンになっているのに動かない場合はUIの
  仕様変更の可能性があるのでClaude Codeセッションで質問してください
- 見た目がイマイチな場合は、益田さんが直接Canva上で修正して投稿すればよい
