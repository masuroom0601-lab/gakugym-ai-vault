"""ネームのコマ割りに、生成したコマ画像をはめ込み、仕上げ処理と縦書きのフキダシを入れて、1ページの原稿にする。

使い方:
    python3 page_compose.py names/ep01_name.py ページ番号 コマ画像フォルダ 出力.png [--pick 1=s2,3=s1]
    コマ画像は「pXX_コマ番号_sシード.png」。--pick でコマごとに使うシードを選ぶ(省略時はs1)
"""
import argparse, importlib.util, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manga_finish import finish

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
if not os.path.exists(FONT): FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
if not os.path.exists(FONT_B): FONT_B = FONT
W, H, M, G = 1000, 1414, 60, 14
VERT = {"ー": "丨", "—": "丨", "―": "丨", "…": "︙", "〜": "\x01", "～": "\x01", "▮": "■", "▯": "□", "(": "︵", ")": "︶", "「": "﹁", "」": "﹂", "『": "﹃", "』": "﹄"}
PUNCT_SHIFT = set("、。")

def load(p):
    s = importlib.util.spec_from_file_location("m", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def panel_rects(rows):
    rects = []; y = M; uh = H - 2*M - G*(len(rows)-1)
    for rh, panels in rows:
        h = int(uh*rh); xr = W - M; uw = W - 2*M - G*(len(panels)-1)
        for pw, *_ in panels:
            w = int(uw*pw); rects.append((xr-w, y, xr, y+h)); xr = xr - w - G
        y += h + G
    return rects

def cover(im, w, h, gravity=0.3):
    r = max(w/im.width, h/im.height); im = im.resize((max(w, int(im.width*r)+1), max(h, int(im.height*r)+1)), Image.LANCZOS)
    x = (im.width - w)//2; y = int((im.height - h)*gravity)
    return im.crop((x, y, x+w, y+h))

def tokens(text):
    """文字列を(文字, ルビ番号)の列に分ける。「漢字《よみ》」の形をルビとして扱う"""
    out = []; rubies = {}
    pos = 0
    for m in re.finditer(r"([一-龥々〆ヶ]+)《([^》]+)》", text):
        out += [(VERT.get(c, c), None) for c in text[pos:m.start()] if c != " "]
        gid = len(rubies); rubies[gid] = m.group(2)
        out += [(VERT.get(c, c), gid) for c in m.group(1)]
        pos = m.end()
    out += [(VERT.get(c, c), None) for c in text[pos:] if c != " "]
    return out, rubies

def vcols(text, per_col):
    """縦書きの列に分ける。読点・句点のあとで、列の半分を超えていれば改行する(漫画の写植の慣習)"""
    toks, rubies = tokens(text)
    cols = []; cur = []
    for t in toks:
        c = t[0]
        if not cur and cols and c in "、。!?！？﹂︶︙":
            cols[-1].append(t); continue  # 行頭禁則: 句読点・感嘆符は前の列にぶら下げる
        cur.append(t)
        if len(cur) >= per_col or (c in "、。!?！？" and len(cur) >= per_col*0.5):
            cols.append(cur); cur = []
    if cur: cols.append(cur)
    cols = [c for c in cols]
    vcols.rubies = rubies
    return cols

def draw_vtext(d, cols, x_right, y_top, font, fill=0, gap=6):
    fs = font.size; rubies = getattr(vcols, "rubies", {})
    rf = ImageFont.truetype(FONT, max(9, fs // 2))
    for ci, col in enumerate(cols):
        x = x_right - (ci+1)*(fs+gap)
        spans = {}
        for ri, (ch, gid) in enumerate(col):
            dx, dy = (fs*0.55, -fs*0.45) if ch in PUNCT_SHIFT else (0, 0)
            if ch == "\x01":  # 波ダッシュは横向きの字形を90度回して縦にする
                g = Image.new("L", (fs*2, fs*2), 0); gd = ImageDraw.Draw(g)
                bx = gd.textbbox((0, 0), "〜", font=font)
                gd.text((fs - (bx[0]+bx[2])/2, fs - (bx[1]+bx[3])/2), "〜", font=font, fill=255)
                g = g.rotate(-90); cb = font.getbbox("国")
                d._image.paste(fill, (int(x + (cb[0]+cb[2])/2 - fs), int(y_top + ri*(fs+2) + (cb[1]+cb[3])/2 - fs)), g)
            else:
                d.text((x+dx, y_top + ri*(fs+2) + dy), ch, font=font, fill=fill)
            if gid is not None: spans.setdefault(gid, []).append(ri)
        for gid, rows in spans.items():  # ルビは親文字の右側に、親文字の範囲いっぱいに並べる
            ruby = rubies.get(gid, ""); top = y_top + rows[0]*(fs+2); span = len(rows)*(fs+2)
            step = span / max(1, len(ruby))
            for k, rc in enumerate(ruby):
                d.text((x + fs + 1, top + k*step + (step - rf.size)/2), rc, font=rf, fill=fill)

def text_box_size(text, font, per_col, gap=6):
    cols = vcols(text, per_col); fs = font.size
    return cols, len(cols)*(fs+gap), max(len(c) for c in cols)*(fs+2)

def parse(line):
    m = re.match(r"^(?:\(中から\))?([^「(]+?)([「(])(.*)[」)]$", line)
    if not m: return ("note", "", line)
    who, br, body = m.group(1), m.group(2), m.group(3)
    if who.startswith("ナレーション"): return ("narr", who, body)
    if who.startswith("囲み"): return ("cap", who, body)
    if who.startswith("効果音"): return ("sfx", who, body)
    if who.startswith("ステータス"): return ("status", who, body)
    if who in ("次回予告", "タイトルロゴ"): return ("narr", who, body)
    return ("mono" if br == "(" else "speech", who, body)

def compose(name_mod, page, img_dir, pick, finishing=True):
    rows = name_mod.PAGES[page]; rects = panel_rects(rows)
    page_img = Image.new("L", (W, H), 255); d = ImageDraw.Draw(page_img)
    f = ImageFont.truetype(FONT, 21); fb = ImageFont.truetype(FONT_B, 21); fsfx = ImageFont.truetype(FONT_B, 46)
    flat = [p for _, ps in rows for p in ps]
    for i, (r, p) in enumerate(zip(rects, flat), 1):
        x0, y0, x1, y1 = r; w, h = x1-x0, y1-y0
        shot = p[1]
        path = os.path.join(img_dir, f"p{page:02d}_{i}_{pick.get(i, 's1')}.png")
        if shot == "黒ベタ":
            d.rectangle(r, fill=0)
        elif shot == "文字":
            d.rectangle(r, fill=255)  # 文字だけのコマ(ステータス表示など)
        elif os.path.exists(path):
            im = cover(Image.open(path).convert("L"), w, h)
            if finishing:
                im = Image.fromarray(finish(np.array(im.convert("RGB"))[:, :, ::-1].copy(), cell=4))
            page_img.paste(im, (x0, y0))
        else:
            d.rectangle(r, fill=235); d.text((x0+8, y0+8), f"[{shot}] {p[2][:40]}", font=ImageFont.truetype(FONT, 16), fill=90)
        d.rectangle(r, outline=0, width=4)
        # フキダシ(右から左へ並べる)
        xr = x1 - 10; ytop = y0 + 10
        for line in p[3]:
            kind, who, body = parse(line)
            if kind == "note": continue
            if kind == "sfx":
                cols, bw, bh = text_box_size(body, fsfx, max(3, int((h-30)/48)), 4)
                draw_vtext(d, cols, x0 + bw + 20, ytop, fsfx, fill=0, gap=4); continue
            font = fb if kind in ("narr", "cap", "status") else f
            per = max(4, min(11, int((h - 70) / 23)))
            while True:  # フキダシがコマの高さに収まるまで、1列の文字数を減らす
                cols, bw, bh = text_box_size(body, font, per)
                if kind == "speech":
                    padx, pady = int(bw*0.22) + 16, int(bh*0.2) + 20
                else:
                    padx, pady = 12, 12
                if bh + 2*pady <= h - 24 or per <= 4: break
                per -= 1
            bx1 = xr; bx0 = bx1 - bw - 2*padx
            if bx0 < x0 + 6:  # 入りきらなければ下の段へ
                xr = x1 - 10; ytop = ytop + bh + 2*pady + 8; bx1 = xr; bx0 = bx1 - bw - 2*padx
            by0 = ytop
            if by0 + bh + 2*pady > y1 - 6: by0 = max(y0 + 6, y1 - 6 - bh - 2*pady)
            by1 = by0 + bh + 2*pady
            if kind == "speech":
                d.ellipse([bx0, by0, bx1, by1], fill=255, outline=0, width=3)
            elif kind == "mono":
                d.rounded_rectangle([bx0, by0, bx1, by1], radius=18, fill=255, outline=110, width=2)
            elif kind == "status":
                d.rectangle([bx0, by0, bx1, by1], fill=255, outline=0, width=3); d.rectangle([bx0+5, by0+5, bx1-5, by1-5], outline=0, width=1)
            else:
                d.rectangle([bx0, by0, bx1, by1], fill=255, outline=0, width=2)
            draw_vtext(d, cols, bx1 - padx + 3, by0 + pady, font)
            xr = bx0 - 8
    return page_img

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("page", type=int); ap.add_argument("img_dir"); ap.add_argument("out")
    ap.add_argument("--pick", default=""); ap.add_argument("--raw", action="store_true", help="仕上げ処理をしない")
    a = ap.parse_args()
    pick = {int(k): v for k, v in (x.split("=") for x in a.pick.split(",") if x)}
    compose(load(a.name), a.page, a.img_dir, pick, not a.raw).save(a.out); print("saved", a.out)
