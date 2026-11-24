"""集合ゴマの合成。一人ずつ白背景で描いたキャラを切り抜き、背景の絵に重ねる。
AIは一枚の絵に何人も描くと、人数や顔が崩れやすい。キャラを別々に描いて重ねると、全員を正しく描ける。

使い方(Pythonから):
    from group_composite import compose_group
    compose_group("背景.png", [("キャラ.png", 横の中心0〜1, 足もと0〜1, 高さ0〜1, 左右反転), ...], "出力.png")
    キャラは手前に来るものほど後ろに並べる
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

_SESSION = None
def cutout(path, tol=30):
    """背景を透明にする。アニメ絵用の切り抜きモデル(rembg / isnet-anime)を使い、
    使えないときは、絵の縁の色に近い領域を背景とみなす方法に切り替える"""
    global _SESSION
    try:
        from rembg import remove, new_session
        if _SESSION is None: _SESSION = new_session("isnet-anime")
        im = remove(Image.open(path).convert("RGB"), session=_SESSION)
        m = np.array(im.getchannel("A")) > 128
        # 人物から離れた墨や集中線のかけらは捨てる(いちばん大きいかたまりと、それに近い大きさのものだけ残す)
        lab, n = ndimage.label(ndimage.binary_opening(m, iterations=2))
        if n > 1:
            sz = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
            m = np.isin(lab, [i + 1 for i, s in enumerate(sz) if s >= sz.max() * 0.15])
        a = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
        im.putalpha(a); box = a.getbbox()
        return im.crop(box) if box else im
    except ImportError:
        return cutout_key(path, tol)

def cutout_key(path, tol=30):
    """背景を透明にする。絵の縁の色(白・薄いグレーなど)に近く、縁からつながっている領域だけを背景とみなす
    (服の白い部分など、キャラの内側にある同じ色は残る)"""
    im = Image.open(path).convert("RGB"); a = np.array(im).astype(int)
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    ref = np.median(edge, axis=0)
    near = np.abs(a - ref).max(axis=2) <= tol
    lab, n = ndimage.label(near)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    bg = ndimage.binary_opening(bg, iterations=1)
    alpha = Image.fromarray(((~bg) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    im.putalpha(alpha)
    box = alpha.getbbox()
    return im.crop(box) if box else im

def compose_group(bg_path, items, out_path, aspect=None):
    """aspect: コマの横÷縦。指定すると、背景をその形に切り取ってから重ねる"""
    bg = Image.open(bg_path).convert("RGBA")
    if aspect:
        W, H = bg.size
        if W / H > aspect: nw = int(H * aspect); bg = bg.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
        else: nh = int(W / aspect); bg = bg.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    W, H = bg.size
    for path, cx, foot, hfrac, flip in items:
        c = cutout(path)
        if flip: c = c.transpose(Image.FLIP_LEFT_RIGHT)
        h = int(H * hfrac); w = int(c.width * h / c.height)
        c = c.resize((w, h), Image.LANCZOS)
        bg.alpha_composite(c, (int(W * cx - w / 2), int(H * foot - h)))
    bg.convert("RGB").save(out_path)
    return out_path

def add_net(path, out_path, top=0.0, bottom=0.8, cols=11, rows=7, seed=0):
    """集合ゴマの上から、天井から落ちてきたネバネバの網を線で描き足す(AIは網をうまく描けないため)。
    白い糸に黒いふちを付け、ところどころから糸を垂らす"""
    import random
    from PIL import ImageDraw
    rnd = random.Random(seed)
    im = Image.open(path).convert("RGB"); W, H = im.size; d = ImageDraw.Draw(im)
    lw = max(3, W // 220)
    pts = []
    for r in range(rows):
        row = []
        for c in range(cols):
            u = c / (cols - 1); v = r / (rows - 1)
            sag = 0.12 * H * (1 - (2 * u - 1) ** 2) * v  # 真ん中ほど重みで垂れ下がる
            row.append((W * (-0.03 + 1.06 * u) + rnd.uniform(-1, 1) * W / cols * 0.25,
                        H * (top + (bottom - top) * v) + sag + rnd.uniform(-1, 1) * H / rows * 0.2))
        pts.append(row)
    segs = []
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols: segs.append((pts[r][c], pts[r][c + 1]))
            if r + 1 < rows: segs.append((pts[r][c], pts[r + 1][c]))
    def curve(a, b):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + abs(b[0] - a[0]) * 0.12
        return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mx + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * my + t * t * b[1]) for t in [i / 12 for i in range(13)]]
    for w, col in ((lw * 2 + 2, "black"), (lw, "white")):
        for a, b in segs: d.line(curve(a, b), fill=col, width=w, joint="curve")
    for _ in range(cols * 2):  # 垂れる糸としずく
        r, c = rnd.randrange(1, rows), rnd.randrange(cols); x0, y0 = pts[r][c]; L = rnd.uniform(0.04, 0.1) * H
        d.line([(x0, y0), (x0 + rnd.uniform(-4, 4), y0 + L)], fill="black", width=lw + 4)
        d.line([(x0, y0), (x0, y0 + L)], fill="white", width=lw)
        rr = lw * 1.6; d.ellipse((x0 - rr, y0 + L - rr, x0 + rr, y0 + L + rr * 1.4), fill="white", outline="black", width=2)
    im.save(out_path); return out_path
