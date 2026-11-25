"""各話のページ画像(names/epNN/pages/pXX.png)をPDFにまとめる。1ページ目に、話数と題名を入れる(第1話は作品の題名ロゴも)。
ページ画像そのものは書きかえない(組み直しても題名が消えないように、PDFを作るときだけ重ねる)。

使い方: python3 tools/build_pdf.py 1 2 3 ...(省略で全話)
"""
import glob, os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
if not os.path.exists(FB): FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def F(n): return ImageFont.truetype(FB, n)

TITLES = {
    1: "アイデアが使えないと言われたので、サークルを辞めました",
    2: "想像を、形にする",
    3: "一方、その頃……",
    4: "あなたの“想像”を、形に",
    5: "崩れていく勇者サークル",
    6: "望まぬ再会",
    7: "もう遅い!",
}
POS = {3: (75, 450), 4: (75, 395)}  # 絵の大事なところ(看板・顔)を隠さない位置
LOGO = [("勇者サークルを追放されたけど、", 30), ("CAPSの人たちが温かく迎え入れてくれたので", 40),
        ("そのまま幸せになります。", 52), ("ついでに強いガクチカも作ります", 32)]

def box(d, x0, y0, lines, pad=18, gap=8, border=6):
    """白い箱に、太い文字を左寄せで並べる。lines = [(文字, 大きさ)]。箱の下端のyを返す"""
    w = max(d.textbbox((0, 0), t, font=F(s))[2] for t, s in lines) + pad * 2
    h = sum(s for _, s in lines) + gap * (len(lines) - 1) + pad * 2 + 10
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=255, outline=0, width=border)
    y = y0 + pad
    for t, s in lines:
        d.text((x0 + pad, y - s * 0.12), t, font=F(s), fill=0); y += s + gap
    return y0 + h

def first_page(ep, im):
    im = im.convert("L"); d = ImageDraw.Draw(im)
    if ep == 1:
        y = box(d, 80, 560, LOGO, pad=22, gap=10, border=8)  # 扉の大ゴマの下のほうに題名ロゴ
        box(d, 80, y + 12, [(f"第1話  {TITLES[1]}", 24)], pad=12)
    else:
        box(d, *POS.get(ep, (75, 75)), [(f"第{ep}話", 40), (TITLES[ep], 30)], pad=16)
    return im

def build(ep):
    d = os.path.join(ROOT, "names", f"ep{ep:02d}", "pages")
    fs = sorted(glob.glob(os.path.join(d, "p[0-9][0-9].png")))
    ims = [Image.open(f).convert("L") for f in fs]
    ims[0] = first_page(ep, ims[0])
    ims = [i.convert("RGB") for i in ims]
    out = os.path.join(d, f"ep{ep:02d}.pdf")
    ims[0].save(out, save_all=True, append_images=ims[1:], resolution=150)
    ims[0].save(os.path.join(d, "_cover.png"))
    print(f"第{ep}話 {len(fs)}ページ → {out}")

if __name__ == "__main__":
    for ep in [int(a) for a in sys.argv[1:]] or range(1, 8): build(ep)
