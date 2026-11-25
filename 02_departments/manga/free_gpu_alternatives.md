# Kaggleが使えなくなったときの、無料でAI漫画を描く方法(2026-11-24 調査)

いまの作画は「Animagine XL 4.0 + 自作LoRA(椎菜・イヅル)+ IP-Adapter(見本の絵)」をKaggleの無料GPUで動かしている。
代わりの方法は、この組み合わせがそのまま動くかどうかで2種類に分かれる。

## A. 今の作り方がそのまま動く(GPU付きのノートブック)
| 方法 | 無料の量(目安) | 自動で送れるか | 評価 |
|---|---|---|---|
| Lightning AI Studio | 毎月の無料クレジット(T4で約20時間前後) | ○ API鍵で外から動かせる | **新規登録を受け付けていない(2026-11-25、益田さんが確認)**。使えない |
| Google Colab(無料) | T4。1回最大12時間だが、空き次第で使えない日もある | × ブラウザで開いて手動実行 | **第一候補(2026-11-25から)**。益田さんがPCで開けば動く |
| Paperspace Gradient(無料) | 古いGPU(M4000)、1回6時間 | △ | 遅い。最後の手段 |
| SageMaker Studio Lab | 1日4時間 | — | 新規登録が2026年7月で終了。使えない |

- どれも、生成スクリプト(tools/kaggle/gen_template.py)と LoRA・見本の絵を持ち込めば同じ絵柄で描ける
- Kaggle の週30時間に比べると、どれも量が少ない。1話(約180枚・1.5時間)なら月に数話は描ける

## B. 自作LoRAは使えないが、手軽(無料の画像生成サービス)
| 方法 | 無料の量(目安) | 注意 |
|---|---|---|
| Hugging Face の無料Space(tools/generate_hf.py、tools/edit_qwen.py で試し済み) | 1日 数分〜数回程度 | 自作LoRAなし。背景・小物ならこれで足りる |
| AI Horde(ボランティアのGPUを借りる仕組み) | 無料。混むと待つ | 公開されたLoRAしか使えない。自作LoRAを公開するのは不可 |

→ Bだけでは椎菜・イヅルの顔がそろわない。背景や小物、見本の絵が要らないコマの「つなぎ」に使う。

## おすすめの備え
1. Lightning AI は新規登録を受け付けていないため見送り(2026-11-25)
2. Kaggle が使えない日は、Claude が Colab 用のノートブック(生成スクリプト・LoRA・見本の絵の読み込みつき)を用意し、益田さんがPCで開いて実行する
3. 背景・小物だけなら、B の無料サービスでつなぐ

参考: https://fastero.com/blog/kaggle-alternatives / https://gputracker.dev/blog/google-colab-alternatives /
https://huggingface.co/docs/hub/spaces-zerogpu / https://dbzer0.com/blog/tag/lora/
