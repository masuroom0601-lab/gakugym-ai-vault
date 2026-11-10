import math, sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]
G = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
INK, GRAY, LIGHT, PAPER = "#222222", "#8a8a8a", "#d9d6cf", "#f4f1ea"
RED, BLUE = "#b4432f", "#2f5d7c"
def F(sz): return ImageFont.truetype(G, sz)

def canvas(w, h):
    im = Image.new("RGB", (w, h), "white"); return im, ImageDraw.Draw(im)

def ctext(d, xy, t, sz, fill=INK, anchor="mm"):
    d.text(xy, t, font=F(sz), fill=fill, anchor=anchor)

def mtext(d, cx, cy, lines, sz, fill=INK, gap=1.35):
    h = sz * gap; y0 = cy - h * (len(lines) - 1) / 2
    for i, l in enumerate(lines): ctext(d, (cx, y0 + i * h), l, sz, fill)

def box(d, x0, y0, x1, y1, fill="white", outline=INK, w=4, r=14):
    d.rounded_rectangle((x0, y0, x1, y1), r, fill=fill, outline=outline, width=w)

def arrow(d, x0, y0, x1, y1, fill=INK, w=5, head=22):
    d.line((x0, y0, x1, y1), fill=fill, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    p1 = (x1 - head * math.cos(a - 0.45), y1 - head * math.sin(a - 0.45))
    p2 = (x1 - head * math.cos(a + 0.45), y1 - head * math.sin(a + 0.45))
    d.polygon([(x1, y1), p1, p2], fill=fill)

# 図1 行動→やる気
im, d = canvas(1800, 900)
ctext(d, (110, 230), "×", 90, RED)
for i, t in enumerate(["やる気が出る", "勉強を始める"]):
    x = 300 + i * 700
    box(d, x, 160, x + 480, 300, fill="white", outline=GRAY)
    ctext(d, (x + 240, 230), t, 54, GRAY)
arrow(d, 800, 230, 990, 230, GRAY)
ctext(d, (1400, 345), "やる気を待っている間に、時間だけが過ぎていく", 34, GRAY)
d.line((80, 440, 1720, 440), fill=LIGHT, width=3)
ctext(d, (110, 640), "○", 90, BLUE)
labels = ["手を動かす", "作業興奮", "やる気が出る"]
for i, t in enumerate(labels):
    x = 230 + i * 520
    box(d, x, 570, x + 400, 710, fill=PAPER if i == 1 else "white", outline=INK)
    ctext(d, (x + 200, 640), t, 54)
    if i < 2: arrow(d, x + 410, 640, x + 510, 640)
ctext(d, (1080, 790), "最初の5分、とにかくペンを動かすことがスイッチになる", 34, INK)
im.save(f"{OUT}/fig1.png")

# 図2 A君とB君の1日
im, d = canvas(1800, 1250)
cols = [("A君　気合いで動く", RED, ["朝｜「今日こそ10時間やるぞ！」と決意する", "昼｜スマホの通知を、意志の力で無視し続ける", "夕方｜疲れ切って、誘惑に勝てなくなる", "夜｜スマホを眺め、自己嫌悪で一日が終わる"]),
        ("B君　仕組みで動く", BLUE, ["朝｜スマホをタイマー付きの箱に入れる", "昼｜机の上には、今日やる1冊だけ", "夕方｜決めた量を、淡々とこなし続ける", "夜｜やった量を記録して、明日の本を開いておく"])]
for c, (title, col, rows) in enumerate(cols):
    x0 = 80 + c * 850; x1 = x0 + 790
    d.rectangle((x0, 80, x1, 180), fill=col)
    ctext(d, ((x0 + x1) / 2, 130), title, 50, "white")
    for r, t in enumerate(rows):
        y = 230 + r * 245
        box(d, x0, y, x1, y + 190, fill="white" if c == 0 else PAPER, outline=col, w=3)
        when, what = t.split("｜")
        ctext(d, (x0 + 40, y + 60), when, 36, col, anchor="lm")
        ctext(d, (x0 + 40, y + 130), what, 36, INK, anchor="lm")
        if r < 3: arrow(d, (x0 + x1) / 2, y + 195, (x0 + x1) / 2, y + 238, col, 4, 16)
im.save(f"{OUT}/fig2.png")

# 図3 スマホの悪循環
im, d = canvas(1600, 1350)
cx, cy, R = 800, 690, 430
nodes = ["勉強が不安・\nしんどい", "スマホを見る", "一時的に\nホッとする", "時間を失い、\n不安が大きくなる"]
ang = [-90, 0, 90, 180]
pts = []
for a in ang:
    pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=LIGHT, width=6)
for i, ((x, y), t) in enumerate(zip(pts, nodes)):
    box(d, x - 220, y - 95, x + 220, y + 95, fill=PAPER if i == 2 else "white", outline=INK)
    mtext(d, x, y, t.split("\n"), 42)
for i in range(4):
    a0 = math.radians(ang[i] + 30); a1 = math.radians(ang[i] + 58)
    x0, y0 = cx + R * math.cos(a0), cy + R * math.sin(a0)
    x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
    arrow(d, x0, y0, x1, y1, RED, 6, 30)
mtext(d, cx, cy, ["負の強化の", "悪循環"], 48, RED)
im.save(f"{OUT}/fig3.png")

# 図4 机の比較(上から見た図)
im, d = canvas(1800, 1000)
for c in range(2):
    x0 = 80 + c * 860; x1 = x0 + 780
    ctext(d, ((x0 + x1) / 2, 90), "集中できない机" if c == 0 else "集中できる机", 48, RED if c == 0 else BLUE)
    d.rectangle((x0, 150, x1, 820), fill=PAPER, outline=INK, width=4)
if True:  # 左：散らかった机
    def item(x0, y0, x1, y1, t, rot=0, sz=30):
        d.rectangle((x0, y0, x1, y1), fill="white", outline=INK, width=3); ctext(d, ((x0+x1)/2, (y0+y1)/2), t, sz)
    item(130, 200, 330, 330, "漫画")
    item(360, 190, 530, 300, "プリント")
    item(560, 210, 800, 330, "別の教科の本", sz=28)
    d.rounded_rectangle((640, 380, 760, 600), 18, fill="white", outline=RED, width=5); ctext(d, (700, 490), "スマホ", 30, RED)
    item(150, 400, 330, 520, "お菓子")
    item(330, 560, 600, 760, "参考書", sz=34)
    item(130, 600, 300, 700, "小物")
    item(620, 650, 790, 760, "プリント")
if True:  # 右：整った机
    d.rectangle((1040, 380, 1340, 700), fill="white", outline=INK, width=4); ctext(d, (1190, 540), "今日やる1冊", 36)
    d.rectangle((1380, 380, 1640, 700), fill="white", outline=INK, width=4); ctext(d, (1510, 540), "ノート", 36)
    d.line((1400, 740, 1620, 740), fill=BLUE, width=10); ctext(d, (1510, 780), "ペン", 30, BLUE)
ctext(d, (470, 890), "目に入るものが、集中力を少しずつ奪う", 34, GRAY)
ctext(d, (1330, 890), "スマホは別の部屋。机には3つだけ", 34, INK)
im.save(f"{OUT}/fig4.png")

# 図5 学習ログの記入例＋積み上げグラフ
im, d = canvas(1800, 1350)
hdr = ["日付", "教科・教材", "やった量", "結果"]
rows = [["月", "英単語帳", "100語", "定着85%"], ["火", "数学 参考書", "例題12問", "正解9問"], ["水", "古文 文法", "15ページ", "読了"], ["木", "英単語帳", "100語", "定着88%"], ["金", "数学 参考書", "例題15問", "正解12問"]]
xs = [80, 280, 900, 1250, 1720]
y = 60
d.rectangle((xs[0], y, xs[-1], y + 90), fill=INK)
for i, h in enumerate(hdr): ctext(d, ((xs[i] + xs[i+1]) / 2, y + 45), h, 38, "white")
for r, row in enumerate(rows):
    yy = y + 90 + r * 85
    if r % 2: d.rectangle((xs[0], yy, xs[-1], yy + 85), fill=PAPER)
    for i, t in enumerate(row): ctext(d, ((xs[i] + xs[i+1]) / 2, yy + 42), t, 36)
d.rectangle((xs[0], y, xs[-1], y + 90 + 85 * 5), outline=INK, width=3)
# グラフ
gx0, gy0, gx1, gy1 = 220, 720, 1700, 1210
d.line((gx0, gy1, gx1, gy1), fill=INK, width=4); d.line((gx0, gy0, gx0, gy1), fill=INK, width=4)
vals = [120, 260, 380, 530, 690, 820, 1000, 1200]
mx = 1300
bw = (gx1 - gx0) / len(vals)
for i, v in enumerate(vals):
    h = (gy1 - gy0) * v / mx
    d.rectangle((gx0 + i * bw + 30, gy1 - h, gx0 + (i + 1) * bw - 30, gy1), fill=BLUE if i == len(vals) - 1 else LIGHT)
    ctext(d, (gx0 + (i + 0.5) * bw, gy1 + 40), f"{i+1}週", 30, INK)
ctext(d, (gx0 + (len(vals) - 0.5) * bw, gy1 - (gy1 - gy0) * vals[-1] / mx - 40), "累計1,200問", 34, BLUE)
for v in (0, 500, 1000):
    yv = gy1 - (gy1 - gy0) * v / mx; ctext(d, (gx0 - 20, yv), str(v), 28, GRAY, anchor="rm")
ctext(d, (gx0, gy0 - 40), "解いた問題数（累計）", 32, INK, anchor="lm")
im.save(f"{OUT}/fig5.png")

# 図6 逆算の階段
im, d = canvas(1800, 1100)
steps = [("今日", "大問1〜3を\n解く"), ("週", "P.50〜100を\n解き切る"), ("月", "この分野の\n基礎を固める"), ("本番", "過去問で\n合格点を取る")]
for i, (k, t) in enumerate(steps):
    x0 = 80 + i * 410; y0 = 730 - i * 155
    d.rectangle((x0, y0, x0 + 410, 1010), fill=PAPER if i < 3 else "white", outline=INK, width=4)
    ctext(d, (x0 + 205, y0 + 60), k, 50, RED if i == 3 else INK)
    mtext(d, x0 + 205, y0 + 160, t.split("\n"), 34)
arrow(d, 1550, 200, 350, 200, RED, 6, 30)
ctext(d, (950, 130), "ゴールから逆にたどって、今日の1歩まで落とし込む", 38, RED)
im.save(f"{OUT}/fig6.png")

# 図7 バッファー入りの1週間
im, d = canvas(1800, 900)
days = ["月", "火", "水", "木", "金", "土", "日"]
slots = ["午前", "午後", "夜"]
x0, y0, cw, rh = 230, 110, 210, 210
for i, dd in enumerate(days): ctext(d, (x0 + i * cw + cw / 2, y0 - 50), dd, 40)
for j, s in enumerate(slots): ctext(d, (x0 - 60, y0 + j * rh + rh / 2), s, 36)
plan = {(0,0):"英語",(0,1):"数学",(0,2):"国語",(1,0):"数学",(1,1):"英語",(1,2):"古文",(2,0):"英語",(2,1):"数学",(3,0):"国語",(3,1):"英語",(3,2):"数学",(4,0):"数学",(4,1):"英語",(4,2):"古文",(5,0):"模試の復習",(5,1):"英語",(5,2):"数学",(6,0):"1週間の\n振り返り"}
for i in range(7):
    for j in range(3):
        bx, by = x0 + i * cw, y0 + j * rh
        buf = (i, j) in [(2, 2), (6, 1), (6, 2)]
        d.rectangle((bx + 8, by + 8, bx + cw - 8, by + rh - 8), fill=PAPER if buf else "white", outline=RED if buf else INK, width=5 if buf else 3)
        t = "予備" if buf else plan.get((i, j), "")
        mtext(d, bx + cw / 2, by + rh / 2, t.split("\n"), 34 if not buf else 40, RED if buf else INK)
ctext(d, (900, 800), "赤い枠＝何も入れない予備の時間（遅れたらここで追いつく）", 34, RED)
im.save(f"{OUT}/fig7.png")

# 図8 読む vs テスト
im, d = canvas(1800, 1100)
gx0, gy0, gx1, gy1 = 260, 120, 1700, 860
d.line((gx0, gy1, gx1, gy1), fill=INK, width=4); d.line((gx0, gy0, gx0, gy1), fill=INK, width=4)
data = [("直後のテスト", 83, 71), ("1週間後のテスト", 40, 61)]
for v in (0, 20, 40, 60, 80, 100):
    yv = gy1 - (gy1 - gy0) * v / 100; ctext(d, (gx0 - 20, yv), f"{v}", 30, GRAY, anchor="rm")
    if v: d.line((gx0, yv, gx1, yv), fill="#eeeeee", width=2)
for g, (lab, a, b) in enumerate(data):
    cx = gx0 + (g + 0.5) * (gx1 - gx0) / 2
    for k, (v, col) in enumerate([(a, LIGHT), (b, BLUE)]):
        x = cx - 230 + k * 250
        h = (gy1 - gy0) * v / 100
        d.rectangle((x, gy1 - h, x + 200, gy1), fill=col)
        ctext(d, (x + 100, gy1 - h - 35), f"{v}%", 38, INK if k == 0 else BLUE)
    ctext(d, (cx, gy1 + 50), lab, 40)
d.rectangle((300, 980, 350, 1030), fill=LIGHT); ctext(d, (370, 1005), "4回くり返し読む", 34, INK, anchor="lm")
d.rectangle((900, 980, 950, 1030), fill=BLUE); ctext(d, (970, 1005), "1回読んで、3回テストする", 34, INK, anchor="lm")
ctext(d, (gx0, gy0 - 50), "思い出せた割合（%）", 32, INK, anchor="lm")
im.save(f"{OUT}/fig8.png")
print("ok")
