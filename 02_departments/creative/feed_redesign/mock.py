import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
OUT = os.path.dirname(os.path.abspath(__file__))
AV = "/home/user/gakugym-ai-vault/02_departments/creative/reel_quiz/avatar_eiken.png"
ND = "/usr/share/fonts/opentype/noto/"
BLACK, CREAM, RED, INK, GRAY, LINE = "#141414", "#f7f3ea", "#d7261e", "#151515", "#5b5b5b", "#d9d2c3"


def F(s, w="Black"): return ImageFont.truetype(ND + f"NotoSansCJK-{w}.ttc", s)
def S(s, w="Bold"): return ImageFont.truetype(ND + f"NotoSerifCJK-{w}.ttc", s)


def avatar(size, ring=None):
    im = Image.open(AV).convert("RGB").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size)); out.paste(im, (0, 0), m)
    if ring:
        ImageDraw.Draw(out).ellipse((2, 2, size - 3, size - 3), outline=ring, width=6)
    return out


def grain(im, amt=10):
    random.seed(1)
    n = Image.effect_noise(im.size, amt).convert("L")
    return Image.blend(im, Image.merge("RGB", (n, n, n)), 0.05)


# ---------- A: 一覧型(受験の王様の型) ----------
def a_cover():
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
    d.rectangle((70, 90, 80, 160), fill=RED)
    d.text((105, 125), "今週のクイズ、全部わかる？", font=S(52), fill=CREAM, anchor="lm")
    d.text((70, 270), "英検", font=F(210), fill=CREAM, anchor="lm")
    d.text((70, 500), "頻出語", font=F(210), fill=CREAM, anchor="lm")
    d.text((60, 790), "7", font=F(430), fill=RED, anchor="lm")
    d.text((330, 900), "問", font=F(200), fill=CREAM, anchor="lm")
    d.text((570, 830), "1週間で\n解いた", font=F(64, "Bold"), fill=CREAM, spacing=12)
    d.line((70, 1090, 1010, 1090), fill=RED, width=6)
    d.text((70, 1170), "保存して、週末の復習に。", font=S(58), fill=CREAM, anchor="lm")
    im.paste(av := avatar(150, RED), (880, 1110), av)
    d.text((70, 1275), "@massu_gakugym", font=F(30, "Bold"), fill="#9a9a9a", anchor="lm")
    return grain(im)


ROWS = [("postpone", "延期する", "準2+"), ("quiet", "静かな", "3級"), ("hungry", "おなかがすいた", "3級"),
        ("afford", "〜する余裕がある", "準2"), ("highest", "一番高い", "3級"),
        ("tarnish", "傷つける・汚す", "準1"), ("remind", "思い出させる", "2級")]


def a_inner():
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    d.text((60, 95), "今週の", font=F(64), fill=INK, anchor="lm")
    d.text((262, 95), "7", font=F(80), fill=RED, anchor="lm")
    d.text((320, 95), "問まとめ", font=F(64), fill=INK, anchor="lm")
    d.line((870, 60, 870, 130), fill=LINE, width=3)
    d.text((1020, 95), "01 / 01", font=F(34, "Bold"), fill=INK, anchor="rm")
    d.line((50, 160, 1030, 160), fill=LINE, width=3)
    top, rh = 195, 130
    d.rectangle((50, top, 1030, top + rh * 7), outline=LINE, width=3)
    for i, (en, ja, lv) in enumerate(ROWS):
        y = top + i * rh
        d.rectangle((50, y, 165, y + rh), fill=RED)
        d.text((107, y + rh // 2), str(i + 1), font=F(58, "Bold"), fill="white", anchor="mm")
        if i: d.line((165, y, 1030, y), fill=LINE, width=3)
        d.text((195, y + rh // 2), en, font=F(56, "Bold"), fill=INK, anchor="lm")
        d.text((520, y + rh // 2), ja, font=F(42, "Bold"), fill=GRAY, anchor="lm")
        d.rounded_rectangle((900, y + 40, 1005, y + rh - 40), 10, outline=RED, width=3)
        d.text((952, y + rh // 2), lv, font=F(30, "Bold"), fill=RED, anchor="mm")
    d.line((50, 1150, 1030, 1150), fill=LINE, width=3)
    d.text((60, 1235), "わからなかった", font=F(46, "Bold"), fill=INK, anchor="lm")
    d.text((400, 1235), "1", font=F(64), fill=RED, anchor="lm")
    d.text((445, 1235), "語だけ覚えよう。", font=F(46, "Bold"), fill=INK, anchor="lm")
    im.paste(av := avatar(120), (920, 1175), av)
    return grain(im)


# ---------- B: 実話型(ライムの型) ----------
BLUE = "#2f7fd6"


def paren(d, box, txt, font):
    _, y0, _, y1 = box
    w = d.textlength(txt, font=font)
    x0, x1 = int(W / 2 - w / 2 - 40), int(W / 2 + w / 2 + 40)
    d.arc((x0 - 40, y0, x0 + 60, y1), 110, 250, fill=INK, width=9)
    d.arc((x1 - 60, y0, x1 + 40, y1), 290, 70, fill=INK, width=9)
    d.text(((x0 + x1) // 2, (y0 + y1) // 2), txt, font=font, fill=INK, anchor="mm")


def bullets(d, y, items, size=44):
    for t in items:
        d.text((150, y), "・" + t, font=F(size, "Medium"), fill=GRAY, anchor="lm"); y += 82
    return y


def b_cover():
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.text((W // 2, 250), "＼ガチの実話／", font=F(60), fill=INK, anchor="mm")
    d.text((W // 2, 420), "学年最下位・0点の僕が", font=F(78), fill=INK, anchor="mm")
    d.text((W // 2, 540), "偏差値66になるまで", font=F(92), fill=INK, anchor="mm")
    for y in (600,):
        d.line((150, y, 930, y + 6), fill=BLUE, width=9)
    # 46→66 の数字を絵の代わりに
    d.text((300, 860), "46", font=F(230), fill="#b9b9b9", anchor="mm")
    d.text((540, 860), "→", font=F(150), fill=INK, anchor="mm")
    d.text((790, 860), "66", font=F(230), fill=RED, anchor="mm")
    d.text((W // 2, 1040), "模試の偏差値", font=F(44, "Bold"), fill=GRAY, anchor="mm")
    d.text((W // 2, 1180), "＼やる気に頼らなくても変われる／", font=F(44, "Bold"), fill=INK, anchor="mm")
    im.paste(av := avatar(110), (60, 1200), av)
    d.text((190, 1255), "@massu_gakugym", font=F(30, "Bold"), fill="#9a9a9a", anchor="lm")
    return im


def b_inner():
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    paren(d, (170, 140, 910, 290), "定期考査で0点", F(84))
    d.text((W // 2, 640), "0", font=F(420), fill=RED, anchor="mm")
    d.text((700, 750), "点", font=F(120), fill=INK, anchor="mm")
    d.line((330, 830, 760, 830), fill=BLUE, width=8)
    y = bullets(d, 930, ["学年順位は最下位", "定期考査のある科目で0点", "スマホを触って1日が終わる"])
    d.text((150, y + 40), "勉強が続かないのは、意志が弱い", font=F(44, "Medium"), fill=GRAY, anchor="lm")
    d.text((150, y + 115), "からだと思っていた。", font=F(44, "Medium"), fill=GRAY, anchor="lm")
    return im


def b_proof():
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    paren(d, (230, 140, 850, 290), "こんな状況から…", F(84))
    d.rounded_rectangle((140, 380, 940, 860), 24, fill="#f1f1f1", outline="#cfcfcf", width=4)
    d.text((W // 2, 590), "合格通知の写真", font=F(56, "Bold"), fill="#9a9a9a", anchor="mm")
    d.text((W // 2, 660), "（名前などはぼかす）", font=F(36, "Medium"), fill="#9a9a9a", anchor="mm")
    y = bullets(d, 960, ["模試の偏差値 46 → 66", "法政大学・中央大学に合格", "やったのは「仕組み」を作ることだけ"])
    d.text((150, y + 50), "意志の力を捨てたら、勉強が続いた。", font=F(44, "Medium"), fill=GRAY, anchor="lm")
    return im


if __name__ == "__main__":
    pages = {"A1_cover": a_cover(), "A2_inner": a_inner(), "B1_cover": b_cover(), "B2_inner": b_inner(), "B3_proof": b_proof()}
    for k, im in pages.items():
        im.save(os.path.join(OUT, k + ".png"))
    sheet = Image.new("RGB", (W * 2 + 40, H), "#888")
    sheet.paste(pages["A1_cover"], (0, 0)); sheet.paste(pages["A2_inner"], (W + 40, 0))
    sheet.resize(((W * 2 + 40) // 2, H // 2)).save(os.path.join(OUT, "A_sheet.jpg"), quality=90)
    sheet = Image.new("RGB", (W * 3 + 80, H), "#888")
    for i, k in enumerate(["B1_cover", "B2_inner", "B3_proof"]):
        sheet.paste(pages[k], (i * (W + 40), 0))
    sheet.resize(((W * 3 + 80) // 2, H // 2)).save(os.path.join(OUT, "B_sheet.jpg"), quality=90)
