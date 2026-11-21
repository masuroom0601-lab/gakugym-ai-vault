"""Kaggle用の生成ノートブックを組み立てて送信する。

使い方:
    python3 build_kernel.py jobs.json 見本.png 作業フォルダ --user KAGGLEユーザー名 [--slug manga-gen]
送信後の確認・回収:
    kaggle kernels status ユーザー名/slug
    kaggle kernels output ユーザー名/slug -p 保存先
"""
import argparse, base64, io, json, os, subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = {
    "style": "monochrome, greyscale, manga, screentone, lineart",
    "quality": "masterpiece, high score, great score, absurdres",
    "negative": ("lowres, bad anatomy, bad hands, text, error, missing finger, extra digits, fewer digits, cropped, "
                 "worst quality, low quality, low score, bad score, average score, signature, watermark, username, blurry, "
                 "color, large breasts, cleavage, nsfw, animal ears, tail, smug, smirk"),
    "steps": 28, "cfg": 5.0, "ip_scale": 0.55,
}

ap = argparse.ArgumentParser()
ap.add_argument("jobs"); ap.add_argument("ref"); ap.add_argument("workdir")
ap.add_argument("--user", required=True); ap.add_argument("--slug", default="manga-gen")
a = ap.parse_args()

ref = Image.open(a.ref).convert("RGB"); ref.thumbnail((512, 512))
buf = io.BytesIO(); ref.save(buf, "JPEG", quality=90)
src = open(os.path.join(HERE, "gen_template.py")).read()
src = (src.replace("__JOBS__", json.dumps(json.load(open(a.jobs))))
          .replace("__REF__", base64.b64encode(buf.getvalue()).decode())
          .replace("__CFG__", json.dumps(CFG)))
os.makedirs(a.workdir, exist_ok=True)
open(os.path.join(a.workdir, "gen.py"), "w").write(src)
json.dump({
    "id": f"{a.user}/{a.slug}", "title": a.slug, "code_file": "gen.py",
    "language": "python", "kernel_type": "script", "is_private": True,
    "enable_gpu": True, "enable_internet": True, "machine_shape": "NvidiaTeslaT4",
    "dataset_sources": [], "competition_sources": [], "kernel_sources": [],
}, open(os.path.join(a.workdir, "kernel-metadata.json"), "w"), indent=1)
subprocess.run(["kaggle", "kernels", "push", "-p", a.workdir], check=True)
