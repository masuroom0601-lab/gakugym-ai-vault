#!/usr/bin/env python3
"""Kindle表紙 v3(2026-11-18)。1600x2560。
v2は競合の表紙(人のアイコン・BEFORE→AFTER・黒帯と吹き出し)に寄りすぎたため、独自の方向に変更:
方眼ノートの上に、赤ペンで「頑張る」を消した書き込み、偏差値46→66の手書きグラフ、付箋、マスキングテープ。
使い方: python3 cover_v3.py <出力.jpg>
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 2560
HERE = os.path.dirname(os.path.abspath(__file__))
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
HAND = os.path.join(HERE, "..", "..", "creative", "highlights", "assets", "fonts", "KleeOne-600.ttf")
INK, RED, GRID, PAPER = (28, 28, 32), (208, 32, 40), (196, 220, 236), (251, 250, 244)
NOTE, TAPE = (255, 226, 92), (120, 196, 190)
random.seed(7)
_fc = {}


def F(w, s):
    k = (w, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(HAND, s) if w == "hand" else ImageFont.truetype(SANS % w, s, index=0)
    return _fc[k]


def tw(d, t, f): return d.textlength(t, font=f)


def pen(d, pts, col, width, wob=4, steps=14):
    """手書き風の少し揺れた線"""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for i in range(steps):
            t = i / steps
            out.append((x0 + (x1 - x0) * t + random.uniform(-wob, wob) * 0.4,
                        y0 + (y1 - y0) * t + random.uniform(-wob, wob)))
    out.append(pts[-1])
    d.line(out, fill=col, width=width, joint="curve")
    r = width // 2
    for x, y in (out[0], out[-1]): d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def paste_rot(im, layer, x, y, ang, shadow=True):
    lr = layer.rotate(ang, expand=True, resample=Image.BICUBIC)
    if shadow:
        a = lr.split()[3].point(lambda v: v * 0.35)
        sh = Image.new("RGBA", lr.size, (0, 0, 0, 0)); sh.putalpha(a)
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        im.alpha_composite(sh, (x + 10, y + 16))
    im.alpha_composite(lr, (x, y))


def main(out):
    im = Image.new("RGBA", (W, H), PAPER + (255,)); d = ImageDraw.Draw(im)
    for x in range(0, W, 50): d.line((x, 0, x, H), fill=GRID, width=2)
    for y in range(0, H, 50): d.line((0, y, W, y), fill=GRID, width=2)
    d.line((150, 0, 150, H), fill=(236, 150, 150), width=4)   # ノートの余白線

    # マスキングテープ「受験生へ、」
    f = F("Black", 104); t = "受験生へ、"
    tp = Image.new("RGBA", (int(tw(d, t, f)) + 120, 170), (0, 0, 0, 0)); td = ImageDraw.Draw(tp)
    td.rectangle((0, 0, tp.width, tp.height), fill=TAPE + (215,))
    for x in range(0, tp.width, 22): td.line((x, 0, x, 8), fill=(0, 0, 0, 0), width=10); td.line((x, tp.height - 8, x, tp.height), fill=(0, 0, 0, 0), width=10)
    td.text((60, 18), t, font=f, fill="white")
    paste_rot(im, tp, 170, 120, 3, shadow=False)

    # 「頑張る」のを(赤ペンで消す)
    parts = [("「頑張る」", INK), ("のを", INK)]
    z = 270
    while sum(tw(d, a, F("Black", z)) for a, _ in parts) > W - 260: z -= 5
    ft = F("Black", z); x = 200; y = 360
    d.text((x, y), "「頑張る」のを", font=ft, fill=INK)
    gx0 = x + tw(d, "「", ft); gx1 = gx0 + tw(d, "頑張る", ft); my = y + z * 0.62
    pen(d, [(gx0 - 20, my - 18), (gx1 + 20, my - 34)], RED, 20, 6)
    pen(d, [(gx0 - 10, my + 26), (gx1 + 30, my + 8)], RED, 20, 6)
    # 赤ペンの書き込み(手書き)
    d.text((gx1 + 10, y - 70), "もう、いらない。", font=F("hand", 68), fill=RED)

    # やめましょう
    s = 320
    while tw(d, "やめましょう", F("Black", s)) > W - 260: s -= 6
    d.text((200, 700), "やめましょう", font=F("Black", s), fill=INK)

    # 手書きのグラフ(偏差値46→66)
    ox, oy, gw, gh = 300, 1700, 1050, 560
    pen(d, [(ox, oy - gh - 40), (ox, oy), (ox + gw + 40, oy)], INK, 9, 2)
    d.text((ox - 10, oy - gh - 120), "模試の偏差値", font=F("hand", 60), fill=INK)
    y46, y66 = oy - 120, oy - gh + 60
    for v, yy in ((46, y46), (66, y66)):
        d.text((ox - 30, yy), str(v), font=F("hand", 64), fill=INK, anchor="rm")
        for xx in range(ox, ox + gw, 40): d.line((xx, yy, xx + 18, yy), fill=(140, 140, 140), width=4)
    pts = [(ox + 60, y46), (ox + 230, y46 + 30), (ox + 400, y46 - 40), (ox + 580, y46 - 170),
           (ox + 760, y66 + 150), (ox + 950, y66)]
    pen(d, pts, RED, 16, 3, 10)
    for px, py in pts: d.ellipse((px - 18, py - 18, px + 18, py + 18), fill=RED)
    cx, cy = pts[-1]
    pen(d, [(cx + 70 * math.cos(a / 10), cy + 60 * math.sin(a / 10)) for a in range(0, 66, 3)], RED, 9, 2, 3)  # 丸で囲む
    d.text((cx - 95, cy - 10), "+20", font=F("hand", 110), fill=RED, anchor="rm")

    # 付箋
    nt = Image.new("RGBA", (980, 440), NOTE + (255,)); nd = ImageDraw.Draw(nt)
    nd.polygon([(980, 360), (980, 440), (900, 440)], fill=(232, 196, 60, 255))
    nd.text((490, 95), "やる気に頼らない", font=F("Black", 80), fill=INK, anchor="mm")
    nd.text((490, 240), "「仕組み化」", font=F("Black", 150), fill=RED, anchor="mm")
    nd.text((490, 370), "勉強法", font=F("Black", 96), fill=INK, anchor="mm")
    paste_rot(im, nt, 470, 1790, -4)

    d = ImageDraw.Draw(im)
    d.text((230, 2290), "学年最下位・テスト0点からの逆転合格", font=F("hand", 58), fill=INK)
    d.text((W - 110, 2445), "益田 大輝", font=F("Black", 90), fill=INK, anchor="rm")
    im = im.convert("RGB"); im.save(out, quality=95)
    im.resize((150, 240), Image.LANCZOS).save(out.replace(".jpg", "_small.png"))
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cover_v3.jpg")
