"""ネームのデータとコマごとのプロンプトから、コマ画像の生成ジョブを組み立ててKaggleに送る。

使い方: python3 build_panels.py names/ep01_name.py names/ep01_panels.py 作業フォルダ --user ユーザー名 --pages 17,18,19 [--slug manga-gen]
- コマの縦横比はネームの枠の大きさから自動で決め、SDXLの解像度の中から一番近いものを使う
"""
import argparse, base64, importlib.util, io, json, os, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, os.path.join(HERE, ".."))
import layout
SIZES = [(1024,1024),(1152,896),(896,1152),(1216,832),(832,1216),(1344,768),(768,1344),(1536,640),(640,1536)]
W, H, M, G = 1000, 1414, 60, 14
def sync_refs(REFS, user):
    """見本の絵を、非公開データセット user/manga-refs にアップロードする(中身が変わったときだけ)。
    Kaggleでは、プログラムのファイルが大きい(約900KB以上)と順番待ちのまま動かないため、絵はプログラムに埋め込まない"""
    import hashlib, shutil, time
    d = os.path.join(HERE, "..", "..", ".kaggle_refs"); os.makedirs(d, exist_ok=True)
    h = hashlib.md5()
    for k, path in sorted(REFS.items()):
        im = Image.open(os.path.join(HERE, "..", "..", path)).convert("RGB"); im.thumbnail((512, 512))
        out = os.path.join(d, f"ref_{k}.jpg"); im.save(out, "JPEG", quality=90); h.update(open(out, "rb").read())
    stamp = os.path.join(d, ".hash"); new = h.hexdigest()
    if os.path.exists(stamp) and open(stamp).read() == new: return REFS
    meta = {"title": "manga-refs", "id": f"{user}/manga-refs", "licenses": [{"name": "other"}]}
    json.dump(meta, open(os.path.join(d, "dataset-metadata.json"), "w"))
    exists = subprocess.run(["kaggle", "datasets", "status", f"{user}/manga-refs"], capture_output=True, text=True).returncode == 0 and \
        "ready" in subprocess.run(["kaggle", "datasets", "status", f"{user}/manga-refs"], capture_output=True, text=True).stdout.lower()
    cmd = ["kaggle", "datasets", "version", "-p", d, "-m", "見本の絵を更新"] if exists else ["kaggle", "datasets", "create", "-p", d]
    r = subprocess.run(cmd, capture_output=True, text=True); print("見本のアップロード:", "成功" if r.returncode == 0 else "失敗 " + r.stdout[-300:] + r.stderr[-300:])
    for _ in range(30):  # データセットの準備ができるまで待つ
        st = subprocess.run(["kaggle", "datasets", "status", f"{user}/manga-refs"], capture_output=True, text=True).stdout.lower()
        if "ready" in st: break
        time.sleep(10)
    open(stamp, "w").write(new)
    return REFS

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
    ap.add_argument("--user", required=True); ap.add_argument("--pages", required=True); ap.add_argument("--slug", default="manga-art")
    a = ap.parse_args()
    name = load(a.name); pan = load(a.panels)
    pages = [int(x) for x in a.pages.split(",")]
    jobs = []
    for p in pages:
        rects = [q["bbox"] for q in layout.page_panels(name, p)]  # 斜めのコマ・重ねゴマも、外接する長方形の大きさで描く
        for i, r in enumerate(rects, 1):
            spec = pan.PANELS.get((p, i))
            if not spec: continue
            w, h = best_size(r[2]-r[0], r[3]-r[1])
            j = {"name": f"p{p:02d}_{i}", "w": w, "h": h, "seeds": spec.get("seeds", [1, 2])}
            j.update({k: v for k, v in spec.items() if k != "seeds"}); jobs.append(j)
    # コマ以外の部品(合成用のキャラ・背景など)。EXTRA = {"名前": {"w":..,"h":.., "prompt":..}}
    for nm, spec in getattr(pan, "EXTRA", {}).items():
        j = {"name": nm, "w": spec.get("w", 832), "h": spec.get("h", 1216), "seeds": spec.get("seeds", [1, 2])}
        j.update({k: v for k, v in spec.items() if k not in ("seeds", "w", "h")}); jobs.append(j)
    refs = sync_refs(pan.REFS, a.user)
    src = open(os.path.join(HERE, "gen2_template.py")).read()
    src = src.replace("__JOBS__", json.dumps(jobs, ensure_ascii=False)).replace("__CFG__", json.dumps(pan.CFG, ensure_ascii=False)).replace("__REFS__", json.dumps(sorted(refs)))
    os.makedirs(a.workdir, exist_ok=True); open(os.path.join(a.workdir, "gen.py"), "w").write(src)
    json.dump({"id": f"{a.user}/{a.slug}", "title": a.slug, "code_file": "gen.py", "language": "python", "kernel_type": "script",
               "is_private": True, "enable_gpu": True, "enable_internet": True, "machine_shape": "NvidiaTeslaT4",
               "dataset_sources": [f"{a.user}/manga-loras", f"{a.user}/manga-refs"], "competition_sources": [], "kernel_sources": []},
              open(os.path.join(a.workdir, "kernel-metadata.json"), "w"), indent=1)
    print(len(jobs), "panels,", sum(len(j["seeds"]) for j in jobs), "images")
    subprocess.run(["kaggle", "kernels", "push", "-p", a.workdir], check=True)
