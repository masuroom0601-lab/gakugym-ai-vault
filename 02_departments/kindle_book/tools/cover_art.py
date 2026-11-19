#!/usr/bin/env python3
"""表紙P4(集中線)の背景に、薄いオレンジの線画を入れた案(2026-11-19)。
  art1: 勉強道具のアイコンを空いている場所に散らす(時計・鉛筆・ノート・鍵をかけたスマホ・電球・チェックリスト)
  art2: 下のほうに机の線画(開いた本・スタンド・箱にしまったスマホ)
使い方: python3 cover_art.py <出力フォルダ>
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cover_bg as cb
from PIL import Image

C = cb.hx("#F5B48C")   # 線の色(集中線より少し濃く、文字よりずっと薄い)
LW = 10


def clock(d, x, y, r):
    d.ellipse((x - r, y - r, x + r, y + r), outline=C, width=LW)
    d.line((x, y, x, y - r * 0.6), fill=C, width=LW); d.line((x, y, x + r * 0.45, y + r * 0.2), fill=C, width=LW)
    for s in (-1, 1):
        d.chord((x + s * r * 0.75 - r * 0.38, y - r * 1.2, x + s * r * 0.75 + r * 0.38, y - r * 0.5), 180, 360, outline=C, width=LW)
        d.line((x + s * r * 0.6, y + r * 0.85, x + s * r * 0.85, y + r * 1.2), fill=C, width=LW)


def pencil(d, x, y, L, ang):
    a = math.radians(ang); ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux; w = L * 0.09
    p = lambda t, s: (x + ux * t + nx * s, y + uy * t + ny * s)
    d.polygon([p(0, -w), p(L * 0.8, -w), p(L, 0), p(L * 0.8, w), p(0, w)], outline=C, width=LW)
    d.line([p(L * 0.8, -w), p(L * 0.8, w)], fill=C, width=LW); d.line([p(L * 0.15, -w), p(L * 0.15, w)], fill=C, width=LW)


def notebook(d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), 14, outline=C, width=LW)
    for k in range(4): d.line((x + w * 0.25, y + h * (0.28 + k * 0.17), x + w * 0.85, y + h * (0.28 + k * 0.17)), fill=C, width=LW - 2)
    for k in range(5): d.ellipse((x - 14, y + h * (0.12 + k * 0.19) - 10, x + 14, y + h * (0.12 + k * 0.19) + 10), outline=C, width=6)


def phone_lock(d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), 26, outline=C, width=LW)
    d.line((x + w * 0.38, y + 24, x + w * 0.62, y + 24), fill=C, width=LW - 2)
    cx, cy = x + w / 2, y + h * 0.58
    d.rounded_rectangle((cx - w * 0.28, cy - w * 0.12, cx + w * 0.28, cy + w * 0.3), 10, outline=C, width=LW)
    d.arc((cx - w * 0.18, cy - w * 0.42, cx + w * 0.18, cy - w * 0.02), 180, 360, fill=C, width=LW)


def bulb(d, x, y, r):
    d.ellipse((x - r, y - r, x + r, y + r), outline=C, width=LW)
    d.rectangle((x - r * 0.45, y + r * 0.9, x + r * 0.45, y + r * 1.35), outline=C, width=LW)
    for a in (-150, -110, -70, -30, 210):
        t = math.radians(a); d.line((x + r * 1.3 * math.cos(t), y + r * 1.3 * math.sin(t), x + r * 1.65 * math.cos(t), y + r * 1.65 * math.sin(t)), fill=C, width=LW)


def checklist(d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), 14, outline=C, width=LW)
    for k in range(3):
        yy = y + h * (0.22 + k * 0.28)
        d.line((x + w * 0.12, yy, x + w * 0.2, yy + 22, x + w * 0.34, yy - 18), fill=C, width=LW - 2)
        d.line((x + w * 0.45, yy, x + w * 0.88, yy), fill=C, width=LW - 2)


def art1(d):
    clock(d, 1180, 245, 80)
    pencil(d, 1330, 330, 260, -60)
    notebook(d, 790, 820, 170, 210)
    phone_lock(d, 140, 1430, 150, 250)
    bulb(d, 470, 1530, 70)
    checklist(d, 640, 1440, 170, 210)


def art2(d):
    y = 1650
    d.line((60, y, 1540, y), fill=C, width=LW + 2)                  # 机
    d.line((140, y, 140, 1690), fill=C, width=LW); d.line((1460, y, 1460, 1690), fill=C, width=LW)
    # スタンド
    d.line((180, y, 360, y), fill=C, width=LW); d.line((270, y, 300, 1440), fill=C, width=LW); d.line((300, 1440, 450, 1380), fill=C, width=LW)
    d.polygon([(420, 1360), (540, 1400), (500, 1460)], outline=C, width=LW)
    # 開いた本
    bx = 620
    d.polygon([(bx, y - 10), (bx + 210, y - 40), (bx + 210, y - 170), (bx, y - 140)], outline=C, width=LW)
    d.polygon([(bx + 210, y - 40), (bx + 420, y - 10), (bx + 420, y - 140), (bx + 210, y - 170)], outline=C, width=LW)
    # 箱にしまったスマホ(フタつき)
    d.rectangle((1150, y - 120, 1380, y), outline=C, width=LW)
    d.polygon([(1140, y - 120), (1390, y - 120), (1360, y - 175), (1170, y - 175)], outline=C, width=LW)
    d.rounded_rectangle((1225, y - 260, 1300, y - 150), 12, outline=C, width=LW - 2)
    d.line((1262, y - 290, 1262, y - 330), fill=C, width=LW - 2)


def main(out):
    os.makedirs(out, exist_ok=True)
    for k, a in (("art1", art1), ("art2", art2)):
        cb.p4(a).save(os.path.join(out, f"cover_{k}.jpg"), quality=95)
    ims = [Image.open(os.path.join(out, f)) for f in ("cover_final.jpg", "cover_art1.jpg", "cover_art2.jpg")]
    sh = Image.new("RGB", (3 * 530 + 30, 880), (238, 238, 238))
    for i, im in enumerate(ims): sh.paste(im.resize((500, 800), Image.LANCZOS), (30 + i * 530, 40))
    sh.save(os.path.join(out, "art_lineup.jpg"), quality=92)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
