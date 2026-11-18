#!/usr/bin/env python3
"""Kindle表紙 v2(2026-11-18)。1600x2560(KDP推奨の 1:1.6)。
参考: 競合の勉強法本の表紙(白地に極太ゴシック+赤のアクセント、BEFORE→AFTERのイラスト、下に濃い色の帯と吹き出し)。
モチーフ・文言は独自(根性で頑張る→仕組みで動く、歯車、右肩上がりのグラフ)。
使い方: python3 cover_v2.py <出力.jpg>
"""
import math, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 2560
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
INK, RED, YEL, BLUE, GRAY = (25, 25, 25), (214, 40, 40), (247, 201, 46), (90, 170, 230), (150, 150, 150)
BAND = (28, 28, 30)
_fc = {}


def F(w, s):
    if (w, s) not in _fc: _fc[(w, s)] = ImageFont.truetype(SANS % w, s, index=0)
    return _fc[(w, s)]


def tw(d, t, f): return d.textlength(t, font=f)


def rich(d, y, parts, f, cx=W / 2):
    """[(文字, 色), ...] を中央ぞろえで1行に描く"""
    x = cx - sum(tw(d, t, f) for t, _ in parts) / 2
    for t, c in parts:
        d.text((x, y), t, font=f, fill=c); x += tw(d, t, f)


def figure(d, cx, cy, happy):
    """本を持つ人(頭の中心 cx, cy)"""
    r = 120
    d.rounded_rectangle((cx - 170, cy + 90, cx + 170, cy + 420), 90, fill=INK)          # 体
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="white", outline=INK, width=12)    # 顔
    d.chord((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), 180, 360, fill=INK)      # 髪
    d.rectangle((cx - r - 6, cy - 10, cx - r + 26, cy + 40), fill=INK)
    d.rectangle((cx + r - 26, cy - 10, cx + r + 6, cy + 40), fill=INK)
    ey = cy + 30
    if happy:
        for ex in (cx - 45, cx + 45):
            d.arc((ex - 22, ey - 18, ex + 22, ey + 22), 200, 340, fill=INK, width=10)
        d.chord((cx - 40, cy + 55, cx + 40, cy + 105), 0, 180, fill=RED)
    else:
        for ex in (cx - 45, cx + 45):
            d.ellipse((ex - 11, ey - 11, ex + 11, ey + 11), fill=INK)
            d.line((ex - 26, ey - 40, ex + 18, ey - 28) if ex < cx else (ex - 18, ey - 28, ex + 26, ey - 40), fill=INK, width=8)
        d.arc((cx - 32, cy + 78, cx + 32, cy + 118), 200, 340, fill=INK, width=9)
        for dx, dy in ((-60, 70), (-68, 130), (60, 70), (66, 135)):          # 涙
            x, y = cx + dx, cy + dy
            d.polygon([(x, y - 22), (x - 13, y + 4), (x + 13, y + 4)], fill=BLUE)
            d.ellipse((x - 13, y - 9, x + 13, y + 17), fill=BLUE)
    # 開いた本
    by = cy + 160
    for s in (-1, 1):
        pts = [(cx, by + 20), (cx + s * 230, by - 10), (cx + s * 230, by + 250), (cx, by + 270)]
        d.polygon(pts, fill="white", outline=INK); d.line(pts + [pts[0]], fill=INK, width=12, joint="curve")
        for k in range(3):
            yy = by + 60 + k * 55
            d.line((cx + s * 40, yy + 4, cx + s * 190, yy - 8), fill=INK, width=8)
        d.ellipse((cx + s * 230 - 38, by + 80, cx + s * 230 + 38, by + 156), fill="white", outline=INK, width=12)  # 手


def cloud(d, cx, cy, s=1.0):
    for dx, dy, r in ((-70, 10, 60), (0, -25, 75), (75, 10, 60), (0, 30, 60)):
        d.ellipse((cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s), fill=GRAY)
    x, y = cx + 10 * s, cy + 70 * s
    d.polygon([(x, y), (x - 40 * s, y + 80 * s), (x - 5 * s, y + 80 * s), (x - 30 * s, y + 160 * s), (x + 40 * s, y + 60 * s), (x + 5 * s, y + 60 * s), (x + 25 * s, y)], fill=YEL, outline=INK)


def battery(d, x, y):
    d.rounded_rectangle((x, y, x + 150, y + 74), 12, outline=INK, width=10)
    d.rectangle((x + 150, y + 22, x + 166, y + 52), fill=INK)
    d.rectangle((x + 16, y + 16, x + 36, y + 58), fill=RED)
    d.text((x + 75, y + 112), "やる気", font=F("Black", 40), fill=INK, anchor="mm")


def gear(d, cx, cy, r, col):
    pts = []
    for i in range(16):
        a = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.78
        for da in (-0.17, 0.17):
            pts.append((cx + rr * math.cos(a + da), cy + rr * math.sin(a + da)))
    d.polygon(pts, fill=col)
    d.ellipse((cx - r * 0.32, cy - r * 0.32, cx + r * 0.32, cy + r * 0.32), fill="white")


def graph(d, x, y):
    d.line((x, y, x, y + 150, x + 190, y + 150), fill=INK, width=9)
    pts = [(x + 20, y + 125), (x + 70, y + 100), (x + 115, y + 70), (x + 165, y + 20)]
    d.line(pts, fill=RED, width=14, joint="curve")
    d.polygon([(x + 185, y), (x + 140, y + 10), (x + 175, y + 45)], fill=RED)


def sparkles(d, cx, cy):
    for a in (-75, -45):
        t = math.radians(a - 90)
        d.line((cx + 150 * math.cos(t), cy + 150 * math.sin(t), cx + 195 * math.cos(t), cy + 195 * math.sin(t)), fill=INK, width=9)


def main(out):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    # 上のリード
    f = F("Bold", 62)
    rich(d, 95, [("勉強しなきゃいけないのに、", INK), ("続かない…", RED)], f)
    rich(d, 180, [("そんな受験生に読んでほしい本です。", INK)], f)
    # タイトル
    rich(d, 300, [("受験生へ、", INK)], F("Black", 130))
    t = [("「", INK), ("頑張る", RED), ("」のを", INK)]
    z = 250
    while sum(tw(d, a, F("Black", z)) for a, _ in t) > W - 90: z -= 5
    ft = F("Black", z)
    rich(d, 440, t, ft)
    x0 = W / 2 - sum(tw(d, s, ft) for s, _ in t) / 2 + tw(d, "「", ft)
    d.rectangle((x0, 740, x0 + tw(d, "頑張る", ft), 770), fill=YEL)   # 黄色のマーカー
    s = 300
    while tw(d, "やめましょう", F("Black", s)) > W - 110: s -= 6
    rich(d, 775, [("やめましょう", INK)], F("Black", s))
    # イラスト(根性 → 仕組み)
    cy = 1420
    figure(d, 370, cy, False); figure(d, 1230, cy, True)
    cloud(d, 165, 1215, 0.8); battery(d, 330, 1150)
    gear(d, 1040, 1225, 62, INK); gear(d, 1125, 1160, 40, RED); graph(d, 1320, 1140); sparkles(d, 1230, cy)
    d.polygon([(690, 1680), (820, 1680), (820, 1630), (910, 1720), (820, 1810), (820, 1760), (690, 1760)], fill=INK)
    for cx, lab in ((370, "根性で頑張る"), (1230, "仕組みで動く")):
        d.text((cx, 1925), lab, font=F("Black", 74), fill=RED if cx > W / 2 else INK, anchor="mm")
    # 偏差値20UPのバッジ
    bx, by, r = 800, 1360, 165
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=RED)
    d.text((bx, by - 70), "偏差値", font=F("Black", 66), fill="white", anchor="mm")
    d.text((bx, by + 25), "20", font=F("Black", 150), fill=YEL, anchor="mm")
    d.text((bx, by + 115), "UP!", font=F("Black", 66), fill="white", anchor="mm")
    # 下の帯
    top = 1990
    d.rectangle((0, top, W, H), fill=BAND)
    d.text((W / 2, top + 95), "ー やる気に頼らない ー", font=F("Black", 92), fill="white", anchor="mm")
    rich(d, top + 170, [("「仕組み化」", YEL), ("勉強法", "white")], F("Black", 150))
    # 吹き出し
    bx0, by0, bx1, by1 = 90, top + 395, 1130, top + 525
    d.rounded_rectangle((bx0, by0, bx1, by1), 40, fill="white")
    d.polygon([(bx1 - 10, by0 + 45), (bx1 + 70, by0 + 20), (bx1 - 10, by0 + 95)], fill="white")
    rich(d, by0 + 25, [("学年最下位・テスト0点から", INK), ("偏差値46→66", RED)], F("Black", 50), cx=(bx0 + bx1) / 2)
    d.text((1380, top + 460), "益田 大輝", font=F("Black", 74), fill="white", anchor="mm")
    im.save(out, quality=95)
    # Amazonの検索結果くらいの大きさでの見え方
    im.resize((150, 240), Image.LANCZOS).save(out.replace(".jpg", "_small.png"))
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cover_v2.jpg")
