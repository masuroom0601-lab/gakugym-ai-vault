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
2. 06:05 クリエイティブ制作(`creative-pipeline.yml`、サムネ・フィード画像を自動生成)
3. 06:10 校正担当チェック(`proofreading-daily-check.yml`、生成画像の文字化けも目視対象)
4. 06:20 秘書担当タスクカード起票・承認待ちリスト更新(`hq-secretary-daily-tasks.yml`)
5. 06:30 統括担当の日次集計・ダッシュボード更新(`hq-director-daily-report.yml`)

益田さんは06:30以降に `01_HQ/tasks/approval-pending.md` とダッシュボードを確認し、
承認待ちの下書きを確認・編集・承認(published/フォルダへ移動)すればよい状態になっています。

**このPhaseが終わると**: 益田さんは毎朝daily-logとdashboardを見るだけで、
「何が承認待ちか」「何が滞留しているか」が一目でわかる状態になる。

### Phase 2: クリエイティブ制作パイプライン
目的: Instagram/TikTokのサムネイル画像・リール動画を、文字化けせず自動生成する。

- [x] Playwright実行環境をGitHub Actions上に用意(`actions/setup-node` + `npx playwright install --with-deps chromium`)
- [x] テンプレA/B/C(フィード用)・リールサムネの固定HTML/CSSテンプレートを作成
      (`03_assets/creative-templates/`、Noto Sans JP埋め込み+CI側にfonts-noto-cjkも
      インストールして二重に文字化け対策)。**益田さんによる目視確認がまだ残っています**
      (テンプレートのデザイン自体をこの目で見て問題なければ「確認済み」として以後固定にしてください)
- [x] 「テキスト内容+科目別配色パラメータ」だけを差し込んでスクリーンショット→PNG化するスクリプトを作成
      (`tools/creative/render.js`。ローカルで実データを使って動作確認済み)
- [x] 文字数ルール(縦4行まで/横17文字まで=サムネの煽り文句・見出し)の自動検証を組み込み、
      フィード本文は自然に折り返す長文のため詰め込み過ぎのみを緩くチェック
- [x] creative部署のGitHub Actionsワークフロー(`creative-pipeline.yml`、06:05 JST)を新規作成し、
      Instagram/TikTok担当の台本 → spec.json変換(Claude) → 画像生成(Playwright、決定的処理)
      → コミットまで自動化
- [ ] 動画側(リール本編)は未着手。テキストを透過PNGで書き出しffmpegでoverlay合成する
      手順は、**背景となる著作権フリーのストック動画素材(勉強机/コーヒー/キャンドル等)を
      益田さんに用意してもらってから**着手する(`03_assets/videos/`に配置)
- [ ] 背景写真素材(`03_assets/images/backgrounds/`)の投入待ち。投入されるまでは
      サムネイルはグラデーションのプレースホルダー背景で生成される

**依存**: Instagram/TikTok部署のdrafts生成が安定稼働していること(Phase 1完了、達成済み)

**次のアクション(益田さん対応)**:
1. `creative-pipeline.yml` を`workflow_dispatch`で一度手動実行し、生成された
   `02_departments/creative/drafts/generated/<task_id>/*.png` を確認する
2. 問題なければテンプレートを「確認済み」として、以後デザイン変更は都度指示制にする
3. 著作権フリーの背景写真(縦長9:16、暗めのトーン)を `03_assets/images/backgrounds/` に追加
4. 余裕があれば、リール本編動画用のストック動画素材を `03_assets/videos/` に追加
   (動画合成パイプラインはこれの後で着手)

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

### Phase 4: 自社ドメインHP構築
目的: readdy版サイトを踏襲しつつ、自社ドメイン+無料ホスティングで再構築する。

- [ ] ドメイン取得(実費、年額) → お名前.com等で取得
- [ ] GitHub PagesまたはCloudflare Pagesでのホスティング設定(無料枠)
- [ ] hp/department.mdのサイト構成(トップ/料金/講師経歴/コラム/お問い合わせ)を
      静的HTML/CSSで実装(readdyのプレビューを参考にしつつ著作権フリー素材へ差し替え)
- [ ] お問い合わせフォーム: 無料の外部フォームサービス(例: Googleフォーム埋め込み、
      または画像認証付きの無料フォームサービス)を選定・連携
- [ ] note/Amebaのコラム記事をHPのコラムページに転載する自動化ワークフローを追加
      (note_ameba/published → hp/drafts への変換タスク)
- [ ] 振込口座情報など機微情報は、公開後に益田さんが直接ソースへ手入力(Vaultには含めない)

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
| ドメイン取得・DNS設定 | Phase4 | 実費(年額) |
| お問い合わせフォームサービスの選定・契約(無料枠) | Phase4 | |
| LINE公式アカウント(Messaging API)チャネル開設 | Phase6 | |
| Amazon KDPアカウント開設 | Phase7 | |
| 各drafts/reviewの最終承認・編集 | 日次運用 | brand-guide.md「6. AI生成コンテンツの扱い」に基づく必須ステップ |
| 景品表示法等、法令に抵触しうる表現の最終判断 | 日次運用 | AIはNGルールでガードするが最終責任は本人 |
| 週次アナリティクス入力シートへの数値記入 | Phase5 | `04_analytics/manual-input/<週の月曜日>.md`。公式APIトークン未設定のため唯一の情報源 |
| 著作権フリーの背景写真の追加 | Phase2 | `03_assets/images/backgrounds/`。未追加の間はプレースホルダー背景 |

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

1. `docs/dashboard/`をGitHub Pagesで公開する(リポジトリのSettings → Pages →
   Branch: main, Folder: /docs を選択。無料・追加コストなし)
2. `hq-director-daily-report.yml`と`planning-monthly-calendar.yml`を一度
   `workflow_dispatch`で手動実行し、正しく動作するか確認する
3. Omnirouteのアカウント情報を用意し、`01_HQ/setup guides/omniroute-setup.md.md`の
   未確定事項を埋めて実接続する
4. Phase1残タスク(秘書担当・校正担当の自動化ワークフロー)の実装を次のセッションで進める
