#!/usr/bin/env python3
"""Kindle表紙・帯つき、背景に図柄のある候補 P1〜P5(2026-11-18)。1600x2560。
O3(背景に右肩上がりの矢印)が好評だったため、ベタ塗りではなく背景に図柄を入れる方向で5案。
配色は data-visual-design スキル(デジタル庁デザインシステム)の考え方に合わせる:
  キーカラーを1系統+差し色の黄色(Secondary)+黒/グレー。文字は背景に対して 4.5:1 以上。
  グラフは誤解を生まない形にする(実際に分かっている2点 46 と 66 だけを打ち、軸に目盛りの値を書く。棒は原点0)。
使い方: python3 cover_bg.py <出力フォルダ>
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 2560
OBI = 1690
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
INK, WHITE = (26, 26, 26), (255, 255, 255)
YEL = (255, 199, 0)              # Secondary Yellow #FFC700
AUTHOR = "益田 大輝"
_fc = {}


def hx(s): return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def F(w, s):
    if (w, s) not in _fc: _fc[(w, s)] = ImageFont.truetype(SANS % w, s, index=0)
    return _fc[(w, s)]


def tw(d, t, f): return d.textlength(t, font=f)


def fitF(d, t, w, maxw, start):
    s = start
    while tw(d, t, F(w, s)) > maxw: s -= 4
    return F(w, s)


def rich(d, x, y, parts, f, center=False):
    if center: x -= sum(tw(d, t, f) for t, _ in parts) / 2
    for t, c in parts:
        d.text((x, y), t, font=f, fill=c); x += tw(d, t, f)


def title(d, accent, ink=INK):
    """O3と同じ左ぞろえの4段タイトル+著者名"""
    d.text((110, 150), "受験生へ、", font=F("Black", 160), fill=ink)
    d.text((110, 370), "「頑張る」", font=F("Black", 300), fill=accent)
    d.text((110, 730), "のを", font=F("Black", 260), fill=ink)
    d.text((W / 2, 1220), "やめましょう", font=fitF(d, "やめましょう", "Black", W - 140, 330), fill=ink, anchor="mm")
    d.text((W - 110, 1530), AUTHOR, font=F("Bold", 90), fill=ink, anchor="rm")


def obi(im, color):
    sh = Image.new("L", (W, 36), 0); sd = ImageDraw.Draw(sh)
    for i in range(36): sd.line((0, i, W, i), fill=int(90 * (i / 36) ** 2))
    im.paste(Image.new("RGB", (W, 36), (0, 0, 0)), (0, OBI - 36), sh)
    d = ImageDraw.Draw(im); d.rectangle((0, OBI, W, H), fill=color)
    return d


def obi_text(d, bg_dark=True, hi=YEL, chips_bg=WHITE, chips_fg=INK):
    fg = WHITE if bg_dark else INK
    # 2026-11-18: サブタイトルを「やる気に頼らない学習「自動化」術」に変更
    # 2026-11-20: サブタイトルを「モチベの波に左右されない学習“自動化”術」に変更
    rich(d, W / 2, OBI + 60, [("モチベの波に左右されない学習", fg), ("“自動化”", hi), ("術", fg)],
         fitF(d, "モチベの波に左右されない学習“自動化”術", "Black", W - 160, 100), center=True)
    d.line((120, OBI + 200, W - 120, OBI + 200), fill=fg, width=3)
    d.text((110, OBI + 240), "学年最下位・定期テスト0点から", font=F("Black", 74), fill=fg)
    rich(d, 100, OBI + 330, [("偏差値", fg), ("46→66", hi)], F("Black", 200))
    items = ["スマホ依存を克服", "三日坊主にならない", "計画が崩れない"]
    z = 56
    while sum(tw(d, t, F("Black", z)) + 60 for t in items) > W - 260: z -= 2
    f = F("Black", z); ws = [tw(d, t, f) + 60 for t in items]
    gap = (W - 200 - sum(ws)) / 2; x = 100; y = OBI + 640
    for t, w in zip(items, ws):
        d.rounded_rectangle((x, y, x + w, y + 100), 50, fill=chips_bg)
        d.text((x + w / 2, y + 50), t, font=f, fill=chips_fg, anchor="mm"); x += w + gap


# ---- P1: Red系。背景に「偏差値46→66」の折れ線グラフ(実データの2点だけ) ----
def p1():
    BG, LINE, AX = hx("#FDEEEE"), hx("#FFBBBB"), hx("#FF7171")
    im = Image.new("RGB", (W, H), hx("#FFFAF8")); d = ImageDraw.Draw(im)
    x0, x1 = 140, 1460
    def Y(v): return 1600 - (v - 40) / 26 * 1300      # 縦軸 40〜70(目盛りの値を書く)
    for v in (40, 50, 60, 70):
        d.line((x0, Y(v), x1, Y(v)), fill=BG, width=4)
        d.text((x1 + 10, Y(v)), str(v), font=F("Bold", 44), fill=LINE, anchor="lm")
    a, b = (230, Y(46)), (1330, Y(66))
    d.line((a, b), fill=LINE, width=60)
    for p in (a, b): d.ellipse((p[0] - 55, p[1] - 55, p[0] + 55, p[1] + 55), fill=AX)
    d.text((a[0] - 60, a[1] + 120), "46", font=F("Black", 90), fill=AX)
    d.text((b[0] - 80, b[1] - 40), "66", font=F("Black", 90), fill=AX, anchor="rm")
    d.text((x1 + 10, Y(70) - 60), "偏差値", font=F("Bold", 40), fill=LINE, anchor="rm")
    title(d, hx("#CE0000"))
    obi_text(obi(im, hx("#1A1A1A")))
    return im


# ---- P2: Blue系。背景に少しずつ高くなる棒(スモールステップの階段。原点0) ----
def p2():
    im = Image.new("RGB", (W, H), hx("#F8F8FB")); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line((x, 0, x, OBI), fill=hx("#E8F1FE"), width=2)
    for y in range(0, OBI, 60): d.line((0, y, W, y), fill=hx("#E8F1FE"), width=2)
    cols = ["#E8F1FE", "#D9E6FF", "#C5D7FB", "#C5D7FB", "#7096F8", "#7096F8"]
    n = 6; bw = 200; gap = (W - 120 - n * bw) / (n - 1); base = OBI
    for i in range(n):
        x = 60 + i * (bw + gap); h = 260 + i * 230
        d.rectangle((x, base - h, x + bw, base), fill=hx(cols[i]))
    title(d, hx("#0017C1"), hx("#000060"))
    obi_text(obi(im, hx("#0017C1")))
    return im


# ---- P3: Green系。背景に大小の歯車(仕組み) ----
def gear(d, cx, cy, r, col, teeth=12):
    pts = []
    for i in range(teeth * 2):
        a = i * math.pi / teeth; rr = r if i % 2 == 0 else r * 0.8
        for da in (-0.12, 0.12): pts.append((cx + rr * math.cos(a + da), cy + rr * math.sin(a + da)))
    d.polygon(pts, fill=col)
    d.ellipse((cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35), fill=hx("#F6FBF8"))


def p3():
    im = Image.new("RGB", (W, H), hx("#F6FBF8")); d = ImageDraw.Draw(im)
    for cx, cy, r, c in ((1250, 520, 420, "#E6F5EC"), (720, 1180, 300, "#E6F5EC"), (1380, 1300, 220, "#CDEBD9"),
                         (250, 330, 200, "#CDEBD9"), (300, 1500, 160, "#E6F5EC")):
        gear(d, cx, cy, r, hx(c))
    title(d, hx("#115A36"))
    obi_text(obi(im, hx("#032213")))
    return im


# ---- P4: Orange系。タイトルの奥から広がる集中線 ----
def p4(art=None):
    im = Image.new("RGB", (W, H), hx("#FFF8F2")); d = ImageDraw.Draw(im)
    cx, cy = W / 2, 760; random.seed(3)
    for k in range(90):
        a = 2 * math.pi * k / 90 + random.uniform(-0.01, 0.01); w = random.uniform(0.008, 0.02)
        r0, r1 = 520, 2600
        d.polygon([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)),
                   (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))], fill=hx("#FFE0CC"))
    if art: art(d)   # 背景の絵(cover_art.py)
    title(d, hx("#AC3E00"))
    # 「のを」の右に「偏差値20UP!」のバッジ(サブタイトルの言葉に合わせる)
    bx, by, r = 1250, 900, 160
    pts = [(bx + (r if i % 2 == 0 else r * 0.86) * math.cos(math.pi * i / 22),
            by + (r if i % 2 == 0 else r * 0.86) * math.sin(math.pi * i / 22)) for i in range(44)]
    d.polygon(pts, fill=hx("#FB5B01"))
    d.text((bx, by - 62), "偏差値", font=F("Black", 54), fill=WHITE, anchor="mm")
    d.text((bx, by + 18), "20", font=F("Black", 112), fill=YEL, anchor="mm")
    d.text((bx, by + 98), "UP!", font=F("Black", 54), fill=WHITE, anchor="mm")
    obi_text(obi(im, hx("#541E00")), hi=YEL)
    return im


# ---- P5: Light Blue系。背景に学習ログのカレンダー(毎日のチェック) ----
def p5():
    im = Image.new("RGB", (W, H), hx("#F0F9FF")); d = ImageDraw.Draw(im)
    cell = 200; x0 = 100; y0 = 130
    for r in range(7):
        for c in range(7):
            x, y = x0 + c * cell, y0 + r * cell
            if y + cell > OBI + 40: continue
            d.rounded_rectangle((x + 10, y + 10, x + cell - 10, y + cell - 10), 22, outline=hx("#C0E4FF"), width=5)
            if r * 7 + c < 38:   # 毎日の「できた」の印が続いていく
                d.line((x + 55, y + 105, x + 90, y + 140, x + 150, y + 65), fill=hx("#C0E4FF"), width=14, joint="curve")
    title(d, hx("#0055AD"), hx("#00234B"))
    obi_text(obi(im, hx("#00234B")))
    return im


def main(out):
    os.makedirs(out, exist_ok=True); ims = {}
    for k, fn in (("P1", p1), ("P2", p2), ("P3", p3), ("P4", p4), ("P5", p5)):
        im = fn(); im.save(os.path.join(out, f"bg_{k}.jpg"), quality=95); ims[k] = im
    tw_, th = 400, 640
    sheet = Image.new("RGB", (len(ims) * (tw_ + 30) + 30, th + 320), (238, 238, 238)); sd = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(ims.items()):
        x = 30 + i * (tw_ + 30)
        sheet.paste(im.resize((tw_, th), Image.LANCZOS), (x, 30))
        sd.text((x + tw_ / 2, th + 70), f"案{k}", font=F("Black", 50), fill=INK, anchor="mm")
        sheet.paste(im.resize((100, 160), Image.LANCZOS), (int(x + tw_ / 2 - 50), th + 120))
    sheet.save(os.path.join(out, "bg_lineup.jpg"), quality=92)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
