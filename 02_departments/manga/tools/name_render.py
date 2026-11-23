"""ネームのデータ(names/epXX_name.py)から、ページのコマ割りサムネイルと、ネーム表(Markdown)を作る。

使い方: python3 02_departments/manga/tools/name_render.py 02_departments/manga/names/ep01_name.py 出力フォルダ
- 漫画は右から左に読むため、各段のコマは右から順に並べる
"""
import importlib.util, os, sys, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
W, H, M, G = 1000, 1414, 60, 14  # B5比率のページ・外側の余白・コマ間のすき間

spec = importlib.util.spec_from_file_location("name", sys.argv[1]); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
f_no = ImageFont.truetype(FONT, 34); f_shot = ImageFont.truetype(FONT, 22); f_txt = ImageFont.truetype(FONT, 19); f_pg = ImageFont.truetype(FONT, 26)

def wrap(d, text, font, width, x, y, maxy, fill=0):
    text = text.replace("▮", "■").replace("▯", "□")  # フォントに無い記号を置きかえる
    chars = max(4, int(width / (font.size * 1.02)))
    for line in textwrap.wrap(text, chars):
        if y + font.size > maxy: d.text((x, y), "…", font=font, fill=fill); return y
        d.text((x, y), line, font=font, fill=fill); y += font.size + 5
    return y

md = [f"# {os.path.basename(sys.argv[1]).split('_')[0]} ネーム(コマ割り)\n", "読み方: 各ページのコマは、右上から左へ、上の段から下の段へ読む(番号の順)。",
      "ショット: 扉/大ゴマ/L=引き(全身・背景まで)/M=腰から上/B=胸から上/UP=顔や物のアップ/手元=手や小物のアップ\n"]
thumbs = []
for pno in sorted(mod.PAGES):
    rows = mod.PAGES[pno]
    img = Image.new("L", (W, H), 255); d = ImageDraw.Draw(img)
    d.text((W - M - 140, 18), f"p.{pno}", font=f_pg, fill=0)
    md.append(f"\n## p.{pno}")
    if pno in getattr(mod, "NOTES", {}): md.append(f"> 演出メモ: {mod.NOTES[pno]}")
    for n, pan in enumerate(layout.page_panels(mod, pno), 1):
        _, shot, desc, lines = pan["data"]; opts = pan["opts"]
        poly = pan["poly"]; x0, y0, x1, y1 = pan["inner"]
        if pan["inset"]: d.polygon(poly, fill=255)
        if shot == "黒ベタ": d.polygon(poly, fill=40)
        if pan["frame"]:
            wd = 5 if shot in ("大ゴマ", "扉(カラー)") else 3
            for a, b in layout.frame_edges(poly): d.line([a, b], fill=0, width=wd)
            if pan["inset"]: d.line(poly + [poly[0]], fill=0, width=wd)
        else:
            d.line(poly + [poly[0]], fill=150, width=1)
        col = 255 if shot == "黒ベタ" else 0
        d.text((x1 - 44, y0 + 6), str(n), font=f_no, fill=col)
        tag = "".join(f"[{t}]" for t, k in (("裁ち切り", "bleed"), ("枠なし", "noframe"), ("はみ出し", "breakout")) if opts.get(k))
        ty = wrap(d, f"[{shot}]{tag} {desc}", f_shot, x1 - x0 - 60, x0 + 10, y0 + 8, y1 - 8, col)
        for ln in lines:
            ty = wrap(d, "・" + ln, f_txt, x1 - x0 - 30, x0 + 14, ty + 4, y1 - 8, col)
        md.append(f"{n}. **[{shot}]**{tag} {desc}" + ("".join(f"\n   - {ln}" for ln in lines)))
    fn = os.path.join(out, f"p{pno:02d}.png"); img.save(fn); thumbs.append(fn)
open(os.path.join(out, "name.md"), "w").write("\n".join(md) + "\n")
# 一覧(8ページずつ)
for k in range(0, len(thumbs), 8):
    grp = thumbs[k:k + 8]; tw, th = 330, 467
    sheet = Image.new("L", (4 * tw + 50, 2 * th + 30), 200)
    for i, fn in enumerate(grp):
        im = Image.open(fn); im.thumbnail((tw, th)); sheet.paste(im, (10 + (i % 4) * (tw + 10), 10 + (i // 4) * (th + 10)))
    sheet.save(os.path.join(out, f"_sheet_{k // 8 + 1}.png"))
print("pages", len(thumbs))
