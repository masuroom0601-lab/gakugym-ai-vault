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
_CASCADE = None
def faces_in(im):
    """コマ画像の中のアニメ顔を検出する(lbpcascade_animeface, MITライセンス)。(x0,y0,x1,y1)のリスト"""
    global _CASCADE
    import cv2
    if _CASCADE is None:
        _CASCADE = cv2.CascadeClassifier(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lbpcascade_animeface.xml"))
    a = cv2.equalizeHist(np.array(im.convert("L")))
    m = max(24, min(im.width, im.height) // 10)
    return [(x, y, x+w, y+h) for x, y, w, h in _CASCADE.detectMultiScale(a, 1.1, 4, minSize=(m, m))]
VERT = {"!": "！", "?": "？", "ー": "丨", "—": "丨", "―": "丨", "…": "︙", "〜": "\x01", "～": "\x01", "▮": "■", "▯": "□", "(": "︵", ")": "︶", "「": "﹁", "」": "﹂", "『": "﹃", "』": "﹄"}
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
    # 縦中横: ちょうど2けたの数字(「10個」など)と「!?」「!!」は、1マスに横に並べる(3けた以上は1字ずつ縦に)
    merged = []; i = 0
    isd = lambda t: t[1] is None and len(t[0]) == 1 and t[0].isascii() and t[0].isdigit()
    while i < len(out):
        t = out[i]
        if isd(t):
            j = i
            while j < len(out) and isd(out[j]): j += 1
            if j - i == 2: merged.append((out[i][0] + out[i + 1][0], None))
            else: merged += out[i:j]
            i = j; continue
        if merged and t[1] is None and merged[-1][1] is None and merged[-1][0] + t[0] in ("！？", "？！", "！！"):
            merged[-1] = (merged[-1][0] + t[0], None); i += 1; continue
        merged.append(t); i += 1
    out = merged
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
            elif len(ch) > 1:  # 縦中横: 小さめの字で、マスの中央に横に並べる
                ch = ch.replace("！", "!").replace("？", "?")
                tf = ImageFont.truetype(font.path, int(fs * (0.8 if ch.isdigit() else 0.85)))
                bb = d.textbbox((0, 0), ch, font=tf); cb = font.getbbox("国")
                d.text((x + (cb[0] + cb[2]) / 2 - (bb[0] + bb[2]) / 2, y_top + ri*(fs+2) + (cb[1] + cb[3]) / 2 - (bb[1] + bb[3]) / 2), ch, font=tf, fill=fill)
            elif ch in PUNCT_SHIFT:
                d.text((x+dx, y_top + ri*(fs+2) + dy), ch, font=font, fill=fill)
            else:  # 字の幅が狭い字(数字・英字・！？など)も、列の中央にそろえる
                bb = font.getbbox(ch); cb = font.getbbox("国")
                d.text((x + (cb[0] + cb[2]) / 2 - (bb[0] + bb[2]) / 2, y_top + ri*(fs+2)), ch, font=font, fill=fill)
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

def _overlap(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))

SC = 4  # 重なり判定に使う地図の縮小率

def avoid_layer(cost, im_rgb, ox0, oy0, fboxes):
    """フキダシを避けたい場所の重みを、ページ全体の地図 cost に書き込む。
    切り抜きモデルでキャラクターの形を取り、頭のあたり(各人物の上の方)を重く、体を軽くする。顔検出の枠はいちばん重くする"""
    from scipy import ndimage
    w, h = im_rgb.size
    a = _cutout_alpha(im_rgb)
    if a is not None:
        m = np.array(a.resize((max(1, w // SC), max(1, h // SC)))) > 128
        lab, n = ndimage.label(m)
        layer = m.astype(np.float32)
        for k, sl in enumerate(ndimage.find_objects(lab), 1):
            if sl is None: continue
            comp = lab[sl] == k
            if comp.sum() < 0.02 * m.size: continue
            ys, xs = sl; hh = ys.stop - ys.start
            big = comp.sum() > 0.45 * m.size  # 顔のアップ: 顔が上の方とは限らないので、範囲を広げる
            hz = ys.start + int(hh * (0.6 if big else 0.32))
            sub = layer[ys.start:hz, xs]; sub[lab[ys.start:hz, xs] == k] = 6
        y0, x0 = oy0 // SC, ox0 // SC
        hh, ww = cost[y0:y0 + layer.shape[0], x0:x0 + layer.shape[1]].shape
        cost[y0:y0 + hh, x0:x0 + ww] = np.maximum(cost[y0:y0 + hh, x0:x0 + ww], layer[:hh, :ww])
    for fx0, fy0, fx1, fy1 in fboxes:
        ex = int((fx1 - fx0) * 0.2)
        cost[max(0, (fy0 - ex) // SC):(fy1 + ex) // SC, max(0, (fx0 - ex) // SC):(fx1 + ex) // SC] = 14

def place_items(d, items, r, cost, fsfx, fixed=None):
    """フキダシの組を、コマの中で、人物(特に顔・頭)との重なりが最も小さい位置へ平行移動して描く。
    重なりが同じくらいなら、読み始めの右上に近い位置を選ぶ。fixed=(横0〜1, 縦0〜1) で位置を手で指定できる"""
    x0, y0, x1, y1 = r
    boxes = [it[4] for it in items if it[0] != "sfx"]
    dx = dy = 0
    if boxes:
        gx0 = min(b[0] for b in boxes); gx1 = max(b[2] for b in boxes)
        gy0 = min(b[1] for b in boxes); gy1 = max(b[3] for b in boxes)
        lo_x, hi_x = (x0 + 6) - gx0, (x1 - 6) - gx1
        lo_y, hi_y = (y0 + 6) - gy0, (y1 - 6) - gy1
        if fixed is not None:
            dx = int(lo_x + (hi_x - lo_x) * (1 - fixed[0])) if hi_x > lo_x else 0
            dy = int(lo_y + (hi_y - lo_y) * fixed[1]) if hi_y > lo_y else 0
        elif cost is not None and hi_x >= lo_x and hi_y >= lo_y:
            ii = np.pad(cost, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
            def rect(bx0, by0, bx1, by1):
                a, b, c, e = max(0, bx0 // SC), max(0, by0 // SC), max(0, bx1 // SC), max(0, by1 // SC)
                c = min(c, cost.shape[1]); e = min(e, cost.shape[0])
                if c <= a or e <= b: return 0.0
                return ii[e, c] - ii[b, c] - ii[e, a] + ii[b, a]
            best = None
            for cdx in list(range(int(hi_x), int(lo_x) - 1, -8)) or [0]:
                for cdy in list(range(int(lo_y), int(hi_y) + 1, 8)) or [0]:
                    sc = sum(rect(b[0] + cdx, b[1] + cdy, b[2] + cdx, b[3] + cdy) for b in boxes)
                    sc += 0.5 * ((hi_x - cdx) + (cdy - lo_y)) / SC  # 右上から離れるほど少し不利
                    if best is None or sc < best[0]: best = (sc, cdx, cdy)
            _, dx, dy = best
    for kind, font, _, cols, (bx0, by0, bx1, by1), padx, pady in items:
        if kind == "sfx":
            draw_vtext(d, cols, bx1, by0, fsfx, fill=0, gap=4); continue
        bx0, bx1, by0, by1 = bx0+dx, bx1+dx, by0+dy, by1+dy
        if kind == "speech":
            d.ellipse([bx0, by0, bx1, by1], fill=255, outline=0, width=3)
        elif kind == "mono":
            d.rounded_rectangle([bx0, by0, bx1, by1], radius=18, fill=255, outline=110, width=2)
        elif kind == "status":
            d.rectangle([bx0, by0, bx1, by1], fill=255, outline=0, width=3); d.rectangle([bx0+5, by0+5, bx1-5, by1-5], outline=0, width=1)
        else:
            d.rectangle([bx0, by0, bx1, by1], fill=255, outline=0, width=2)
        draw_vtext(d, cols, bx1 - padx + 3, by0 + pady, font)

def _cutout_alpha(im):
    """キャラクターの切り抜き用の透明度(はみ出し演出用)。切り抜きモデルが無ければ None"""
    try:
        from rembg import remove, new_session
        global _RB
        if "_RB" not in globals(): _RB = new_session("isnet-anime")
        return remove(im.convert("RGB"), session=_RB).getchannel("A").point(lambda v: 255 if v > 128 else 0)
    except ImportError:
        return None

def compose(name_mod, page, img_dir, pick, finishing=True):
    import layout
    pans = layout.page_panels(name_mod, page)
    page_img = Image.new("L", (W, H), 255); d = ImageDraw.Draw(page_img)
    f = ImageFont.truetype(FONT, 21); fb = ImageFont.truetype(FONT_B, 21); fsfx = ImageFont.truetype(FONT_B, 46)
    breakouts = []; texts = []
    cost = np.zeros((H // SC + 1, W // SC + 1), np.float32)
    for i, pan in enumerate(pans, 1):
        _, shot, desc, lines = pan["data"]; opts = pan["opts"]; poly = pan["poly"]
        bx0, by0, bx1, by1 = pan["bbox"]
        mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
        fboxes = []
        path = os.path.join(img_dir, f"p{page:02d}_{i}_{pick.get(i, 's1')}.png")
        if shot == "黒ベタ":
            page_img.paste(0, (0, 0), mask)
        elif shot == "文字":
            page_img.paste(255, (0, 0), mask)  # 文字だけのコマ(ステータス表示など)
        elif os.path.exists(path):
            src = Image.open(path)
            if os.environ.get("DEINK", "1") == "1" and not path.endswith("_ui.png"):  # 白地に落ちた墨の飛び散りを消す(tools/deink.py)
                from deink import clean
                src = clean(src, path)
            if opts.get("breakout"):  # はみ出し用に、コマより一回り大きく貼る
                ex = int(0.08 * max(bx1 - bx0, by1 - by0))
                ox0, oy0, ox1, oy1 = max(0, bx0 - ex), max(0, by0 - ex), min(W, bx1 + ex), min(H, by1 + ex)
            else:
                ox0, oy0, ox1, oy1 = bx0, by0, bx1, by1
            im = cover(src.convert("L"), ox1 - ox0, oy1 - oy0)
            fboxes = [(ox0+a, oy0+b, ox0+c, oy0+e) for a, b, c, e in faces_in(im)]
            avoid_layer(cost, cover(src.convert("RGB"), ox1 - ox0, oy1 - oy0), ox0, oy0, fboxes)
            if finishing:
                im = Image.fromarray(finish(np.array(im.convert("RGB"))[:, :, ::-1].copy(), cell=4))
            layer = Image.new("L", (W, H), 255); layer.paste(im, (ox0, oy0))
            page_img.paste(layer, (0, 0), mask)
            if opts.get("breakout"):
                a = _cutout_alpha(cover(src.convert("RGB"), ox1 - ox0, oy1 - oy0))
                if a is not None:
                    full = Image.new("L", (W, H), 0); full.paste(a, (ox0, oy0)); breakouts.append((layer, full))
        else:
            page_img.paste(235, (0, 0), mask)
            d.text((pan["inner"][0]+8, pan["inner"][1]+8), f"[{shot}] {desc[:40]}", font=ImageFont.truetype(FONT, 16), fill=90)
        if pan["inset"]:  # 重ねゴマは白いふちで浮かせる
            d.line(poly + [poly[0]], fill=255, width=14)
        if pan["frame"]:
            for a, b in layout.frame_edges(poly): d.line([a, b], fill=0, width=4)
            for pt in poly: d.ellipse([pt[0]-2, pt[1]-2, pt[0]+2, pt[1]+2], fill=0)
        texts.append((pan, lines, fboxes))
    for layer, a in breakouts:  # キャラクターを枠の上に重ねる(はみ出し)
        page_img.paste(layer, (0, 0), a)
    for pan, lines, fboxes in texts:
        draw_texts(d, pan["inner"], lines, cost, f, fb, fsfx, pan["opts"].get("fuki"))
    return page_img

def draw_texts(d, r, lines, cost, f, fb, fsfx, fixed=None):
    """コマの中にフキダシ・ナレーション・効果音を置く(右から左へ並べ、顔に重ならない位置へずらす)"""
    x0, y0, x1, y1 = r; h = y1 - y0
    items = []
    xr = x1 - 10; ytop = y0 + 10
    for line in lines:
        kind, who, body = parse(line)
        if kind == "note": continue
        if kind == "sfx":
            cols, bw, bh = text_box_size(body, fsfx, max(3, int((h-30)/48)), 4)
            items.append(("sfx", None, None, cols, [x0 + 20, ytop, x0 + bw + 20, ytop + bh], 0, 0)); continue
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
        items.append((kind, font, None, cols, [bx0, by0, bx1, by1], padx, pady))
        xr = bx0 - 8
    place_items(d, items, r, cost, fsfx, fixed)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("page", type=int); ap.add_argument("img_dir"); ap.add_argument("out")
    ap.add_argument("--pick", default=""); ap.add_argument("--raw", action="store_true", help="仕上げ処理をしない")
    a = ap.parse_args()
    pick = {int(k): v for k, v in (x.split("=") for x in a.pick.split(",") if x)}
    compose(load(a.name), a.page, a.img_dir, pick, not a.raw).save(a.out); print("saved", a.out)
