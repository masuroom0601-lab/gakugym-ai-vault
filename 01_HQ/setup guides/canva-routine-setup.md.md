---
title: Canva日次クリエイティブ生成 Routine 設定手順書(claude.ai Routines)
status: 着手済
---

## 背景
Instagram/TikTokのリール(サムネ+本編)は、当初PlaywrightでHTML/CSSテンプレートを
レンダリングする方式(`tools/creative/render.js`)で自動化していましたが、
益田さんの希望で**実際にご自身が使っているCanvaデザインをそのまま複製・編集する方式**
に切り替えました。

Claude Code経由(このリポジトリのGitHub Actions)からは、組織の設定上Canva連携を
スケジュール実行に持たせられなかったため、**claude.aiのRoutines機能から、
益田さんご自身のアカウントでスケジュールを作成する**必要があります
(益田さんのアカウントならCanvaコネクタを直接アタッチできるはずです)。

## 前提
- claude.aiでCanvaが連携済みであること(既に連携済みのはずです)
- このGitHubリポジトリ(`masuroom0601-lab/gakugym-ai-vault`、
  ブランチ`claude/brave-ride-yq7uep`、将来的にはmainにマージ後はmain)に
  Claude Codeがアクセスできること

## 手順

1. claude.ai にログインし、**Routines**(スケジュール実行/定期タスク)の設定画面を開く
   (サイドバーやSettingsから「Routines」「スケジュールされたタスク」等の項目を探してください。
   UIの名称・場所は変わることがあります)

2. 「新規Routine作成」を選び、以下を設定する:
   - **名前**: `Canva日次クリエイティブ生成`
   - **スケジュール**: 毎日 06:15(日本時間)
     (Instagram/TikTok担当AIの下書き生成が毎朝06:00 JSTに終わった後を狙っています)
   - **環境/リポジトリ**: このセッションと同じ環境(`gakugym-ai-vault`が使える環境)を選択
   - **コネクタ**: **Canva を必ずオンにする**(これが今回一番重要な設定です)
   - **プロンプト**: 下記「Routineに貼り付けるプロンプト」をそのまま貼り付ける

3. 保存後、可能であれば「今すぐ実行」のようなテスト実行機能で1回動かし、
   `02_departments/creative/drafts/` にファイルが増えているか確認する

## Routineに貼り付けるプロンプト

```
あなたは「学ジム」のcreative担当AIです。gakugym-ai-vaultリポジトリ
(masuroom0601-lab/gakugym-ai-vault)で作業してください(mainブランチ。
まだリポジトリが無ければ追加してクローンしてください)。

## 最初に確認すること(重要)
Canva関連のツール(read-design, copy-design, edit-design, export-design等)が
使えるかどうかを最初に確認してください。使えない場合は、以下の手順を実行せず、
`02_departments/creative/drafts/canva-access-check-<today>.md` に
「Canva連携が利用できなかったため生成をスキップした」旨を記録してコミット・プッシュし、
終了してください。

**【重大な既知の制約】(2026-09-15〜16判明、未解決)**: 本編動画デザインを
`copy-design`で複製した後、`read-design(open_transaction: true)`で構造を読むと
`"type": "unsupported"` しか返らず、テキスト要素が一切取得できないことが
複数デザイン(`DAHVNWWCKE0`、`DAHCx0JM7Q4`等)で確認されている。これは
動画背景を持つCanvaデザイン全般に対する構造的な制約と考えられ、現状では
本編動画のテキスト自動差し替えができない可能性が高い。もし手順3で
`read-design`の結果が`"type": "unsupported"`だった場合は、無理に
`replace_text`等を試みず、`02_departments/creative/drafts/<today>-canva.md`に
「本編動画のテキスト編集がCanva側の制約で実行できなかった(page type:
unsupported)」旨を記録してコミット・プッシュし、サムネイル(手順4)のみ
続行してください。

## 背景
このVaultは学ジムのSNS運用を自動化するためのObsidian Vaultです。毎朝06:00 JST頃に
Instagram/TikTok担当AIが台本(下書き)を自動生成しています。あなたの仕事は、
その台本をもとにCanvaで実際の画像・動画を作ることです。

## 手順

1. 本日の日付(YYYY-MM-DD)を確認し、
   `02_departments/instagram_tiktok/drafts/task-<today>-ig-*.md` を探す。
   無ければ何もせず終了する(コミット不要)。

2. そのファイルから以下を読み取る:
   - subject(科目カテゴリ)
   - サムネ案: 煽り文句・インパクト大文字(見出し)・数字・SWIPE文言
   - リール本編: 本文の箇条書き項目(通常5〜9個程度)とタイトル

3. 本編動画を作る(尺は15秒。2026-09-16再変更): 以下の既存デザインを copy-design で
   複製し、ベースにする(背景の動画・全体レイアウト・フォント・色は一切変更しない。
   変えるのはテキストのみ):
   DAHCx0JM7Q4
   (旧デザイン DAHEwbMbAmc/DAHEwfFJ4jE/DAHCw2jmnm8/DAHC3sQx064/DAHVNWWCKE0 は
   使用しないこと。益田さんが15秒の新しい参考デザインを追加したら、
   このリストに追加してよい)
   複製後、read-design(open_transaction: true)でテキスト要素を確認し、
   タイトル用テキスト要素を今日のタイトルに、本文の大きな1つのテキスト要素を
   「1. 項目1\n\n2. 項目2\n\n...」のように番号を本文に含めた形で差し替える
   (番号が別要素として固定位置に置かれている場合は、その番号要素は削除して
   本文に統合すること。番号を固定位置のまま残すと文字数が変わったときに
   本文とズレるため、絶対にそのままにしないこと)。
   問題なければ finalize: "commit" で確定する。

4. サムネイルを作る: デザインID DAHCqkxcHDM(5ページの複数トピック集)を確認し、
   今日のトピックに近いページがあれば copy-design で該当ページ(page_numbers指定)を
   複製してベースにする。無ければ最初のページ構成を流用し、テキストを差し替える。
   タイトル・煽り文句・数字を今日の内容に更新する。同様に finalize: "commit" で確定する。

5. **(2026-09-16変更: エクスポート・ダウンロードの手順は廃止)** 以前はここで
   export-design → curlでダウンロード → リポジトリに保存、という手順だったが、
   実行環境の送信(egress)ポリシー上、Canvaのエクスポート用ダウンロードURLに
   アクセスできないことが判明した(`connect_rejected`)。ファイルのダウンロードは
   行わず、次のステップでCanvaの編集URLのみを記録すること。

6. `02_departments/creative/drafts/<today>-canva.md` というファイルを作成し、
   以下を記録する:
   ---
   date: <today>
   status: draft
   source_draft: 02_departments/instagram_tiktok/drafts/task-<today>-ig-*.md
   ---
   ## Canvaデザイン
   - サムネイル: <copy-designで作った新デザインのedit_url>
   - 本編: <copy-designで作った新デザインのedit_url>

   (ファイルはダウンロードせず、上記のCanva編集URLから直接確認・投稿する運用とする)

7. 最後に以下でコミット・プッシュする:
   git config user.name "gakugym-ai-bot"
   git config user.email "bot@example.com"
   git add 02_departments/creative/drafts/
   git commit -m "canva creative generation <today>"
   git push

## 制約
- Canvaデザインの背景写真・動画・フォント・全体レイアウトは変更しないこと
  (固定テンプレートとして扱う)
- 文字数が多すぎて明らかにテキストがはみ出す場合は、要点を保ったまま短く要約してよい
- 何か失敗した場合(台本が無い、Canvaでの編集に失敗した等)は、無理に続けず
  `02_departments/creative/drafts/<today>-canva.md` に失敗理由を記録してコミットする
```

## テスト済みの実績(参考)
このプロンプトのロジックは、2026-09-12のセッションで手動で1回試して確認済みです:
- 実在のデザイン(`DAHCx0JM7Q4`「大学受験の残酷な数字」)を複製し、
  「スマホ依存 防ぎ方7選」の内容に差し替えて動作することを確認
- 最初、番号(1.〜7.)が本文と別要素だったため文字数が変わるとズレる問題を発見し、
  番号を本文に統合する形に修正したところ安定した
  (このプロンプトは修正後の安定版の手順を反映しています)
- 試作デザイン: https://www.canva.com/d/TPF9ZlphVqKrfs4 (益田さんのCanvaアカウント内)

**2026-09-14: 実際のRoutine初回実行が成功**(cronのタイムゾーン不具合を修正した翌朝)。
`DAHVNWWCKE0`「古文単語 直前暗記法5選」が自動生成され、番号を本文に統合するルールも
正しく反映されていた。益田さんがこの動画を10秒→15秒に手直しし、以後はこちらを
尺・参考デザインの基準にするよう指示があったため、上記の手順3を更新した。

**【訂正・重要】2026-09-15〜16判明**: 上記の2件の「成功」記録は、実際には
Claude Code側から技術的に検証されていなかった可能性が高いことが判明した。
2026-09-16に`DAHCx0JM7Q4`(まさにこの節で「動作確認済み」とされているデザイン)を
`read-design(open_transaction: true)`で読んだところ`"type": "unsupported"`しか
返らず、テキスト編集が一切できなかった。このリポジトリに一度も
`canva creative generation`系のコミットが存在しないことも合わせると、
実際には自動生成が成立していなかった可能性が高い。

一つの仮説として、**Canvaの動画編集UI(尺の調整等)で手動編集した結果、
デザインの内部的な種別が「動画背景付きの固定ページ」から「動画タイムライン」に
変わってしまい、以後API経由の構造化編集ができなくなった**のではないかと考えている
(未確認の推測)。もしこの仮説が正しい場合、今後15秒の新しい参考デザインを作る際は、
Canvaの本格的な動画編集モードで尺を調整するのではなく、元の「固定ページ+動画フィール」
の構造を保ったまま(可能であれば)尺を調整する方が、API編集の互換性を保てる
かもしれない。ただし検証できていないため、益田さんのご協力(実際にどう編集したか
教えていただく等)が今後の切り分けに役立つと思われる。

## うまくいかない場合
- Canvaコネクタがオンになっているのに動かない場合、claude.aiのRoutines UI側の
  仕様変更の可能性があるので、Claude Codeセッションで質問してください
- 生成された動画・画像の見た目がイマイチな場合は、益田さんが直接Canva上で
  そのデザインを修正して投稿すればよい(下書き生成の役割なので、最終承認前に
  自由に手直ししてください)
