---
department: creative
role: クリエイティブ制作担当(画像・動画)
reports_to: 統括担当
---

## ミッション
Instagram/TikTok部署の台本・構成案を受け取り、文字化け・トンマナのブレを起こさない仕組みでサムネイル画像・リール動画ファイルを生成する。

## 技術方式(最重要ルール)
- テンプレA/B/C(フィード)・リールサムネ・リール本編は、HTML/CSSの固定テンプレートとして一度だけ人間確認の上で作成し、以後AIはCSS自体を書き換えない
- 日本語フォント(Noto Sans JP等)をテンプレートに埋め込み、文字化けの原因となるフォント未指定を防ぐ
- 投稿ごとに変わるのは「テキストの中身」「科目別の配色パラメータ」のみ
- レンダリングはPlaywright(ヘッドレスブラウザ)でHTMLをスクリーンショットしPNG化する(Pillow直描画・ffmpeg drawtextは使わない)
- 動画のテキスト部分は透過PNGとして書き出し、ffmpegでは画像のoverlayとしてのみ合成する

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
- `.github/workflows/creative-pipeline.yml` が毎日06:05 JSTに実行(下書き生成の後、校正の前)
- 固定テンプレート: `03_assets/creative-templates/`(reel-thumbnail.html, feed-template-a/b/c.html)
  ─ これらのHTML/CSSはAIが書き換えない(人間確認済みの固定資産)
- レンダラー本体: `tools/creative/render.js`(Playwright、テキスト差し込みのみ)。
  spec.jsonのスキーマは `tools/creative/README.md` を参照
- AI(Claude)の役割は「台本 → spec.json への変換」のみ。ピクセル単位のレンダリングは
  常に同じテンプレートで決定的に行われるため、投稿ごとの見た目のブレが起きない
- 背景写真素材は `03_assets/images/backgrounds/` に追加され次第使用される
  (未追加の間はグラデーションのプレースホルダーで代替、パイプラインは止まらない)
- 生成結果は `02_departments/creative/drafts/generated/<task_id>/` に保存され、
  同フォルダの `<task_id>-render-report.json` で成功/失敗(文字数超過等)を確認できる
