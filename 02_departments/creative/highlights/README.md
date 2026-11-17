# プロフィールのハイライト用画像(2026-11-17追加)

各アカウントのプロフィールに置くハイライト(ストーリー画像 1080x1920)。台本は各部署の `highlights/*.md`。
- ③スマホ対策「受験の考え方」: `sumaho_habit/highlights/juken-kangaekata.md` → `out/sumaho_habit/`
- ①英検「英語の考え方」: `instagram_tiktok/highlights/eigo-kangaekata.md` → `out/instagram_tiktok/`
- ②総合型「総合型の考え方」: `sougou/highlights/sougou-kangaekata.md` → `out/sougou/`

描き直し: `python3 render_highlight.py <台本.md> out/<部署>`(01.png〜と、ハイライトのカバー用 cover.png)。
写真背景は `assets/photo_bg/*.jpg` に置いた写真を順番に使う(無い間は勉強風景の素材動画の1コマ)。
