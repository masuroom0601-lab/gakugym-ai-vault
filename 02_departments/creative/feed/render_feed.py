#!/usr/bin/env python3
"""②総合型・③スマホ対策アカウントのフィード(カルーセル)画像を台本から描く(2026-11-14追加)。

デザインは 2026-11-14 に益田さんと決めた形(受験の王様・ライム@早慶逆転塾を参考にした一覧型/実話型)。
AI画像は使わず、文字と図形だけで描く。人物はまっすーのアイコン(reel_quiz/avatar.png)だけ。

台本: <部署>/drafts/feed-<日付>-001.md の「## スライド」節にある ```json のリスト。
使い方: python3 render_feed.py <台本md> <出力フォルダ>
  → 出力フォルダに 01.png, 02.png ... (1080x1350) を書き出す

スライドの種類(type)と項目:
  cover    : kicker, line1, line2, num, unit, sub, foot          … 黒地の表紙(一覧型)
  table    : title, rows[](最大10)                                … 番号付きの表。番号は通しで自動、ページ番号も自動
  points   : title, items[{title, sub}](最大3)                   … 番号+見出し+補足を3つ(「迷ったらこの3つ」など)
  scover   : kicker, line1, line2, from, to, label, tagline     … 白地の表紙(実話型)。from→to を大きく
  scene    : heading, big, unit, bullets[](最大3), body         … 実話の1場面
  proof    : heading, bullets[], body                            … 証拠(assets/proof.jpg があれば写真を載せる)
  quote    : text, by                                            … 紙の質感の地に一言
  end      : title, lines[]                                      … 締め(保存・フォローのお願い)
文字の中の **…** はアクセント色(③赤・②青)になる。
"""
import json, os, re, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))
AVATAR = os.path.join(HERE, "..", "reel_quiz", "avatar.png")
PROOF = os.path.join(HERE, "assets", "proof.jpg")
FONT_DIRS = ["/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/noto"]
BLACK, CREAM, INK, GRAY, LINE, PAPER = "#141414", "#f7f3ea", "#151515", "#5b5b5b", "#d9d2c3", "#ececea"
LINE_BLUE = "#2f7fd6"
ACCOUNTS = {  # 部署フォルダ名 → アクセント色・アカウント名
    "sumaho_habit": {"acc": "#d7261e", "handle": "@massu_smartphone"},
    "sougou": {"acc": "#2a5bb8", "handle": "@gakugym_sougougata"},
}
LIMITS = {"list": (6, 10), "story": (7, 10)}  # 一覧型は6〜10枚、実話型は7〜10枚(2026-11-14 益田さん決定)


def _font(kind, w, s):
    for d in FONT_DIRS:
        p = os.path.join(d, f"Noto{kind}CJK-{w}.ttc")
        if os.path.exists(p):
            return ImageFont.truetype(p, s)
    sys.exit("フォントがありません(apt-get install fonts-noto-cjk fonts-noto-cjk-extra)")


def F(s, w="Black"): return _font("Sans", w, s)
def S(s, w="Bold"): return _font("Serif", w, s)


def segs(text):
    """'スマホに勝つ**30**選' → [('スマホに勝つ',False),('30',True),('選',False)]"""
    parts = re.split(r"\*\*(.+?)\*\*", text)
    return [(p, i % 2 == 1) for i, p in enumerate(parts) if p]


def plain(text): return text.replace("**", "")


def draw_rich(d, xy, text, font, color, acc, anchor="l", accfont=None):
    """**…** をアクセント色で描く。anchor は l(左揃え)か m(中央揃え)。縦は中央"""
    sg = segs(text)
    fs = [(t, accfont if (a and accfont) else font, acc if a else color) for t, a in sg]
    tw = sum(d.textlength(t, font=f) for t, f, _ in fs)
    x, y = xy
    if anchor == "m": x -= tw / 2
    for t, f, c in fs:
        d.text((x, y), t, font=f, fill=c, anchor="lm"); x += d.textlength(t, font=f)
    return tw


def fit(d, text, maxsize, width, w="Black", mk=F):
    s = maxsize
    while s > 24 and d.textlength(plain(text), font=mk(s, w)) > width:
        s -= 2
    return mk(s, w)


def avatar(size, ring=None):
    im = Image.open(AVATAR).convert("RGB").resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size)); out.paste(im, (0, 0), m)
    if ring: ImageDraw.Draw(out).ellipse((2, 2, size - 3, size - 3), outline=ring, width=6)
    return out


def grain(im):
    n = Image.effect_noise(im.size, 10).convert("L")
    return Image.blend(im, Image.merge("RGB", (n, n, n)), 0.05)


NO_HEAD = "。、，．）」』！？…ー々ぁぃぅぇぉっゃゅょァィゥェォッャュョ"


def wrap_ja(d, text, font, width):
    """日本語を幅で折り返す。句読点や小さい「っ」などが行頭に来ないよう前の行に入れる(行頭禁則)"""
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > width and cur and ch not in NO_HEAD:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines


# ---------------- 一覧型 ----------------
def cover(s, A):
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im); acc = A["acc"]
    d.rectangle((70, 90, 80, 160), fill=acc)
    d.text((105, 125), s["kicker"], font=fit(d, s["kicker"], 52, 900, "Bold", S), fill=CREAM, anchor="lm")
    tf = fit(d, max(s["line1"], s["line2"], key=lambda t: len(plain(t))), 180, 940)
    draw_rich(d, (70, 280), s["line1"], tf, CREAM, acc)
    draw_rich(d, (70, 490), s["line2"], tf, CREAM, acc)
    nf = F(360) if len(s["num"]) <= 2 else F(280)
    d.text((60, 800), s["num"], font=nf, fill=acc, anchor="lm")
    x = 60 + d.textlength(s["num"], font=nf) + 20
    d.text((x, 900), s["unit"], font=F(200), fill=CREAM, anchor="lm")
    if s.get("sub"):
        d.text((x + 225, 840), s["sub"].replace("\\n", "\n"), font=F(52, "Bold"), fill=CREAM, spacing=12)
    d.line((70, 1090, 1010, 1090), fill=acc, width=6)
    d.text((70, 1170), s["foot"], font=fit(d, s["foot"], 58, 780, "Bold", S), fill=CREAM, anchor="lm")
    im.paste(av := avatar(150, acc), (880, 1110), av)
    d.text((70, 1275), A["handle"], font=F(30, "Bold"), fill="#9a9a9a", anchor="lm")
    return grain(im)


def header(d, title, page, acc):
    f = fit(d, title, 56, 790); draw_rich(d, (60, 95), title, f, INK, acc)
    d.line((880, 60, 880, 130), fill=LINE, width=3)
    d.text((1020, 95), page, font=F(34, "Bold"), fill=INK, anchor="rm")
    d.line((50, 160, 1030, 160), fill=LINE, width=3)


def footer(im, d, text, acc):
    d.line((50, 1175, 1030, 1175), fill=LINE, width=3)
    draw_rich(d, (60, 1250), text, fit(d, text, 46, 820, "Bold"), INK, acc, accfont=F(60))
    im.paste(av := avatar(120), (920, 1195), av)


def table(s, A, start, page):
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im); acc = A["acc"]
    header(d, s["title"], page, acc)
    rows = s["rows"]; top, rh = 190, 95
    d.rectangle((50, top, 1030, top + rh * len(rows)), outline=LINE, width=3)
    for i, t in enumerate(rows):
        y = top + i * rh
        d.rectangle((50, y, 160, y + rh), fill=acc)
        d.text((105, y + rh // 2), str(start + i), font=F(48 if start + i < 100 else 40, "Bold"), fill="white", anchor="mm")
        if i: d.line((160, y, 1030, y), fill=LINE, width=3)
        draw_rich(d, (190, y + rh // 2), t, fit(d, t, 46, 820, "Bold"), INK, acc)
    footer(im, d, s.get("foot", "できる**1**つを、今日から。"), acc)
    return grain(im)


def points(s, A, page):
    im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im); acc = A["acc"]
    header(d, s["title"], page, acc)
    y = 230
    for i, it in enumerate(s["items"][:3], 1):
        d.rounded_rectangle((60, y, 170, y + 110), 14, fill=acc)
        d.text((115, y + 55), f"{i:02d}", font=F(56, "Bold"), fill="white", anchor="mm")
        draw_rich(d, (200, y + 40), it["title"], fit(d, it["title"], 62, 800), INK, acc)
        for k, ln in enumerate(wrap_ja(d, it.get("sub", ""), F(40, "Medium"), 800)[:2]):
            d.text((200, y + 115 + k * 56), ln, font=F(40, "Medium"), fill=GRAY, anchor="lm")
        y += 300
        if i < 3: d.line((60, y - 50, 1020, y - 50), fill=LINE, width=3)
    footer(im, d, s.get("foot", "まずは**1**つだけ、試してみよう。"), acc)
    return grain(im)


def end(s, A):
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im); acc = A["acc"]
    im.paste(av := avatar(260, acc), ((W - 260) // 2, 230), av)
    draw_rich(d, (W // 2, 620), s["title"], fit(d, s["title"], 96, 940), CREAM, acc, anchor="m")
    y = 760
    for ln in s.get("lines", [])[:4]:
        draw_rich(d, (W // 2, y), ln, fit(d, ln, 50, 900, "Bold", S), CREAM, acc, anchor="m"); y += 90
    d.rounded_rectangle((190, 1120, 890, 1230), 55, fill=acc)
    d.text((W // 2, 1175), "保存　＆　フォロー", font=F(52), fill="white", anchor="mm")
    d.text((W // 2, 1285), A["handle"], font=F(32, "Bold"), fill="#9a9a9a", anchor="mm")
    return grain(im)


# ---------------- 実話型 ----------------
def paren(d, y0, y1, text, font):
    w = d.textlength(plain(text), font=font)
    x0, x1 = int(W / 2 - w / 2 - 40), int(W / 2 + w / 2 + 40)
    d.arc((x0 - 40, y0, x0 + 60, y1), 110, 250, fill=INK, width=9)
    d.arc((x1 - 60, y0, x1 + 40, y1), 290, 70, fill=INK, width=9)


def bullets(d, y, items, acc):
    for t in items[:3]:
        draw_rich(d, (150, y), "・" + t, fit(d, "・" + t, 44, 840, "Medium"), GRAY, acc); y += 82
    return y


def body(d, y, text):
    for ln in wrap_ja(d, text, F(44, "Medium"), 800)[:3]:
        d.text((150, y), ln, font=F(44, "Medium"), fill=GRAY, anchor="lm"); y += 66
    return y


def scover(s, A):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im); acc = A["acc"]
    d.text((W // 2, 250), "＼" + s.get("kicker", "ガチの実話") + "／", font=F(60), fill=INK, anchor="mm")
    draw_rich(d, (W // 2, 420), s["line1"], fit(d, s["line1"], 78, 940), INK, acc, anchor="m")
    draw_rich(d, (W // 2, 540), s["line2"], fit(d, s["line2"], 92, 940), INK, acc, anchor="m")
    d.line((150, 600, 930, 606), fill=LINE_BLUE, width=9)
    if s.get("from") and s.get("to"):
        d.text((300, 860), s["from"], font=fit(d, s["from"], 230, 330), fill="#b9b9b9", anchor="mm")
        d.text((540, 860), "→", font=F(150), fill=INK, anchor="mm")
        d.text((790, 860), s["to"], font=fit(d, s["to"], 230, 330), fill=acc, anchor="mm")
        d.text((W // 2, 1040), s.get("label", ""), font=F(44, "Bold"), fill=GRAY, anchor="mm")
    d.text((W // 2, 1180), "＼" + s.get("tagline", "") + "／", font=fit(d, s.get("tagline", ""), 44, 860, "Bold"), fill=INK, anchor="mm")
    im.paste(av := avatar(110), (60, 1200), av)
    d.text((190, 1255), A["handle"], font=F(30, "Bold"), fill="#9a9a9a", anchor="lm")
    return im


def scene(s, A):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im); acc = A["acc"]
    hf = fit(d, s["heading"], 84, 760); paren(d, 140, 290, s["heading"], hf)
    draw_rich(d, (W // 2, 215), s["heading"], hf, INK, acc, anchor="m")
    if s.get("big"):
        bf = fit(d, s["big"], 360, 700)
        bw = d.textlength(s["big"], font=bf); uw = d.textlength(s.get("unit", ""), font=F(120))
        x = W / 2 - (bw + uw) / 2
        d.text((x, 640), s["big"], font=bf, fill=acc, anchor="lm")
        d.text((x + bw + 10, 750), s.get("unit", ""), font=F(120), fill=INK, anchor="lm")
        d.line((x, 830, x + bw + uw + 10, 830), fill=LINE_BLUE, width=8)
    y = bullets(d, 930, s.get("bullets", []), acc)
    body(d, y + 40, s.get("body", ""))
    return im


def proof(s, A):
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im); acc = A["acc"]
    hf = fit(d, s["heading"], 84, 760); paren(d, 140, 290, s["heading"], hf)
    draw_rich(d, (W // 2, 215), s["heading"], hf, INK, acc, anchor="m")
    if os.path.exists(PROOF):
        ph = Image.open(PROOF).convert("RGB"); ph.thumbnail((800, 480))
        im.paste(ph, ((W - ph.width) // 2, 380 + (480 - ph.height) // 2))
    else:
        d.rounded_rectangle((140, 380, 940, 860), 24, fill="#f1f1f1", outline="#cfcfcf", width=4)
        d.text((W // 2, 620), "（合格通知の写真・準備中）", font=F(44, "Bold"), fill="#9a9a9a", anchor="mm")
    y = bullets(d, 960, s.get("bullets", []), acc)
    body(d, y + 40, s.get("body", ""))
    return im


def quote(s, A):
    im = Image.new("RGB", (W, H), PAPER); im = grain(grain(im)); d = ImageDraw.Draw(im)
    f = F(92, "Bold"); lines = []
    for part in s["text"].split("\\n"):
        lines += wrap_ja(d, part, f, 880)
    y = H // 2 - len(lines) * 70
    for ln in lines:
        d.text((W // 2, y), ln, font=f, fill=INK, anchor="mm", stroke_width=6, stroke_fill="white"); y += 140
    if s.get("by"):
        d.text((980, y + 40), "— " + s["by"], font=F(44, "Medium"), fill=INK, anchor="rm")
    return im


def render(md, outdir):
    t = open(md, encoding="utf-8").read()
    dept = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(md))))
    if dept not in ACCOUNTS:
        sys.exit(f"対応していない部署です: {dept}")
    A = ACCOUNTS[dept]
    kind = (re.search(r"^feed_type:\s*(\S+)", t, re.M) or [None, "list"])[1]
    m = re.search(r"^## スライド\s*\n.*?```json\s*\n(.*?)```", t, re.M | re.S)
    if not m:
        sys.exit("「## スライド」節の ```json が見つかりません")
    slides = json.loads(m.group(1))
    lo, hi = LIMITS.get(kind, (6, 10))
    if not lo <= len(slides) <= hi:
        sys.exit(f"枚数が決まり({kind}: {lo}〜{hi}枚)の範囲外です: {len(slides)}枚")
    ntab = sum(1 for s in slides if s["type"] in ("table", "points"))
    os.makedirs(outdir, exist_ok=True)
    num, tabi, paths = 1, 0, []
    for i, s in enumerate(slides, 1):
        ty = s["type"]
        if ty in ("table", "points"):
            tabi += 1; page = f"{tabi:02d} / {ntab:02d}"
        if ty == "cover": im = cover(s, A)
        elif ty == "table":
            if len(s["rows"]) > 10: sys.exit(f"{i}枚目: 表は1枚10行まで")
            im = table(s, A, num, page); num += len(s["rows"])
        elif ty == "points": im = points(s, A, page)
        elif ty == "end": im = end(s, A)
        elif ty == "scover": im = scover(s, A)
        elif ty == "scene": im = scene(s, A)
        elif ty == "proof": im = proof(s, A)
        elif ty == "quote": im = quote(s, A)
        else: sys.exit(f"{i}枚目: 知らない種類です: {ty}")
        p = os.path.join(outdir, f"{i:02d}.png"); im.convert("RGB").save(p); paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    render(sys.argv[1], sys.argv[2])
