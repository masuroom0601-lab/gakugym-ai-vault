import sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-%s.ttc"
def F(kind, w, sz): return ImageFont.truetype((SANS if kind == "s" else SERIF) % w, sz, index=0)
W, H = 1600, 2560

def tw(d, t, f): return d.textlength(t, font=f)
def fit(d, t, kind, w, maxw, start):
    sz = start
    while tw(d, t, F(kind, w, sz)) > maxw: sz -= 4
    return F(kind, w, sz)
def center(d, y, t, f, fill):
    d.text(((W - tw(d, t, f)) / 2, y), t, font=f, fill=fill)

# ---- A: 白地・「頑張る」に赤い取り消し線 ----
im = Image.new("RGB", (W, H), "#f7f4ee"); d = ImageDraw.Draw(im)
INK, RED = "#1d1d1d", "#c0392b"
center(d, 250, "受験生へ、", F("s", "Bold", 110), INK)
fA = F("s", "Black", 300)
t1 = "「頑張る」"; x = (W - tw(d, t1, fA)) / 2; y = 420
d.text((x, y), t1, font=fA, fill=INK)
bb = d.textbbox((x, y), "頑張る", font=fA); bx0 = x + tw(d, "「", fA); bx1 = bx0 + tw(d, "頑張る", fA)
ym = (bb[1] + bb[3]) / 2 + 20
d.line((bx0 - 10, ym + 40, bx1 + 10, ym - 40), fill=RED, width=34)
center(d, 790, "のを", F("s", "Black", 230), INK)
center(d, 1060, "やめましょう", fit(d, "やめましょう", "s", "Black", W - 160, 300), INK)
# バッジ
cx, cy, r = 1320, 1590, 170
d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED)
for k, (t, sz) in enumerate([("偏差値", 64), ("20UP!", 100)]):
    f = F("s", "Black", sz); d.text((cx - tw(d, t, f) / 2, cy - 100 + k * 82), t, font=f, fill="white")
d.text((120, 1470), "やる気に頼らない", font=F("s", "Bold", 84), fill=INK)
d.text((105, 1585), "「仕組み化」勉強法", font=F("s", "Black", 100), fill=RED)
d.line((120, 1830, W - 120, 1830), fill=INK, width=4)
center(d, 1880, "学年最下位・定期テスト０点から", F("s", "Medium", 66), INK)
center(d, 1970, "逆転合格した著者が教える、続く勉強の仕組み", F("s", "Medium", 66), INK)
center(d, 2290, "益田 大輝", F("s", "Bold", 96), INK)
im.save(f"{OUT}/cover_A.jpg", quality=95)

# ---- B: 紺地・白文字・黄色のアクセント ----
im = Image.new("RGB", (W, H), "#18305a"); d = ImageDraw.Draw(im)
YEL, WHITE = "#f2c230", "#ffffff"
d.text((120, 200), "受験生へ、", font=F("s", "Bold", 120), fill=WHITE)
fB = F("s", "Black", 290)
d.text((110, 380), "「頑張る」", font=fB, fill=YEL)
d.text((110, 700), "のを", font=F("s", "Black", 220), fill=WHITE)
d.text((110, 960), "やめましょう", font=fit(d, "やめましょう", "s", "Black", W - 220, 280), fill=WHITE)
# 46→66 の線グラフ
gx0, gy0, gx1, gy1 = 160, 1380, 1440, 1780
d.line((gx0, gy1, gx1, gy1), fill="#6f86b0", width=4)
pts = [(gx0 + 40, gy1 - 60), (gx0 + 360, gy1 - 90), (gx0 + 700, gy1 - 200), (gx0 + 1020, gy1 - 330), (gx1 - 60, gy1 - 400)]
d.line(pts, fill=YEL, width=16, joint="curve")
for p in (pts[0], pts[-1]): d.ellipse((p[0] - 22, p[1] - 22, p[0] + 22, p[1] + 22), fill=YEL)
d.text((pts[0][0] - 20, pts[0][1] + 30), "46", font=F("s", "Black", 80), fill=WHITE)
d.text((pts[-1][0] - 90, pts[-1][1] - 140), "66", font=F("s", "Black", 120), fill=YEL)
d.text((gx0 + 380, gy1 + 50), "偏差値20UP！", font=F("s", "Black", 90), fill=WHITE)
center(d, 2020, "やる気に頼らない「仕組み化」勉強法", fit(d, "やる気に頼らない「仕組み化」勉強法", "s", "Bold", W - 200, 96), WHITE)
center(d, 2320, "益田 大輝", F("s", "Bold", 96), WHITE)
im.save(f"{OUT}/cover_B.jpg", quality=95)

# ---- C: 白地・明朝の大きなタイトル・赤い帯 ----
im = Image.new("RGB", (W, H), "#ffffff"); d = ImageDraw.Draw(im)
INK, RED = "#111111", "#b8322a"
d.rectangle((0, 0, W, 330), fill=RED)
center(d, 95, "偏差値20UP！やる気に頼らない「仕組み化」勉強法", fit(d, "偏差値20UP！やる気に頼らない「仕組み化」勉強法", "s", "Bold", W - 160, 84), "white")
center(d, 470, "受験生へ、", F("m", "Bold", 130), INK)
for k, t in enumerate(["「頑張る」の", "を", "やめましょう"]):
    pass
center(d, 680, "「頑張る」のを", fit(d, "「頑張る」のを", "m", "Black", W - 140, 260), INK)
center(d, 1020, "やめましょう", fit(d, "やめましょう", "m", "Black", W - 140, 280), INK)
d.line((W / 2 - 300, 1420, W / 2 + 300, 1420), fill=RED, width=6)
center(d, 1500, "学年最下位・定期テスト０点。", F("s", "Medium", 74), INK)
center(d, 1600, "意志の力を捨てて、仕組みに変えたら", F("s", "Medium", 74), INK)
center(d, 1700, "勉強は勝手に続くようになった。", F("s", "Medium", 74), INK)
center(d, 2300, "益田 大輝", F("m", "Bold", 100), INK)
im.save(f"{OUT}/cover_C.jpg", quality=95)
print("ok")
