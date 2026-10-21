---
title: 学ジムAI事業部 実現ロードマップ(超詳細版)
owner: 益田大輝
last_reviewed: 2026-09-12
---

# 学ジムAI事業部 実現ロードマップ

このドキュメントは「1人会社計画(AI社員による事業部体制)」を実際に回るところまで
持っていくための、現状整理・詳細タスク・運用フローをまとめたものです。
Claude Codeセッションを跨いでも迷わないよう、常にこのファイルを起点に「今どこまで進んでいて、
次に何をやるか」を確認してください。

---

## 0. 現状サマリー(2026-09-12時点)

### すでに実装済み
- Obsidian Vault構造一式(00_INBOX 〜 04_analytics、02_departmentsに12部署)
- 12部署すべての department.md(役割・アウトプット形式・承認フロー定義)
- 03_assets/brand-guide.md(全部署共通のトーン・NGルール・キーワード集)
- GitHub Actions による下書き自動生成(すべて「下書き作成まで」で、公開は人間判断):
  - `instagram-tiktok-daily-draft.yml`(毎日06:00 JST)
  - `x-threads-daily-draft.yml`(毎日06:00 JST)
  - `line-select-draft.yml`(毎週月・木、X/Threads publishedから選定)
  - `note-ameba-weekly-draft.yml`(毎週月曜)
  - `note-ameba-weekly-insights.yml`(毎週日曜、2026-10-17追加: note/Amebaのインサイト収集・分析→改善指示)
- Instagram/TikTok初回投稿1本が承認・published済み(実績あり)
- Instagram Graph API / Threads API のセットアップ手順書(自分用メモとして完成)

### 今回のセッションで追加したもの
- `01_HQ/calendar.md`: 9月後半〜10月の週テーマカレンダー(企画担当アウトプットの初版)
- `.github/workflows/hq-director-daily-report.yml`: 統括担当による日次集計・daily-log作成
- `.github/workflows/planning-monthly-calendar.yml`: 企画担当による翌月カレンダー叩き台の自動作成(毎月25日)
- `docs/dashboard/`: ドット絵ゲーム風オフィスダッシュボード(静的HTML、GitHub Pagesで無料公開可能)
- `01_HQ/setup guides/omniroute-setup.md.md`: Omniroute接続によるトークン最適化の手順書(要・本人のアカウント情報)
- このロードマップ
- `proofreading-daily-check.yml`: 校正担当の自動チェック(status: draft → review、または差し戻し)
- `hq-secretary-daily-tasks.yml`: 秘書担当のタスクカード自動起票・LINEストック確認・承認待ちリスト更新
- `02_departments/hq_secretary/_templates/task-card-template.md`: タスクカードの共通フォーマット
- `03_assets/creative-templates/`: サムネ・フィード(テンプレA/B/C)の固定HTML/CSSテンプレート
- `tools/creative/render.js`: Playwrightによる画像レンダラー(ローカルで実データ動作確認済み)
- `.github/workflows/creative-pipeline.yml`: creative部署の日次自動生成(06:05 JST)
- `04_analytics/_templates/weekly-input-template.md` / `manual-input/2026-09-07.md`: 週次手入力シート
- `.github/workflows/analytics-weekly-report.yml`: 週次レポート生成+翌週分シート作成
- `.github/workflows/improvement-weekly-suggestions.yml`: 週次改善提案タスクの自動起票
- `.github/workflows/analytics-monthly-summary.yml`: 月次サマリー集計
- `01_HQ/setup guides/tiktok-content-posting-api-setup.md.md` / `youtube-data-api-setup.md.md`:
  TikTok/YouTubeのセットアップ手順書(監査・審査の制約を明記)
- `tools/line/broadcast.js`: LINE配信の決定的スクリプト(Claudeを経由しない。テスト済み)
- `.github/workflows/line-broadcast-publish.yml`: 承認即配信+日次フォールバック
- `04_analytics/line-message-usage.json`: LINE月間メッセージ上限の追跡ファイル
- `docs/index.html` 他4ページ: 学ジム公式サイト本体(静的HTML/CSS、レスポンシブ対応、Phase4は一旦保留)
- `01_HQ/setup guides/custom-domain-setup.md.md` / `contact-form-setup.md.md`:
  独自ドメイン接続・お問い合わせフォーム連携の手順書
- リールのサムネ・本編生成をCanva方式に移行(`01_HQ/setup guides/canva-routine-setup.md.md`)。
  益田さんがclaude.ai Routinesで実際にRoutineを作成し、稼働開始済み
- フィードは過去投稿が編集不可のべた画像と判明したため、実物に合わせて
  `03_assets/creative-templates/feed-template-{a,b,c}.html` を全面的に作り直し、
  `creative-pipeline.yml` の日次cronを再有効化(対象をフィードのみに変更)

これでPhase1(HQ運用ループ)・Phase2(クリエイティブ制作の画像生成)・
Phase5(分析・改善ループ)まで実装が完了しています。
Phase3(TikTok/YouTube横展開)は、ドキュメント・設定ルール面(セットアップ手順書、
department.mdのアウトプット定義、トークン管理エスカレーション)は整備済みですが、
**実際のアップロード自動化コードはまだ書いていません**(理由は下記Phase3の節を参照)。

### まだ手つかず(次フェーズ)
- hp の自動化ワークフロー(Phase4)
- creativeの動画生成(ストック動画素材が届いてから着手、Phase3の前提でもある)
- TikTok/YouTubeへの実際のアップロード自動化(トークン発行後に実装。Phase3参照)
- LINE実配信のMessaging API連携(Phase6)
- クリエイティブ制作の実技術パイプライン(Playwrightレンダリング環境)
- TikTok/YouTube Shortsへの横展開(現状は「Instagram/TikTok」department.mdに統合されているが、
  実際のTikTok/YouTube個別アップロードの自動化・API連携は未着手)
- 自社ドメインHPの実制作・デプロイ
- 公式LINEの実配信(Messaging API連携)
- Omnirouteの実接続(アカウント情報待ち)
- 電子書籍(音読法/学習習慣)制作フロー

---

## 1. 全体アーキテクチャ(目指す最終形)

```
益田さん(最終承認者)
   ▲
   │ daily-log / dashboard確認
   │
[統括担当AI] ── 進行管理・エスカレーション
   │
[秘書担当AI] ── タスクカード分解(01_HQ/tasks/)
   │
   ├─ [企画担当AI] ── 月間テーマカレンダー(01_HQ/calendar.md)
   │
   ├─ [Instagram/TikTok担当AI] → drafts → [校正担当AI] → 益田さん承認 → published
   │        └─(将来)クリエイティブ制作AI → サムネ/動画生成(Playwright)
   │        └─(将来)TikTok/YouTube Shorts 個別横展開
   │
   ├─ [X/Threads担当AI] → drafts → 校正 → 承認 → (当面手動投稿)
   │        └─ [LINE担当AI]がX/Threads publishedから選定・横流し
   │
   ├─ [note/Ameba担当AI] → drafts → 校正 → 承認 → (手動投稿) → HPコラムへ転載
   │
   ├─ [HP担当AI] ── 自社ドメインサイトの構築・保守・コラム転載
   │
   ├─ [分析担当AI] ── 週次/月次レポート(04_analytics/)
   │
   └─ [投稿改善提案担当AI] ── 分析結果から改善タスクを起票 → 各部署へ

[docs/dashboard] ── 全部署の状態をドット絵オフィスとして可視化(GitHub Pages)
[Omniroute] ── 全AI呼び出しの裏側でモデルルーティングし、トークンコストを最適化
```

### 運用の大原則(brand-guide.md / 各department.mdより一貫)
- コンテンツ生成は自動化するが、**公開は必ず益田さんの最終確認を経る**
- 追加のサブスク費用はかけない(Claude Code Pro + ドメイン代等の実費のみ)
- 各SNSの公式API制限・規約変更(Threadsトークン60日失効、X API有料化など)に追従する

---

## 2. フェーズ別ロードマップ

### Phase 0: 基盤構築(完了)
- Vault構造・部署定義・ブランドガイド・4つの下書き自動生成ワークフロー
- ステータス: ✅ 完了

### Phase 1: HQ運用ループの完成(今回着手・継続要)
目的: 「統括→秘書→各部署→校正→承認」のループを人手を最小化して回す。

- [x] 統括担当の日次集計ワークフロー(`hq-director-daily-report.yml`)を追加
- [x] 企画担当の月間カレンダーを初期投入、翌月自動生成ワークフローを追加
- [x] 校正担当の自動チェックワークフロー(`proofreading-daily-check.yml`、06:10 JST)
      drafts内ファイルをbrand-guide.mdと突合し、問題なければstatus: reviewに変更、
      問題あればコメント付きでdraftのまま差し戻す
- [x] 秘書担当のタスクカード自動生成ワークフロー(`hq-secretary-daily-tasks.yml`、06:20 JST)
      当日/翌日分のタスクカード起票、LINEストック確認、承認待ちリスト(approval-pending.md)更新
- [ ] Omnirouteの実接続(`01_HQ/setup guides/omniroute-setup.md.md`のアカウント情報待ち部分を埋める)

### 日次ワークフローの実行順序(JST)
1. 06:00 各部署の下書き生成(instagram-tiktok / x-threads / ※月木のみline / ※月のみnote-ameba)
2. 06:10 校正担当チェック(`proofreading-daily-check.yml`)
3. 06:15 クリエイティブ制作(claude.aiのRoutine、Canvaで実デザインを複製・編集して
   サムネ・本編動画を生成。GitHub Actionsではなくclaude.ai側で動く点に注意。
   `01_HQ/setup guides/canva-routine-setup.md.md`参照)
4. 06:20 秘書担当タスクカード起票・承認待ちリスト更新(`hq-secretary-daily-tasks.yml`)
5. 06:30 統括担当の日次集計・ダッシュボード更新(`hq-director-daily-report.yml`)

益田さんは06:30以降に `01_HQ/tasks/approval-pending.md` とダッシュボードを確認し、
承認待ちの下書きを確認・編集・承認(published/フォルダへ移動)すればよい状態になっています。

**このPhaseが終わると**: 益田さんは毎朝daily-logとdashboardを見るだけで、
「何が承認待ちか」「何が滞留しているか」が一目でわかる状態になる。

### Phase 2: クリエイティブ制作パイプライン(2026-09-12: リール・フィードともにCanva方式に確定)
目的: Instagram/TikTokのサムネイル画像・リール動画・フィード画像を、文字化けせず自動生成する。

**経緯**: 当初PlaywrightでHTML/CSSテンプレートを自前レンダリングする方式で
リール・フィードとも実装したが、益田さんの希望でリールを「実際にご自身が使っている
Canvaデザインを複製・編集する」方式に切り替えた。続けてフィードもCanva化しようとしたが、
過去のフィード投稿8件(Genspark制)が**全ページ編集不可のべた画像**だったため、
一時的に「実物に寄せて作り直したPlaywright方式」に確定していた。しかし同日中に
益田さんから改めてフィードの方針共有があり、**フィードもCanva上で1から構築した
自前テンプレートを複製する方式に統一**することになった(Playwright方式は廃止。
`02_departments/creative/department.md`の「廃止した方式」節参照)。
フィードのテンプレは【通常版】(ベージュ/手書き風)と【図解で覚えるシリーズ】
(紺×写真背景/極太文字)の2種類。

#### リール(サムネ・本編動画): Canva方式
- [x] 益田さんの過去のCanvaデザイン(サムネ5ページセット+本編5種)を実際に確認し、
      構造を把握(本編は静止画ではなく**動画背景**であることが判明。エクスポートすれば
      そのままリール動画になる)
- [x] `copy-design`(複製)+`edit-design`(テキスト差し替え)+`export-design`
      (PNG/MP4書き出し)の一連の流れを、実際に1件試作して動作確認済み
      (試作: https://www.canva.com/d/TPF9ZlphVqKrfs4)
- [x] **重要な不具合を発見・修正**: 元デザインは番号(1.〜7.)が本文と別の固定位置
      要素だったため、文字数が変わると本文とズレる。番号を本文のテキストに統合する
      形に直し、文字数に依存しない安定した構造にした
- [x] `01_HQ/setup guides/canva-routine-setup.md.md`: claude.ai Routinesでの
      設定手順+貼り付け用プロンプトを作成
- [x] **益田さんがclaude.ai Routinesで実際にRoutineを作成・稼働開始済み**
- [ ] 初回実行結果を確認し、`02_departments/creative/drafts/`に
      期待通りのファイルが生成されるか検証する(継続してウォッチ)

**技術的な制約メモ(重要)**: Claude Code(GitHub Actions経由)からはCanvaの
公式開発者API(Autofill等)を使った完全無人の自動化は、調査の結果
**Canva Enterprise(高額な法人プラン)が事実上必須**と判明し、無料方針に反するため
見送った。今回のRoutine方式は、益田さんのClaude.aiアカウントに紐づくCanva連携を
「毎日決まった時刻に呼び出す」形なので、追加コストはかからない。

#### フィード(カルーセル): Canva方式(2種類のテンプレ、2026-09-12確定)
- [x] 過去のフィード投稿8件(和紙×手書き/カラーグラデーション/紺×白アイコン、
      各3〜9ページ)を実際に確認 → **全ページ編集不可のべた画像**と判明し、
      これらの実例そのものは複製編集に使えないと判明
- [x] 一時的にPlaywright方式(`03_assets/creative-templates/feed-template-{a,b,c}.html`、
      `tools/creative/render.js`)を実装したが、益田さんの最終判断でCanva方式に
      置き換え。`.github/workflows/creative-pipeline.yml`の日次cronは無効化済み
      (ファイル自体は参考記録として残置)
- [x] 【通常版】: 参考画像(`DAHEu1KxPDA`等、Genspark制で編集不可)の見た目
      (ベージュ背景+角の手書きドードル+太字丸ゴシックタイトル)を踏襲しつつ、
      Canva上で1から`insert_shape`/`add_text`/`format_text`で構築したマスター
      テンプレート`DAHU-f_gDOU`を作成(全6ページ、実データ入りで検証済み)。
      益田さんの「文字が上に偏っている」フィードバックを受けて、各ページとも
      テキストブロックをページ縦方向中央付近にまとめる配置に修正済み
- [x] 【図解で覚えるシリーズ】: 参考デザイン`DAHCqMT3jhw`は表紙(1ページ目)が
      テキスト要素として編集可能と判明したため、リールと全く同じ
      「`copy-design`で複製→`replace_text`でテキストだけ差し替え」方式が
      そのまま使えることを確認。テスト複製(数学 公式10選: `DAHU-yV9l9Y`)で
      動作検証済み。中面(2ページ目以降)はシリーズ内で統一しなくてよい方針
      (益田さん指示)
- [x] 上記2テンプレを使ったclaude.ai Routineのセットアップ手順を
      `01_HQ/setup guides/canva-feed-routine-setup.md.md`として作成(2026-09-13)。
      毎日06:20 JST(リールの06:15の直後)。**益田さんがclaude.ai Routines画面から
      「Canva日次フィード生成」という名前で作成する必要あり**(手順書参照)
- [x] `DAHCqMT3jhw`右上のロゴバッジ(「受験革命」)については、益田さんに確認済み。
      そのまま使用してよいとの回答

### Phase 3: 横展開の拡大(TikTok単独投稿・YouTube Shorts)
目的: Instagramリールで作った動画をTikTok・YouTube Shortsにも展開する。

- [x] 各APIのアクセストークン管理手順書を`01_HQ/setup guides/`に追加
      (`tiktok-content-posting-api-setup.md.md` / `youtube-data-api-setup.md.md`)
- [x] hq_directorのエスカレーション基準にTikTok/YouTubeのトークン期限管理を追加
- [x] instagram_tiktok/department.mdに「TikTok単独投稿」「YouTube Shorts」を
      明示的なアウトプット単位として追加(キャプション・タイトル・公開範囲のルール)
- [ ] TikTok for Developers(Content Posting API)のアプリ申請・監査
      (**益田さん対応。申請してもすぐには公開投稿できず、監査通過まで非公開投稿限定**)
- [ ] YouTube Data API v3のOAuth同意画面 本番公開審査
      (**益田さん対応。プライバシーポリシーページが必要=Phase4のHP完成が実質的な前提**)
- [ ] 実際のアップロード自動化ワークフローの実装
      (下記「実装時の技術メモ」を参照。**トークンが実際に発行されてから実装・動作確認する**
      方針とした。認証情報なしに書いたAPI呼び出しコードは検証できず、後で書き直しになる
      可能性が高いため、今回はガイドと仕様メモの整備までに留めている)
- [ ] 当面は「動画ファイルの自動生成まで」とし、実際のアップロードは承認後に
      益田さんが手動で行う運用を継続する(Phase2の動画パイプライン自体もまだ未着手のため、
      実質的にはPhase2の動画生成が先に必要)

**依存関係(重要)**: このPhaseは以下の順で詰まっている、いわば「三重待ち」の状態です。
1. Phase2の動画生成(ストック動画素材待ち)がまだ完了していない → 横展開する動画そのものがない
2. TikTokのアプリ監査、YouTubeのOAuth審査(ともに益田さん申請・数日〜数週間)
3. YouTubeの審査にはプライバシーポリシーページが必要 → 実質Phase4(HP)完成が前提
上記1・2は今すぐ並行着手可能なので、**動画素材の用意とAPI申請だけでも先に進めておく**
ことを強く推奨する(承認・監査の待ち時間そのものは短縮できないため)。

**実装時の技術メモ(トークン発行後に着手)**:
- TikTok: `/v2/post/publish/video/init/` で初期化→`upload_url`にチャンクアップロード。
  実行のたびにrefresh_tokenからaccess_tokenを再発行する処理が必須(24時間で失効するため)
- YouTube: resumable upload(`/upload/youtube/v3/videos`)。`privacyStatus`は
  最初`private`にし、益田さんの確認後に`public`へ切り替えるステップを挟む
- どちらも、creative-pipelineが将来生成する動画ファイルのパスをGitHub Actions内で
  参照できるようにする必要がある(現状のcreative-pipelineは画像のみ生成)

### Phase 4: 自社ドメインHP構築(2026-09-13再開 — readdy版のデザインに合わせて全面刷新)
目的: readdy版サイトのデザインをほぼそのまま踏襲し、自社ドメイン+無料ホスティングで再構築する。

**経緯**: readdy.ccのプレビューURLはこのセッションのネットワークポリシーで直接
アクセスできない(egress proxyでpolicy denial)ため、当初はhp/department.mdの文言
仕様のみで構築し、配色は無関係な紺×オレンジになっていた。2026-09-13、益田さんから
readdy版サイトの実際のスクリーンショット(トップ/料金・システム/講師紹介/コラム/
お問い合わせの5ページ)を共有してもらい、それを見て配色・タイポグラフィ・
レイアウトを全面的に作り直した。

- [x] デザインをクリーム×深緑×テラコッタの上品なトーンに全面刷新
      (`docs/assets/style.css`。フォントはShippori Mincho(見出し)+
      Cormorant Garamond(ロゴ)+Noto Sans JP(本文))
- [x] 5ページ(`docs/index.html`/`pricing.html`/`profile.html`/`column.html`/
      `contact.html`)をスクリーンショットのセクション構成に合わせて再構築
      (ヒーロー写真+eyebrowラベル、料金3カード、アコーディオン式レッスン一覧、
      お客様の声、講師のストーリー年表、事業者情報、お問い合わせフォーム等)
- [ ] 写真素材は未着手(現在はグラデーションのプレースホルダー)。
      著作権フリーの類似写真(warm tone・デスク/勉強机の雰囲気)を選定して差し替える
- [ ] お客様の声は実在の声が集まるまで `fill-in` プレースホルダーのまま
      (brand-guide.md「AI生成コンテンツの扱い」に基づき、架空の声は作成していない)
- [ ] 講師プロフィールの出身校・保有資格・事業者情報(所在地・連絡先)は
      `✏️要記入`のまま。公開前に益田さん本人が入力すること
- [x] hp/department.mdのサイト構成(トップ/料金/講師経歴/コラム/お問い合わせ)を
      静的HTML/CSSで実装(`docs/index.html` 他4ページ、レスポンシブ対応)
- [x] `01_HQ/setup guides/custom-domain-setup.md.md`: 独自ドメイン接続手順
      (GitHub PagesのCNAME設定・DNS設定。ホスティングは無料、ドメイン代のみ実費)
- [x] `01_HQ/setup guides/contact-form-setup.md.md`: Formspree(無料枠)+
      reCAPTCHA(画像認証)の連携手順
- [x] 振込口座情報など機微情報はVaultに含めず、事業者情報欄は「要記入」の
      プレースホルダーのみにしてある(profile.html)
- [x] お客様の声は実在しない推薦文を作らず、空のプレースホルダーのままにしてある
- [ ] ドメイン取得(実費、年額。益田さん対応)
- [ ] GitHub Pagesの有効化・カスタムドメイン接続(益田さん対応、上記guide参照)
- [ ] お問い合わせフォームの送信先・画像認証の実設定(益田さん対応、上記guide参照)
- [ ] 講師経歴ページの「✏️ 要記入」箇所(資格・ストーリー・事業者情報等)の記入(益田さん対応)
- [ ] 料金ページのキャンセル規定・解約規定の正式文言の確定(益田さん対応)
- [ ] note/Amebaのコラム記事をHPのコラムページに転載する自動化ワークフローを追加
      (note_ameba/published → docs/column/ への変換タスク。現状コラムページは
      「準備中」表示のまま。note/Amebaの実運用が安定してから着手する)
- [ ] 著作権フリーの人物写真の調達・profile.htmlの写真枠への設置(益田さん対応)

### Phase 5: 分析・改善ループの自動化(実装済み、要・毎週の数値入力)
目的: 「投稿→分析→改善提案→次の投稿に反映」のループを回す。

- [x] 手入力フォーム(`04_analytics/_templates/weekly-input-template.md`)を用意。
      Instagram/Threads/YouTube/LINEの公式APIトークンが未設定のため、
      **当面はInstagram/TikTok/X/Threads/note/Ameba/LINEすべて手入力が情報源**
      (トークン設定後、対象プラットフォームから自動取得に置き換え予定)
- [x] `analytics-weekly-report.yml`(毎週日曜05:30 JST相当): 前週の手入力シートを集計し
      weekly-report.mdを更新、履歴を04_analytics/history/に保存、翌週分の
      入力シートを新規作成
- [x] `improvement-weekly-suggestions.yml`(毎週日曜05:45 JST相当): weekly-report.mdから
      部署別の改善提案タスクカードを01_HQ/tasks/に起票
- [x] `analytics-monthly-summary.yml`(毎月1日): 履歴を月次集計し04_analytics/monthly-summary.mdに追記
- [x] 今週分(2026-09-07週)の入力シートを先行作成済み(`04_analytics/manual-input/2026-09-07.md`)
- [ ] 企画担当が改善提案を翌月カレンダーに反映するロジックをplanning-monthly-calendar.ymlに追記
      (現状は04_analytics/weekly-report.mdを「参考にする」という記載のみで、
      具体的な反映ロジックは未実装)
- [ ] Instagram/Threads/YouTube/LINEの公式トークン設定後、該当プラットフォームの
      Insight/Analytics APIから自動取得するロジックをanalytics-weekly-report.ymlに追加
      (Instagram/Threadsは投稿を手動で行っている限りmedia idが記録されないため、
      当面はアカウントレベルの指標(フォロワー数等)のみ自動取得可能になる見込み)

**次のアクション(益田さん対応)**:
1. `04_analytics/manual-input/2026-09-07.md` に今週の投稿数値を記入する
   (投稿するたびに1行ずつでOK、frontmatterの `filled: true` を忘れずに)
2. 以後は月曜朝に自動生成される最新の入力シートに、その週の数値を記入し続ける
3. 慣れてきたら`analytics-weekly-report.yml`を`workflow_dispatch`で一度手動実行し、
   weekly-report.mdが期待通りに生成されるか確認する

### Phase 6: LINE公式配信の完全自動化(実装済み、要・トークン発行)
目的: 現状「published/フォルダに置くだけ」のLINE配信を、Messaging APIで実配信まで自動化する。

- [x] `01_HQ/setup guides/line-messaging-api-setup.md.md` を作成
      (無料プランの月間メッセージ上限リスクを明記。Instagram/TikTok/YouTubeと違い、
      チャネルアクセストークンは長期(無期限)なので定期更新は不要)
- [x] line/department.mdの承認フローを更新:
      `status: approved` に変更してpushすると自動配信される仕組みに変更
- [x] 誤配信防止ガード: `status: approved` のファイルのみ配信対象
      (`tools/line/broadcast.js`)
- [x] **月間メッセージ上限の自動追跡・超過時の自動見送り**を実装
      (`04_analytics/line-message-usage.json`。フォロワー数×配信回数で
      無料枠を使い切るリスクに対する安全装置)
- [x] `line-broadcast-publish.yml`: drafts/へのpush時に即実行+毎日06:15 JST相当の
      フォールバック実行
- [x] 配信処理自体は**Claudeを経由しない決定的スクリプト**として実装
      (取り消せない配信のため、LLMの解釈ではなく固定ロジックで処理する方針。
      frontmatter解析・本文抽出・上限判定のロジックはこのセッション内でテスト済み)
- [ ] LINE公式アカウント(Messaging API)のチャネル作成・アクセストークン取得
      (**益田さん対応**。トークン発行後は追加のコード変更なしで動くはず)
- [ ] 実際の配信(1通)での動作確認 — トークン発行後、まず`workflow_dispatch`で
      1件だけ承認した状態で手動実行し、正常に届くか確認する

### Phase 7: 電子書籍・特典コンテンツ制作
目的: 「英語音読法」「モチベに左右されない学習習慣作り」の電子書籍を、
LINE特典・Amazon自費出版用に制作する。

- [ ] 電子書籍担当の役割定義(department.md)を新規作成(02_departments/ebook/)
- [ ] 既存のnote/Ameba記事・Instagram投稿をベースに構成案を作成
- [ ] Kindleダイレクト・パブリッシング(KDP)向けフォーマット(EPUB/PDF)の生成手順を確立
- [ ] LINE特典として配布する場合のURL配布・ダウンロード導線を設計
- [ ] 表紙デザインはcreative部署のテンプレート方式を流用

---

## 3. 運用サイクル(完成形の1日〜1ヶ月の流れ)

### 日次(GitHub Actions cronで自動実行、詳細は「1. Phase 1」の実行順序表を参照)
1. Instagram/TikTok担当・X/Threads担当: 下書き生成(06:00 JST)
2. クリエイティブ担当: サムネ・フィード画像生成(06:05 JST)
3. 校正担当: drafts内容をチェックしreviewへ(06:10 JST)
4. 秘書担当: タスクカード起票・承認待ちリスト更新(06:20 JST)
5. 統括担当: dashboard-state.json更新、daily-log記録(06:30 JST)
6. (3日に1回・月木)LINE担当: X/Threads publishedから選定
7. **益田さん**: dashboard(docs/dashboard)とapproval-pending.mdを確認し、
   reviewフォルダの内容を承認 or 修正指示。投稿した内容の数値を
   `04_analytics/manual-input/<今週の月曜日>.md` に随時記入

### 週次
- 日曜05:30 JST相当: 分析担当が前週の手入力データからweekly-report.mdを更新し、
  今週分の入力シートを新規作成(`analytics-weekly-report.yml`)
- 日曜05:45 JST相当: 投稿改善提案担当がweekly-report.mdから改善タスクを起票
  (`improvement-weekly-suggestions.yml`)
- 月曜: note/Ameba担当が長文記事を1本生成

### 月次
- 1日: 分析担当が前月のweekly-report履歴を集計しmonthly-summary.mdを更新
  (`analytics-monthly-summary.yml`)
- 25日: 企画担当が翌月のテーマカレンダー叩き台を自動作成 → 益田さんが確認・確定
- 月初: 確定したカレンダーを各部署に反映

---

## 4. 益田さんが対応する必要がある「人にしかできない」タスク一覧

これらはAIには実行できない(アカウント権限・審査・実費が絡む)ため、
このロードマップの各Phaseに沿って都度対応してください。

| 項目 | 関連Phase | 内容 |
|---|---|---|
| Instagram/Threads長期トークンの初回取得・60日毎の更新 | Phase1 | セットアップ手順書済み、実行は本人 |
| Omnirouteアカウント・APIキー発行 | Phase1 | omniroute-setup.md.mdの前提条件 |
| GitHub Secretsへのトークン登録 | 各Phase共通 | Settings → Secrets and variables → Actions |
| TikTok for Developersアプリ申請・アプリ監査 | Phase3 | `tiktok-content-posting-api-setup.md.md`。監査前は非公開投稿のみ |
| YouTube OAuth同意画面の本番公開審査 | Phase3 | `youtube-data-api-setup.md.md`。プライバシーポリシーページが必要(Phase4依存) |
| 著作権フリーのストック動画素材の用意 | Phase2/3 | `03_assets/videos/`。Phase3の横展開はこの動画が前提 |
| LINE公式アカウントのMessaging APIチャネル作成・長期トークン発行 | Phase6 | `line-messaging-api-setup.md.md`。発行後は自動配信が有効になる |
| LINE配信の月間メッセージ上限確認・プラン判断 | Phase6 | 無料枠超過時、待つか有料プランにするかは本人判断(追加予算の方針に関わる) |
| 独自ドメイン取得・DNS設定・GitHub Pages連携 | Phase4 | `custom-domain-setup.md.md`。ドメイン代のみ実費 |
| お問い合わせフォーム(Formspree)・reCAPTCHA設定 | Phase4 | `contact-form-setup.md.md` |
| profile.html/pricing.htmlの「✏️ 要記入」箇所への実データ入力 | Phase4 | 資格・ストーリー・事業者情報・規定文言など、本人にしか書けない内容 |
| 著作権フリーの人物写真・トップページ用画像の調達 | Phase4 | プレースホルダーのままでは公開に適さない |
| Amazon KDPアカウント開設 | Phase7 | |
| 各drafts/reviewの最終承認・編集 | 日次運用 | brand-guide.md「6. AI生成コンテンツの扱い」に基づく必須ステップ |
| 景品表示法等、法令に抵触しうる表現の最終判断 | 日次運用 | AIはNGルールでガードするが最終責任は本人 |
| 週次アナリティクス入力シートへの数値記入 | Phase5 | `04_analytics/manual-input/<週の月曜日>.md`。公式APIトークン未設定のため唯一の情報源 |
| **claude.ai Routinesで「Canva日次クリエイティブ生成」を作成(Canvaコネクタ必須)** | Phase2 | `canva-routine-setup.md.md`。GitHub Actions側では設定不可だったための対応 |
| (フォールバック用途のみ)著作権フリーの背景写真の追加 | Phase2 | `03_assets/images/backgrounds/`。Canva経路が使えない場合のPlaywright代替経路向け |

---

## 5. リスク・注意点

- **API規約変更**: X(2026年2月以降有料化)、Threads(60日トークン失効)など、
  各プラットフォームのAPI仕様変更に継続的に追従する必要がある。統括担当のエスカレーション
  ルールに組み込み済みだが、Phase3以降で連携先が増えるたびに同様の管理項目を追加すること。
- **著作権・薬機法・景品表示法**: 素材(画像・動画)の著作権、学習効果の誇大表現は
  brand-guide.mdのNGルールで一次ガードしているが、校正担当の自動チェック実装(Phase1)完了まで
  は益田さんの目視確認への依存度が高い。
- **トークンコスト**: Omniroute接続前は、Claude Code Pro契約の範囲でGitHub Actionsからの
  呼び出し回数が積み重なる。Phase1でのOmniroute接続を優先度高めに進めることを推奨。
- **属人化**: このVault自体がAI事業部の「本社」であるため、Claude Codeセッションが変わっても
  必ずこのroadmap.mdとdaily-log、dashboard-state.jsonを起点に状況把握すること。

---

## 6. 次にやること(直近アクション)

### 【解決】リール本編の「編集不可」問題、原因確定・回避策確立(2026-09-20)
上記ブロッカー1(リール本編が編集できない問題)について、益田さんのご協力で
原因を確定できた。**Canva上で動画デザインの尺(タイムライン)を一度でも手動で
伸縮すると、そのデザインが構造化編集API(read-design/edit-design)から一切
読めなくなる(page type: "unsupported")。** これは以下の実証実験で確認した:
- 一度も尺を触っていない`DAHEwbMbAmc`・`DAHEwfFJ4jE`は正常に読める(`"type": "fixed"`)
- 益田さんが`DAHEwfFJ4jE`を目の前で15秒に伸ばした直後、同じデザインが
  `"type": "unsupported"`に変わった(再現性のある実証実験)
- 一方`export-design`(書き出し)は尺変更後の"unsupported"なデザインでも
  問題なく動作することを確認(`DAHVlYUUjJA`で検証)

`DAHCx0JM7Q4`(旧基準デザイン)とその複製である`DAHVNWWCKE0`・`DAHVlYUUjJA`が
軒並み編集不可だったのは、過去のどこかの時点で尺が調整されていたためと判明した
(2026-09-12・09-14の「動作確認済み」記録は実際には検証されていなかった可能性が高い)。

**確立した回避策(ハイブリッド運用)**: マスターテンプレートを尺未変更の
`DAHEwbMbAmc`(10秒)に固定し、Routineは10秒のままテキスト自動編集・commitまでを
完全自動で行う。その後、益田さんがその日の複製デザインのみをCanva上で15秒に
手動で伸ばしてから書き出し・投稿する。「テキストを考えて差し替える」という
一番手間のかかる部分は自動化を維持し、「尺を伸ばす」ワンタッチ操作だけ手動で残す形。
詳細・Routineプロンプトの更新版は`01_HQ/setup guides/canva-routine-setup.md.md`参照。

### 【重大】自動化パイプラインの技術的ブロッカー2件(2026-09-15〜16実テストで発覚)
益田さんの依頼で、リール・フィード(通常版)を実際にCanva MCPツールで
テスト生成したところ、これまでの自動化前提を根底から揺るがす2つの技術的制約が
判明した。詳細は`02_departments/creative/drafts/2026-09-16-feed-canva.md`参照。

1. **リール本編(動画背景デザイン)はCanva MCPで一切テキスト編集できない**。
   `copy-design`後に`read-design(open_transaction:true)`しても
   `"type":"unsupported"`しか返らず、`replace_text`対象の要素が取得できない
   (新15秒デザイン・旧10秒デザインいずれも同じ)。オートフィル代替手段もなし。
   → `canva-routine-setup.md.md`が前提とする「リール本編の自動テキスト差し替え」は
   現状のツールでは実現不可能。過去の「初回実行成功」記録は未検証だった可能性が高い。
2. **`export-design`で取得したダウンロードURLに、このセッションの送信(egress)
   ポリシー上アクセスできない**(`export-download.canva.com`が組織ポリシーで
   ブロックされる)。そのため生成したPNG/MP4をリポジトリに保存する手順が
   実行できない。GitHub Actions/claude.ai Routines側でも同様の制約がある
   可能性が高く、これまで`canva creative generation`系のコミットが
   このリポジトリに一度も存在しなかった根本原因と考えられる。

フィード(通常版)のテキスト編集自体は問題なく動作することを確認済み
(サムネイルも編集は可能だが、文字数が変わると位置・サイズの手動調整が必要)。
**この2点への対応方針(egressの許可リスト追加を試みるか、運用を
編集URL共有ベースに切り替えるか等)は益田さんのご判断が必要**。

### 重要な運用上の教訓(2026-09-16): フィードの「まとめ」項目数不一致・リール/フィードのテーマ重複
益田さんから、フィード投稿(通常版)で本編(中面)は学習法4つ紹介しているのに、
まとめスライドには3つしか表示されない不整合の指摘があった。調査したところ、
`02_departments/instagram_tiktok/department.md`のフィード(カルーセル)節が
**「締め: まとめ3点」と項目数を決め打ちしていた**ことが直接原因と判明
(実際に`task-2026-09-16-ig-001.md`で中面4項目・まとめ3項目という不整合が
発生していた)。また同department.mdのフィード節は、廃止済みの旧テンプレA/B/C
(Playwright方式)の記述が残ったままで、実際に運用しているCanva通常版/図解シリーズ
方式に更新されていなかったことも判明。

併せて、益田さんから「毎日のリールとフィードのテーマがほぼ同じで使い回しに見える」
「フィード(通常版)と図解で覚えるシリーズを1日ごとに交互にしたい」という要望があった。

**対応(2026-09-16)**:
1. `department.md`のフィード節を全面改訂: まとめの項目数は中面と必ず一致させる
   ルールを明文化(固定数を書かない)。テンプレ名を通常版/図解シリーズに更新。
2. フィードのテンプレ選定を「内容の性質で判定」から「**日付の奇偶で機械的に
   交互**(奇数日=通常版、偶数日=図解シリーズ)」に変更。下書きの
   フィードセクション冒頭に「使用テンプレート: ◯◯」と明記させ、
   `canva-feed-routine-setup.md.md`側もその明記を最優先で読むよう更新
   (明記が無い場合のみ日付奇偶で自己判定するフォールバックを追加)。
3. 「リールとフィードは必ず異なるテーマ・切り口にすること」というテーマ選定
   ルールをdepartment.mdに新設し、`instagram-tiktok-daily-draft.yml`の
   プロンプトにも二重に明記。
4. `task-2026-09-16-ig-001.md`のまとめ項目を中面の4項目と一致するよう修正済み。

**次回以降の生成で、まとめの項目数一致・テンプレ交互・テーマ分離が実際に
守られているか要確認**。

### 重要な運用上の教訓(2026-09-14〜15): Instagram「AI生成メディアを含む」表示の原因と対処
毎朝Canva Routineが自動生成したフィード投稿を実際にInstagramへ投稿したところ、
「AI生成メディアを含む」という表示が出た。原因を調査したところ、これはInstagram側が
独自にAI判定しているのではなく、**Canvaが書き出すファイルに埋め込まれるC2PA
「Content Credentials」メタデータ**(AIツールの利用履歴を記録する業界標準規格)を
Meta/Instagramが読み取って表示していることが判明(参考:
[lilachbullock.com](https://www.lilachbullock.com/why-instagram-ai-info-label/)、
[c2pa.ai/instagram](https://c2pa.ai/instagram))。根本原因は、通常版マスターテンプレート
`DAHU-f_gDOU`が元々Canvaの`generate-design`(AI生成機能)で作られており、背景の紙質画像
+角の手書き風ドードル画像がAI生成アセットのまま使われ続けていたこと。

**対応方針**: このメタデータそのものを消す/偽装する処理は行わない(閲覧者に対して
「AIが関与していないように見せかける」ことになり誠実性に反するため)。代わりに、
**AI生成アセットそのものを削除し、正真正銘AIを使っていないアセットに置き換える**
という正攻法で対応した。

**実施内容(2026-09-15)**: `DAHU-f_gDOU`の全6ページから、AI生成画像(背景1種+
角のドードル画像、計23要素)をすべて削除し、`insert_shape`で1から手描きしたベクター
図形(輪っか+キラキラのドードル、色は既存トンマナの`#a8763f`を継承)に置き換えた。
テキスト(タイトル・本文・ページ番号・ロゴ)は一切変更していない。これでこのデザイン
ファイルにはCanvaのAI生成コンポーネントが含まれなくなったはず。
**次回このテンプレートから投稿した際に、実際に「AI生成メディアを含む」表示が
消えているか要確認**(Instagram側の表示ロジックの詳細は外部からは検証できないため)。

途中、Canva MCP連携が数回切断・再接続を繰り返し、編集トランザクションが度々失われる
不具合があった(`edit-design`の`transaction_id`がコミット前に無効になる)。その都度
`read-design(open_transaction: true)`でトランザクションを取り直し、各ページの編集を
連続して素早く適用することで最終的に全ページの編集とコミットに成功した。

### 重要な運用上の教訓(2026-09-13): cronの日付が1日ずれるバグ
GitHub Actionsのcronは**UTC基準**で動く。`- cron: '0 21 * * *'`(毎日06:00 JSTの
つもり)は実際には「UTC 21:00」に発火するが、これはJSTでは**翌日の06:00**にあたる。
一方、各ワークフローが`git commit -m "... $(date +%F)"`のように`date +%F`で
「今日の日付」を求める処理は、ランナーのタイムゾーン(UTC)でその日の日付を返すため、
**JST視点での「今日」より必ず1日古い日付になる**。

実際に2026-09-12〜13、instagram-tiktok-daily-draftの生成物が
`instagram/tiktok daily draft 2026-09-11`(本当は9/12分)、
`instagram/tiktok daily draft 2026-09-12`(本当は9/13分)のように
1日ズレたコミット名で保存され続けていたことが判明。これが原因で、
Canva日次クリエイティブ生成Routine(claude.ai側、正しくJSTの「今日」を
認識する)が`task-<今日の日付>-ig-*.md`を探しても見つからず、
毎回スキップされていた。

**対応**: `.github/workflows/`配下の日付を扱う全ワークフロー(instagram-tiktok/
x-threads/note-ameba/line-select/line-broadcast/hq-secretary/hq-director/
proofreading/planning/analytics×2/improvement/creative-pipeline、計13本)に
`env: { TZ: Asia/Tokyo }`をワークフロー直下に追加(2026-09-13)。これにより
ワークフロー内の`date`コマンド(Claude自身がBashツールで実行するものも含む)が
すべてJSTを返すようになり、日付のズレが解消される見込み。
**次回の各Routine/cron実行時に、生成ファイルの日付が正しくなっているか要確認**。

### 重要な運用上の教訓(2026-09-12): ブランチの取り扱い
GitHub Actionsの`schedule`は**デフォルトブランチ(main)にあるワークフローファイルしか
自動実行しない**。このセッションはずっと`claude/brave-ride-yq7uep`という開発ブランチで
作業していたため、Phase2以降に作った自動化(HQ本部の日次集計・ドット絵ダッシュボード・
creative部署のCanva化・LINE配信・分析部署など)が**2026-09-12まで一度も本番実行
されていなかった**(実行されていたのは元々mainにあったInstagram/TikTok・X/Threads・
note/Ameba・LINE下書きの4本のみ)。益田さんの承認を得て、この日に開発ブランチを
mainへfast-forward統合し、全14ワークフローがGitHub Actions上で有効化されたことを確認済み。
**以後、両ブランチはコミットのたびにfast-forwardで同期させること**(mainが常に
本番の実体であるため、mainに反映されていない変更は「存在しないもの」として扱われる)。

1. [x] `hq-director-daily-report.yml`と`hq-secretary-daily-tasks.yml`を
   `workflow_dispatch`で手動実行し、正常動作を確認済み(2026-09-12)。
   `dashboard-state.json`に初めて実データが反映された
2. [ ] `docs/dashboard/`が実際にGitHub Pagesで公開されているか確認する
   (このセッションのネットワーク制限で直接確認できなかった。未公開の場合は
   リポジトリのSettings → Pages → Branch: main, Folder: /docs を選択。無料・追加コストなし)
3. [ ] `planning-monthly-calendar.yml`も一度`workflow_dispatch`で手動実行し、
   正しく動作するか確認する
4. Omnirouteのアカウント情報を用意し、`01_HQ/setup guides/omniroute-setup.md.md`の
   未確定事項を埋めて実接続する

### 重要な運用上の教訓(2026-09-28): フィード通常版マスターテンプレートの消失と再構築
益田さんから「フィードのテンプレートがCanva上で見当たらない」との報告を受け調査したところ、
通常版フィードのマスターテンプレート`DAHU-f_gDOU`が`read-design`で`design_not_found`
エラーを返す状態になっていることを確認した(2026-09-17に別の本編動画マスターで発生した
ものと同種の、原因不明のままCanva側でデザインが消失する現象)。search-designsでも
該当デザインは見つからず、復旧不可と判断。

益田さんの承認を得て、同一レイアウト仕様(ベージュ背景`#f3e7ce`、四隅の手描きベクター
装飾、6ページ構成: 表紙/中面4枚/締め)で新マスターテンプレート`DAHWhf0nHMY`をゼロから
再構築した。手順: 既存デザインを`copy-design`で複製→`resize-design`で1080×1350に
リサイズ→旧要素を全削除→`insert_shape`/`add_text`/`format_text`でレイアウトを再現
(古文単語をテスト内容として使用)→全ページ完成後に`update_title`でデザイン名を
「【通常版】フィードマスター(全6ページ)」に変更→コミット。

作業中、Canva MCP連携が複数回切断・再接続を繰り返し、未コミットのトランザクションが
その都度失われる不具合が再発した(2026-09-15の教訓と同じ現象)。そのため、今回は
**ページ単位で編集→即座にcommitする**運用に切り替えて対応し、最終的に6ページ全ての
再構築に成功した。

`01_HQ/setup guides/canva-feed-routine-setup.md.md`、`02_departments/creative/department.md`、
`02_departments/instagram_tiktok/department.md`内の`DAHU-f_gDOU`参照は全て新ID
`DAHWhf0nHMY`に置き換え済み。過去の日付入り記録ファイル(`02_departments/creative/drafts/
*-feed-canva.md`)や本セクションより前の教訓記録内の`DAHU-f_gDOU`表記は、当時の実績を
示す historical な記録のためそのまま残してある。

### 重要な運用上の教訓(2026-09-29): フィードの文字サイズを全面拡大(競合分析を踏まえて)
上記で再構築した`DAHWhf0nHMY`を益田さんに見せたところ、「これ全然ダメ。文字が
小さすぎる」と強い差し戻しを受けた。加えて「競合のアカウントをくまなく分析し、
文字を最大限大きくした、視聴者を惹きつけるデザインを作成して」との指示があった。

Instagramは実行環境のegressポリシーでアクセスがブロックされているため、
個別の競合アカウントを直接閲覧することはできなかった(`www.instagram.com`への
`WebFetch`は`EGRESS_BLOCKED`で失敗することを確認)。その旨を正直に伝えた上で、
代わりにWebSearchで教育系Instagramカルーセル投稿の一般的なデザイントレンド
(2026年時点)を調査し、「大きく太い見出し+最小限の短い補足文」「余白を活かして
伝えたい要点だけを大きく見せる」「1枚1メッセージ」という共通原則を確認した。

この原則に基づき、`DAHWhf0nHMY`の全6ページの文字サイズを次のように拡大した:
- 表紙: アイキャッチ34→48px、タイトル78→140px
- 中面(4ページ共通): アイコン64→110px、タイトル54→92px、本文38→54px
- 締め: アイコン64→110px、見出し58→92px、リスト46→64px、締めの一言34→44px
- 各ページ下部のページ番号/ロゴ: 24→28px

文字を大きくした分、そのままでは文章がページからはみ出すため、本文・リスト項目は
すべて1行(全角13〜16文字程度)に収まる短い言い切り文に書き換えた(例:
「現代語の「とても」ではなく文脈で判断。程度を表す副詞として使われることが多い。」
→「「とても」ではない、程度の副詞。」)。見出し色もより濃い`#2b1a0a`に変更し、
本文もbold指定にしてコントラストを強めた。

この過程でも前回同様、Canva MCP連携の切断・再接続が複数回発生した。**ページ単位で
編集→即座にcommit**という前回確立した運用で対応し、6ページ全ての拡大とタイトル更新
(「【通常版】フィードマスター(文字拡大版)」)に成功した。

`01_HQ/setup guides/canva-feed-routine-setup.md.md`の手順4のレイアウト数値、
チェック役エージェントの確認項目、`## 制約`節を新しい数値・ルール
(**フォントサイズを縮小する方向の変更は禁止、はみ出す場合はテキストを短くする**)
に更新し、`02_departments/creative/department.md`にも同様の注記を追加した。

### 重要な運用上の教訓(2026-10-11): リール本編テンプレートの刷新・サムネイル生成の廃止
益田さんの指示により、リール本編動画のマスターテンプレートを`DAHCp5O4ANA`へ変更した。
理由: 従来のテンプレート(`DAHEwbMbAmc`)は別途サムネイル画像(`DAHCqkxcHDM`から
複製)を作る必要があり、投稿のたびに手間だった。新テンプレートは動きを増やした
長尺の動画で、「認知拡大」を狙う方針転換に伴い、動画の冒頭フレーム自体が
サムネイル代わりになるため、**サムネイル生成の手順を廃止**した。

新テンプレートの構成は3パート: 表紙(0〜2.5秒ごろ、テーマを表す色文字)→本編
(2.5〜17.8秒ごろ、タイトル+箇条書き)→CTA・キャプション誘導(17.8秒以降、
テンプレート固定・自動編集の対象外)。毎朝のRoutineは17.8秒より前の部分だけを
編集し、それ以降は一切触らない運用とした。

表紙のテーマ文字色は科目/テーマごとに固定することになり、当初益田さんから
「総合型選抜=紫、英語=黄色、古文=赤、日本史=緑、その他学習法=ピンク」という
指定があったが、5科目のうち現代文の色が抜けていたため確認したところ、
最終的に「総合型選抜=紫、英語=黄色、古文=ピンク、現代文=赤、日本史=緑、
科目非依存のテーマ=青」に修正された(確認して正解だった例)。

**制約**: このセッションではCanva連携の認証が切れており(再認証が必要)、新
マスターテンプレート`DAHCp5O4ANA`の実際のページ構成・タイムライン・テキスト要素を
直接確認することができなかった。そのため、`canva-routine-setup.md.md`の手順は
「時間帯でCTAパートを判断し、触らない」という一般的な方針を記述するにとどめ、
具体的な要素位置やlocator_idはあえて書かず、実行時にRoutineのワーカーエージェントが
`read-design`で都度把握する形にした。**新テンプレートでの自動生成は2026-10-11時点で
まだ一度も実地検証されていない**。初回実行時は特に注意してチェック役エージェントに
確認させ、問題があれば記録を残すこと。

`01_HQ/setup guides/canva-routine-setup.md.md`(マスターID・手順3/4・制約・
テスト済みの実績・うまくいかない場合)、`02_departments/creative/department.md`
(リール節)、`02_departments/instagram_tiktok/department.md`(リール節、
サムネ生成ルールを表紙配色ルールに置き換え)を更新した。

### 重要な運用上の教訓(2026-10-11続報): リール方式を「複製+直接編集」から「ブランドテンプレート+Autofill」へ全面移行
上記の教訓で「新テンプレート`DAHCp5O4ANA`は実地検証未了」としていたが、同日中に
Canva連携が復活し、実際に検証できた。結果、当初の想定とは異なる、より根本的な
技術的制約が判明した。

**判明した事実**:
1. `DAHCp5O4ANA`を`read-design(open_transaction: true)`で開くと`"type": "unsupported"`
   で、構造化編集API(`edit-design`)によるテキスト要素の直接編集が一切できなかった。
2. 当初は「尺を手動で伸縮したのが原因」(旧テンプレートで確認済みの制約)を疑い、
   益田さんに尺を一切伸縮していない新規複製(`DAHXtSqLKl4`)を作ってもらったが、
   **それでも同じく`unsupported`だった**。つまり原因は尺の伸縮ではなく、**この
   テンプレート自体の動画の作り方(複数クリップ・動きの多い演出)が、構造化編集に
   そもそも対応していない形式だった**ということが分かった。
3. 代替として、Canvaの「ブランドテンプレート+Autofill(データフィールド自動入力、
   `autofill-design`)」機能を検証した。これは構造化編集とは別のAPI経路のため、
   `unsupported`な動画デザインでも機能する。益田さんにCanva上で
   「Bulk create」アプリを使ってデータフィールドを設定してもらい(`title`・
   `cover_theme`・本編5項目×メイン文/補足文の`body1-1`〜`body5-2`、計12フィールド)、
   `DAHXtSqLKl4`をブランドテンプレート(`EAHXtgN-KXU`)として公開してもらった。
4. 試行錯誤の過程で、最初は`body`という1つのフィールド名を10個の別要素に重複
   接続してしまい同じ文字が10回繰り返される不具合、次に`body1-1`〜`body5-2`の
   命名のまま`body`1つにまとめようとして逆にフィールドが消える不具合が発生したが、
   最終的に益田さんに「各項目はメイン文(`bodyN-1`)+補足文(`bodyN-2`)の意図的な
   ペア構成である」ことを確認してもらい、正しい構成だと判明した。
5. `autofill-design`でテスト生成(`DAHXtjiI3ms`)を行い、全12フィールドが重複・
   欠落なく正しい位置に反映され、CTA・キャプション誘導パートが変更されないことを
   `read-design`の`design_content`で確認した。**これで新方式は実地検証済みとなった**。

**判明した追加の仕様変更**: 益田さんから、台本の項目数は「本編5項目+キャプション
行き5項目の計10項目」で**常に固定**という方針が示された。これに伴い、従来の
「タイトルの数字と本編の箇条書き項目数を完全一致させる」「『残り◯つはキャプション
check』のような文言を使わない」という2026-09-27制定のルールを廃止し、「常に
『10選』で統一、本編は前半5個・残り5個はキャプション誘導に固定」という新ルールに
置き換えた(`.github/workflows/instagram-tiktok-daily-draft.yml`のルール3を更新)。

**色分けの扱い**: `autofill-design`のデータフィールドはプレーンテキストのみで
色指定ができず、Autofill後のデザインも構造化編集非対応のため後から色を変更する
こともできない。そのため、表紙の科目別配色ルール自体はドキュメントに残したが、
**自動生成では適用せず、益田さんが投稿前にCanva上で手動設定する運用**とした
(益田さんの明示的な判断)。将来的に自動化する場合は、科目ごとに色違いの
ブランドテンプレートを複数用意する方式が候補として残っている。

更新したファイル: `01_HQ/setup guides/canva-routine-setup.md.md`(全面書き換え)、
`02_departments/creative/department.md`(リール節)、
`02_departments/instagram_tiktok/department.md`(リール節・キャプション節)、
`.github/workflows/instagram-tiktok-daily-draft.yml`(ルール3)。

### 重要な運用上の教訓(2026-10-12): 英検クイズ リール動画の投稿用キャプション整備・日次レビューRoutine新設
別セッションで、X/Threads「今日の1問」(英検クイズ)がCanva画像からリール動画
(スクリプト製、`02_departments/creative/reel_quiz/`+GitHub Actions
`eiken-quiz-reel.yml`、毎日06:45 JST)に切り替わり、旧claude.ai Routine
「Canva日次英検クイズ生成」は益田さんの指示で無効化された(本セッションで
`list_triggers`により`enabled: false`であることを確認済み)。

このセッションで判明した整合性の問題: 新しい動画のエンド画面は「答え&解説は
概要欄へ!」と案内する仕様になっていたが、台本生成(`x-threads-daily-draft.yml`)は
旧仕様のまま「正解はコメント欄に後で別途投稿する」解答文しか作っておらず、
投稿時のキャプション(概要欄)に正解を書く仕組みが存在しなかった。この矛盾を解消する
ため、`x-threads-daily-draft.yml`を更新し、投稿用キャプション(フック文→正解・解説→
次回誘導/保存訴求→ハッシュタグ最大5個)を生成する工程を追加し、旧「コメント欄に
投稿する解答文」節は廃止した。ハッシュタグ上限は`instagram_tiktok`部署の
「最大5個」ルールに統一した。

また、下書きのfrontmatterが`status: review`で生成されていたため、校正担当の日次
チェック(`proofreading-daily-check.yml`、対象は`status: draft`のみ)がこのファイルを
一度もチェックしていなかった不具合も発見し、`status: draft`で生成するよう修正した
(校正担当が実際にチェックし`review`へ進める運用に戻した)。

益田さんから、毎朝「リール動画ファイル・投稿用キャプション(ハッシュタグ込み)・
校正担当の報告」をまとめてClaudeチャットに表示してほしいという依頼があったため、
claude.aiのRoutine「英検クイズ日次レビュー」(毎日07:05 JST、このセッションの
会話に直接メッセージを送る形)を新設した。台本生成(06:00)→校正(06:10)→動画生成
(06:45)がすべて終わった後の時刻を狙って設定した。

更新したファイル: `.github/workflows/x-threads-daily-draft.yml`(キャプション生成・
status修正)、`02_departments/x_threads/department.md`(今日の1問節・投稿用
キャプション節・承認フロー)、`02_departments/creative/department.md`(該当箇所に
追記)。新設: claude.ai Routine「英検クイズ日次レビュー」。

### 重要な運用上の教訓(2026-10-13): GitHub Actionsのスケジュール実行が毎日3〜5時間ずれる問題
2026-10-12・13と、本編リール(Canva Autofill)・英検クイズ動画の生成がいずれも
「台本がまだ無い」として失敗した。2026-10-12はRoutine側のJST日付判定バグが原因
だったが、益田さんに確認を依頼したところ2026-10-13は別の原因だった: 台本生成
(`x-threads-daily-draft.yml`、本来06:00 JST)自体が実際には11:19 JSTまで
遅延していた。

過去1週間のコミット時刻を確認したところ、**これは2026-10-13限定の一時的な現象では
なく、少なくとも10/7〜10/13の7日間毎日継続しているパターン**だった(実際の
実行時刻: 10/7=09:16、10/8=09:40、10/9=09:53、10/11=09:01、10/12=09:08、
10/13=11:19、いずれもJST)。原因はGitHub Actions側のスケジュール実行の混雑に
よるものと考えられ、cronで指定した時刻通りに動く保証がそもそも無いことが
判明した。

このため、「◯◯分後ろにずらす」という固定時刻の微調整では根本解決にならない
(今日のように数時間単位でずれる日もあるため)。対策として、`eiken-quiz-reel.yml`
に`workflow_run`トリガーを追加し、**`x-threads-daily-draft`の完了を直接検知して
即座に実行される**方式に変更した(固定スケジュールの06:45 JSTはフォールバックとして
残す。どちらが先に走っても、生成済みなら後続はスキップする既存のロジックで
安全に共存する)。

**残課題(本セッションでは対応していない)**: 同じ根本原因(GitHub Actionsの
スケジュール遅延)は、`instagram-tiktok-daily-draft.yml`→`proofreading-daily-check.yml`→
各Canvaリール/フィードRoutineの依存関係にも共通して存在する可能性が高い。
益田さんから要望があれば、同様に`workflow_run`チェーン化を検討すること。

### 重要な運用上の教訓(2026-10-17): 自社エンゲージメント分析→学習→投稿改善パイプラインの新設(フェーズ2)
益田さんから「競合Instagramアカウントの自動分析」の依頼があったが、検討の結果、
(a) InstagramのAPIは自分が管理するアカウントのデータしか取得できず競合アカウントの
自動分析は公式手段が無い、(b) スクレイピングは規約違反かつGitHub Actions上での
継続実行は現実的でない、ことを説明した。益田さんと相談し、方針を
「自社アカウントの実エンゲージメントデータを分析して学習し、投稿作成に反映する」
(フェーズ2)を優先し、競合トレンドはWeb検索ベースの簡易調査(フェーズ3、未着手)に
留めることで合意した。

着手前に重大な事実が判明した: **`04_analytics/manual-input/`の週次手入力シートが
2026-09以降一度も入力されておらず(全て`filled: false`・空欄)、分析の元になる
実エンゲージメントデータが現状ゼロ**。`04_analytics/weekly-report.md`もこれまで
毎週「入力データなし」としか出力されていなかった。

この状態を踏まえ、「データが貯まり次第、自動的に学習が始まる」設計にして
フェーズ2を実装した:
- `02_departments/analytics/learned-patterns.md`(新設): 各部署の台本生成が参照する
  「学習済みパターン集」。エンゲージメントデータに基づく知見の節は現時点では空だが、
  これまでの益田さんの直接フィードバック・過去の不具合から確定している知見
  (フィード文字サイズ・項目数一致ルール等、既にdepartment.mdに反映済みのもの)を
  先に転記し、空のファイルにしないようにした
- `.github/workflows/analytics-pattern-learning.yml`(新設): `analytics-weekly-report`
  完了を`workflow_run`で検知して自動実行し、週次レポート・履歴から傾向を分析して
  `learned-patterns.md`に追記する。**実データの投稿件数が10件未満ならは分析自体を
  スキップする**設計にして、少数データからの誤った断定を防いでいる
- `instagram-tiktok-daily-draft.yml`・`x-threads-daily-draft.yml`の台本生成プロンプトに、
  `learned-patterns.md`を事前に読むよう指示を追加した

**残課題**: このパイプラインは「データが来れば動く」状態で止まっている。
`04_analytics/manual-input/`への入力が再開されない限り、エンゲージメントベースの
学習は実質的に進まない。フェーズ1(Instagram Insightsの自動取得によるAPI化)は
未着手のまま(`01_HQ/setup guides/instagram-graph-api-setup.md.md`は投稿用の
手順のみで、インサイト取得にはFacebookページ連携の旧ルートが別途必要)。
フェーズ3(競合トレンドのWeb検索調査)も未着手。

### 重要な運用上の教訓(2026-10-17続報): エルグラム連携によるフェーズ1の代替手段
上記の「フェーズ1未着手」課題に対し、同日中に益田さんが「エルグラム」
(Instagram分析ツール、投稿ごとのいいね・保存・リーチ等が取得できる)を
claude.aiに接続した。Meta for Developersでのアプリ作成・Facebookページ連携
(`instagram-graph-api-setup.md.md`の旧手順)を経由せずに、Instagram Insightsに
近いデータが取得できる見込みとなった。

実際に`list_bots`・`list_posts`・`get_user_stats`で動作確認したところ、連携自体は
正常(学ジムのアカウント`massu_gakugym`、フォロワー237人を正しく認識)。ただし
2026-10-17時点では**エルグラム側に過去の投稿データがまだ同期されておらず
(`list_posts`が0件)、フォロワー推移の履歴も空**だった。エルグラムは今日以降の
新しい投稿から記録し始める可能性が高いと判断した。

このセッションで重要な技術的制約が判明した: **エルグラムはこのチャット専用に
有効化されたMCPコネクタであり、GitHub Actions(`analytics-pattern-learning.yml`等)
からは直接アクセスできない**。また、claude.aiのRoutineをAPI(`create_trigger`)
経由で新規作成する際、このセッションが持つコネクタの権限を自動的に引き継ぐ
ことができなかった(`connectors`パラメータ自体がこの組織では無効)。実際に
試しに作成したRoutineは「コネクタなし」の状態になってしまったため削除し、
Canva Routineの時と同様、**益田さんご自身がclaude.ai画面上でRoutineを作成し、
画面上でエルグラムコネクタを手動でオンにする**方式に切り替えた
(`01_HQ/setup guides/elgram-weekly-fetch-routine-setup.md`に手順書を作成)。

この「エルグラム週次データ取得」Routine(毎週日曜04:50 JST予定、
`analytics-weekly-report.yml`の05:30より前)は、`04_analytics/manual-input/`の
Instagram欄を自動で埋め、`filled: true`に変更する設計。TikTok/X/note/Ameba/LINEは
引き続き手動入力が必要。益田さんがRoutineを作成し、エルグラム側にデータが
同期され次第、2026-10-17に構築したフェーズ2(`analytics-pattern-learning.yml`)が
実際に動き出す見込み。

### 重要な運用上の教訓(2026-10-17続報): note/Amebaブログの自動投稿化(ブラウザ操作代行)
益田さんから「note/Amebaにも自動で投稿できないか」との依頼があった。確認したところ、
note.com・Amebaとも投稿用の公式APIが存在せず(Instagram/TikTok/LINEと異なる点)、
Zapierでの連携アプリ検索でも該当なしだった。残る手段はブラウザ自動操作による代行のみで、
その場合のトレードオフ(半自動=都度呼び出しが必要だが認証情報を新たに預けずに済む/
完全自動=無人実行できるがログイン情報をGitHub Actions secretsに保存する必要があり
規約リスク・認証情報漏洩リスクが生じる)を説明した上で、益田さんの判断で
「完全自動(無人スケジュール投稿)」を選択した。

既存の`line-broadcast-publish.yml`(LINE公式Messaging API配信)と同じ設計方針
(承認ゲート+LLMを経由しない決定的スクリプト)を踏襲し、以下を新設した:
- `tools/note_ameba/publish.js`(新設): Playwrightでnote.com/Amebaにログインし、
  承認済み下書きのタイトル・本文を貼り付けて投稿するNode.jsスクリプト
- `.github/workflows/note-ameba-auto-publish.yml`(新設): drafts/へのpush時に実行
  (毎日06:20 JST相当のフォールバックあり)
- `02_departments/note_ameba/department.md`の承認フローを更新:
  益田さんがfrontmatterの`status`を`approved`に変更してpushすると自動投稿される
  (LINEと同じ承認モデル)。note・Ameba両方成功して初めてpublished/へ移動し、
  片方のみ成功時は次回実行時に残りを再試行する設計
- `01_HQ/setup guides/note-ameba-auto-publish-setup.md`(新設): GitHub Actions secrets
  (`NOTE_EMAIL`/`NOTE_PASSWORD`/`AMEBA_ID`/`AMEBA_PASSWORD`/`AMEBA_BLOG_ID`)の
  設定手順と、初回は必ず`workflow_dispatch`で手動実行して人の目で確認することを明記

**重要な制約・残課題**: note.com/Amebaとも非公式のブラウザ操作であり、CAPTCHA・
2段階認証が表示されると自動突破できず失敗する設計になっている(その場合は
下書きがstatus: approvedのままdrafts/に残り、手動投稿にフォールバック可能。
データは失われない)。また、note.comのエディタはリッチテキストのため、Markdownの
見出し・太字の装飾は現状のスクリプトでは再現されない(プレーンテキスト段落として
貼り付けるのみ)。secretsは益田さんがGitHub側で設定する必要があり、未設定の間は
これまで通り手動投稿で運用できる。実際にログイン・投稿が成功するかは、
益田さんによる初回の手動実行(workflow_dispatch)での確認待ち。

### 2026-10-17続報(2): note/Amebaの週次インサイト分析と、投稿時の画像・ハッシュタグ自動選定
益田さんから「毎週note/Amebaのインサイト分析を行って改善を加える」「投稿時に最適な画像と
ハッシュタグを選ぶ」の2点の追加依頼があり、自動投稿の仕組みに以下を追加した:

- **週次インサイト分析**(`.github/workflows/note-ameba-weekly-insights.yml`、毎週日曜05:00 JST):
  `tools/note_ameba/insights.js`がnote/Amebaにログインして記事ごとのビュー・スキ/いいね・
  コメントを収集(`04_analytics/note_ameba/raw/`)→ `analyze.js`がハッシュタグ・見出し画像ごとの
  成績を集計(`performance.json`)→ Claudeが考察して週次レポート
  (`04_analytics/note_ameba/weekly-report.md`)と**次回記事への改善指示**
  (`02_departments/note_ameba/insights.md`)を更新。月曜の記事生成はこの改善指示を必ず読む
- **投稿時の画像・ハッシュタグ選定**(`tools/note_ameba/select.js`・`header-image.js`):
  記事内容・下書き時のAI提案(`hashtag_candidates`/`image_keywords`)・過去実績から
  ハッシュタグ(note/Ameba各最大5個、候補は`02_departments/note_ameba/hashtag-pool.yml`)と
  見出し画像の背景写真(`03_assets/images/note_ameba/catalog.yml`)を選び、
  固定テンプレート(`03_assets/creative-templates/note-header.html`)で
  1280x670の見出し画像を生成して投稿時に設定する。LLMを使わない決定的ロジック
- 実際に設定できたタグ・画像は公開記事のfrontmatter(`note_hashtags`/`ameba_hashtags`/
  `image_source`)に記録され、翌週以降の分析で効果が測られる(選定→投稿→計測→選定の循環)

**残課題・制約**: インサイト収集も非公式のブラウザ操作で、note/Amebaの管理画面の仕様変更で
数値が取れなくなる可能性がある(取れない場合は画面の文字を保存し、Claudeが読み取る)。
見出し画像のアップロード・ハッシュタグ入力欄の位置も実画面での確認が必要で、失敗しても
記事の投稿自体は続行し、frontmatterの`publish_warnings`に記録する。写真素材
(`03_assets/images/note_ameba/`)は未登録のため、当面は写真なしのベージュ地+タイトル文字の
見出し画像になる。

### 重要な運用上の教訓(2026-10-17続報): 競合分析の週次自動化(フェーズ3着手)
益田さんから「Instagram/TikTokのインサイト分析・競合分析・必要なら制作マニュアル変更を
週次で回したい」との依頼があった。確認したところ、自社データ分析(フェーズ2)は
仕組みは完成しているが実データ待ちの状態、競合分析(フェーズ3)は今日1回の手動調査のみで
週次自動化は未着手だった。

vidIQ(競合分析ツール)はエルグラムと同様、このチャットセッション専用のMCPコネクタで
GitHub Actionsから直接呼べない制約があるため、エルグラムの時と同じ設計
(claude.ai Routine+益田さんによるコネクタの手動オン)を踏襲した:

- `02_departments/analytics/competitor-accounts.yml`(新設): 今日の手動調査で使った
  競合Instagramアカウント約30件(英語/数学カテゴリ)を保存。元のGoogleスプレッドシートへの
  ライブ同期はせず、このファイルを正とすることでコネクタ依存を増やさない設計にした
- `01_HQ/setup guides/competitor-analysis-weekly-routine-setup.md`(新設): 「週次競合分析」
  Routine(毎週日曜03:00 JST)の設定手順書。毎週最大8アカウント(tier: highを優先)を
  ローテーションでチェックし、vidIQのクレジット消費を抑える設計(1回あたり目安45クレジット)。
  クレジット残高不足時は無理に実行せずスキップする
- `02_departments/analytics/learned-patterns.md`の「競合アカウント分析に基づく知見」節を
  週次更新の説明に更新。今日の手動調査結果は「初回」として残した
- `02_departments/analytics/department.md`に「競合分析(フェーズ3)」節を新設し、
  **department.md自体は競合分析結果で自動的には書き換わらない**(複数週にわたり同じ傾向が
  繰り返し観察された場合のみ`01_HQ/tasks/approval-pending.md`に改善提案として記録し、
  益田さんの判断を経てルール化する)設計を明記した。誤検知・サンプル不足での早まった
  マニュアル変更を防ぐための意図的な歯止め

**残課題**: 益田さんがRoutineを作成し、vidIQコネクタをオンにするまでは自動実行されない。
初回実行時にクレジット消費量・分析の質を確認する必要がある。

### 2026-10-18: note/Amebaの自動投稿は廃止(手動投稿に戻す)
益田さんの判断で、note/Ameba記事の自動投稿計画は取りやめ、これまで通り週1で生成する下書きを
益田さんが手動投稿する運用に戻した。`note-ameba-auto-publish.yml` の自動実行(push・毎朝の定時実行)は停止。
停止前の2026-10-18 06:20頃の定時実行で、承認済みだった2026-10-05の記事がnoteに公開された
(https://note.com/deft_agapan6959/n/ndd1579e14687)。Amebaは公開を確認できず、益田さんの確認待ち。
- 同日、益田さんの判断で **週次インサイト分析** と **画像・ハッシュタグ提案** は残すことにした。
  提案は自動投稿ではなく、毎週の下書き作成直後に `tools/note_ameba/suggest.js` が下書きに添付する形に変更
  (`suggested_hashtags` / `suggested_header_image`)。分析は手動投稿された記事をタイトルで下書きと突き合わせて集計する。

### 重要な運用上の教訓(2026-10-18〜19): リール本編テンプレートの「推薦入試」固定表示バグ
益田さんがInstagram/TikTokリール本編用のCanvaブランドテンプレート(`EAHXtgN-KXU`)の
表紙デザインを更新した際、確認してほしいとの依頼があった。確認したところ、データフィールド
構成(title/cover_theme/body1-1〜body5-2)自体は変わっていなかったが、**表紙の科目カテゴリ
ラベル部分が「推薦入試」という固定テキストになっており、投稿の科目(古文/日本史等)に
関係なく常に「推薦入試」と表示されてしまう不具合**を発見した。

原因調査のため`create-brand-template-draft`でテンプレートの編集用ドラフトを開いたところ、
益田さんが別件(「指定校推薦の闇5選」という投稿)で編集していた、公開版とは内容が異なる
下書きが既に存在していることが判明した。誤ってこの作業中の内容を壊さないよう、一旦作業を
止めて益田さんに状況(作業中かどうか)を確認した。「もう触っていない」との返答を得てから
修正を再開した。

自分でCanvaの構造化編集API(`edit-design`)を使い、「推薦入試」テキスト要素を自動入力
フィールド化しようとしたが、このテンプレートは動画(リール)形式のページであるため
`page type: "unsupported"`となり、要素単位の編集操作自体に対応していないことが判明した
(Canva公式ヘルプでも「動画タイムラインのブランドテンプレートへのデータフィールド接続は
現状サポートされていない」ことを確認)。このため、**益田さんご自身にCanva画面上で
「推薦入試」テキストを自動入力フィールド化していただく**よう依頼し、フィールド名
`category`で設定していただいた。

設定後、`get-brand-template-dataset`で`category`フィールドの追加を確認し、
`autofill-design`で「日本史」を流し込むテストを行い、表紙の表示が正しく
「推薦入試」→「日本史」に差し替わることを確認できた。`02_departments/creative/department.md`
のデータフィールド一覧に`category`を追記した。

**残課題**: このフィールドへの値渡しは、まだ`instagram-tiktok-daily-draft.yml`や
「Canva日次リール生成」Routine側のプロンプトには反映していない。次にリール生成の
自動化プロンプトを更新し、台本のsubject(科目)から`category`フィールドへ値を渡す
処理を追加する必要がある(未着手)。

### 追記(2026-10-19): categoryフィールドのRoutine反映、および「10選」表記の分離
「Canva日次リール生成」Routine(`created_via: http_api`のため自分では編集不可)に、
益田さんご自身がプロンプトへ以下の指示を追加してくださった。これで台本のsubject
(科目)からCanvaの`category`フィールドへ値が渡るようになった。
```
     - `category`: 台本の「科目カテゴリ」(古文/英語/日本史/現代文/総合型選抜のいずれか)をそのまま入れる
```

さらに益田さんから、Canvaのリールテンプレートで「10選」の文字を`title`フィールドから
分離し、常時固定表示のテキスト要素に変更した、との報告があった。`autofill-design`で
`title: "テスト科目"`・`category: "英語"`を渡して確認したところ、生成結果の
本文は以下のようになっており、「10選」が固定行として`category`・`title`の値の前に
単独で表示され、どちらの値にも「10選」が付加されていないことを確認できた:
```
...
10選

英語
テスト科目
...
```
これにより、従来の「`title`には必ず『〇〇10選』と入れる」という旧ルールのまま運用すると、
テンプレート側の固定「10選」と二重表示になってしまうことが判明した。
`02_departments/creative/department.md`の`title`フィールド説明、および
`02_departments/instagram_tiktok/department.md`の台本作成ルール(「タイトルは
『10選』で統一」の記述)を、「`title`には科目名・テーマの一言のみを入れ、『10選』は
含めない」という内容に修正した。

### 日本史コンテンツの対象科目からの除外(2026-10-21)
益田さんより、リール・フィード共に日本史関連の投稿は他の対象科目に比べて再生数・
いいね数が明確に低く、受験生側の需要が低いことを示していると思うとの指摘があった。
確かに短尺学習コンテンツ市場では英語・古文(単語暗記系)や総合型選抜(出願・面接系)
のように「毎年多数の受験生が共通して悩む」科目に比べ、日本史は選択者自体が限られる
科目であり、需要の薄さが数字に表れているというのは合理的な解釈だと考える。
このため、Instagram/TikTokの科目別コンテンツの対象科目を以下の通り更新した
(5科目→4科目):
- 現代文・古文(漢文除く)・英語・総合型選抜
- 日本史は対象から除外(今後、リール・フィード共に新規作成しない)

更新したファイル:
- `02_departments/instagram_tiktok/department.md`(対象科目リスト、サムネ配色ルール)
- `02_departments/creative/department.md`(Canva`category`フィールドの説明)
- `02_departments/planning/department.md`(カレンダー作成時の対象科目制約)
- `03_assets/brand-guide.md`(媒体別フォーマットの配色ルール。本ファイルは旧ルールが
  一部残る注記付きだったが、該当箇所も合わせて修正した)
- `01_HQ/calendar.md`(11/17〜11/23週のIG/TikTokテーマを「日本史の年号・出来事の
  暗記整理法」→「現代文の選択肢の消去法・読解テクニック」に変更。対象科目リストの
  注記も4科目に更新)

過去に作成済みの日本史関連ドラフト(`02_departments/instagram_tiktok/drafts/`配下)
は記録としてそのまま残し、削除・修正は行っていない。
