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

def cutout(path, tol=30):
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

def compose_group(bg_path, items, out_path):
    bg = Image.open(bg_path).convert("RGBA"); W, H = bg.size
    for path, cx, foot, hfrac, flip in items:
        c = cutout(path)
        if flip: c = c.transpose(Image.FLIP_LEFT_RIGHT)
        h = int(H * hfrac); w = int(c.width * h / c.height)
        c = c.resize((w, h), Image.LANCZOS)
        bg.alpha_composite(c, (int(W * cx - w / 2), int(H * foot - h)))
    bg.convert("RGB").save(out_path)
    return out_path
