#!/usr/bin/env python3
"""Kindle表紙の候補 A〜D(2026-11-18)。1600x2560。
売れている勉強法・教育書の表紙に多い作り(白地に大きなタイトル+帯の実績、黄色の全面、紺×金の上質感、縦書きの和風)を
それぞれ1案ずつ。特定の本の構図・イラストはまねしない。
使い方: python3 cover_cands.py <出力フォルダ>
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 2560
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-%s.ttc"
INK, RED, BLUE, YEL, NAVY, GOLD = (24, 24, 28), (214, 40, 40), (22, 88, 170), (255, 212, 0), (18, 30, 58), (201, 168, 92)
SUB = ("やる気に頼らない", "「仕組み化」勉強法")
AUTHOR = "益田 大輝"
_fc = {}


def F(w, s, serif=False):
    k = (w, s, serif)
    if k not in _fc: _fc[k] = ImageFont.truetype((SERIF if serif else SANS) % w, s, index=0)
    return _fc[k]


def tw(d, t, f): return d.textlength(t, font=f)


def fit(d, t, w, maxw, start, serif=False):
    s = start
    while tw(d, t, F(w, s, serif)) > maxw: s -= 4
    return F(w, s, serif)


def rich(d, x, y, parts, f, anchor="l"):
    total = sum(tw(d, t, f) for t, _ in parts)
    if anchor == "c": x -= total / 2
    for t, c in parts:
        d.text((x, y), t, font=f, fill=c); x += tw(d, t, f)


def burst(d, cx, cy, r, col, n=24):
    import math
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        rr = r if i % 2 == 0 else r * 0.86
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)


# ---- A: 白地×青の大きなタイトル+青い帯(実績と悩み) ----
def cand_A():
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    f = F("Bold", 70)
    d.text((W / 2, 150), "やる気に頼らない「仕組み化」勉強法", font=f, fill=INK, anchor="mm")
    d.line((140, 215, W - 140, 215), fill=INK, width=4)
    d.text((W / 2, 360), "受験生へ、", font=F("Black", 150), fill=BLUE, anchor="mm")
    parts = [("「", BLUE), ("頑張る", RED), ("」のを", BLUE)]
    z = 300
    while sum(tw(d, a, F("Black", z)) for a, _ in parts) > W - 120: z -= 5
    rich(d, W / 2, 470, parts, F("Black", z), "c")
    d.text((W / 2, 1010), "やめましょう", font=fit(d, "やめましょう", "Black", W - 120, 330), fill=BLUE, anchor="mm")
    d.text((140, 1320), AUTHOR, font=F("Bold", 84), fill=INK, anchor="lm")
    # 帯
    top = 1450
    d.rectangle((0, top, W, H), fill=BLUE)
    d.text((110, top + 120), "学年最下位・定期テスト0点から", font=F("Bold", 78), fill="white")
    rich(d, 110, top + 250, [("偏差値 ", "white"), ("46→66", YEL)], F("Black", 170))
    d.text((110, top + 520), "こんな悩みに効く!", font=F("Bold", 64), fill="white")
    chips = ["やる気が出ない", "スマホに負ける", "三日坊主", "計画倒れ"]
    x, y = 110, top + 630
    for c in chips:
        fw = tw(d, c, F("Black", 64)) + 80
        if x + fw > W - 100: x, y = 110, y + 130
        d.rounded_rectangle((x, y, x + fw, y + 104), 52, fill="white")
        d.text((x + fw / 2, y + 52), c, font=F("Black", 64), fill=BLUE, anchor="mm"); x += fw + 30
    by = top - 110
    burst(d, 1340, by, 200, YEL)
    d.text((1340, by - 85), "心理学で", font=F("Black", 54), fill=INK, anchor="mm")
    d.text((1340, by + 5), "続く", font=F("Black", 120), fill=RED, anchor="mm")
    d.text((1340, by + 100), "仕組みを作る", font=F("Black", 50), fill=INK, anchor="mm")
    return im


# ---- B: 黄色の全面×黒の極太 ----
def cand_B():
    im = Image.new("RGB", (W, H), YEL); d = ImageDraw.Draw(im)
    d.text((120, 150), "受験生へ、", font=F("Black", 160), fill=INK)
    fz = F("Black", 300)
    x, y = 120, 400
    d.text((x, y), "「", font=fz, fill=INK); x += tw(d, "「", fz)
    w = tw(d, "頑張る", fz)
    d.rectangle((x - 10, y + 40, x + w + 10, y + 380), fill=INK)
    d.text((x, y), "頑張る", font=fz, fill=YEL); x += w
    d.text((x, y), "」", font=fz, fill=INK)
    d.text((120, 760), "のを", font=F("Black", 260), fill=INK)
    d.text((120, 1060), "やめましょう", font=fit(d, "やめましょう", "Black", W - 200, 330), fill=INK)
    # 46→66
    d.text((120, 1520), "模試の偏差値", font=F("Bold", 76), fill=INK)
    rich(d, 110, 1600, [("46", INK), ("→", RED), ("66", RED)], F("Black", 330))
    burst(d, 1330, 290, 165, RED)
    d.text((1330, 250), "偏差値", font=F("Black", 52), fill="white", anchor="mm")
    d.text((1330, 330), "+20", font=F("Black", 110), fill="white", anchor="mm")
    top = 2060
    d.rectangle((0, top, W, H), fill=INK)
    rich(d, W / 2, top + 70, [("やる気に頼らない", "white"), ("「仕組み化」", YEL), ("勉強法", "white")], fit(d, "やる気に頼らない「仕組み化」勉強法", "Black", W - 160, 100), "c")
    d.text((W / 2, top + 330), AUTHOR, font=F("Bold", 90), fill="white", anchor="mm")
    return im


# ---- C: 紺×白×金(明朝)。保護者にも手に取られやすい落ち着いた作り ----
def cand_C():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.rectangle((60, 60, W - 60, H - 60), outline=GOLD, width=4)
    d.rectangle((80, 80, W - 80, H - 80), outline=GOLD, width=1)
    d.text((W / 2, 260), "やる気に頼らない「仕組み化」勉強法", font=F("Bold", 70, True), fill=GOLD, anchor="mm")
    d.line((W / 2 - 300, 340, W / 2 + 300, 340), fill=GOLD, width=3)
    d.text((W / 2, 520), "受験生へ、", font=F("Black", 160, True), fill="white", anchor="mm")
    parts = [("「", "white"), ("頑張る", GOLD), ("」のを", "white")]
    z = 290
    while sum(tw(d, a, F("Black", z, True)) for a, _ in parts) > W - 240: z -= 5
    rich(d, W / 2, 640, parts, F("Black", z, True), "c")
    d.text((W / 2, 1150), "やめましょう", font=fit(d, "やめましょう", "Black", W - 240, 320, True), fill="white", anchor="mm")
    d.line((200, 1420, W - 200, 1420), fill=GOLD, width=2)
    d.text((W / 2, 1530), "模試の偏差値", font=F("Medium", 70, True), fill=GOLD, anchor="mm")
    d.text((W / 2, 1760), "46 → 66", font=F("Bold", 260, True), fill="white", anchor="mm")
    d.text((W / 2, 1990), "学年最下位・定期テスト0点からの逆転合格", font=F("Medium", 64, True), fill="white", anchor="mm")
    d.line((200, 2100, W - 200, 2100), fill=GOLD, width=2)
    d.text((W / 2, 2280), AUTHOR, font=F("Bold", 100, True), fill="white", anchor="mm")
    return im


# ---- D: 縦書きの大タイトル×赤い判子 ----
def vt(d, x, y, t, f, fill):
    d.text((x, y), t, font=f, fill=fill, direction="ttb", features=["vert"], anchor="mt")


def cand_D():
    BG = (250, 247, 240)
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    vt(d, 1390, 170, "受験生へ、", F("Black", 170), INK)
    vt(d, 1060, 150, "「頑張る」", F("Black", 300), RED)
    vt(d, 1060, 150 + 300 * 5 + 10, "のを", F("Black", 220), INK)
    vt(d, 640, 150, "やめましょう", F("Black", 330), INK)
    # 副題(縦)
    vt(d, 300, 170, "やる気に頼らない", F("Bold", 92), INK)
    vt(d, 170, 330, "「仕組み化」勉強法", F("Black", 92), RED)
    # 判子
    cx, cy, r = 260, 1700, 170
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=RED, width=16)
    d.text((cx, cy - 75), "偏差値", font=F("Black", 62), fill=RED, anchor="mm")
    d.text((cx, cy + 30), "+20", font=F("Black", 120), fill=RED, anchor="mm")
    d.line((120, 2210, W - 120, 2210), fill=INK, width=4)
    d.text((120, 2260), "学年最下位・テスト0点 → 偏差値46→66", font=F("Bold", 64), fill=INK)
    d.text((W - 120, 2440), AUTHOR, font=F("Black", 96), fill=INK, anchor="rm")
    return im


def main(out):
    os.makedirs(out, exist_ok=True)
    ims = {}
    for k, fn in (("A", cand_A), ("B", cand_B), ("C", cand_C), ("D", cand_D)):
        im = fn(); im.save(os.path.join(out, f"cand_{k}.jpg"), quality=95); ims[k] = im
    v3 = os.path.join(out, "cover_v3.jpg")
    if os.path.exists(v3): ims["E"] = Image.open(v3).convert("RGB")
    # 一覧(大きめ)と、Amazonの検索結果くらいの大きさ
    tw_, th = 420, 672
    sheet = Image.new("RGB", (len(ims) * (tw_ + 30) + 30, th + 330), (238, 238, 238)); sd = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(ims.items()):
        x = 30 + i * (tw_ + 30)
        sheet.paste(im.resize((tw_, th), Image.LANCZOS), (x, 30))
        sd.text((x + tw_ / 2, th + 70), f"案{k}", font=F("Black", 50), fill=INK, anchor="mm")
        sm = im.resize((100, 160), Image.LANCZOS); sheet.paste(sm, (int(x + tw_ / 2 - 50), th + 120))
    sheet.save(os.path.join(out, "cands_lineup.jpg"), quality=92)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
