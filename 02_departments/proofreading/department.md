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
- 対象は instagram_tiktok / x_threads / note_ameba / line / sumaho_habit の drafts/ で status: draft のもの
  (sumaho_habitは2026-11-03追加。直近2日分のみ。③専用のチェック項目
  〔送客なし・書式・dopamine版の表現・重複〕はワークフローのプロンプトに記載。
  ③の下書き生成ワークフロー完了直後にも自動で走る)
- ファイルの物理的な移動は行わず、frontmatterの status のみを変更する
  (status: review = 校正担当のチェック済み・あなたの最終承認待ち)

## 大学 学部別倍率ランキングのファクトチェック(2026-11-03追加・必須)
③massu_smartphoneで投稿する倍率ランキングリールのデータ(`02_departments/sougou/ranking/data/*.json`)は、
校正担当が**毎回必ず**ファクトチェックする(`.github/workflows/ranking-factcheck.yml`、毎日06:20 JST+手動実行)。
- まず `factcheck_ranking.py` が大学公式の出典を取りに行き、年度・志願者(受験者)数・合格者数・倍率を機械照合
- そのうえで校正担当AIが、行と出典の表の対応(学科・方式・列の取り違え)・年度ルール・倍率の定義・
  「非公開」の理由・出典/写真クレジットを確認し、JSONの`factcheck.status`を ok / ng にする
- `render_ranking.py` は `factcheck.status: ok` のデータでしか本番の動画を作らない(見本のみ例外)
