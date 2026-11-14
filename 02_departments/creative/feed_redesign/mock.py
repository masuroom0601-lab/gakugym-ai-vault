import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1350
OUT = os.path.dirname(os.path.abspath(__file__))
AV = "/home/user/gakugym-ai-vault/02_departments/creative/reel_quiz/avatar.png"
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
def a_cover(kicker, l1, l2, num, unit, sub, foot, handle, acc):
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
    d.rectangle((70, 90, 80, 160), fill=acc)
    d.text((105, 125), kicker, font=S(52), fill=CREAM, anchor="lm")
    def fit(t, mx, w=940):
        z = mx
        while d.textlength(t, font=F(z)) > w: z -= 4
        return F(z)
    tf = fit(l2 if len(l2) > len(l1) else l1, 180)
    d.text((70, 280), l1, font=tf, fill=CREAM, anchor="lm")
    d.text((70, 490), l2, font=tf, fill=CREAM, anchor="lm")
    nf = F(360)
    d.text((60, 800), num, font=nf, fill=acc, anchor="lm")
    x = 60 + d.textlength(num, font=nf) + 20
    d.text((x, 900), unit, font=F(200), fill=CREAM, anchor="lm")
    d.text((x + 225, 840), sub, font=F(52, "Bold"), fill=CREAM, spacing=12)
    d.line((70, 1090, 1010, 1090), fill=acc, width=6)
    d.text((70, 1170), foot, font=S(58), fill=CREAM, anchor="lm")
    im.paste(av := avatar(150, acc), (880, 1110), av)
    d.text((70, 1275), handle, font=F(30, "Bold"), fill="#9a9a9a", anchor="lm")
    return grain(im)


def a_inner(title_parts, rows, page, foot_parts, acc):
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
    x = 60
    tot = sum(d.textlength(t, font=F(sz)) for t, c, sz in title_parts)
    k = min(1.0, 790 / tot)
    title_parts = [(t, c, int(sz * k)) for t, c, sz in title_parts]
    for t, c, sz in title_parts:
        f = F(sz); d.text((x, 95), t, font=f, fill=acc if c else INK, anchor="lm"); x += d.textlength(t, font=f)
    d.line((880, 60, 880, 130), fill=LINE, width=3)
    d.text((1020, 95), page, font=F(34, "Bold"), fill=INK, anchor="rm")
    d.line((50, 160, 1030, 160), fill=LINE, width=3)
    top, rh = 190, 95
    d.rectangle((50, top, 1030, top + rh * len(rows)), outline=LINE, width=3)
    for i, (n, t) in enumerate(rows):
        y = top + i * rh
        d.rectangle((50, y, 160, y + rh), fill=acc)
        d.text((105, y + rh // 2), str(n), font=F(48, "Bold"), fill="white", anchor="mm")
        if i: d.line((160, y, 1030, y), fill=LINE, width=3)
        d.text((190, y + rh // 2), t, font=F(46, "Bold"), fill=INK, anchor="lm")
    d.line((50, 1175, 1030, 1175), fill=LINE, width=3)
    x = 60
    for t, c in foot_parts:
        f = F(64) if c else F(46, "Bold")
        d.text((x, 1250), t, font=f, fill=acc if c else INK, anchor="lm"); x += d.textlength(t, font=f) + 6
    im.paste(av := avatar(120), (920, 1195), av)
    return grain(im)


SUMAHO = ["起きてすぐスマホを見ない", "勉強中のスマホは別の部屋へ", "通知はぜんぶオフにする", "最初の5分だけやると決める",
          "勉強する時間と場所を固定する", "25分やったら5分休む", "休憩中もスマホは触らない", "やったことを1行だけ記録する",
          "寝る1時間前にスマホを手放す", "できなかった日も自分を責めない"]
SOUGOU = ["志望理由が「憧れ」で終わっている", "パンフレットの言葉をそのまま使う", "大学で学びたいことがぼんやり",
          "自分の経験と志望がつながらない", "卒業後の目標が書かれていない", "アドミッション・ポリシーを読まない",
          "字数の半分を自己紹介に使う", "「〜したいと思います」が多い", "先生に一度も読んでもらっていない",
          "締切の前日に書き始める"]
NAVY = "#2a5bb8"


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
    d.text((190, 1255), "@massu_smartphone", font=F(30, "Bold"), fill="#9a9a9a", anchor="lm")
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
    pages = {
        "S_A1_cover": a_cover("スマホに負けて1日が終わる君へ。", "スマホに勝つ", "勉強ルーティン", "10", "選",
                              "今日から\nひとつだけ", "保存して、今夜からひとつ。", "@massu_smartphone", RED),
        "S_A2_inner": a_inner([("スマホに勝つ勉強ルーティン", 0, 52), ("10", 1, 64), ("選", 0, 52)],
                              list(enumerate(SUMAHO, 1)), "01 / 01", [("できる", 0), ("1", 1), ("つを、今夜から。", 0)], RED),
        "G_A1_cover": a_cover("総合型選抜を受ける君へ。", "志望理由書で", "落ちる人の特徴", "10", "選",
                              "出す前に\nチェック", "保存して、提出前に見返そう。", "@（総合型アカウント）", NAVY),
        "G_A2_inner": a_inner([("志望理由書で落ちる人の特徴", 0, 52), ("10", 1, 64), ("選", 0, 52)],
                              list(enumerate(SOUGOU, 1)), "01 / 01", [("当てはまったら", 0), ("1", 1), ("つずつ直そう。", 0)], NAVY),
        "S_B1_cover": b_cover(), "S_B2_inner": b_inner(), "S_B3_proof": b_proof(),
    }
    for k, im in pages.items():
        im.save(os.path.join(OUT, k + ".png"))
    for name, keys in {"sheet_sumaho_list": ["S_A1_cover", "S_A2_inner"], "sheet_sougou_list": ["G_A1_cover", "G_A2_inner"],
                       "sheet_sumaho_story": ["S_B1_cover", "S_B2_inner", "S_B3_proof"]}.items():
        sh = Image.new("RGB", (len(keys) * (W + 40) - 40, H), "#888")
        for i, k in enumerate(keys):
            sh.paste(pages[k], (i * (W + 40), 0))
        sh.resize((sh.width // 2, H // 2)).save(os.path.join(OUT, name + ".jpg"), quality=90)
