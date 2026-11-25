"""AIの絵に出る「墨の飛び散り」を、人物の外側だけ自動で消す(2026-11-25)。

考え方
- 人物は切り抜きモデル(isnet-anime)で見つけ、少し広げた範囲には手を出さない(髪・服の黒は残す)
- 人物の外側で、細い線(背景の線・トーン)ではない「塗りつぶされた黒いかたまり」を探す。
  かたまりの大きさが絵の 0.01%〜2% のものを飛び散りとみなす(夜空のような大きな黒は残す)
- 小さな丸い黒点(しずく)も、まわりに線がなく孤立していれば消す
- 消した跡は、まわりの模様で埋める(cv2.inpaint)
結果はファイルの中身ごとにキャッシュする(~/.cache/manga_deink)

使い方: python3 deink.py 入力.png 出力.png   (単体で試す)
        page_compose.py からは clean(PIL画像, 元のパス) を呼ぶ
"""
import hashlib, os, sys
import numpy as np
import cv2
from PIL import Image

CACHE = os.path.expanduser("~/.cache/manga_deink")
_RB = None

def _char_mask(rgb):
    global _RB
    try:
        from rembg import remove, new_session
    except ImportError:
        z = np.zeros(rgb.shape[:2], bool); return [z, z]
    if _RB is None: _RB = (new_session("isnet-anime"), new_session("isnet-general-use"))
    im = Image.fromarray(rgb)
    # 人物は anime、セーター・鍋さん・ハニワ君・スマホなどの物は general で見つけ、どちらかに入れば残す
    return [np.array(remove(im, session=s, only_mask=True)) > 100 for s in _RB]

def _light_around(g, comp, x, y, bw, bh, k):
    """かたまりのまわり(少し外側の輪)が、白っぽい無地かどうか。白地に落ちた墨だけを消すため"""
    h, w = g.shape; pad = k * 3
    x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(w, x + bw + pad), min(h, y + bh + pad)
    sub = comp[y0:y1, x0:x1].astype(np.uint8)
    ring = (cv2.dilate(sub, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (pad * 2 + 1, pad * 2 + 1))) > 0) & (sub == 0)
    v = g[y0:y1, x0:x1][ring]
    if v.size == 0: return False
    return np.median(v) > 175 and (v > 120).mean() > 0.7

def clean_array(rgb, char=None):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    h, w = g.shape; N = h * w
    if char is None: char = _char_mask(rgb)
    k = max(3, int(min(h, w) / 90))
    big = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k * 3, k * 3))
    keep = cv2.dilate(char[0].astype(np.uint8), big) > 0                    # 人物(anime)
    obj = cv2.dilate((char[0] | char[1]).astype(np.uint8), big) > 0         # 人物+物(general)
    dark = (g < 70).astype(np.uint8)
    # 1) 塗りつぶされた黒いかたまり(細い線はオープニングで消える)
    op = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(op, 8)
    rm = np.zeros_like(dark)
    for i in range(1, n):
        x, y, bw, bh, a = st[i]
        if not (N * 0.0001 <= a <= N * 0.02): continue
        comp = lab == i
        if (comp & keep).sum() > a * 0.02: continue  # 人物・物に少しでもかかるものは残す
        if bw > w * 0.6 or bh > h * 0.6: continue    # 画面をまたぐ大きな影は残す
        if not _light_around(g, comp, x, y, bw, bh, k): continue  # 模様のある背景の中の黒は残す
        cnt, _ = cv2.findContours(comp[y:y + bh, x:x + bw].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hull = cv2.contourArea(cv2.convexHull(max(cnt, key=cv2.contourArea)))
        if hull > 0 and a / hull > 0.85: continue  # 丸い・四角いまとまった黒(目・レンズ・画面)は物として残す
        rm |= comp.astype(np.uint8)
    # かたまりから飛び出した、元の黒い部分(しぶきの筋)もいっしょに消す
    grow = cv2.dilate(rm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k * 2 + 1, k * 2 + 1)))
    rm = ((grow > 0) & (dark > 0) & ~keep).astype(np.uint8) | rm if rm.any() else rm
    # 2) 孤立した小さな丸い黒点(しずく)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(dark, 8)
    near = cv2.dilate(dark, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k * 3, k * 3)))
    for i in range(1, n2):
        x, y, bw, bh, a = st2[i]
        if a < 12 or a > (k * 4) ** 2: continue
        if a / float(bw * bh) < 0.45 or max(bw, bh) > 3 * min(bw, bh): continue
        x0, y0, x1, y1 = max(0, x - k * 2), max(0, y - k * 2), min(w, x + bw + k * 2), min(h, y + bh + k * 2)
        win = dark[y0:y1, x0:x1].sum()
        if win > a * 1.3: continue                  # まわりに線がある(模様の一部)
        if obj[y:y + bh, x:x + bw].any(): continue  # ハニワ君の目など、物の中の点は残す
        rm[lab2 == i] = 1
    if not rm.any(): return rgb, 0.0
    m = cv2.dilate(rm, np.ones((3, 3), np.uint8))
    out = cv2.inpaint(rgb, m * 255, 5, cv2.INPAINT_TELEA)
    bright = cv2.dilate(m, np.ones((k, k), np.uint8)) > 0
    bg = np.percentile(g[~keep], 90) if (~keep).any() else 255  # 背景の地の明るさで埋める
    out[bright & (cv2.cvtColor(out, cv2.COLOR_RGB2GRAY) > 150)] = int(bg)
    return out, float(m.sum()) / N

def clean(im, path=None):
    """PIL画像を受け取り、飛び散りを消したPIL画像(RGB)を返す。pathがあれば中身でキャッシュする"""
    key = None
    if path and os.path.exists(path):
        key = hashlib.md5(open(path, "rb").read()).hexdigest()
        cp = os.path.join(CACHE, key + ".png")
        if os.path.exists(cp): return Image.open(cp).convert("RGB")
    out, _ = clean_array(np.array(im.convert("RGB")))
    res = Image.fromarray(out)
    if key:
        os.makedirs(CACHE, exist_ok=True); res.save(cp)
    return res

if __name__ == "__main__":
    im = Image.open(sys.argv[1]).convert("RGB")
    out, frac = clean_array(np.array(im))
    Image.fromarray(out).save(sys.argv[2]); print(f"消した面積: {frac * 100:.2f}%")
