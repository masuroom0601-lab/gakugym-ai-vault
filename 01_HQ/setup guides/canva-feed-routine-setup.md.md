---
title: Canva日次フィード生成 Routine 設定手順書(claude.ai Routines)
status: 未着手(益田さんがclaude.ai Routines画面から設定)
---

## 背景
フィード(カルーセル)投稿も、リールと同じくCanva上で1から構築したマスターテンプレートを
複製・編集する方式に統一した(2026-09-12確定。詳細: `02_departments/creative/department.md`)。
テンプレは2種類:
- **【通常版】** マスターデザイン `DAHU-f_gDOU`(全6ページ、ベージュ背景+手書き風ドードル+
  太字丸ゴシック。体験談・ノウハウ系のテーマ向け)
- **【図解で覚えるシリーズ】** 表紙のみ `DAHCqMT3jhw` を複製してテキスト差し替え
  (紺×写真背景+極太文字+「◯◯選」。中面は自由。暗記・網羅系のテーマ向け)

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

3. テンプレートを判定する(**2026-09-16更新: 内容の性質ではなく明記/日付で機械的に決める**):
   - 台本の「## フィード下書き(カルーセル)」直後に
     「**使用テンプレート: 通常版**」または「**使用テンプレート: 図解で覚えるシリーズ**」
     という明記があれば、必ずそれに従う(instagram_tiktok担当が日付の奇偶で
     あらかじめ決定しているため、これが最優先)。
   - 明記が無い場合のみフォールバックとして: 本日の日付(JST)の日にちが
     **奇数**なら【通常版】、**偶数**なら【図解で覚えるシリーズ】とする。

### 【通常版】を選んだ場合
4. `DAHU-f_gDOU` を copy-design で複製する(page_numbersを指定しなければ全6ページ複製される)。
   台本のスライド数が6枚(表紙+中面4+締め)と異なる場合は、`add_page`で不足分を追加、
   または`delete_element`は使わずページごと削除できないため、余ったページはテキストだけ
   「(このページは今回未使用)」等にせず、中面の`add_page`テンプレート(下記5参照)を
   台本のスライド数に合わせて過不足なく作ること。

5. 複製したデザインを `read-design(open_transaction: true)` で開き、以下のレイアウト
   ルールを**必ず守って**テキストを差し替える(2026-09-12にDAHU-f_gDOU本体で検証済みの値。
   **2026-09-15更新**: マスターテンプレート自体からAI生成の背景・ドードル画像を削除し、
   手描きベクター図形に置き換えたため、以下も合わせて更新した。台本のページ数が6枚と
   一致していれば、複製した6ページはそのまま手描きベクター版になっているのでこの節の
   背景・角装飾の指定は無視してよい。台本のページ数が6枚と異なり`add_page`で
   ページを追加する場合のみ、以下の指定に従うこと):
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

### 【図解で覚えるシリーズ】を選んだ場合
4. `DAHCqMT3jhw` を copy-design で **page_numbers: [1] のみ**複製する(表紙だけでよい。
   このデザインは表紙以外テキスト編集できないページもあるため中面は複製しない)。
5. 複製した表紙を `read-design(open_transaction: true)` で開き、3つのテキスト要素
   (科目/サブテーマ/数字。例:「英語」「前置詞」「20」)を今日のテーマに`replace_text`
   で差し替える。「選」と「図解で覚える」の文言・フォント・レイアウトは変更しない。
   `finalize: "commit"` で確定する。
6. 中面(2枚目以降)を `add_page` で台本のスライド数だけ追加する。背景は`insert_shape`
   で `background_color`(department.mdの配色ルールに沿った落ち着いた色でよい。
   紺・クリーム・白などシリーズの世界観を大きく外さない色)を指定し、台本のタイトル・本文を
   `add_text`で配置する。可能であれば`insert_shape`(直線・図形の組み合わせ)で図解らしい
   簡単な図(表・矢印・簡単な図形)を1つ添える(2026-09-12に「三平方の定理」の直角三角形の
   図解サンプルを作成済み。過度に凝る必要はなく、内容が視覚的に伝わればよい)。
   `finalize: "commit"` で確定する。

## 共通の後処理

7. **(2026-09-16変更: エクスポート・ダウンロードの手順は廃止)** 以前はここで
   export-design → curlでダウンロード → リポジトリに保存、という手順だったが、
   実行環境の送信(egress)ポリシー上、Canvaのエクスポート用ダウンロードURLに
   アクセスできないことが判明した(`connect_rejected`)。ファイルのダウンロードは
   行わず、次のステップでCanvaの編集URLのみを記録すること。

8. コミット前に、必ず全ページの見た目を`read-design`のサムネイルで確認すること。
   **特に表紙(1ページ目)は、テキストがデータ上正しく入っていても実際には
   空白で表示される不具合が2026-09-16に実際に発生した**(原因不明。該当の
   テキスト要素を`delete_element`で一度削除し、`add_text`で作り直したら
   解決した)。表紙が空白に見える場合は、この手順で作り直すこと。

9. `02_departments/creative/drafts/<today>-feed-canva.md` というファイルを作成し、
   以下を記録する:
   ---
   date: <today>
   status: draft
   template: 通常版 または 図解で覚えるシリーズ
   source_draft: 02_departments/instagram_tiktok/drafts/task-<today>-ig-*.md
   ---
   ## Canvaデザイン
   - <copy-designで作った新デザインのedit_url>

   (ファイルはダウンロードせず、上記のCanva編集URLから直接確認・投稿する運用とする)

10. 最後に以下でコミット・プッシュする:
    git config user.name "gakugym-ai-bot"
    git config user.email "bot@example.com"
    git add 02_departments/creative/drafts/
    git commit -m "canva feed generation <today>"
    git push

## 制約
- 通常版のマスターテンプレート(DAHU-f_gDOU)のレイアウト数値は上記の通り厳守すること。
  独自の位置・サイズに変更しない(過去に「文字が上に偏っている」という差し戻しが
  発生したため、中央配置のルールは特に重要)
- 図解シリーズは表紙のデザイン・フォント・配色を変更しないこと。中面は自由だが、
  シリーズとして分かる程度の世界観の一貫性は保つこと
- テキストが長すぎて明らかにはみ出す場合は、要点を保ったまま短く要約してよい
- 何か失敗した場合は、無理に続けず `02_departments/creative/drafts/<today>-feed-canva.md`
  に失敗理由を記録してコミットする
```

## テスト済みの実績(参考)
- 通常版: `DAHU-f_gDOU`(全6ページ、総合型選抜の実データ)で上記レイアウトルールを検証済み
- 図解シリーズ: `DAHU-yV9l9Y`(数学 公式10選)で表紙差し替え+三平方の定理の図解入り
  中面を試作済み

## うまくいかない場合
- リール用Routineと同様、Canvaコネクタがオンになっているのに動かない場合はUIの
  仕様変更の可能性があるのでClaude Codeセッションで質問してください
- 見た目がイマイチな場合は、益田さんが直接Canva上で修正して投稿すればよい
