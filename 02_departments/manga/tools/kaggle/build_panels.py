"""ネームのデータとコマごとのプロンプトから、コマ画像の生成ジョブを組み立ててKaggleに送る。

使い方: python3 build_panels.py names/ep01_name.py names/ep01_panels.py 作業フォルダ --user ユーザー名 --pages 17,18,19 [--slug manga-gen]
- コマの縦横比はネームの枠の大きさから自動で決め、SDXLの解像度の中から一番近いものを使う
"""
import argparse, base64, importlib.util, io, json, os, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = [(1024,1024),(1152,896),(896,1152),(1216,832),(832,1216),(1344,768),(768,1344),(1536,640),(640,1536)]
W, H, M, G = 1000, 1414, 60, 14
def load(p):
    s = importlib.util.spec_from_file_location(os.path.basename(p)[:-3], p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def panel_rects(rows):
    rects = []; y = M; uh = H - 2*M - G*(len(rows)-1)
    for rh, panels in rows:
        h = int(uh*rh); xr = W - M; uw = W - 2*M - G*(len(panels)-1)
        for pw, *_ in panels:
            w = int(uw*pw); rects.append((xr-w, y, xr, y+h)); xr = xr - w - G
        y += h + G
    return rects
def best_size(w, h):
    r = w/h; return min(SIZES, key=lambda s: abs(s[0]/s[1]-r))
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("panels"); ap.add_argument("workdir")
    ap.add_argument("--user", required=True); ap.add_argument("--pages", required=True); ap.add_argument("--slug", default="manga-gen")
    a = ap.parse_args()
    name = load(a.name); pan = load(a.panels)
    pages = [int(x) for x in a.pages.split(",")]
    jobs = []
    for p in pages:
        rects = panel_rects(name.PAGES[p])
        for i, r in enumerate(rects, 1):
            spec = pan.PANELS.get((p, i))
            if not spec: continue
            w, h = best_size(r[2]-r[0], r[3]-r[1])
            j = {"name": f"p{p:02d}_{i}", "w": w, "h": h, "seeds": spec.get("seeds", [1, 2])}
            j.update({k: v for k, v in spec.items() if k != "seeds"}); jobs.append(j)
    refs = {}
    for k, path in pan.REFS.items():
        im = Image.open(os.path.join(HERE, "..", path)).convert("RGB"); im.thumbnail((512, 512))
        b = io.BytesIO(); im.save(b, "JPEG", quality=90); refs[k] = base64.b64encode(b.getvalue()).decode()
    src = open(os.path.join(HERE, "gen2_template.py")).read()
    src = src.replace("__JOBS__", json.dumps(jobs, ensure_ascii=False)).replace("__CFG__", json.dumps(pan.CFG, ensure_ascii=False)).replace("__REFS__", json.dumps(refs))
    os.makedirs(a.workdir, exist_ok=True); open(os.path.join(a.workdir, "gen.py"), "w").write(src)
    json.dump({"id": f"{a.user}/{a.slug}", "title": a.slug, "code_file": "gen.py", "language": "python", "kernel_type": "script",
               "is_private": True, "enable_gpu": True, "enable_internet": True, "machine_shape": "NvidiaTeslaT4",
               "dataset_sources": [f"{a.user}/manga-loras"], "competition_sources": [], "kernel_sources": []},
              open(os.path.join(a.workdir, "kernel-metadata.json"), "w"), indent=1)
    print(len(jobs), "panels,", sum(len(j["seeds"]) for j in jobs), "images")
    subprocess.run(["kaggle", "kernels", "push", "-p", a.workdir], check=True)
