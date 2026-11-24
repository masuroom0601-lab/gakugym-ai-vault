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

def draw_finger(d, tx, ty, H):
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

ALL = {"p06_2": p06_2, "p11_2": p11_2, "p12_1": p12_1, "p13_2": p13_2, "p14_2": p14_2, "p15_1": p15_1, "p15_2": p15_2, "p17_2": p17_2, "p07_4": p07_4, "p13_3": p13_3, "p18_4": p18_4}

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    args = sys.argv[1:]; finger = None
    if "--finger" in args: i = args.index("--finger"); finger = args[i + 1]; del args[i:i + 2]
    out = args[0]; names = args[1:] or list(ALL); os.makedirs(out, exist_ok=True)
    for n in names:
        im = ALL[n](finger=finger) if n == "p11_2" else ALL[n]()
        im.save(os.path.join(out, f"{n}_ui.png")); print(f"{n} を描きました")
