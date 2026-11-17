#!/usr/bin/env python3
"""③の「〇選」リールを台本から作る(カード型・7秒)。2026-11-17に全面変更。

益田さんの指示で、@reo.toudai_mainichi_juku の伸びているリールと同じ作りにした:
- 7秒。最初の1コマから最後まで同じ画面(項目を1つずつ出す動きは無し)
- 手元の実写動画を背景に、左右に余白を残した細めの白いカードを1枚
- カードの中: 太字のタイトル(1〜2行) → 小さめの文字で項目7〜8個(各1行。キーワードだけ太字+下線、
  行末に絵文字可。見出し3つ×3〜5項目の形も可) → まとめの一言 → 締めの誘導
- あわせて、リールのカバー画像(暗くした背景に「＼上の小見出し／」+大きな2行)も作る

使い方: python3 render_rules7.py <台本 task-<日付>-sumaho-001.md> <出力mp4>
  → <出力>.mp4 と <出力>-cover.png(投稿時にカバーとして設定する画像)を書き出す。
背景: creative/reel_quiz/assets/rules7_bg/*.mp4 を日付で順番に使う(無ければ ranking/assets/study_bg.mp4)。

台本の書式(「## リール台本」節の中):
  **カバー上**: 受験期の
  **カバー**: ありがたい親            (「/」で改行。1行8文字以内×2行まで)
  **タイトル**: 受験期のありがたい親❤️   (「/」で改行。2行まで)
  **項目**:
  - 模試が終わった直後に「どう?」って**聞かない**
  - 無理に**スマホ**を取り上げない📱
  (見出しを使う場合は「### 絶対やるな🙅」のあとに「- 」の項目を続ける)
  **まとめ**: 習慣化するには、/最低**3週間**かかる。
  **締め**: **保存**して今日から実践しよう👉
"""
import datetime, glob, io, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 7.0
HERE = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(HERE, "assets", "rules7_bg")
BG_FALLBACK = os.path.join(HERE, "..", "ranking", "assets", "study_bg.mp4")
FD = ["/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/noto"]
EMOJI_FONT = ["/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"]
INK, SUB, LINEC = (40, 40, 40), (70, 70, 70), (40, 40, 40)
CARD_X0, CARD_X1, CARD_TOP = 120, 960, 470   # 細めのカード(左右に120pxの余白)
PAD = 46
INNER = CARD_X1 - CARD_X0 - PAD * 2
_fc = {}


def F(s, w="Regular"):
    k = (s, w)
    if k not in _fc:
        for d in FD:
            p = os.path.join(d, f"NotoSansCJK-{w}.ttc")
            if os.path.exists(p):
                _fc[k] = ImageFont.truetype(p, s); break
        else:
            sys.exit("フォントがありません(fonts-noto-cjk)")
    return _fc[k]


def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or 0x231A <= o <= 0x231B or 0x23E9 <= o <= 0x23FA or 0x2B00 <= o <= 0x2BFF or o in (0x3297, 0x3299, 0x203C, 0x2049, 0x2122, 0x2139, 0x24C2)


_ec = {}


def emoji_img(ch, size):
    """カラー絵文字を1文字描いて size px の正方形にする(Noto Color Emoji は109pxでしか描けない)"""
    k = (ch, size)
    if k in _ec: return _ec[k]
    path = next((p for p in EMOJI_FONT if os.path.exists(p)), None)
    if not path:
        _ec[k] = None; return None
    f = ImageFont.truetype(path, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
    bb = im.getbbox()
    im = im.crop(bb) if bb else im
    r = size / max(im.width, im.height)   # 縦長・横長の絵文字も同じ大きさの枠に収める
    im = im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)
    _ec[k] = im
    return im


def segments(text):
    """'**強調**' と絵文字を分けた [(文字列, 種類)] を返す。種類: n=通常 b=太字+下線 e=絵文字"""
    out = []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        kind = "b" if i % 2 else "n"
        buf = ""
        for ch in part:
            if ch in "️‍": continue
            if is_emoji(ch):
                if buf: out.append((buf, kind)); buf = ""
                out.append((ch, "e"))
            else:
                buf += ch
        if buf: out.append((buf, kind))
    return out


def rich_width(d, segs, size, bold_w="Bold", base_w="Regular"):
    w = 0
    for t, k in segs:
        if k == "e": w += size * 1.15
        else: w += d.textlength(t, font=F(size, bold_w if k == "b" else base_w))
    return w


def draw_rich(im, d, x, y, segs, size, color, base_w="Regular", bold_w="Bold", underline=True):
    """y はその行の上端。太字部分に下線を引く"""
    for t, k in segs:
        if k == "e":
            e = emoji_img(t, int(size * 0.88))
            if e is not None:
                im.alpha_composite(e, (int(x + size * 0.08 + (size * 0.88 - e.width) / 2), int(y + size * 0.26 + (size * 0.88 - e.height) / 2)))
            x += size * 1.15
            continue
        f = F(size, bold_w if k == "b" else base_w)
        d.text((x, y), t, font=f, fill=color + (255,))
        tw = d.textlength(t, font=f)
        if k == "b" and underline:
            uy = y + size * 1.28
            d.line((x, uy, x + tw, uy), fill=color + (255,), width=max(2, size // 13))
        x += tw
    return x


def parse(md):
    t = open(md, encoding="utf-8").read()
    sec = re.search(r"^## リール台本.*?(?=^## )", t + "\n## ", re.M | re.S)
    if not sec: sys.exit("台本に「## リール台本」節がありません")
    s = sec.group(0)

    def field(name, need=True):
        m = re.search(r"\*\*" + name + r"\*\*\s*[:：]\s*(.+)", s)
        if not m:
            if need: sys.exit(f"台本に「**{name}**:」がありません")
            return ""
        return m.group(1).strip()

    body = re.search(r"\*\*項目\*\*\s*[:：]?\s*\n(.*?)(?=\n\*\*まとめ\*\*)", s, re.S)
    if not body: sys.exit("台本の「**項目**:」〜「**まとめ**:」の間が読めません")
    blocks, cur = [], None
    for ln in body.group(1).splitlines():
        ln = ln.strip()
        if ln.startswith("### "):
            cur = [ln[4:].strip(), []]; blocks.append(cur)
        elif ln.startswith("- ") or re.match(r"^[0-9０-９]+[\.．、]\s*", ln):
            item = re.sub(r"^(- |[0-9０-９]+[\.．、]\s*)", "", ln).strip()
            if cur is None: cur = [None, []]; blocks.append(cur)
            cur[1].append(item)
    n = sum(len(b[1]) for b in blocks)
    heads = [b for b in blocks if b[0]]
    if heads:
        if not (2 <= len(heads) <= 3 and all(3 <= len(b[1]) <= 5 for b in heads)):
            sys.exit("見出しを使うときは見出し2〜3個×各3〜5項目にしてください")
    elif not 6 <= n <= 8:
        sys.exit(f"項目は6〜8個にしてください(いま{n}個)")
    return {
        "cover_kicker": field("カバー上"), "cover": field("カバー"),
        "title": field("タイトル"), "blocks": blocks,
        "summary": field("まとめ"), "cta": field("締め"),
    }


def card(sc):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lay = []   # (y, 描画関数) を先に並べて高さを決める
    y = 0
    tsize = 54
    for ln in sc["title"].split("/"):
        segs = segments(ln.strip())
        while rich_width(d, segs, tsize, "Bold", "Bold") > INNER and tsize > 40: tsize -= 2
    for ln in sc["title"].split("/"):
        lay.append((y, "title", segments(ln.strip()))); y += int(tsize * 1.45)
    y += 34
    # 項目の文字サイズ: いちばん長い行が収まる大きさ(最大34、最小25)
    numbered = all(b[0] is None for b in sc["blocks"])
    isize = 34
    def item_segs(i, it):
        return segments((f"{i}.  " if numbered else "・") + it)
    allitems = [it for b in sc["blocks"] for it in b[1]]
    while isize > 25 and max(rich_width(d, item_segs(9, it), isize) for it in allitems) > INNER: isize -= 1
    if max(rich_width(d, item_segs(9, it), isize) for it in allitems) > INNER:
        sys.exit("項目が長すぎて1行に収まりません(1項目は全角22文字程度まで)")
    k = 0
    for head, items in sc["blocks"]:
        if head:
            lay.append((y, "head", segments(head))); y += int(isize * 1.55)
        for it in items:
            k += 1
            lay.append((y, "item", item_segs(k, it))); y += int(isize * 1.62)
        if head: y += int(isize * 0.9)
    y += int(isize * 1.1)
    for ln in sc["summary"].split("/"):
        lay.append((y, "sum", segments(ln.strip()))); y += int(isize * 1.6)
    y += int(isize * 1.3)
    lay.append((y, "cta", segments(sc["cta"]))); y += int(isize * 1.6)
    h = y + PAD * 2
    top = min(CARD_TOP, H - 260 - h)
    d.rectangle((CARD_X0, top, CARD_X1, top + h), fill=(255, 255, 255, 250))
    x = CARD_X0 + PAD
    for yy, kind, segs in lay:
        yy += top + PAD
        if kind == "title":
            draw_rich(im, d, x, yy, segs, tsize, INK, "Bold", "Bold", underline=False)
        elif kind == "head":
            draw_rich(im, d, x, yy, segs, isize, INK, "Bold", "Bold", underline=False)
        else:
            draw_rich(im, d, x, yy, segs, isize, SUB if kind != "cta" else INK)
    return im


def pick_bg(date):
    bgs = sorted(glob.glob(os.path.join(BG_DIR, "*.mp4")))
    if not bgs: return BG_FALLBACK
    return bgs[date.toordinal() % len(bgs)]


def bg_frame(bg, t=1.0):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", bg, "-frames:v", "1",
                        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    if p.returncode or not p.stdout: sys.exit("背景動画からカバー用の1コマを取り出せません")
    return Image.open(io.BytesIO(p.stdout)).convert("RGB")


def cover(sc, bg):
    im = bg_frame(bg, 2.0).filter(ImageFilter.GaussianBlur(2))
    im = Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), 0.45).convert("RGBA")
    d = ImageDraw.Draw(im)
    cy = H // 2
    kick = "＼ " + sc["cover_kicker"] + " ／"
    lines = [l.strip() for l in sc["cover"].split("/") if l.strip()][:2]
    size = 170
    while size > 90 and max(d.textlength(l, font=F(size, "Black")) for l in lines) > W - 120: size -= 6
    total = 90 + len(lines) * int(size * 1.2)
    y = cy - total // 2
    d.text((W // 2, y + 30), kick, font=F(64, "Bold"), fill="white", anchor="mm")
    y += 90
    for l in lines:
        d.text((W // 2, y + size * 0.6), l, font=F(size, "Black"), fill="white", anchor="mm")
        y += int(size * 1.2)
    return im.convert("RGB")


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    md, out = sys.argv[1], sys.argv[2]
    sc = parse(md)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(md))
    date = datetime.date.fromisoformat(m.group(1)) if m else datetime.date.today()
    bg = pick_bg(date)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    ov = io.BytesIO(); card(sc).save(ov, "PNG")
    tmp = out + ".card.png"
    open(tmp, "wb").write(ov.getvalue())
    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=1:1,fps={FPS}[bg];"
          f"[bg][1:v]overlay=0:0,format=yuv420p[v]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", bg, "-loop", "1", "-i", tmp,
           "-f", "lavfi", "-t", str(DUR), "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", vf, "-map", "[v]", "-map", "2:a",
           "-c:v", "libx264", "-c:a", "aac", "-t", str(DUR), "-movflags", "+faststart", out]
    r = subprocess.run(cmd)
    os.remove(tmp)
    if r.returncode: sys.exit("動画の書き出しに失敗しました")
    cv = re.sub(r"\.mp4$", "", out) + "-cover.png"
    cover(sc, bg).save(cv)
    print(out); print(cv)


if __name__ == "__main__":
    main()
