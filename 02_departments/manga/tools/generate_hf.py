"""Hugging Faceの無料Space(Animagine XL 4.0)で漫画用の画像を生成する。

鍵(Hugging Faceのトークン)はクラウド環境のネットワーク設定に保存済みで、
通信時に自動で差し込まれる。このスクリプトには鍵を書かない。

使い方:
    python3 02_departments/manga/tools/generate_hf.py "プロンプト" 出力先.png [--seed 123] [--size 896x1152]
"""
import argparse
import shutil

from gradio_client import Client

SPACE = "Asahina2K/animagine-xl-4.0"
# 漫画の絵柄にそろえるため、全ての生成に付ける共通タグ
STYLE = "monochrome, greyscale, manga, screentone, lineart"
NEGATIVE = (
    "lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, "
    "worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry, "
    "color, large breasts, cleavage, nsfw, animal ears, fox ears, cat ears, tail, kemonomimi"
)
SIZES = ["1024x1024", "1152x896", "896x1152", "1216x832", "832x1216", "1344x768", "768x1344"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--size", default="896x1152", choices=SIZES)
    a = ap.parse_args()

    # gradio_clientは鍵を独自のヘッダーで送るため、プロキシが鍵を差し込める
    # Authorizationヘッダーにダミー値を入れておく(実際の鍵はプロキシが上書きする)
    client = Client(SPACE, headers={"Authorization": "Bearer proxy-injected"}, verbose=False)
    images, meta = client.predict(
        prompt=f"{a.prompt}, {STYLE}",
        negative_prompt=NEGATIVE,
        seed=a.seed,
        aspect_ratio_selector=a.size.replace("x", " x "),
        style_selector="(None)",
        api_name="/generate",
    )
    shutil.copy(images[0]["image"], a.out)
    print("saved", a.out, "seed", meta.get("seed", a.seed) if isinstance(meta, dict) else a.seed)


if __name__ == "__main__":
    main()
