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
