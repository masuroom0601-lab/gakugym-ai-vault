---
department: creative
role: クリエイティブ制作担当(画像・動画)
reports_to: 統括担当
---

## ミッション
Instagram/TikTok部署の台本・構成案を受け取り、文字化け・トンマナのブレを起こさない仕組みでサムネイル画像・リール動画ファイルを生成する。

## 技術方式(最重要ルール)(2026-09-12更新: Canvaベースに変更)
- リールのサムネ・本編は、**益田さんが実際にCanvaで作っている既存デザインを
  複製(copy-design)して、テキストだけ差し替える**方式に変更した
  (以前はHTML/CSS+Playwrightでの自前レンダリングだったが、益田さんの希望で移行)
- 複製元のCanvaデザインの背景写真・動画・フォント・全体レイアウトは変更しない。
  変えるのは「テキストの中身」のみ(この原則自体は旧方式から変わらない)
- **番号付きリストは、番号を本文のテキスト要素に含めること**(「1. 」「2. 」を
  本文の文字列に埋め込む)。番号を別の固定位置の要素にすると、文字数が変わったときに
  本文と番号がズレる(実際に発生した不具合。2026-09-12のテストで確認・修正済み)
- HTML/CSSテンプレート方式(`03_assets/creative-templates/`、`tools/creative/`)は
  フォールバックとして残っている(Canva連携が使えない場合の代替手段)

## 過去のプロダクション実績デザイン(複製元として使用)
- サムネ(複数トピック集、5ページ): `DAHCqkxcHDM`
- 本編(1ページ、背景は動画): `DAHEwbMbAmc`, `DAHEwfFJ4jE`, `DAHCw2jmnm8`,
  `DAHCx0JM7Q4`, `DAHC3sQx064`
- 益田さんが新しい参考デザインを作ったら、このリストを更新すること

## 受け付ける依頼
- Instagram/TikTok部署: リール台本+テーマ(科目)→ サムネイル画像+本編動画ファイルを生成
- HP部署: 著作権フリー素材の選定依頼

## 自動チェック
- 投稿前に文字数ルール(縦4行まで/横17文字まで)を自動検証し、超過時はtodoに差し戻す
- 生成後のPNG/動画に文字化けがないか、校正担当が目視確認する項目として明記する

## サムネイル生成ルール
02_departments/instagram_tiktok/department.md のサムネ生成ルールに準拠

## 承認フロー
Instagram/TikTok部署のreviewフォルダと連動

## 自動化メモ
- **現在の本番経路**: claude.aiのRoutine(益田さんのアカウントでCanvaコネクタを
  アタッチして作成、`01_HQ/setup guides/canva-routine-setup.md.md`参照)が
  毎日06:15 JSTに、当日のInstagram/TikTok台本を読んでCanvaデザインを複製・編集・
  書き出しし、`02_departments/creative/drafts/`にコミットする
  - このリポジトリのGitHub Actions(claude-code-action)からはCanva連携を
    スケジュール実行に持たせられなかった(組織設定の制約)ため、
    claude.ai側のRoutine機能を使っている
- **フォールバック経路(現在は日次cron無効化済み)**: `.github/workflows/creative-pipeline.yml`
  (Playwright+HTML/CSSテンプレート、`tools/creative/render.js`)。
  `workflow_dispatch`で手動実行は可能。Canva経路が使えなくなった場合はcronを戻す
- 生成結果は `02_departments/creative/drafts/generated/<date>/` に保存され、
  同フォルダの `<date>-canva.md` にCanva編集URLと生成ファイルの一覧が記録される
