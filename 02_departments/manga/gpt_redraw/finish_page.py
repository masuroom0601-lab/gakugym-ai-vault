"""GPTで描いたページ(1024x1536)を、網点で仕上げて文字を入れ、原稿の大きさ(1000x1414)にする。
使い方: python3 finish_page.py 元の絵.png 出力.png 'balloon|cx|cy|文字' 'box|x|y|文字' ...
  balloon = だ円のフキダシ(中心の座標)、box = ナレーションの四角、think = 心の声(角の丸い四角)。座標は元の絵(1024x1536)の上で指定する
  末尾に |fs をつけると文字の大きさ(既定 30)、|per で1列の文字数(既定 8)"""
import sys, os, numpy as np, cv2
HERE = sys.path[0]; sys.path.insert(0, HERE + '/../tools')
import page_compose as pc
from manga_finish import xdog, halftone
from PIL import Image, ImageDraw, ImageFont
src, out, items = sys.argv[1], sys.argv[2], sys.argv[3:]
im = Image.open(src).convert('RGB').resize((1024, 1536), Image.LANCZOS)
def finish_gpt(gray, cell=4, black=40, white=215):
    """今の原稿と同じ網点の仕上げ。GPTの絵は灰色が細かく揺れるので、濃さを段に分けると境目がまだらになる。
    そこで段に分けず、灰色の濃さに比例した大きさの網点にする(白っぽい所は白、真っ黒な所はベタ)"""
    lines = xdog(gray) < 0.97
    sm = cv2.GaussianBlur(cv2.bilateralFilter(gray, 9, 40, 9), (0, 0), 1.5)
    # GAMMA(1未満)で、黒以外の灰色を明るくする。全体が灰色っぽい絵を、今の原稿の白っぽさに寄せるため
    gm = float(os.environ.get('GAMMA', 1.0))
    lt = (255 * (sm / 255.0) ** gm).astype(np.uint8) if gm != 1.0 else sm
    out = halftone(lt, cell=cell)
    out[lt >= white] = 255; out[sm < black] = 0
    out[lines] = 0
    return out
# BLACK: これより暗い所はベタ(黒)にする。イヅルの黒髪が灰色に描かれたときは、上げて黒くする(例: BLACK=90)
import os
im = Image.fromarray(finish_gpt(np.array(im.convert('L')), black=int(os.environ.get('BLACK', 40)))).convert('L')
d = ImageDraw.Draw(im)
for it in items:
    p = it.split('|'); kind, x, y, text = p[0], float(p[1]), float(p[2]), p[3]
    fs = int(p[4]) if len(p) > 4 else 30; per = int(p[5]) if len(p) > 5 else 8
    f = ImageFont.truetype(pc.FONT_B if kind == 'balloon' else pc.FONT, fs)
    cols, w, h = pc.text_box_size(text, f, per)
    if kind == 'balloon':
        rw, rh = w / 2 + fs * 1.4, h / 2 + fs * 1.4
        d.ellipse([x - rw, y - rh, x + rw, y + rh], fill=255, outline=0, width=3)
        pc.draw_vtext(d, cols, x + w / 2, y - h / 2, f); print(kind, int(x - rw), int(y - rh), int(x + rw), int(y + rh))
    else:
        pad = 14
        if kind == 'think': d.rounded_rectangle([x, y, x + w + pad * 2, y + h + pad * 2], radius=16, fill=255, outline=0, width=3)
        else: d.rectangle([x, y, x + w + pad * 2, y + h + pad * 2], fill=255, outline=0, width=3)
        pc.draw_vtext(d, cols, x + w + pad, y + pad, f); print(kind, int(x), int(y), int(x + w + pad * 2), int(y + h + pad * 2))
# 今の原稿と同じく、まわりに白い余白(約40px)を残す
pg = Image.new('L', (1000, 1414), 255); pg.paste(im.resize((889, 1334), Image.LANCZOS), (56, 40)); pg.save(out)
