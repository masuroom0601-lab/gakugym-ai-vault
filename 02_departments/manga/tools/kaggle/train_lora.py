"""キャラクター専用LoRAの学習をKaggleに送る。

使い方:
    python3 train_lora.py 設定.json 作業フォルダ --user KAGGLEユーザー名 --slug lora-shiina
設定.json の例は characters/shiina/lora_v1.json を参照。学習データは事前に
Kaggleの非公開データセット(dataset)としてアップロードしておく。
"""
import argparse, json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("cfg"); ap.add_argument("workdir")
ap.add_argument("--user", required=True); ap.add_argument("--slug", required=True)
a = ap.parse_args()
cfg = json.load(open(a.cfg))
src = open(os.path.join(HERE, "train_template.py")).read().replace("__CFG__", json.dumps(cfg, ensure_ascii=False))
os.makedirs(a.workdir, exist_ok=True)
open(os.path.join(a.workdir, "train.py"), "w").write(src)
json.dump({"id": f"{a.user}/{a.slug}", "title": a.slug, "code_file": "train.py", "language": "python",
           "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
           "machine_shape": "NvidiaTeslaT4", "dataset_sources": [f"{a.user}/{cfg['dataset']}"],
           "competition_sources": [], "kernel_sources": []},
          open(os.path.join(a.workdir, "kernel-metadata.json"), "w"), indent=1)
subprocess.run(["kaggle", "kernels", "push", "-p", a.workdir], check=True)
