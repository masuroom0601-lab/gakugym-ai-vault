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

これでPhase1(HQ運用ループ)は「統括→秘書→各部署→校正→承認」のうち、
Omniroute接続以外はワークフロー化が完了しています。

### まだ手つかず(次フェーズ)
- analytics・improvement・creative・hp の自動化ワークフロー
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
3. 06:20 秘書担当タスクカード起票・承認待ちリスト更新(`hq-secretary-daily-tasks.yml`)
4. 06:30 統括担当の日次集計・ダッシュボード更新(`hq-director-daily-report.yml`)

益田さんは06:30以降に `01_HQ/tasks/approval-pending.md` とダッシュボードを確認し、
承認待ちの下書きを確認・編集・承認(published/フォルダへ移動)すればよい状態になっています。

**このPhaseが終わると**: 益田さんは毎朝daily-logとdashboardを見るだけで、
「何が承認待ちか」「何が滞留しているか」が一目でわかる状態になる。

### Phase 2: クリエイティブ制作パイプライン
目的: Instagram/TikTokのサムネイル画像・リール動画を、文字化けせず自動生成する。

- [ ] Playwright実行環境をGitHub Actions上に用意(`actions/setup-node` + `npx playwright install --with-deps chromium`)
- [ ] テンプレA/B/C(フィード用)・リールサムネ・リール本編の固定HTML/CSSテンプレートを、
      益田さんと1回だけ人間確認しながら作成(Noto Sans JP埋め込み必須)
- [ ] 「テキスト内容+科目別配色パラメータ」だけを差し込んでスクリーンショット→PNG化するスクリプトを作成
- [ ] 動画側は、テキストを透過PNGで書き出し、ffmpegでoverlay合成する手順を確立
- [ ] 文字数ルール(縦4行まで/横17文字まで)の自動検証を組み込む
- [ ] creative部署のGitHub Actionsワークフローを新規作成し、
      Instagram/TikTok担当が生成した台本を受け取って画像・動画を自動生成 → reviewへ

**依存**: Instagram/TikTok部署のdrafts生成が安定稼働していること(Phase 1完了後)

### Phase 3: 横展開の拡大(TikTok単独投稿・YouTube Shorts)
目的: Instagramリールで作った動画をTikTok・YouTube Shortsにも展開する。

- [ ] TikTok for Developers(Content Posting API)のアプリ申請・審査
      (個人利用でも審査が必要な場合があるため早めに申請)
- [ ] YouTube Data API v3の認証設定(OAuth、Shorts判定は動画の縦横比・尺で自動)
- [ ] 各APIのアクセストークン管理を`01_HQ/setup guides/`に手順書として追加
      (Threads同様、有効期限管理をhq_directorのエスカレーション対象に追加)
- [ ] Instagram/TikTok部署のdepartment.mdを更新し、「TikTok単独投稿」「YouTube Shorts」を
      明示的なアウトプット単位として追加
- [ ] 当面は「動画ファイルの自動生成まで」とし、実際のアップロードは承認後に
      益田さんが手動 or 半自動(承認後ワンクリックでAPI投稿)で行う運用から始める

**リスク**: 各プラットフォームのAPI審査・規約変更に時間がかかる可能性が高いため、
このPhaseは並行してPhase 4(HP)を進めながら気長に進める。

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

### Phase 5: 分析・改善ループの自動化
目的: 「投稿→分析→改善提案→次の投稿に反映」のループを回す。

- [ ] Instagram/Threads/YouTube/LINEの公式Insight/Analytics APIから自動取得するワークフロー
- [ ] X/note/Amebaは公式APIがないため、益田さんが手動入力するための簡易フォーム
      (Obsidianのテンプレート or 04_analytics/input.mdのような固定フォーマット)を用意
- [ ] analytics部署の週次レポート生成ワークフロー
- [ ] improvement部署の週次改善提案タスク起票ワークフロー(レポート更新後にトリガー)
- [ ] 企画担当が改善提案を翌月カレンダーに反映するロジックをplanning-monthly-calendar.ymlに追記

### Phase 6: LINE公式配信の完全自動化
目的: 現状「published/フォルダに置くだけ」のLINE配信を、Messaging APIで実配信まで自動化する。

- [ ] LINE公式アカウント(Messaging API)のチャネル作成・アクセストークン取得
- [ ] `01_HQ/setup guides/line-messaging-api-setup.md.md` を新規作成
- [ ] line/department.mdの承認フロー(published → 配信)の「配信」ステップをAPI連携に置き換え
- [ ] 誤配信防止のため、承認済み(status: approved)のファイルのみ配信対象にするガードを実装

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

### 日次(GitHub Actions cronで自動実行、JST 06:00前後)
1. 統括担当: 前日の滞留チェック・当日必要なネタの洗い出し
2. 秘書担当: タスクカード起票(Phase1で実装予定)
3. Instagram/TikTok担当・X/Threads担当: 下書き生成
4. (3日に1回)LINE担当: X/Threads publishedから選定
5. 校正担当: drafts内容をチェックしreviewへ(Phase1で実装予定)
6. 統括担当: dashboard-state.json更新、daily-log記録
7. **益田さん**: dashboard(docs/dashboard)とdaily-logを確認し、reviewフォルダの内容を承認 or 修正指示

### 週次
- 月曜: note/Ameba担当が長文記事を1本生成
- 分析担当が週次レポートを更新(Phase5)
- 投稿改善提案担当が改善タスクを起票(Phase5)

### 月次
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
| TikTok Developer / YouTube Data API 申請 | Phase3 | 審査に時間がかかる可能性 |
| ドメイン取得・DNS設定 | Phase4 | 実費(年額) |
| お問い合わせフォームサービスの選定・契約(無料枠) | Phase4 | |
| LINE公式アカウント(Messaging API)チャネル開設 | Phase6 | |
| Amazon KDPアカウント開設 | Phase7 | |
| 各drafts/reviewの最終承認・編集 | 日次運用 | brand-guide.md「6. AI生成コンテンツの扱い」に基づく必須ステップ |
| 景品表示法等、法令に抵触しうる表現の最終判断 | 日次運用 | AIはNGルールでガードするが最終責任は本人 |

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
