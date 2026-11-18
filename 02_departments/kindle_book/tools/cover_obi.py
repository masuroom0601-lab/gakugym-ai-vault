#!/usr/bin/env python3
"""Kindle表紙・帯つきの候補 O1〜O4(2026-11-18)。1600x2560。
帯は表紙の下およそ1/3。紙が1枚重なって見えるよう、帯の上端に影をつける。
使い方: python3 cover_obi.py <出力フォルダ>
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1600, 2560
OBI = 1690   # 帯の上端
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
INK, RED, YEL, NAVY, CREAM = (22, 22, 26), (212, 36, 42), (255, 214, 0), (17, 32, 66), (250, 246, 236)
AUTHOR = "益田 大輝"
_fc = {}


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


def rich_fit(d, parts, w, maxw, start):
    s = start
    while sum(tw(d, t, F(w, s)) for t, _ in parts) > maxw: s -= 4
    return F(w, s)


def obi(im, color):
    """帯(上端に影)を貼って、帯に描くための Draw を返す"""
    sh = Image.new("L", (W, 36), 0); sd = ImageDraw.Draw(sh)
    for i in range(36): sd.line((0, i, W, i), fill=int(90 * (i / 36) ** 2))
    im.paste(Image.new("RGB", (W, 36), (0, 0, 0)), (0, OBI - 36), sh)
    d = ImageDraw.Draw(im)
    d.rectangle((0, OBI, W, H), fill=color)
    d.line((0, OBI, W, OBI), fill=tuple(max(0, c - 40) for c in color), width=3)
    return d


def burst(d, cx, cy, r, col, n=22):
    pts = [(cx + (r if i % 2 == 0 else r * 0.85) * math.cos(math.pi * i / n),
            cy + (r if i % 2 == 0 else r * 0.85) * math.sin(math.pi * i / n)) for i in range(2 * n)]
    d.polygon(pts, fill=col)


def chips(d, y, items, bg, fg, size=58):
    f = F("Black", size)
    ws = [tw(d, t, f) + 70 for t in items]
    gap = (W - 160 - sum(ws)) / (len(items) - 1)
    x = 80
    for t, w in zip(items, ws):
        d.rounded_rectangle((x, y, x + w, y + size + 50), 16, fill=bg)
        d.text((x + w / 2, y + (size + 50) / 2), t, font=f, fill=fg, anchor="mm"); x += w + gap


# ---- O1: 白×黒×赤。売れ筋の王道。帯は赤で「偏差値46→66」を大きく ----
def o1():
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    lab = "やる気に頼らない「仕組み化」勉強法"; f = F("Black", 64)
    lw = tw(d, lab, f) + 80
    d.rounded_rectangle(((W - lw) / 2, 110, (W + lw) / 2, 220), 14, fill=INK)
    d.text((W / 2, 165), lab, font=f, fill="white", anchor="mm")
    d.text((110, 290), "受験生へ、", font=F("Black", 170), fill=INK)
    p = [("「", INK), ("頑張る", RED), ("」のを", INK)]
    rich(d, 80, 500, p, rich_fit(d, p, "Black", W - 160, 320))
    d.text((W / 2, 1150), "やめましょう", font=fitF(d, "やめましょう", "Black", W - 140, 340), fill=INK, anchor="mm")
    d.text((W - 110, 1500), AUTHOR, font=F("Bold", 90), fill=INK, anchor="rm")
    d = obi(im, RED)
    d.text((100, OBI + 70), "学年最下位・定期テスト0点から", font=F("Black", 76), fill="white")
    rich(d, 90, OBI + 170, [("偏差値", "white"), ("46→66", YEL)], F("Black", 230))
    d.text((100, OBI + 470), "勉強が続かないのは、意志が弱いからじゃない。", font=fitF(d, "勉強が続かないのは、意志が弱いからじゃない。", "Bold", W - 200, 64), fill="white")
    chips(d, OBI + 600, ["スマホに負けない", "三日坊主にならない", "計画が崩れない"], "white", RED, 54)
    return im


# ---- O2: 紺×黄。「頑張る」スイッチをOFF、「仕組み」をON ----
def switch(d, x, y, label, on):
    w, h = 520, 210
    d.text((x - 40, y + h / 2), label, font=F("Black", 120), fill="white", anchor="rm")
    d.rounded_rectangle((x, y, x + w, y + h), h / 2, fill=YEL if on else (90, 100, 120))
    cx = x + w - h / 2 if on else x + h / 2
    d.ellipse((cx - 85, y + 20, cx + 85, y + h - 20), fill="white")
    d.text((x + (w - h) / 2 if on else x + w - (w - h) / 2 - 20, y + h / 2), "ON" if on else "OFF",
           font=F("Black", 80), fill=INK if on else (200, 205, 215), anchor="mm")


def o2():
    im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
    d.text((W / 2, 220), "受験生へ、", font=F("Black", 160), fill="white", anchor="mm")
    p = [("「", "white"), ("頑張る", YEL), ("」のを", "white")]
    rich(d, W / 2, 330, p, rich_fit(d, p, "Black", W - 160, 300), center=True)
    d.text((W / 2, 900), "やめましょう", font=fitF(d, "やめましょう", "Black", W - 140, 330), fill="white", anchor="mm")
    switch(d, 760, 1130, "頑張る", False)
    switch(d, 760, 1390, "仕組み", True)
    d = obi(im, YEL)
    d.text((W / 2, OBI + 110), "やる気に頼らない「仕組み化」勉強法", font=fitF(d, "やる気に頼らない「仕組み化」勉強法", "Black", W - 160, 92), fill=INK, anchor="mm")
    d.line((120, OBI + 200, W - 120, OBI + 200), fill=INK, width=5)
    d.text((110, OBI + 250), "学年最下位・定期テスト0点 →", font=F("Black", 74), fill=INK)
    rich(d, 100, OBI + 350, [("偏差値", INK), ("66", RED), ("へ", INK)], F("Black", 190))
    burst(d, 1390, OBI + 470, 150, RED)
    d.text((1390, OBI + 435), "偏差値", font=F("Black", 50), fill="white", anchor="mm")
    d.text((1390, OBI + 505), "+20", font=F("Black", 100), fill="white", anchor="mm")
    d.text((W / 2, OBI + 700), AUTHOR, font=F("Black", 86), fill=INK, anchor="mm")
    return im


# ---- O3: クリーム地に大きな赤い右肩上がりの矢印。帯は黒 ----
def o3():
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    pts = [(-40, 1560), (380, 1260), (620, 1380), (1250, 760)]
    d.line(pts, fill=(246, 196, 190), width=150, joint="curve")
    a, b = pts[-2], pts[-1]
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    tip = (b[0] + 190 * math.cos(ang), b[1] + 190 * math.sin(ang))
    l = (b[0] + 190 * math.cos(ang + 2.2), b[1] + 190 * math.sin(ang + 2.2))
    r = (b[0] + 190 * math.cos(ang - 2.2), b[1] + 190 * math.sin(ang - 2.2))
    d.polygon([tip, l, r], fill=(246, 196, 190))
    d.text((110, 150), "受験生へ、", font=F("Black", 160), fill=INK)
    d.text((110, 370), "「頑張る」", font=F("Black", 300), fill=RED)
    d.text((110, 730), "のを", font=F("Black", 260), fill=INK)
    d.text((W / 2, 1220), "やめましょう", font=fitF(d, "やめましょう", "Black", W - 140, 330), fill=INK, anchor="mm")
    d.text((W - 110, 1530), AUTHOR, font=F("Bold", 90), fill=INK, anchor="rm")
    d = obi(im, INK)
    rich(d, W / 2, OBI + 60, [("やる気に頼らない", "white"), ("「仕組み化」", YEL), ("勉強法", "white")], rich_fit(d, [("やる気に頼らない「仕組み化」勉強法", INK)], "Black", W - 160, 100), center=True)
    for i, (t, hl) in enumerate([("学年最下位から", None), ("偏差値46→66", "46→66"), ("法政大学・中央大学に合格", None)]):
        y = OBI + 230 + i * 150
        d.ellipse((120, y + 18, 170, y + 68), fill=YEL)
        d.text((145, y + 43), "✓" if False else "", font=F("Black", 40), fill=INK, anchor="mm")
        if hl:
            pre = t.replace(hl, "")
            rich(d, 210, y, [(pre, "white"), (hl, YEL)], F("Black", 84))
        else:
            d.text((210, y), t, font=F("Black", 84), fill="white")
    d.text((W / 2, OBI + 740), "心理学で作る、続く勉強の仕組み", font=F("Bold", 66), fill=(210, 210, 210), anchor="mm")
    return im


# ---- O4: 黒地×白。「頑張る」に黄色の取り消し線。帯は黄色で「+20」を特大 ----
def o4():
    im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
    d.text((110, 170), "受験生へ、", font=F("Black", 170), fill="white")
    fz = rich_fit(d, [("「頑張る」のを", INK)], "Black", W - 180, 320)
    x0, y0 = 90, 420
    d.text((x0, y0), "「頑張る」のを", font=fz, fill="white")
    gx = x0 + tw(d, "「", fz); gw = tw(d, "頑張る", fz)
    d.line((gx - 10, y0 + fz.size * 0.72, gx + gw + 10, y0 + fz.size * 0.5), fill=YEL, width=36)
    d.text((W / 2, 1040), "やめましょう", font=fitF(d, "やめましょう", "Black", W - 140, 340), fill="white", anchor="mm")
    d.text((W / 2, 1380), "根性論は、もう古い。", font=F("Black", 96), fill=YEL, anchor="mm")
    d.text((W / 2, 1540), AUTHOR, font=F("Bold", 84), fill="white", anchor="mm")
    d = obi(im, YEL)
    d.text((110, OBI + 80), "模試の偏差値", font=F("Black", 90), fill=INK)
    d.text((100, OBI + 160), "+20", font=F("Black", 420), fill=RED)
    d.text((960, OBI + 250), "46→66", font=F("Black", 150), fill=INK)
    d.text((960, OBI + 440), "学年最下位・", font=F("Black", 70), fill=INK)
    d.text((960, OBI + 530), "テスト0点から", font=F("Black", 70), fill=INK)
    d.rectangle((0, H - 170, W, H), fill=INK)
    d.text((W / 2, H - 85), "やる気に頼らない「仕組み化」勉強法", font=fitF(d, "やる気に頼らない「仕組み化」勉強法", "Black", W - 160, 80), fill=YEL, anchor="mm")
    return im


def main(out):
    os.makedirs(out, exist_ok=True); ims = {}
    for k, fn in (("O1", o1), ("O2", o2), ("O3", o3), ("O4", o4)):
        im = fn(); im.save(os.path.join(out, f"obi_{k}.jpg"), quality=95); ims[k] = im
    tw_, th = 420, 672
    sheet = Image.new("RGB", (len(ims) * (tw_ + 30) + 30, th + 330), (238, 238, 238)); sd = ImageDraw.Draw(sheet)
    for i, (k, im) in enumerate(ims.items()):
        x = 30 + i * (tw_ + 30)
        sheet.paste(im.resize((tw_, th), Image.LANCZOS), (x, 30))
        sd.text((x + tw_ / 2, th + 70), f"案{k}", font=F("Black", 50), fill=INK, anchor="mm")
        sheet.paste(im.resize((100, 160), Image.LANCZOS), (int(x + tw_ / 2 - 50), th + 120))
    sheet.save(os.path.join(out, "obi_lineup.jpg"), quality=92)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
