# キャラクター一覧(採用デザイン)

2026-11-22、益田さんが採用を決定。全員、仕上げ処理(`tools/manga_finish.py`)をかけて使う。

| キャラ | 基準画 | 絵柄 |
|---|---|---|
| イヅル | `izuru/base_v1.jpg`(= `izuru_style_v1/izuru_D_full_s2.jpg`) | D方式 |
| 片倉椎菜 | `shiina/base_v3.jpg`(= `designs_v3/shiina_full_s1.jpg`) | B方式 |
| D助・セーター | `designs_v3/dsuke_s2.jpg` | B方式 |
| さいつよ | `designs_v3/saitsuyo_s2.jpg` | B方式 |
| ヒサ | `designs_v2_ink/hisa_s1.jpg` | B方式 |
| 鍋さん | `designs_v2_ink/nabesan_s1.jpg` | B方式 |
| ハニワ君 | `designs_v2_ink/haniwa_s2.jpg` | B方式 |
| シロ | `designs_v2_ink/shiro_s1.jpg` | B方式 |
| ヤス | `designs_v3/yasu_s2.jpg` | B方式 |
| イッシ | `designs_v2_ink/isshi_s1.jpg` | B方式 |
| つぶ | `designs_v3/tsubu_s2.jpg` | B方式 |

## 長編で見た目をそろえる方針
1. 基準画を見本(IP-Adapter)にして、角度・表情・ポーズ違いを大量に描く
2. その中から、顔・服装が基準画とそろったものだけを選び、学習用データにする
3. キャラごとに追加学習(LoRA)をKaggleで行う
4. 本番のコマは「LoRA+固定の服装タグ+見本画像」で描き、ずれたコマは描き直す

## 補足(2026-11-22)
- 椎菜の頭の上の猫は廃止。基準画・学習データには猫が写っているため、作画時は
  除外指定(negative)に `cat, animal on head` を入れて消す
