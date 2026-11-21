"""見本画像(キャラクターの基準画)を渡して、同じキャラを別のポーズ・表情・構図で描かせる。

Hugging Faceの無料Space(Qwen-Image-Edit、Apache 2.0ライセンス)を使う。
鍵はクラウド環境のネットワーク設定に保存済みで、通信時に自動で差し込まれる。

使い方:
    python3 02_departments/manga/tools/edit_qwen.py 見本.png "指示文(英語)" 出力先.png [--seed 1] [--full]

    --full: 高速版ではなく公式版(40ステップ、高品質だが無料枠の消費が大きい)を使う
"""
import argparse
import shutil

from gradio_client import Client, handle_file

FAST = "multimodalart/Qwen-Image-Edit-Fast"
FULL = "Qwen/Qwen-Image-Edit-2511"
# 漫画の絵柄を保つための共通指示
STYLE = (
    "Keep exactly the same character: same face, same hairstyle, same ribbons, same outfit and colors "
    "(white puffy-sleeve blouse, black necktie, black choker, dark high-waist skirt, black gloves). "
    "Black-and-white Japanese manga style with screentone and clean ink lines, plain white background."
)
HEADERS = {"Authorization": "Bearer proxy-injected"}  # 実際の鍵はプロキシが上書きする


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("prompt")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    prompt = f"{a.prompt} {STYLE}"

    if a.full:
        c = Client(FULL, headers=HEADERS, verbose=False)
        result, seed = c.predict(
            images=[{"image": handle_file(a.ref), "caption": None}], prompt=prompt,
            seed=a.seed, randomize_seed=False, height=1216, width=832,
            rewrite_prompt=False, api_name="/infer",
        )
        path = result[0]["image"] if isinstance(result[0]["image"], str) else result[0]["image"]["path"]
    else:
        c = Client(FAST, headers=HEADERS, verbose=False)
        result, seed = c.predict(
            image=handle_file(a.ref), prompt=prompt, seed=a.seed, randomize_seed=False,
            rewrite_prompt=False, api_name="/infer",
        )
        path = result if isinstance(result, str) else result["path"]
    shutil.copy(path, a.out)
    print("saved", a.out, "seed", seed)


if __name__ == "__main__":
    main()
