#!/usr/bin/env python3
"""プロフィールのハイライト用ストーリー画像(1080x1920)を台本から描く(2026-11-17追加)。

参考: 「MARCH受験英語のプロ@そら」のハイライト「受験の考え方」(黒背景に大きな見出し2行+短い行の本文、
ときどき写真背景に白い帯の文字)。益田さんの指示で、黒背景と写真背景を混ぜる。

使い方: python3 render_highlight.py <台本.md> <出力フォルダ>
  台本の ```json ブロック: {"cover": "考え方", "color": "#d7261e", "slides": [
      {"style": "black" | "photo", "title": "やる気を/待つな", "body": ["段落1の1行目/段落1の2行目", "段落2", ...]}, ...]}
  title と body の「/」は改行。body の要素ごとに段落(間を1行あける)。
  → 01.png, 02.png, ... と、ハイライトのカバー用アイコン cover.png を書き出す。
写真背景: creative/highlights/assets/photo_bg/*.jpg を順番に使う(無ければ ranking/assets/study_bg.mp4 の1コマ)。
"""
import glob, io, json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(HERE, "assets", "photo_bg")
BG_VIDEO = os.path.join(HERE, "..", "ranking", "assets", "study_bg.mp4")
FD = ["/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/noto"]
BLACK = (22, 22, 22)
_fc = {}


def F(s, w="Bold"):
    k = (s, w)
    if k not in _fc:
        for d in FD:
            p = os.path.join(d, f"NotoSansCJK-{w}.ttc")
            if os.path.exists(p):
                _fc[k] = ImageFont.truetype(p, s); break
        else:
            sys.exit("フォントがありません(fonts-noto-cjk)")
    return _fc[k]


def photos():
    ps = sorted(glob.glob(os.path.join(PHOTO_DIR, "*.jpg")) + glob.glob(os.path.join(PHOTO_DIR, "*.png")))
    if ps:
        return [Image.open(p).convert("RGB") for p in ps]
    out = []
    for t in (0.5, 3.5, 7.0):   # 背景動画から3コマ
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", BG_VIDEO, "-frames:v", "1",
                            "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if r.returncode == 0 and r.stdout:
            out.append(Image.open(io.BytesIO(r.stdout)).convert("RGB"))
    if not out: sys.exit("写真背景がありません")
    return out


def cover_fit(im):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def title_size(d, lines, mx=150, width=W - 140):
    s = mx
    while s > 80 and max(d.textlength(l, font=F(s, "Black")) for l in lines) > width: s -= 4
    return s


def body_lines(body):
    return [[l.strip() for l in para.split("/") if l.strip()] for para in body]


def body_size(d, paras, width, mx=50):
    s = mx
    while s > 34 and max(d.textlength(l, font=F(s)) for p in paras for l in p) > width: s -= 1
    if max(d.textlength(l, font=F(s)) for p in paras for l in p) > width:
        sys.exit("本文の1行が長すぎます(1行は全角19文字程度まで。「/」で改行してください)")
    return s


def slide_black(sl):
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
    tl = [l.strip() for l in sl["title"].split("/")]
    ts = title_size(d, tl)
    paras = body_lines(sl["body"])
    bs = body_size(d, paras, W - 260)
    lh, gap = int(bs * 1.45), int(bs * 1.1)
    body_h = sum(len(p) * lh for p in paras) + gap * (len(paras) - 1)
    title_h = len(tl) * int(ts * 1.18)
    top = max(220, (H - (title_h + 150 + body_h)) // 2 - 60)
    y = top
    for l in tl:
        d.text((W // 2, y + ts // 2), l, font=F(ts, "Black"), fill="white", anchor="mm"); y += int(ts * 1.18)
    y += 150
    x = 130
    for p in paras:
        for l in p:
            d.text((x, y), l, font=F(bs), fill="white"); y += lh
        y += gap
    return im


def slide_photo(sl, photo):
    im = cover_fit(photo).filter(ImageFilter.GaussianBlur(1.5))
    im = Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), 0.12)
    d = ImageDraw.Draw(im)
    tl = [l.strip() for l in sl["title"].split("/")]
    ts = title_size(d, tl, 140, W - 220)
    y = 260
    for l in tl:   # 見出しは白い角丸の帯に黒文字
        tw = d.textlength(l, font=F(ts, "Black"))
        x0 = (W - tw) // 2 - 40
        d.rounded_rectangle((x0, y, x0 + tw + 80, y + int(ts * 1.25)), 24, fill="white")
        d.text((W // 2, y + int(ts * 0.62)), l, font=F(ts, "Black"), fill=BLACK, anchor="mm")
        y += int(ts * 1.25) - 6
    y += 90
    paras = body_lines(sl["body"])
    bs = body_size(d, paras, W - 220, 46)
    lh = int(bs * 1.42)
    for p in paras:   # 本文は1行ずつ白い帯
        for l in p:
            tw = d.textlength(l, font=F(bs))
            d.rounded_rectangle((95, y - 4, 95 + tw + 40, y + lh - 8), 10, fill="white")   # 帯同士は重ねない
            d.text((115, y + 2), l, font=F(bs), fill=BLACK)
            y += lh
        y += int(bs * 0.75)
    if y > H - 120: sys.exit(f"写真背景の本文が長すぎて下にはみ出します: {sl['title']}")
    return im


def cover_icon(text, color):
    im = Image.new("RGB", (1080, 1080), color); d = ImageDraw.Draw(im)
    s = 260
    while d.textlength(text, font=F(s, "Black")) > 760: s -= 10
    d.text((540, 540), text, font=F(s, "Black"), fill="white", anchor="mm")
    return im


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    t = open(sys.argv[1], encoding="utf-8").read()
    m = re.search(r"```json\s*(.*?)```", t, re.S)
    if not m: sys.exit("台本に ```json ブロックがありません")
    spec = json.loads(m.group(1))
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    ph = photos(); k = 0
    for i, sl in enumerate(spec["slides"], 1):
        if sl.get("style") == "photo":
            im = slide_photo(sl, ph[k % len(ph)]); k += 1
        else:
            im = slide_black(sl)
        im.save(os.path.join(out, f"{i:02d}.png"))
    cover_icon(spec.get("cover", "考え方"), spec.get("color", "#222222")).save(os.path.join(out, "cover.png"))
    print(out)


if __name__ == "__main__":
    main()
