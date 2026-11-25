# プロフィールのハイライト用画像(2026-11-17追加)

各アカウントのプロフィールに置くハイライト(ストーリー画像 1080x1920)。台本は各部署の `highlights/*.md`。
- ③スマホ対策「受験の考え方」: `sumaho_habit/highlights/juken-kangaekata.md` → `out/sumaho_habit/`
- ①英検「英語の考え方」: `instagram_tiktok/highlights/eigo-kangaekata.md` → `out/instagram_tiktok/`
- ②総合型「総合型の考え方」: `sougou/highlights/sougou-kangaekata.md` → `out/sougou/`

描き直し: `python3 render_highlight.py <台本.md> out/<部署>`(01.png〜と、ハイライトのカバー用 cover.png)。
写真背景は `assets/photo_bg/*.jpg` に置いた写真を順番に使う(無い間は勉強風景の素材動画の1コマ)。

## 自己紹介(2026-11-17追加)
- 台本: 各部署の `highlights/jikoshoukai.md`(17枚。16枚目までは3アカウント共通、17枚目のフォロー誘導だけ違う。経歴は中学進学後から。中学受験・寮生活は出さない)
- 描画: `python3 render_intro.py <台本.md> out/<部署>/intro`(淡くした写真の背景+手書き風の文字 Klee One、赤字と黄色のマーカー)
- 出典: `sumaho_habit/story-episodes.md`(Kindle本の序章)の事実だけ。合格した大学名は益田さんの判断で出す
- 最後の「フォローして〜」の帯は押せないので、投稿時にリンクスタンプ(またはメンション)を重ねる

## 怪我をしていました(2026-11-25追加)
- 台本: `creative/highlights/kega.md`(7枚。①②③共通)→ `out/common/kega/`
- 描画: `python3 render_intro.py kega.md out/common/kega`。写真は `[photo] ファイル名` で `assets/photos/` から載せる(益田さん提供の写真)
