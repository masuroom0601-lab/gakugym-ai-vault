#!/usr/bin/env python3
"""ハイライト「自己紹介」用のストーリー画像(1080x1920)を台本から描く(2026-11-17追加)。

参考: 競合アカウントのハイライト「自己紹介」(淡くした写真の背景に手書き風の文字、赤字と黄色のマーカーで強調)。
写真は益田さんが撮ったものではないフリー素材を淡くして使う(assets/photo_bg/*.jpg、無ければ勉強風景の素材動画の1コマ)。
文字は Klee One(SIL Open Font License、assets/fonts/)。

使い方: python3 render_intro.py <台本.md> <出力フォルダ>
台本の ```json ブロック: {"slides": [[行, 行, ...], ...]}
  行の書き方(先頭の記号で種類を決める):
    ""            … 空行(すき間)
    "テキスト"     … ふつうの文字(中央ぞろえ)
    "# テキスト"   … 大きい文字
    "! テキスト"   … 赤い文字
    "#! テキスト"  … 大きい赤い文字
    "~ テキスト"   … 赤い文字+下に黄色のマーカー線
    "[box] 項目:内容|項目:内容"  … 枠で囲んだプロフィール表
    "[btn] テキスト"  … リンクボタン風の帯(押せるリンクにはならない。投稿時にリンクスタンプを重ねる)
    "[proof]"     … ぼかし済みの合格通知の画像(creative/feed/assets/proof.jpg)
    "[photo] ファイル名"  … 益田さんの写真を白枠つきで大きく載せる(assets/photos/ のファイル。2026-11-25追加)
  1行の中の **…** は赤字になる。
"""
import glob, io, json, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "assets", "fonts", "KleeOne-600.ttf")
PHOTO_DIR = os.path.join(HERE, "assets", "photo_bg")
BG_VIDEO = os.path.join(HERE, "..", "ranking", "assets", "study_bg.mp4")
PROOF = os.path.join(HERE, "..", "feed", "assets", "proof.jpg")
INK, RED, MARK, BLUE = (25, 25, 25), (178, 34, 52), (236, 205, 80), (40, 140, 220)
_fc = {}


def F(s):
    if s not in _fc: _fc[s] = ImageFont.truetype(FONT, s)
    return _fc[s]


def photos():
    ps = sorted(glob.glob(os.path.join(PHOTO_DIR, "*.jpg")) + glob.glob(os.path.join(PHOTO_DIR, "*.png")))
    if ps: return [Image.open(p).convert("RGB") for p in ps]
    out = []
    for t in (0.5, 3.5, 7.0):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", BG_VIDEO, "-frames:v", "1",
                            "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if r.returncode == 0 and r.stdout: out.append(Image.open(io.BytesIO(r.stdout)).convert("RGB"))
    if not out: sys.exit("背景の写真がありません")
    return out


def bg(photo):
    s = max(W / photo.width, H / photo.height)
    im = photo.resize((round(photo.width * s), round(photo.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(4))
    return Image.blend(im, Image.new("RGB", (W, H), (252, 251, 247)), 0.84)   # 白く淡くする


def segs(t, base):
    return [(p, RED if i % 2 else base) for i, p in enumerate(re.split(r"\*\*(.+?)\*\*", t)) if p]


def tw(d, sg, f):
    return sum(d.textlength(p, font=f) for p, _ in sg)


def layout(lines):
    """各行の(種類, 内容, 文字サイズ, 高さ)を返す"""
    out = []
    for ln in lines:
        if ln == "": out.append(("gap", None, 0, 50)); continue
        if ln.startswith("[box]"):
            items = [x.strip(" ") for x in ln[5:].strip().split("|")]
            out.append(("box", items, 58, 82 * len(items) + 90)); continue
        if ln.startswith("[btn]"): out.append(("btn", ln[5:].strip(), 64, 150)); continue
        if ln.startswith("[proof]"): out.append(("proof", None, 0, 470)); continue
        if ln.startswith("[photo]"): out.append(("photo", ln[7:].strip(), 0, 1180)); continue
        kind, size, col = "text", 60, INK
        m = re.match(r"^(#?)(!?)(~?)\s*(.*)$", ln)
        big, red, mark, t = m.group(1), m.group(2), m.group(3), m.group(4)
        if big: size = 108
        if red or mark: col = RED
        if mark: kind = "mark"; size = max(size, 76)
        out.append((kind, (t, col), size, int(size * 1.5) + (26 if mark else 0)))
    return out


def slide(lines, photo):
    im = bg(photo).convert("RGBA"); d = ImageDraw.Draw(im)
    lay = layout(lines)
    # 長すぎる行は文字を小さくする
    fixed = []
    for kind, v, size, h in lay:
        if kind in ("text", "mark"):
            sg = segs(v[0], v[1])
            while tw(d, sg, F(size)) > W - 120 and size > 34: size -= 2
            if tw(d, sg, F(size)) > W - 120: sys.exit(f"1行が長すぎます: {v[0]}")
            h = int(size * 1.5) + (26 if kind == "mark" else 0)
        fixed.append((kind, v, size, h))
    total = sum(h for *_, h in fixed)
    if total > H - 240: sys.exit(f"1枚に入りきりません(高さ {total}px): {lines[:2]}")
    y = max(200, (H - total) // 2 - 80)
    for kind, v, size, h in fixed:
        if kind in ("text", "mark"):
            sg = segs(v[0], v[1]); x = (W - tw(d, sg, F(size))) / 2
            if kind == "mark":
                w = tw(d, sg, F(size))
                d.rounded_rectangle((x - 30, y + size * 1.32, x + w + 30, y + size * 1.32 + 16), 8, fill=MARK + (255,))
            for p, c in sg:
                d.text((x, y), p, font=F(size), fill=c + (255,)); x += d.textlength(p, font=F(size))
        elif kind == "box":
            d.rectangle((110, y, W - 110, y + h - 30), outline=INK + (255,), width=4, fill=(255, 255, 255, 120))
            yy = y + 40
            for it in v:
                d.text((150, yy), it, font=F(size), fill=INK + (255,)); yy += 82
        elif kind == "btn":
            d.rectangle((150, y + 10, W - 150, y + 34), fill=MARK + (255,))
            d.rectangle((120, y + 104, W - 220, y + 126), fill=MARK + (255,))
            d.rounded_rectangle((190, y + 22, W - 190, y + 118), 30, fill=(255, 255, 255, 255))
            d.text((W // 2, y + 70), v, font=F(size), fill=BLUE + (255,), anchor="mm")
        elif kind == "photo":
            p = ImageOps.exif_transpose(Image.open(os.path.join(HERE, "assets", "photos", v))).convert("RGB"); p.thumbnail((W - 200, 1120))
            px = (W - p.width) // 2
            d.rectangle((px - 18, y + 10 - 18, px + p.width + 18, y + 10 + p.height + 18), fill=(255, 255, 255, 255))
            im.paste(p, (px, y + 10))
        elif kind == "proof":
            p = Image.open(PROOF).convert("RGB"); p.thumbnail((W - 200, 440))
            im.paste(p, ((W - p.width) // 2, y + 10))
        y += h
    return im.convert("RGB")


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    t = open(sys.argv[1], encoding="utf-8").read()
    m = re.search(r"```json\s*(.*?)```", t, re.S)
    if not m: sys.exit("台本に ```json ブロックがありません")
    spec = json.loads(m.group(1)); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    ph = photos()
    for i, lines in enumerate(spec["slides"], 1):
        slide(lines, ph[(i - 1) % len(ph)]).save(os.path.join(out, f"{i:02d}.png"))
    print(out)


if __name__ == "__main__":
    main()
