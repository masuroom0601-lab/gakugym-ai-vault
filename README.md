# 学ジムAI事業部 Obsidian Vault

このVaultは、学ジムのSNS/Web発信をAI社員体制で運用するための共有メモリです。
全体設計・実現までのロードマップの詳細は **`01_HQ/roadmap.md`** を参照してください
(現状整理・フェーズ別タスク・運用サイクル・益田さんが対応すべき人手タスク一覧をまとめています)。

## フォルダの見方
- 00_INBOX: ネタ・思いつきの一時置き場
- 01_HQ: 統括・秘書担当が使うタスクカード/日次ログ/月間カレンダー/roadmap.md/setup guides
- 02_departments: 各部署のdepartment.md(役割定義)とdrafts/review/publishedフォルダ
- 03_assets: brand-guide.md(全部署共通ルール)と素材(画像・動画)
- 04_analytics: 分析担当のレポート置き場
- docs: GitHub Pagesで公開する静的サイト一式
  - docs/index.html 他: 学ジム公式サイト本体(トップ/料金/講師経歴/コラム/お問い合わせ)
  - docs/dashboard: ドット絵ゲーム風オフィスダッシュボード。
    dashboard-state.jsonはダッシュボード用の集計データ(統括担当AIが日次自動更新、手編集しない)

## 運用の基本ルール
- 投稿content生成は自動化するが、公開前には必ず本人が確認する
- 追加予算はかけず、Claude Code Proの契約のみで完結させる(ドメイン代等の実費のみ許容)
- トークン使用量最適化のためのOmniroute連携手順は `01_HQ/setup guides/omniroute-setup.md.md` を参照

## サイト/ダッシュボードの公開方法(初回のみ)
1. GitHubリポジトリの Settings → Pages を開く
2. Source: "Deploy from a branch"、Branch: `main` / Folder: `/docs` を選択して保存
3. 数分後に `https://<ユーザー名>.github.io/gakugym-ai-vault/`(公式サイト)、
   `https://<ユーザー名>.github.io/gakugym-ai-vault/dashboard/`(ダッシュボード)で閲覧可能
4. 独自ドメインに接続したい場合は `01_HQ/setup guides/custom-domain-setup.md.md` を参照
   (ホスティングは無料、ドメイン取得のみ実費)
