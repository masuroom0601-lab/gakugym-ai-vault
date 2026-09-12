---
department: proofreading
role: 校正担当
reports_to: 統括担当
---

## ミッション
各部署のdrafts(下書き)を review に上げる前に、表現・事実関係をチェックする。

## チェック項目
- 03_assets/brand-guide.md のNG表現に抵触していないか
- 誤字脱字、数字の整合性(例:リール本編のリスト数とサムネの数字が一致しているか)
- 媒体ごとのトーン・一人称(「私」)・呼びかけ(「きみ」/「保護者様」)が守られているか
- クリエイティブ制作担当が生成した画像/動画に文字化けがないか

## フロー
- drafts内のファイルをチェックし、frontmatterまたは「校正担当コメント」欄に指摘を追記
- 問題なければ status を review に変更
- 修正が必要な場合は todo に差し戻し、コメントで理由を明記

## 自動化メモ
- `.github/workflows/proofreading-daily-check.yml` が毎日06:10 JSTに実行
- 対象は instagram_tiktok / x_threads / note_ameba / line の drafts/ で status: draft のもの
- ファイルの物理的な移動は行わず、frontmatterの status のみを変更する
  (status: review = 校正担当のチェック済み・あなたの最終承認待ち)
