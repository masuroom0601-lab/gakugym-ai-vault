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

3. テーマの性質でテンプレートを判定する:
   - 体験談・ノウハウ系(個人の経験・アドバイス調) → 【通常版】
   - 暗記・網羅系(「◯◯20選」のような一覧・公式・単語など) → 【図解で覚えるシリーズ】
   台本内に「テンプレA」等の記載があればそれを優先してよい。迷ったら【通常版】を選ぶ。

### 【通常版】を選んだ場合
4. `DAHU-f_gDOU` を copy-design で複製する(page_numbersを指定しなければ全6ページ複製される)。
   台本のスライド数が6枚(表紙+中面4+締め)と異なる場合は、`add_page`で不足分を追加、
   または`delete_element`は使わずページごと削除できないため、余ったページはテキストだけ
   「(このページは今回未使用)」等にせず、中面の`add_page`テンプレート(下記5参照)を
   台本のスライド数に合わせて過不足なく作ること。

5. 複製したデザインを `read-design(open_transaction: true)` で開き、以下のレイアウト
   ルールを**必ず守って**テキストを差し替える(2026-09-12にDAHU-f_gDOU本体で検証済みの値):
   - 背景画像: 全ページ共通で mediaId `MAHU-TNADlQ`(既に表紙に入っている。中面を
     追加する場合は `insert_shape`ではなく`insert_fill`でこのmediaIdを
     `top:0, left:0, width:1080, height:1350` で挿入する)
   - 角の装飾(小さいsparkle/leaf画像、任意2点): `MAHU-Z_WPzY`, `MAHU-Z0BijE`,
     `MAHU-a5mEfQ`, `MAHU-ZYSzWY`, `MAHU-Qi_RSs`, `MAHU-RXm5Ag`, `MAHU-V0Ctzc`,
     `MAHU-cLg2E8`, `MAHU-WCCcPM` からページごとに2つ選び、top-right(top:40,left:880,
     width:63,height:69)とbottom-left(top:1190,left:50,width:42,height:69)に配置
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
     line_height:1.6。番号は本文の文字列に埋め込むこと。別要素にしない) →
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
7. 完成した各デザインを `export-design` でPNG書き出しする(先に`get-export-formats`で
   対応形式を確認)。全ページまとめて `as_single_image: false` で個別PNGとして書き出す。

8. エクスポートされたダウンロードURLから、Bashのcurlでファイルを取得し、
   `02_departments/creative/drafts/generated/<today>/` に保存する
   (例: `<today>-feed-01.png`, `<today>-feed-02.png` ...)。

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

   ## 生成ファイル
   - 02_departments/creative/drafts/generated/<today>/<today>-feed-01.png ...

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
