"""スマホの画面・通知・数字・コメント欄など、文字が中心のコマを描く。
AIの絵では文字が意味不明になり、黒いぐちゃぐちゃに見えてしまうため、こうしたコマは図形と文字で描く。

使い方: python3 ui_panels.py 出力フォルダ [コマ名 ...]
    出力は「pXX_コマ番号_ui.png」。page_compose.py の --pick で「番号=ui」と指定して使う
    11-2(震える指)は、指の部品 c_finger_sN.png を --finger で渡すと、切り抜いて画面の上に重ねる
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def F(sz, bold=False): return ImageFont.truetype(FONT_B if bold else FONT, sz)
K = 2  # 実際のコマの2倍の大きさで描く

def canvas(w, h, bg=235): return Image.new("L", (w * K, h * K), bg)

def focus_lines(im, cx, cy, n=140, inner=0.32, seed=1):
    """集中線"""
    import random; rnd = random.Random(seed); d = ImageDraw.Draw(im); w, h = im.size
    R = math.hypot(w, h)
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi); r0 = R * rnd.uniform(inner, inner + 0.15); wd = rnd.uniform(0.004, 0.012)
        p = [(cx + math.cos(a - wd) * R, cy + math.sin(a - wd) * R), (cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a + wd) * R, cy + math.sin(a + wd) * R)]
        d.polygon(p, fill=0)

def tone(im, level=200, step=10):
    """網点風の背景"""
    d = ImageDraw.Draw(im); w, h = im.size; r = max(1, int(step * (255 - level) / 255 * 0.7))
    for y in range(0, h, step):
        for x in range((y // step % 2) * step // 2, w, step): d.ellipse([x - r, y - r, x + r, y + r], fill=90)

def heart(d, x, y, s, fill=0, outline=None):
    pts = []
    for t in range(0, 360, 6):
        a = math.radians(t)
        pts.append((x + s * 16 * math.sin(a) ** 3 / 17, y - s * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 17))
    d.polygon(pts, fill=fill, outline=outline)

def phone(im, box, angle=0):
    """スマホの外形を描き、画面の領域(画面の画像, 貼り付け関数)を返す"""
    x0, y0, x1, y1 = [int(v) for v in box]; w, h = x1 - x0, y1 - y0
    body = Image.new("LA", (w, h), (0, 0)); d = ImageDraw.Draw(body)
    r = int(min(w, h) * 0.12)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(20, 255))
    bz = int(min(w, h) * 0.04)
    d.rounded_rectangle([bz, bz, w - 1 - bz, h - 1 - bz], radius=int(r * 0.7), fill=(255, 255))
    d.rounded_rectangle([w // 2 - w // 10, bz + 4, w // 2 + w // 10, bz + 4 + max(8, h // 50)], radius=6, fill=(20, 255))
    scr = (bz + 6, bz + max(8, h // 50) + 14, w - bz - 6, h - bz - 10)
    def paste(screen_img):
        sw, sh = scr[2] - scr[0], scr[3] - scr[1]
        body.paste(Image.merge("LA", (screen_img.resize((sw, sh)), Image.new("L", (sw, sh), 255))), (scr[0], scr[1]))
        b = body.rotate(angle, expand=True, resample=Image.BICUBIC)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        im.paste(b.getchannel(0), (cx - b.width // 2, cy - b.height // 2), b.getchannel(1))
    return (scr[2] - scr[0], scr[3] - scr[1]), paste

def post_card(d, x0, y0, x1, title, likes=None, sz=1.0):
    """投稿のカード(アイコン・アカウント名・図解のサムネイル・タイトル・いいね)。下端のyを返す"""
    s = sz; d.ellipse([x0, y0, x0 + 44 * s, y0 + 44 * s], outline=0, width=3); d.text((x0 + 11 * s, y0 + 6 * s), "C", font=F(int(26 * s), True), fill=0)
    d.text((x0 + 56 * s, y0 + 6 * s), "CAPS公式", font=F(int(24 * s), True), fill=0)
    ty = y0 + 60 * s; th = (x1 - x0) * 0.62
    d.rectangle([x0, ty, x1, ty + th], outline=0, width=3)
    # 手描き風の図解: 番号つきの箱が並ぶ
    for k in range(3):
        bx = x0 + 16 * s + k * (x1 - x0 - 32 * s) / 3
        d.rounded_rectangle([bx + 4, ty + th * 0.42, bx + (x1 - x0 - 32 * s) / 3 - 8, ty + th * 0.88], radius=10, outline=0, width=3)
        d.text((bx + 14 * s, ty + th * 0.48), str(k + 1), font=F(int(30 * s), True), fill=0)
    d.text((x0 + 16 * s, ty + 12 * s), title, font=F(int(26 * s), True), fill=0)
    y = ty + th + 14 * s
    if likes is not None:
        heart(d, x0 + 18 * s, y + 18 * s, 18 * s, fill=None if likes == "0" else 0, outline=0)
        d.text((x0 + 44 * s, y + 2 * s), likes, font=F(int(28 * s), True), fill=0)
        d.text((x0 + 150 * s, y + 2 * s), "コメント", font=F(int(22 * s)), fill=60)
    return y + 40 * s

TITLE = "履修登録で失敗しない5つのコツ"

def p06_2(w=314, h=319):
    """想像: 新入生のスマホに流れてくる投稿(どれも宣伝ばかりで、困りごとに答えていない)"""
    im = canvas(w, h, 250); tone(im, 215, 12)
    (sw, sh), paste = phone(im, (w * K * 0.18, h * K * 0.06, w * K * 0.82, h * K * 1.15), angle=-8)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    y = 14
    for name, msg in [("テニスサークル", "新歓BBQ!参加費無料!"), ("軽音部", "ライブやります!"), ("写真部", "部員募集中!")]:
        d.ellipse([14, y, 50, y + 36], outline=0, width=3); d.text((58, y + 4), name, font=F(22, True), fill=0)
        d.rectangle([14, y + 46, sw - 14, y + 120], outline=0, width=2)
        d.text((24, y + 64), msg, font=F(22), fill=0); y += 140
    paste(scr)
    return im

def p11_2(w=1000, h=321, finger=None):
    """「投稿する」ボタンの上で止まる、震える指"""
    im = canvas(w, h, 255); d = ImageDraw.Draw(im); W, H = im.size
    # 画面のアップ(左に投稿の下書き、右に大きな「投稿する」ボタン)
    d.rectangle([0, 0, W, H], fill=255)
    post_card(d, 70, 30, 900, TITLE, sz=2.0)
    bx0, by0, bx1, by1 = W * 0.6, H * 0.6, W * 0.92, H * 0.88
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=int((by1 - by0) / 2), fill=0)
    t = "投稿する"; f = F(int((by1 - by0) * 0.5), True); tw = d.textlength(t, font=f)
    d.text(((bx0 + bx1) / 2 - tw / 2, by0 + (by1 - by0) * 0.16), t, font=f, fill=255)
    if not finger:
        draw_finger(d, (bx0 + bx1) / 2, by0 - 60, H)
    if finger:
        fg = finger_cutout(finger); fh = int(H * 0.95); fg = fg.resize((int(fg.width * fh / fg.height), fh))
        fx, fy = int((bx0 + bx1) / 2 - fg.width * 0.45), int(by0 - fh * 0.98)
        im.paste(fg.getchannel(0), (fx, max(-fh // 2, fy)), fg.getchannel(1))
        # 震えを表す線
        cx = fx + fg.width * 0.45
        for s in (-1, 1):
            for k in range(3):
                x = cx + s * (fg.width * 0.32 + k * 22); y = by0 - 120 - k * 18
                d.arc([x - 30, y - 40, x + 30, y + 40], 60 if s > 0 else 240, 120 if s > 0 else 300, fill=0, width=5)
    return im

def draw_finger(d, tx, ty, H, shake=True):
    """上から伸びて、ボタンの少し上で止まる人差し指(線画)。まわりに震えを表す線を入れる"""
    fw = 120  # 指の太さ
    top = -40
    # 手の甲とパーカーの袖(コマの上の端から入ってくる)
    d.polygon([(tx - 330, top), (tx + 260, top), (tx + 170, ty - 380), (tx - 140, ty - 400)], fill=255, outline=0, width=7)
    d.line([(tx - 330, top + 90), (tx + 240, top + 90)], fill=0, width=6)
    for k in range(6): d.line([(tx - 300 + k * 90, top), (tx - 280 + k * 90, top + 90)], fill=0, width=4)  # 袖のリブ
    # 曲げたほかの指
    for k, ox in enumerate((60, 150, 225)):
        d.rounded_rectangle([tx + ox - 40, ty - 430 + k * 25, tx + ox + 50, ty - 300 + k * 25], radius=40, fill=255, outline=0, width=6)
    # 伸ばした人差し指と爪
    d.rounded_rectangle([tx - fw / 2, ty - 520, tx + fw / 2, ty], radius=fw / 2, fill=255, outline=0, width=7)
    d.arc([tx - fw / 2 + 8, ty - 330, tx + fw / 2 - 8, ty - 290], 200, 340, fill=0, width=4)  # 関節のしわ
    d.arc([tx - fw / 2 + 8, ty - 200, tx + fw / 2 - 8, ty - 160], 200, 340, fill=0, width=4)
    d.rounded_rectangle([tx - fw / 2 + 22, ty - 95, tx + fw / 2 - 22, ty - 18], radius=24, outline=0, width=5)  # 爪
    if not shake: return
    # 震え: 指の両わきの短い線と、汗
    for s in (-1, 1):
        for k in range(3):
            x = tx + s * (fw / 2 + 30 + k * 26); y0 = ty - 230 + k * 50
            d.line([(x, y0), (x + s * 8, y0 + 40), (x, y0 + 80)], fill=0, width=6)
    d.ellipse([tx + fw / 2 + 120, ty - 360, tx + fw / 2 + 150, ty - 315], outline=0, width=5)

def finger_cutout(path):
    from group_composite import cutout
    return cutout(path).convert("LA")

def p12_1(w=501, h=384):
    """投稿直後の画面。「投稿しました」、いいねは0"""
    im = canvas(w, h, 245); tone(im, 220, 12)
    (sw, sh), paste = phone(im, (w * K * 0.2, h * K * 0.04, w * K * 0.8, h * K * 1.2), angle=4)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    d.rounded_rectangle([20, 18, sw - 20, 84], radius=30, fill=0); d.text((sw / 2 - 100, 28), "✓ 投稿しました", font=F(30, True), fill=255)
    post_card(d, 24, 110, sw - 24, TITLE, likes="0", sz=0.92)
    paste(scr)
    return im

def p13_2(w=366, h=379):
    """夜の机の上のスマホ。投稿から数時間たっても、いいねは3"""
    im = canvas(w, h, 60); d = ImageDraw.Draw(im); W, H = im.size
    for y in range(0, H, 6): d.line([(0, y), (W, y + 30)], fill=40, width=2)  # 暗い机
    (sw, sh), paste = phone(im, (W * 0.2, H * 0.08, W * 0.8, H * 1.05), angle=-10)
    scr = Image.new("L", (sw, sh), 255); s = ImageDraw.Draw(scr)
    s.text((24, 12), "3時間前", font=F(26, True), fill=90)
    post_card(s, 20, 52, sw - 20, TITLE, likes="3", sz=0.75)
    heart(s, sw / 2 - 30, sh * 0.8, 48, fill=0, outline=0); s.text((sw / 2 + 30, sh * 0.8 - 46), "3", font=F(80, True), fill=0)
    paste(scr)
    return im

def p14_2(w=459, h=381):
    """通知が山のようにたまったスマホ"""
    im = canvas(w, h, 255); focus_lines(im, w * K / 2, h * K / 2, n=160, inner=0.28)
    (sw, sh), paste = phone(im, (w * K * 0.22, h * K * 0.02, w * K * 0.78, h * K * 1.25), angle=0)
    scr = Image.new("L", (sw, sh), 230); d = ImageDraw.Draw(scr)
    d.text((sw / 2 - 70, 20), "7:02", font=F(56, True), fill=0)
    msgs = ["さんがいいねしました", "さんがフォローしました", "さんがコメントしました", "さんがいいねしました", "さんが保存しました", "さんがいいねしました"]
    y = 110
    for k, m in enumerate(msgs):
        d.rounded_rectangle([12, y, sw - 12, y + 62], radius=14, fill=255, outline=0, width=2)
        d.text((24, y + 6), "CAPS公式", font=F(18, True), fill=0); d.text((24, y + 30), f"新入生{k + 1}{m}", font=F(18), fill=0); y += 72
    d.text((sw / 2 - 80, y + 4), "ほか 99+件", font=F(26, True), fill=0)
    paste(scr)
    return im

def p15_1(w=464, h=461):
    """インプレッション数が増えていく画面"""
    im = canvas(w, h, 255); focus_lines(im, w * K * 0.5, h * K * 0.5, n=120, inner=0.42, seed=3)
    d = ImageDraw.Draw(im); W, H = im.size
    x0, y0, x1, y1 = W * 0.1, H * 0.1, W * 0.9, H * 0.9
    d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=255, outline=0, width=6)
    d.text((x0 + 30, y0 + 24), "インプレッション", font=F(40, True), fill=0)
    vals = [("1,200", 0.1), ("5,800", 0.45), ("12,000", 0.95)]
    gx0, gy0, gx1, gy1 = x0 + 40, y0 + 110, x1 - 40, y1 - 200
    pts = [(gx0 + (gx1 - gx0) * k / 2, gy1 - (gy1 - gy0) * v) for k, (_, v) in enumerate(vals)]
    d.line([(gx0, gy1), (gx1, gy1)], fill=0, width=3); d.line(pts, fill=0, width=10)
    for (t, _), (px, py) in zip(vals, pts): d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=0)
    d.text((x0 + 30, y1 - 180), "1,200 → 5,800 →", font=F(42, True), fill=0)
    d.text((x0 + 30, y1 - 120), "12,000", font=F(92, True), fill=0)
    return im

def p15_2(w=462, h=484):
    """コメント欄"""
    im = canvas(w, h, 255); tone(im, 210, 12); d = ImageDraw.Draw(im); W, H = im.size
    x0, y0, x1 = W * 0.07, H * 0.05, W * 0.93
    d.rounded_rectangle([x0, y0, x1, H * 0.95], radius=30, fill=255, outline=0, width=6)
    d.text((x0 + 30, y0 + 20), "コメント 248件", font=F(38, True), fill=0)
    y = y0 + 100
    for c in ["これ新入生全員見て", "保存した", "先輩、神すぎる", "CAPSって何? 気になる"]:
        d.ellipse([x0 + 26, y, x0 + 86, y + 60], outline=0, width=4)
        d.rounded_rectangle([x0 + 100, y - 4, x1 - 26, y + 70], radius=20, fill=235)
        d.text((x0 + 120, y + 8), c, font=F(36, True), fill=0); y += 104
    return im

def p17_2(w=463, h=278):
    """イヅルのスマホの画面(いいねが大きく増えた投稿)"""
    im = canvas(w, h, 255); focus_lines(im, w * K / 2, h * K / 2, n=100, inner=0.35, seed=5)
    (sw, sh), paste = phone(im, (w * K * 0.1, h * K * 0.12, w * K * 0.9, h * K * 1.6), angle=-6)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    heart(d, 60, 70, 44, fill=0); d.text((120, 18), "3,481", font=F(84, True), fill=0)
    d.text((sw - 230, 44), "保存 912", font=F(40, True), fill=0)
    post_card(d, 24, 140, sw - 24, TITLE, sz=1.0)
    paste(scr)
    return im

def p07_4(w=430, h=269):
    """ノートパソコンの画面: 手描き風のイラストと図解が並ぶ、投稿のデザイン"""
    im = canvas(w, h, 255); tone(im, 215, 12); d = ImageDraw.Draw(im); W, H = im.size
    d.rounded_rectangle([W * 0.06, H * 0.06, W * 0.94, H * 1.02], radius=24, fill=30)
    x0, y0, x1, y1 = W * 0.1, H * 0.13, W * 0.9, H * 0.98
    d.rectangle([x0, y0, x1, y1], fill=255)
    pw = (x1 - x0 - 60) / 3
    for k, t in enumerate(["コツ1", "コツ2", "コツ3"]):
        px = x0 + 15 + k * (pw + 15)
        d.rectangle([px, y0 + 20, px + pw, y1 - 20], outline=0, width=4)
        d.text((px + 16, y0 + 32), t, font=F(30, True), fill=0)
        # 手描き風の小さなキャラ(丸い顔)と、矢印の図解
        cx, cy = px + pw / 2, y0 + 150
        d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], outline=0, width=4)
        d.ellipse([cx - 16, cy - 8, cx - 6, cy + 2], fill=0); d.ellipse([cx + 6, cy - 8, cx + 16, cy + 2], fill=0)
        d.arc([cx - 14, cy + 4, cx + 14, cy + 22], 20, 160, fill=0, width=3)
        for j in range(3):
            d.rounded_rectangle([px + 14, cy + 60 + j * 46, px + pw - 14, cy + 96 + j * 46], radius=8, outline=0, width=3)
    return im

def notebook(d, W, H, box, ideas, f, title_f, row_h, circle=None):
    """リングノートのページ。上に「ネタ帳」の見出し、下に番号つきのアイデアを2列で並べる"""
    nx0, ny0, nx1, ny1 = box
    d.rectangle([nx0, ny0, nx1, ny1], fill=255, outline=0, width=6)
    for k in range(int((ny1 - ny0) / 82) + 1): d.ellipse([nx0 - 18, ny0 + 40 + k * 82, nx0 + 18, ny0 + 64 + k * 82], outline=0, width=4)  # リング
    tw = d.textlength("ネタ帳", font=title_f); tx = (nx0 + nx1) / 2 - tw / 2
    d.rounded_rectangle([tx - 40, ny0 + 24, tx + tw + 40, ny0 + 24 + title_f.size * 1.5], radius=16, outline=0, width=5)
    d.text((tx, ny0 + 24 + title_f.size * 0.12), "ネタ帳", font=title_f, fill=0)
    top = ny0 + 24 + title_f.size * 1.5 + 40; per = (len(ideas) + 1) // 2
    for k, t in enumerate(ideas):
        col, row = (k // per, k % per) if len(ideas) > 3 else (0, k)
        x = nx0 + 60 + col * (nx1 - nx0) * 0.5; y = top + row * row_h
        d.line([(nx0 + 40, y + f.size * 1.5), (nx1 - 30, y + f.size * 1.5)], fill=190, width=2)
        d.text((x, y), f"{k + 1}. {t}", font=f, fill=0)
        if circle == k:  # 手描きの丸
            tl = d.textlength(f"{k + 1}. {t}", font=f)
            d.ellipse([x - 30, y - 22, x + tl + 30, y + f.size * 1.45], outline=0, width=7)

IDEAS = ["履修登録のコツ", "サークルの選び方", "空きコマの過ごし方", "学食ランキング", "図書館の使い方",
         "時間割の組み方", "教科書の買い方", "バイトとの両立", "先輩に聞きたいこと", "CAPSってどんなところ?"]

def p13_3(w=880, h=549):
    """ノート(ネタ帳)に、次の投稿のアイデアを書き出していく"""
    im = canvas(w, h, 200); d = ImageDraw.Draw(im); W, H = im.size
    for y in range(0, H, 9): d.line([(0, y), (W, y + 60)], fill=170, width=2)  # 机
    notebook(d, W, H, (W * 0.08, H * 0.03, W * 0.86, H * 1.05), IDEAS, F(48, True), F(64, True), 108)
    # ペン
    d.polygon([(W * 0.9, H * 0.97), (W * 1.02, H * 0.5), (W * 1.06, H * 0.53), (W * 0.93, H * 1.0)], fill=255, outline=0, width=6)
    d.polygon([(W * 0.9, H * 0.97), (W * 0.93, H * 1.0), (W * 0.89, H * 1.04)], fill=0)
    return im

def p18_4(w=880, h=357):
    """イヅルの手もとのネタ帳。「1. 履修登録のコツ」に丸がつく"""
    im = canvas(w, h, 200); d = ImageDraw.Draw(im); W, H = im.size
    for y in range(0, H, 9): d.line([(0, y), (W, y + 60)], fill=170, width=2)  # 机
    notebook(d, W, H, (W * 0.06, H * 0.04, W * 0.7, H * 1.1), IDEAS[:3], F(60, True), F(60, True), 130, circle=0)
    return im

# ---- 第3話(冒険サークル版)の画面のコマ ----
def messy(d, xy, text, f, jitter=6, seed=0, fill=0):
    """手書きの乱れた字(一文字ずつ少しずらし、傾ける)"""
    import random; rnd = random.Random(seed); x, y = xy
    for ch in text:
        im = Image.new("LA", (f.size * 2, f.size * 2), (0, 0)); ImageDraw.Draw(im).text((f.size // 2, f.size // 4), ch, font=f, fill=(fill, 255))
        im = im.rotate(rnd.uniform(-14, 14), resample=Image.BICUBIC)
        d._image.paste(im.getchannel(0), (int(x - f.size // 2), int(y + rnd.uniform(-jitter, jitter) - f.size // 4)), im.getchannel(1))
        x += d.textlength(ch, font=f) * rnd.uniform(0.95, 1.15)

def ep3_p04_1(w=940, h=410):
    """その場で書いた冒険許可書の申請書(字が乱れている)を、職員の手が受け取る"""
    im = canvas(w, h, 225); tone(im, 215, 12); d = ImageDraw.Draw(im); W, H = im.size
    x0, y0, x1, y1 = W * 0.18, H * 0.08, W * 0.82, H * 1.05
    d.polygon([(x0, y0 + 20), (x1, y0), (x1 + 20, y1), (x0 + 10, y1)], fill=255, outline=0)
    d.text((x0 + 60, y0 + 40), "冒険許可書 申請書", font=F(64, True), fill=0)
    rows = [("団体名", "勇者サークル"), ("代表者", "シロ"), ("入る層", "第3そう"), ("目的", "まおう とうばつ")]
    for k, (a, v) in enumerate(rows):
        y = y0 + 170 + k * 120
        d.text((x0 + 60, y), a, font=F(40, True), fill=0); d.line([(x0 + 260, y + 60), (x1 - 60, y + 60)], fill=0, width=3)
        messy(d, (x0 + 290, y - 4), v, F(52, True), seed=k)
    # 受け取る職員の手(袖と指先だけ、線で)
    d.rounded_rectangle([W * 0.82, H * 0.55, W * 1.02, H * 0.85], radius=40, fill=255, outline=0, width=6)
    for k in range(4): d.rounded_rectangle([W * 0.75, H * 0.55 + k * 70, W * 0.86, H * 0.55 + k * 70 + 56], radius=28, fill=255, outline=0, width=5)
    return im

def ep3_p09_3(w=457, h=322):
    """受付の机に置かれたメモ「先に帰ります」"""
    im = canvas(w, h, 200); d = ImageDraw.Draw(im); W, H = im.size
    for y in range(0, H, 10): d.line([(0, y), (W, y + 50)], fill=180, width=2)  # 机の木目
    d.polygon([(W * 0.2, H * 0.18), (W * 0.82, H * 0.12), (W * 0.86, H * 0.86), (W * 0.24, H * 0.9)], fill=255, outline=0)
    messy(d, (W * 0.3, H * 0.4), "先に帰ります", F(84, True), jitter=4, seed=3)
    return im

def ep3_p10_2(w=501, h=319):
    """公式SNSのログイン画面「パスワードが違います」"""
    im = canvas(w, h, 245); tone(im, 220, 12)
    (sw, sh), paste = phone(im, (w * K * 0.18, h * K * 0.04, w * K * 0.82, h * K * 1.3), angle=-5)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    d.text((30, 40), "勇者サークル 公式", font=F(34, True), fill=0)
    d.rounded_rectangle([30, 110, sw - 30, 170], radius=12, outline=0, width=3); d.text((46, 124), "yuusha_circle", font=F(26), fill=0)
    d.rounded_rectangle([30, 190, sw - 30, 250], radius=12, outline=0, width=3); d.text((46, 204), "●●●●●●", font=F(26), fill=0)
    d.rounded_rectangle([30, 280, sw - 30, 360], radius=14, fill=0); d.text((50, 296), "パスワードが違います", font=F(32, True), fill=255)
    paste(scr)
    return im

def ep3_p11_2(w=880, h=550, selfie=None):
    """シロの個人アカウントの投稿(キメ顔の自撮り+「第1層、余裕だった」)。いいね2、コメント2件"""
    im = canvas(w, h, 255); tone(im, 215, 12); d = ImageDraw.Draw(im); W, H = im.size
    x0, y0, x1, y1 = W * 0.16, H * 0.04, W * 0.84, H * 0.98
    d.rounded_rectangle([x0, y0, x1, y1], radius=30, fill=255, outline=0, width=6)
    d.ellipse([x0 + 30, y0 + 26, x0 + 96, y0 + 92], outline=0, width=4); d.text((x0 + 116, y0 + 36), "shiro_yuusha", font=F(34, True), fill=0)
    ix0, iy0, ix1, iy1 = x0 + 30, y0 + 120, x1 - 30, y0 + 120 + (x1 - x0 - 60) * 0.5
    if selfie:
        s = Image.open(selfie).convert("L"); r = max((ix1 - ix0) / s.width, (iy1 - iy0) / s.height)
        s = s.resize((int(s.width * r) + 1, int(s.height * r) + 1)); s = s.crop((0, 0, int(ix1 - ix0), int(iy1 - iy0))); im.paste(s, (int(ix0), int(iy0)))
    d.rectangle([ix0, iy0, ix1, iy1], outline=0, width=4)
    y = iy1 + 20
    d.text((ix0, y), "第1層、余裕だった", font=F(40, True), fill=0)
    heart(d, ix0 + 20, y + 84, 20, fill=None, outline=0); d.text((ix0 + 50, y + 62), "2", font=F(34, True), fill=0)
    for k, c in enumerate(["髪、なんかついてない?", "第1層で?"]):
        d.text((ix0, y + 130 + k * 56), f"・{c}", font=F(32), fill=0)
    return im

def ep3_p13_1(w=458, h=377):
    """アイミのスマホ。履修登録の投稿(インプレッション3.2万)。作成者の名前は、アイミの指に隠れて見えない"""
    im = canvas(w, h, 245); tone(im, 220, 12)
    (sw, sh), paste = phone(im, (w * K * 0.14, h * K * 0.04, w * K * 0.86, h * K * 1.25), angle=4)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    post_card(d, 24, 24, sw - 24, TITLE, sz=0.9)
    d.text((24, sh * 0.66), "インプレッション 3.2万", font=F(34, True), fill=0)
    paste(scr)
    d = ImageDraw.Draw(im); W, H = im.size
    # 作成者名を隠す指(線画)
    fx, fy = W * 0.36, H * 0.12
    d.rounded_rectangle([fx - 40, fy - 30, fx + 260, fy + 70], radius=50, fill=255, outline=0, width=6)
    d.rounded_rectangle([fx + 180, fy - 14, fx + 250, fy + 50], radius=20, outline=0, width=4)
    return im

def ep3_p17_2(w=880, h=169):
    """動画の画面の端の文字「〇〇大生の1日に密着してみた」"""
    im = canvas(w, h, 40); d = ImageDraw.Draw(im); W, H = im.size
    d.rectangle([0, 0, W, H], fill=40)
    d.rounded_rectangle([40, H * 0.2, W * 0.75, H * 0.8], radius=20, fill=255)
    d.text((80, H * 0.27), "〇〇大生の1日に密着してみた", font=F(78, True), fill=0)
    d.ellipse([W * 0.86, H * 0.3, W * 0.86 + 60, H * 0.3 + 60], fill=255); d.text((W * 0.86 + 80, H * 0.3), "REC", font=F(54, True), fill=255)
    return im

def ep3_p18_3(w=880, h=268):
    """イヅルの撮影メモ。何度も書き直した質問のリスト"""
    im = canvas(w, h, 200); d = ImageDraw.Draw(im); W, H = im.size
    for y in range(0, H, 9): d.line([(0, y), (W, y + 60)], fill=170, width=2)
    nx0, ny0, nx1 = W * 0.08, H * 0.06, W * 0.92
    d.rectangle([nx0, ny0, nx1, H * 1.05], fill=255, outline=0, width=5)
    d.text((nx0 + 40, ny0 + 16), "撮影メモ  質問リスト", font=F(46, True), fill=0)
    qs = [("好きな授業は?", True), ("今日のファッションを教えてください", False), ("今日の予定を教えてください", False), ("おすすめの学食は?", True)]
    for k, (q, cut) in enumerate(qs):
        y = ny0 + 100 + k * 92; col = k % 2
        x = nx0 + 40 + col * (nx1 - nx0) * 0.5; yy = ny0 + 100 + (k // 2) * 92
        d.text((x, yy), q, font=F(38, True), fill=0)
        if cut: d.line([(x - 6, yy + 26), (x + d.textlength(q, font=F(38, True)) + 6, yy + 26)], fill=0, width=5)  # 書き直した跡
    return im

ALL = {"p06_2": p06_2, "p11_2": p11_2, "p12_1": p12_1, "p13_2": p13_2, "p14_2": p14_2, "p15_1": p15_1, "p15_2": p15_2, "p17_2": p17_2, "p07_4": p07_4, "p13_3": p13_3, "p18_4": p18_4, "ep3_p04_1": ep3_p04_1, "ep3_p09_3": ep3_p09_3, "ep3_p10_2": ep3_p10_2, "ep3_p11_2": ep3_p11_2, "ep3_p13_1": ep3_p13_1, "ep3_p17_2": ep3_p17_2, "ep3_p18_3": ep3_p18_3}

# ---- 第4話 ----
def marker(d, xy, text, f, seed=0):
    """ホワイトボードのマーカーの手書き風(少しだけ揺らす)"""
    messy(d, xy, text, f, jitter=3, seed=seed)

def whiteboard(w, h):
    im = canvas(w, h, 150); d = ImageDraw.Draw(im); W, H = im.size
    d.rectangle([W * 0.04, H * 0.05, W * 0.96, H * 0.92], fill=255, outline=0, width=10)
    d.rectangle([W * 0.04, H * 0.92, W * 0.96, H * 0.96], fill=90)  # ペン置き
    return im, d, W, H

def ep4_p01_2(w=880, h=269):
    """ノートパソコンの動画編集の画面。書き出し完了"""
    im = canvas(w, h, 30); d = ImageDraw.Draw(im); W, H = im.size
    d.rectangle([W * 0.03, H * 0.08, W * 0.55, H * 0.7], fill=200)  # 映像のプレビュー
    d.rounded_rectangle([W * 0.05, H * 0.5, W * 0.53, H * 0.66], radius=12, fill=255)
    d.text((W * 0.07, H * 0.52), "〇〇大生の1日に密着してみた", font=F(40, True), fill=0)
    for k in range(3):  # タイムライン
        y = H * 0.76 + k * 34
        for j in range(6): d.rounded_rectangle([W * (0.03 + j * 0.155), y, W * (0.03 + j * 0.155 + 0.14), y + 24], radius=6, fill=120 + k * 30)
    d.rounded_rectangle([W * 0.6, H * 0.18, W * 0.97, H * 0.62], radius=20, fill=255)
    d.text((W * 0.63, H * 0.24), "書き出し完了", font=F(56, True), fill=0)
    d.line([(W * 0.66, H * 0.5), (W * 0.69, H * 0.56), (W * 0.75, H * 0.43)], fill=0, width=10)
    d.text((W * 0.78, H * 0.45), "100%", font=F(40, True), fill=0)
    return im

def ep4_p01_4(w=459, h=321):
    """「投稿する」ボタンに、まっすぐ伸びる指(今度は震えていない)"""
    im = canvas(w, h, 255); d = ImageDraw.Draw(im); W, H = im.size
    bx0, by0, bx1, by1 = W * 0.18, H * 0.66, W * 0.82, H * 0.92
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=int((by1 - by0) / 2), fill=0)
    t = "投稿する"; f = F(int((by1 - by0) * 0.5), True); tw = d.textlength(t, font=f)
    d.text(((bx0 + bx1) / 2 - tw / 2, by0 + (by1 - by0) * 0.16), t, font=f, fill=255)
    draw_finger(d, (bx0 + bx1) / 2, by0 + 10, H, shake=False)
    return im

def ep4_p02_4(w=880, h=637):
    """動画の画面。再生数2.4万回と、コメント"""
    im = canvas(w, h, 245); tone(im, 220, 12)
    (sw, sh), paste = phone(im, (w * K * 0.26, h * K * 0.03, w * K * 0.74, h * K * 1.12), angle=-3)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    d.rectangle([0, 0, sw, sh * 0.38], fill=60)
    d.polygon([(sw * 0.44, sh * 0.13), (sw * 0.44, sh * 0.25), (sw * 0.58, sh * 0.19)], fill=255)  # 再生ボタン
    d.text((24, sh * 0.41), "〇〇大生の1日に密着してみた", font=F(int(sw * 0.06), True), fill=0)
    d.text((24, sh * 0.48), "再生数 2.4万回", font=F(int(sw * 0.075), True), fill=0)
    d.line([(24, sh * 0.57), (sw - 24, sh * 0.57)], fill=150, width=3)
    for k, c in enumerate(["大学生活、楽しみになった", "次は理系の人も見たい", "出てみたい!"]):
        y = sh * 0.6 + k * sh * 0.12
        d.ellipse([24, y, 24 + sw * 0.08, y + sw * 0.08], outline=0, width=3)
        d.text((40 + sw * 0.1, y + 4), c, font=F(int(sw * 0.055), True), fill=0)
    paste(scr)
    return im

def storyboard(d, x0, y0, x1, y1, seed=0, crossed=True):
    """絵コンテ1枚(コマの枠と、手書きの線)"""
    import random; rnd = random.Random(seed)
    d.rectangle([x0, y0, x1, y1], fill=255, outline=0, width=4)
    fh = (y1 - y0 - 40) / 3
    for k in range(3):
        fy = y0 + 20 + k * fh
        d.rectangle([x0 + 20, fy, x0 + (x1 - x0) * 0.55, fy + fh - 14], outline=0, width=3)
        cx, cy = x0 + (x1 - x0) * 0.3, fy + fh * 0.45
        d.ellipse([cx - 20, cy - 26, cx + 20, cy + 14], outline=0, width=3); d.line([(cx, cy + 14), (cx, cy + 50)], fill=0, width=3)
        for j in range(3):
            ly = fy + 14 + j * 22; d.line([(x0 + (x1 - x0) * 0.6, ly), (x1 - 20 - rnd.uniform(0, 60), ly)], fill=0, width=3)
        if crossed and rnd.random() < 0.5:
            d.line([(x0 + (x1 - x0) * 0.6, fy + 10), (x1 - 30, fy + 70)], fill=0, width=4)  # 書き直した跡

def ep4_p04_2(w=880, h=474):
    """イヅルのカバンからのぞく、何度も書き直した撮影メモと絵コンテの束"""
    im = canvas(w, h, 210); d = ImageDraw.Draw(im); W, H = im.size
    for y in range(0, H, 10): d.line([(0, y), (W, y + 40)], fill=190, width=2)
    for k in range(5):  # 紙の束(少しずつずらす)
        ox = W * (0.2 + k * 0.05); oy = H * (0.05 + k * 0.03)
        storyboard(d, ox, oy, ox + W * 0.38, oy + H * 0.9, seed=k)
    d.text((W * 0.42, H * 0.08), "撮影メモ", font=F(48, True), fill=0)
    d.rounded_rectangle([W * 0.08, H * 0.55, W * 0.92, H * 1.2], radius=60, fill=60, outline=0, width=8)  # カバン
    d.line([(W * 0.08, H * 0.7), (W * 0.92, H * 0.7)], fill=20, width=8)
    return im

def ep4_p04_3(w=880, h=442):
    """絵コンテの束のアップ。ステータス表示の窓は page_compose が文字として重ねる"""
    im = canvas(w, h, 230); d = ImageDraw.Draw(im); W, H = im.size
    storyboard(d, W * 0.55, H * 0.06, W * 0.95, H * 1.1, seed=7)
    storyboard(d, W * 0.5, H * 0.1, W * 0.9, H * 1.15, seed=8)
    focus_lines(im, W * 0.35, H * 0.5, n=60, inner=0.45, seed=4)
    return im

def ep4_p09_2(w=880, h=847):
    """ホワイトボード。フェス/小学生の学習支援/大学生向けのアプリ"""
    im, d, W, H = whiteboard(w, h)
    for k, t in enumerate(["フェス", "小学生の学習支援", "大学生向けのアプリ"]):
        y = H * (0.16 + k * 0.25)
        d.ellipse([W * 0.12, y + 20, W * 0.12 + 40, y + 60], fill=0)
        marker(d, (W * 0.18, y), t, F(120, True), seed=k)
    return im

def ep4_p12_1(w=940, h=439):
    """会場の壁のポスター(架空のもの)"""
    im = canvas(w, h, 190); d = ImageDraw.Draw(im); W, H = im.size
    for x in range(0, W, 120): d.line([(x, 0), (x, H)], fill=175, width=3)  # 壁
    x0, y0, x1, y1 = W * 0.2, H * 0.05, W * 0.8, H * 0.97
    d.rectangle([x0, y0, x1, y1], fill=255, outline=0, width=6)
    d.text((x0 + 50, y0 + 40), "夏休み親子理科実験教室", font=F(78, True), fill=0)
    d.rounded_rectangle([x0 + 50, y0 + 160, x1 - 50, y0 + 250], radius=40, fill=0)
    d.text((x0 + 80, y0 + 172), "たった1.5時間で自由研究が完結!", font=F(54, True), fill=255)
    # くらげとばねの絵
    cx, cy = x0 + 200, y0 + 450
    d.pieslice([cx - 90, cy - 90, cx + 90, cy + 90], 180, 360, outline=0, width=6, fill=255)
    for k in range(5): d.line([(cx - 70 + k * 35, cy), (cx - 80 + k * 35, cy + 130)], fill=0, width=5)
    for k in range(10): d.arc([x1 - 420 + k * 30, cy - 30, x1 - 380 + k * 30, cy + 30], 0, 360, fill=0, width=5)
    d.text((x1 - 300, y1 - 90), "主催 CAPS", font=F(50, True), fill=0)
    return im

def ep4_p14_1(w=940, h=453):
    """新入生Cが手で描いた、アプリの画面の設計図"""
    im = canvas(w, h, 215); d = ImageDraw.Draw(im); W, H = im.size
    d.polygon([(W * 0.06, H * 0.06), (W * 0.94, H * 0.02), (W * 0.96, H * 0.98), (W * 0.04, H * 1.0)], fill=255, outline=0)
    f = F(40, True)
    px0, py0, px1, py1 = W * 0.1, H * 0.1, W * 0.42, H * 0.95  # 手描きのスマホの枠
    d.rounded_rectangle([px0, py0, px1, py1], radius=40, outline=0, width=5)
    messy(d, (px0 + 30, py0 + 30), "時間割", f, seed=1)
    for r in range(3):
        for c in range(4): d.rectangle([px0 + 30 + c * 60, py0 + 100 + r * 50, px0 + 80 + c * 60, py0 + 140 + r * 50], outline=0, width=3)
    d.rectangle([px0 + 90, py0 + 150, px0 + 140, py0 + 190], fill=0)  # 空きコマ
    messy(d, (px0 + 30, py0 + 280), "学内イベント", f, seed=2)
    for k in range(3): d.line([(px0 + 30, py0 + 360 + k * 50), (px1 - 40, py0 + 360 + k * 50)], fill=0, width=3)
    notes = [("← 空きコマが", 0.2), ("   ひと目で分かる", 0.3), ("← イベントも同じ画面に", 0.62)]
    for k, (t, yy) in enumerate(notes): messy(d, (W * 0.47, H * yy), t, F(52, True), seed=k + 5)
    return im

def ep4_p14_5(w=452, h=300):
    """スマホの画面「CAPSナビ リリースしました」"""
    im = canvas(w, h, 245); tone(im, 220, 12)
    (sw, sh), paste = phone(im, (w * K * 0.12, h * K * 0.03, w * K * 0.88, h * K * 1.4), angle=3)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    s = int(sw * 0.22); d.rounded_rectangle([sw / 2 - s / 2, 30, sw / 2 + s / 2, 30 + s], radius=s // 4, fill=0)
    d.text((sw / 2 - s * 0.28, 30 + s * 0.16), "C", font=F(int(s * 0.6), True), fill=255)
    t = "CAPSナビ"; f = F(int(sw * 0.1), True); d.text((sw / 2 - d.textlength(t, font=f) / 2, 50 + s), t, font=f, fill=0)
    d.rounded_rectangle([30, 90 + s + sw * 0.1, sw - 30, 90 + s + sw * 0.25], radius=20, fill=0)
    t = "リリースしました"; f = F(int(sw * 0.075), True); d.text((sw / 2 - d.textlength(t, font=f) / 2, 100 + s + sw * 0.12), t, font=f, fill=255)
    paste(scr)
    return im

def ep4_p15_1(w=940, h=617):
    """ホワイトボードいっぱいの「みんなの“想像”リスト」"""
    im, d, W, H = whiteboard(w, h)
    marker(d, (W * 0.1, H * 0.09), "みんなの“想像”リスト", F(84, True), seed=9)
    done = ["フェス", "小学生の学習支援", "大学生向けのアプリ"]
    todo = ["留学生との交流会", "学園祭で謎解き", "ゼミ紹介の動画", "1日密着 理系編", "みんなでボードゲーム会", "就活の先輩に聞く会"]
    for k, t in enumerate(done + todo):
        col, row = (0, k) if k < 5 else (1, k - 5)
        x = W * (0.1 + col * 0.45); y = H * (0.26 + row * 0.13)
        d.rectangle([x, y + 10, x + 46, y + 56], outline=0, width=6)
        if t in done: d.line([(x + 6, y + 30), (x + 20, y + 50), (x + 56, y)], fill=0, width=9)
        marker(d, (x + 66, y), t, F(52, True), seed=k + 20)
    return im

ALL.update({"ep4_p01_2": ep4_p01_2, "ep4_p01_4": ep4_p01_4, "ep4_p02_4": ep4_p02_4, "ep4_p04_2": ep4_p04_2, "ep4_p04_3": ep4_p04_3,
            "ep4_p09_2": ep4_p09_2, "ep4_p12_1": ep4_p12_1, "ep4_p14_1": ep4_p14_1, "ep4_p14_5": ep4_p14_5, "ep4_p15_1": ep4_p15_1})

# ---- 第5話 ----
def ep5_p06_2(w=880, h=474):
    """テーブルの上のイヅルの手に、椎菜の手がそっと重なる(袖口と手だけ、線画)"""
    im = canvas(w, h, 225); d = ImageDraw.Draw(im); W, H = im.size
    for y in range(0, H, 10): d.line([(0, y), (W, y + 30)], fill=205, width=2)  # テーブル
    # イヅルの手(左から。グレーのパーカーの袖)
    d.polygon([(-20, H * 0.45), (W * 0.36, H * 0.42), (W * 0.38, H * 0.82), (-20, H * 0.86)], fill=150, outline=0, width=6)
    for k in range(5): d.line([(W * (0.3 + k * 0.012), H * 0.43), (W * (0.3 + k * 0.012), H * 0.82)], fill=0, width=3)  # 袖のリブ
    d.rounded_rectangle([W * 0.36, H * 0.48, W * 0.62, H * 0.78], radius=70, fill=255, outline=0, width=6)  # 手の甲
    for k in range(4): d.rounded_rectangle([W * 0.58, H * (0.47 + k * 0.08), W * 0.72, H * (0.47 + k * 0.08) + 52], radius=26, fill=255, outline=0, width=5)
    # 椎菜の手(右上から。白いシャツの袖口)
    d.polygon([(W + 20, H * 0.05), (W * 0.7, H * 0.12), (W * 0.62, H * 0.42), (W + 20, H * 0.36)], fill=255, outline=0, width=6)
    d.line([(W * 0.71, H * 0.14), (W * 0.64, H * 0.4)], fill=0, width=5)  # カフス
    d.rounded_rectangle([W * 0.42, H * 0.34, W * 0.66, H * 0.6], radius=60, fill=255, outline=0, width=6)
    for k in range(4): d.rounded_rectangle([W * (0.33 + k * 0.035), H * 0.36, W * (0.33 + k * 0.035) + 44, H * 0.66], radius=22, fill=255, outline=0, width=5)
    for k in range(10):  # きらめき
        import random; rnd = random.Random(k); cx, cy, r = rnd.uniform(0.1, 0.95) * W, rnd.uniform(0.05, 0.3) * H, rnd.uniform(6, 14)
        d.line([(cx - r, cy), (cx + r, cy)], fill=0, width=3); d.line([(cx, cy - r), (cx, cy + r)], fill=0, width=3)
    return im

def ep5_p07_3(w=320, h=379):
    """これまでのイヅル: ネタ帳(第2話)"""
    im = canvas(w, h, 200); d = ImageDraw.Draw(im); W, H = im.size
    notebook(d, W, H, (W * 0.12, H * 0.04, W * 0.95, H * 1.02), IDEAS[:3], F(34, True), F(44, True), 110)
    return im

def ep5_p07_4(w=301, h=379):
    """これまでのイヅル: 何度も書き直した撮影メモ(第3話)"""
    im = canvas(w, h, 200); d = ImageDraw.Draw(im); W, H = im.size
    d.rectangle([W * 0.08, H * 0.04, W * 0.94, H * 1.02], fill=255, outline=0, width=5)
    d.text((W * 0.14, H * 0.07), "撮影メモ", font=F(46, True), fill=0)
    qs = [("好きな授業は?", True), ("今日のファッションは?", False), ("おすすめの学食は?", True), ("今日の予定は?", False), ("一言どうぞ", True)]
    for k, (q, cut) in enumerate(qs):
        y = H * (0.22 + k * 0.15); d.text((W * 0.14, y), q, font=F(32, True), fill=0)
        if cut: d.line([(W * 0.12, y + 22), (W * 0.14 + d.textlength(q, font=F(32, True)) + 8, y + 22)], fill=0, width=5)
    return im

def ep5_p11_4(w=453, h=300):
    """勇者サークルの公式SNS。最後の投稿は1年前のまま"""
    im = canvas(w, h, 245); tone(im, 220, 12)
    (sw, sh), paste = phone(im, (w * K * 0.12, h * K * 0.03, w * K * 0.88, h * K * 1.4), angle=-4)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    d.text((24, 24), "勇者サークル 公式", font=F(int(sw * 0.075), True), fill=0)
    d.text((24, 24 + sw * 0.1), "最後の投稿: 1年前", font=F(int(sw * 0.055)), fill=80)
    d.rectangle([24, 40 + sw * 0.18, sw - 24, 40 + sw * 0.6], fill=170)
    d.text((24, 60 + sw * 0.62), "冒険の記録 第3層到達!", font=F(int(sw * 0.065), True), fill=0)
    paste(scr)
    return im

def ep5_p12_2(w=454, h=276):
    """アイミの手描きの、ぐちゃぐちゃな地図"""
    import random; rnd = random.Random(5)
    im = canvas(w, h, 215); d = ImageDraw.Draw(im); W, H = im.size
    d.polygon([(W * 0.05, H * 0.1), (W * 0.93, H * 0.04), (W * 0.97, H * 0.95), (W * 0.08, H * 0.98)], fill=245, outline=0)
    x, y = W * 0.15, H * 0.8
    for k in range(40):  # 行ったり来たりする線
        nx, ny = x + rnd.uniform(-70, 90), y + rnd.uniform(-60, 50)
        nx, ny = min(max(nx, W * 0.12), W * 0.9), min(max(ny, H * 0.15), H * 0.88)
        d.line([(x, y), (nx, ny)], fill=0, width=4); x, y = nx, ny
    for k in range(5): d.text((rnd.uniform(0.2, 0.8) * W, rnd.uniform(0.2, 0.75) * H), "?", font=F(64, True), fill=0)
    messy(d, (W * 0.12, H * 0.12), "たぶんこっち", F(40, True), seed=2)
    return im

def credit_screen(w, h, title, body, angle, seed):
    im = canvas(w, h, 245); tone(im, 220, 12)
    (sw, sh), paste = phone(im, (w * K * 0.14, h * K * 0.03, w * K * 0.86, h * K * 1.4), angle=angle)
    scr = Image.new("L", (sw, sh), 255); d = ImageDraw.Draw(scr)
    d.rectangle([0, 0, sw, sh * 0.42], fill=150)
    body(d, sw, sh)
    d.text((20, sh * 0.45), title, font=F(int(sw * 0.065), True), fill=0)
    d.rounded_rectangle([sw * 0.38, sh * 0.56, sw - 16, sh * 0.56 + sw * 0.1], radius=10, fill=0)
    d.text((sw * 0.41, sh * 0.565), "企画・制作:イヅル", font=F(int(sw * 0.055), True), fill=255)
    paste(scr)
    return im

def ep5_p16_2(w=453, h=319):
    def body(d, sw, sh):
        for k in range(3): d.rounded_rectangle([20 + k * sw * 0.31, sh * 0.15, sw * 0.28 + k * sw * 0.31, sh * 0.35], radius=10, outline=0, width=3, fill=255)
    return credit_screen(w, h, "履修登録で失敗しない5つのコツ", body, 3, 1)

def ep5_p16_3(w=453, h=301):
    def body(d, sw, sh): d.polygon([(sw * 0.44, sh * 0.12), (sw * 0.44, sh * 0.3), (sw * 0.58, sh * 0.21)], fill=255)
    return credit_screen(w, h, "〇〇大生の1日に密着してみた", body, -3, 2)

def ep5_p16_4(w=453, h=300):
    def body(d, sw, sh):
        d.text((sw * 0.08, sh * 0.1), "CAPS", font=F(int(sw * 0.12), True), fill=0)
        d.text((sw * 0.08, sh * 0.22), "ENTERTAINMENT FES", font=F(int(sw * 0.075), True), fill=0)
    return credit_screen(w, h, "フェス開催のお知らせ", body, 2, 3)

def ep5_p16_5(w=452, h=300):
    def body(d, sw, sh):
        s = sw * 0.22; d.rounded_rectangle([sw / 2 - s / 2, sh * 0.08, sw / 2 + s / 2, sh * 0.08 + s], radius=s / 4, fill=0)
        d.text((sw / 2 - s * 0.25, sh * 0.08 + s * 0.12), "C", font=F(int(s * 0.6), True), fill=255)
    return credit_screen(w, h, "アプリ「CAPSナビ」", body, -2, 4)

def ep5_p19_1(w=940, h=559):
    """シロのスマホに届いた、勇者サークルのOBからのメッセージ"""
    im = canvas(w, h, 60); d0 = ImageDraw.Draw(im)
    (sw, sh), paste = phone(im, (w * K * 0.22, h * K * 0.03, w * K * 0.78, h * K * 1.3), angle=-3)
    scr = Image.new("L", (sw, sh), 240); d = ImageDraw.Draw(scr)
    d.rectangle([0, 0, sw, sh * 0.1], fill=255); d.text((24, sh * 0.025), "勇者サークル OB", font=F(int(sw * 0.05), True), fill=0)
    msg = ["去年は春のうちに第3層まで", "行ったのに、今年はまだ", "第1層だって?", "公式SNSも、全然", "更新されてないぞ。", "部長として、しっかりしろよ"]
    fs = int(sw * 0.048); bx1 = sw * 0.92
    d.rounded_rectangle([24, sh * 0.14, bx1, sh * 0.14 + fs * 1.5 * len(msg) + 40], radius=26, fill=255, outline=0, width=3)
    for k, t in enumerate(msg): d.text((48, sh * 0.14 + 20 + k * fs * 1.5), t, font=F(fs, True), fill=0)
    paste(scr)
    return im

ALL.update({"ep5_p06_2": ep5_p06_2, "ep5_p07_3": ep5_p07_3, "ep5_p07_4": ep5_p07_4, "ep5_p11_4": ep5_p11_4, "ep5_p12_2": ep5_p12_2,
            "ep5_p16_2": ep5_p16_2, "ep5_p16_3": ep5_p16_3, "ep5_p16_4": ep5_p16_4, "ep5_p16_5": ep5_p16_5, "ep5_p19_1": ep5_p19_1})

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    args = sys.argv[1:]; finger = None
    if "--finger" in args: i = args.index("--finger"); finger = args[i + 1]; del args[i:i + 2]
    out = args[0]; names = args[1:] or list(ALL); os.makedirs(out, exist_ok=True)
    for n in names:
        im = ALL[n](finger=finger) if n == "p11_2" else ALL[n]()
        im.save(os.path.join(out, f"{n}_ui.png")); print(f"{n} を描きました")
