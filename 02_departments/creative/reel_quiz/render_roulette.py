#!/usr/bin/env python3
"""③スマホ対策の「ルーレットシリーズ」リールを台本から作る(2026-11-23追加、益田さん指示)。

視聴者が画面を長押しして止めた所で、名言/やることが決まる参加型リール。
  - roulette_quote : 名言ルーレット。名言カードが約0.08秒ごとに切り替わる(約9秒)
  - roulette_action: 止まったことをするルーレット。中央の針が回り、指した行動が光る(約7秒)
参考: 益田さんが送った2本の参考リール(構成だけ借りる。アニメのキャラ・セリフは使わない)。

台本(task-<日付>-sumaho-001.md)の ```json ブロック:
  名言: {"title": "勉強したくなる名言", "quotes": [{"lead": "前置き(任意)", "main": "大きく出す一言(/で改行)",
          "tail": "後ろ(任意)", "by": "老子", "mark": "円相の中に置く漢字1字"}, ...6〜8個],
         "save": "保存して、/勉強前に見返そう。", "save_sub": "好きな名言をコメントで教えてね"}
  行動: {"title": "止まったことをする/受験生ルーレット", "sub": "長押しで行動を決めよう!",
         "options": ["勉強10分", "スマホの/電源オフ", ... 8個(1行6文字以内、/で2行まで)]}
使い方: python3 render_roulette.py <台本.md> <出力.mp4>
"""
import io, json, math, os, random, re, struct, subprocess, sys, tempfile, wave
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
BG_VIDEO = os.path.join(HERE, "..", "ranking", "assets", "study_bg.mp4")
FD = ["/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/noto"]
INK, GOLD, NAVY = (28, 30, 40), (205, 150, 60), (38, 58, 110)
PORTRAITS = os.path.join(HERE, "assets", "portraits")   # 偉人の肖像(パブリックドメイン、sources.json)
AVATAR = os.path.join(HERE, "avatar.png")                # まっすー(オリジナルの言葉)
_fc = {}


def F(s, w="Bold", serif=False):
    """Black が無い環境(fonts-noto-cjk だけ)では Bold で代用する"""
    k = (s, w, serif)
    if k not in _fc:
        for ww in (w, "Bold", "Regular"):
            ps = [os.path.join(d, f"Noto{'Serif' if serif else 'Sans'}CJK-{ww}.ttc") for d in FD]
            ps = [p for p in ps if os.path.exists(p)]
            if ps:
                _fc[k] = ImageFont.truetype(ps[0], s); break
        else:
            if serif: return F(s, w, False)
            sys.exit("フォントがありません(fonts-noto-cjk)")
    return _fc[k]


def tw(d, t, f): return d.textlength(t, font=f)


def fit(d, lines, w, serif, start, maxw, minsize=40):
    s = start
    while s > minsize and max(tw(d, l, F(s, w, serif)) for l in lines) > maxw: s -= 4
    return F(s, w, serif)


# ---------------- 名言ルーレット ----------------
def washi(seed):
    """和紙風の背景+墨のにじみ(写真やキャラクターは使わない)"""
    rnd = random.Random(seed)
    im = Image.new("RGB", (W, H), (246, 240, 228))
    d = ImageDraw.Draw(im)
    for _ in range(2500):   # 紙の繊維
        x, y = rnd.randrange(W), rnd.randrange(H)
        c = rnd.randint(228, 240)
        d.line((x, y, x + rnd.randint(-14, 14), y + rnd.randint(-4, 4)), fill=(c, c - 4, c - 14), width=1)
    # 墨の円相(筆で描いた丸)と飛び散り。キャラクターや写真は使わない
    ink = Image.new("L", (W, H), 0); di = ImageDraw.Draw(ink)
    cx, cy, R = W // 2 + rnd.randint(-40, 40), 640, rnd.randint(250, 290)
    start = rnd.uniform(0, 360); span = rnd.uniform(300, 335)
    steps = 220
    for i in range(steps):
        t = i / steps
        a = math.radians(start + span * t)
        wdt = 46 * (1 - t) ** 0.6 + 6 + rnd.uniform(-3, 3)          # 筆の入りは太く、払いは細く
        rr = R + rnd.uniform(-3, 3)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        di.ellipse((x - wdt / 2, y - wdt / 2, x + wdt / 2, y + wdt / 2), fill=230)
    for _ in range(40):
        a = rnd.uniform(0, 2 * math.pi); dist = R + rnd.uniform(-60, 140)
        r = rnd.uniform(2, 11); x, y = cx + dist * math.cos(a), cy + dist * math.sin(a)
        di.ellipse((x - r, y - r, x + r, y + r), fill=rnd.randint(120, 220))
    wash = Image.new("L", (W, H), 0); dw = ImageDraw.Draw(wash)   # 薄いにじみ
    dw.ellipse((cx - R - 80, cy - R * 0.8, cx + R + 80, cy + R * 0.8), fill=55)
    ink = Image.composite(ink, wash.filter(ImageFilter.GaussianBlur(60)), ink).filter(ImageFilter.GaussianBlur(1.2))
    color = Image.new("RGB", (W, H), rnd.choice([(40, 60, 110), (30, 40, 70), (120, 80, 40)]))
    im = Image.composite(color, im, ink)
    # 円相の中に、名言を表す漢字を1字(台本の "mark"。無ければ「学」)
    return im
    return im


def brush(d, x0, x1, y, h=14, color=GOLD):
    """筆で引いたような金色の下線"""
    for i in range(h):
        a = 1 - abs(i - h / 2) / (h / 2)
        d.line((x0 + (1 - a) * 30, y + i, x1 - (1 - a) * 60, y + i), fill=color, width=1)


def portrait_for(by):
    """台本の by(例: 孔子『論語』/ まっすー)から肖像の画像と切り抜き位置を探す。無ければ (None, None)"""
    if "まっすー" in by and os.path.exists(AVATAR):
        return AVATAR, [0.5, 0.5, 1.0]
    try:
        people = json.load(open(os.path.join(PORTRAITS, "sources.json"), encoding="utf-8"))["people"]
    except Exception:
        return None, None
    for p in people:
        f = os.path.join(PORTRAITS, p["key"] + ".jpg")
        if p["key"] in by and os.path.exists(f):
            return f, p.get("focus", [0.5, 0.3, 1.3])
    return None, None


def put_portrait(im, path, focus, cx=W // 2, cy=640, r=235):
    """円相の中に、肖像を丸く切り抜いて置く(偉人は和紙になじむよう少しセピアに)"""
    src = Image.open(path).convert("RGB")
    fx, fy, zoom = focus
    side = min(src.width, src.height) / zoom
    x0 = min(max(0, fx * src.width - side / 2), src.width - side)
    y0 = min(max(0, fy * src.height - side / 2), src.height - side)
    src = src.crop((round(x0), round(y0), round(x0 + side), round(y0 + side))).resize((2 * r, 2 * r), Image.LANCZOS)
    if path != AVATAR:
        g = src.convert("L")
        src = Image.merge("RGB", [g.point(lambda v: min(255, v * 1.02 + 18)), g.point(lambda v: v * 0.95 + 12), g.point(lambda v: v * 0.82 + 8)])
    mask = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(mask).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    im.paste(src, (cx - r, cy - r), mask.filter(ImageFilter.GaussianBlur(2)))


def quote_card(spec, q, seed):
    im = washi(seed); d = ImageDraw.Draw(im)
    pic, focus = portrait_for(q.get("by", ""))
    if pic:
        put_portrait(im, pic, focus); d = ImageDraw.Draw(im)
    else:
        d.text((W // 2, 640), q.get("mark", "学"), font=F(300, "Black", True), fill=(40, 50, 80), anchor="mm")
    title = spec.get("title", "勉強したくなる名言")
    ft = fit(d, [title], "Black", True, 96, W - 160)
    d.text((W // 2, 190), title, font=ft, fill=INK, anchor="mm")
    brush(d, 140, W - 140, 262)
    y = 1060
    lead = [l for l in q.get("lead", "").split("/") if l]
    main = [l for l in q.get("main", "").split("/") if l]
    tail = [l for l in q.get("tail", "").split("/") if l]
    if lead:
        fl = fit(d, lead, "Bold", True, 66, W - 160)
        for l in lead:
            d.text((W // 2, y), l, font=fl, fill=INK, anchor="mm"); y += int(fl.size * 1.35)
        y += 20
    fm = fit(d, main, "Black", True, 132, W - 120)
    for l in main:
        d.text((W // 2, y + fm.size // 2), l, font=fm, fill=INK, anchor="mm")
        y += int(fm.size * 1.25)
    brush(d, 160, W - 160, y + 4, 16)
    y += 70
    if tail:
        fl = fit(d, tail, "Bold", True, 62, W - 160)
        for l in tail:
            d.text((W // 2, y), l, font=fl, fill=INK, anchor="mm"); y += int(fl.size * 1.35)
    d.text((W // 2, max(y + 60, 1720)), q.get("by", ""), font=F(46, "Bold", True), fill=(70, 70, 80), anchor="mm")
    return im


def save_card(spec, seed):
    im = washi(seed); d = ImageDraw.Draw(im)
    d.text((W // 2, 640), "保", font=F(300, "Black", True), fill=(40, 50, 80), anchor="mm")
    title = spec.get("title", "勉強したくなる名言")
    d.text((W // 2, 190), title, font=fit(d, [title], "Black", True, 96, W - 160), fill=INK, anchor="mm")
    brush(d, 140, W - 140, 262)
    lines = [l for l in spec.get("save", "保存して、/勉強前に見返そう。").split("/") if l]
    f = fit(d, lines, "Black", True, 120, W - 140); y = 1060
    for l in lines:
        d.text((W // 2, y), l, font=f, fill=NAVY, anchor="mm"); y += int(f.size * 1.3)
    brush(d, 200, W - 200, y - 30, 14)
    sub = spec.get("save_sub", "")
    if sub:
        d.text((W // 2, y + 80), sub, font=fit(d, [sub], "Regular", True, 44, W - 160), fill=(70, 70, 80), anchor="mm")
    return im


def build_quote(spec):
    qs = spec["quotes"]
    cards = [quote_card(spec, q, i + 1) for i, q in enumerate(qs)] + [save_card(spec, 99)]
    order = []
    n = len(cards)
    rnd = random.Random(7)
    # 2026-11-23 益田さん指示で2倍速: 2コマと3コマを交互(平均2.5コマ=約0.083秒)ごとに切り替え、約9秒
    frames, ticks = [], []
    while len(frames) < int(9.0 * FPS):
        i = rnd.randrange(n)
        if order and order[-1] == i: continue
        order.append(i); ticks.append(len(frames))
        frames += [i] * (2 if len(order) % 2 else 3)
    return cards, frames, ticks


# ---------------- 止まったことをするルーレット ----------------
def study_bg():
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "2", "-i", BG_VIDEO, "-frames:v", "1", "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True)
    if r.returncode == 0 and r.stdout:
        p = Image.open(io.BytesIO(r.stdout)).convert("RGB")
        s = max(W / p.width, H / p.height)
        p = p.resize((round(p.width * s), round(p.height * s)))
        x, y = (p.width - W) // 2, (p.height - H) // 2
        p = p.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(10))
    else:
        p = Image.new("RGB", (W, H), (40, 44, 60))
    return Image.blend(p, Image.new("RGB", (W, H), (0, 0, 0)), 0.55)


def glow_text(base, xy, text, font, fill=(255, 255, 255), glow=(120, 140, 255)):
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).text(xy, text, font=font, fill=glow + (255,), anchor="mm")
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    base.alpha_composite(lay); base.alpha_composite(lay)
    ImageDraw.Draw(base).text(xy, text, font=font, fill=fill + (255,), anchor="mm", stroke_width=3, stroke_fill=(20, 20, 30, 255))


def build_action(spec):
    opts = spec["options"]; n = len(opts)
    bg = study_bg().convert("RGBA"); d = ImageDraw.Draw(bg)
    tl = [l for l in spec.get("title", "止まったことをする/受験生ルーレット").split("/") if l]
    ft = fit(d, tl, "Black", False, 96, W - 120); y = 170
    for l in tl:
        glow_text(bg, (W // 2, y), l, ft); y += int(ft.size * 1.2)
    sub = spec.get("sub", "長押しで行動を決めよう!")
    d.rounded_rectangle((W // 2 - 330, y + 10, W // 2 + 330, y + 100), 45, fill=(255, 214, 0, 255))
    d.text((W // 2, y + 55), sub, font=fit(d, [sub], "Black", False, 52, 600), fill=(30, 30, 30), anchor="mm")
    cx, cy, R = W // 2, 1150, 390
    ov = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse((cx - R - 90, cy - R - 90, cx + R + 90, cy + R + 90), fill=(255, 255, 255, 38), outline=(255, 255, 255, 170), width=5)
    bg.alpha_composite(ov); d = ImageDraw.Draw(bg)
    pos = []
    for k in range(n):
        a = -math.pi / 2 + 2 * math.pi * k / n
        pos.append((cx + R * math.cos(a), cy + R * math.sin(a), a))
    def label(dd, k, hi):
        x, y, _ = pos[k]; lines = [l for l in opts[k].split("/") if l]
        f = fit(dd, lines, "Black", False, 62, 300)
        hgt = len(lines) * int(f.size * 1.15)
        if hi:
            wmax = max(tw(dd, l, f) for l in lines)
            dd.rounded_rectangle((x - wmax / 2 - 26, y - hgt / 2 - 18, x + wmax / 2 + 26, y + hgt / 2 + 18), 24, fill=(255, 214, 0, 255))
        yy = y - hgt / 2 + f.size * 0.55
        for l in lines:
            dd.text((x, yy), l, font=f, fill=(30, 30, 30) if hi else (255, 255, 255), anchor="mm",
                    stroke_width=0 if hi else 3, stroke_fill=(20, 20, 30)); yy += int(f.size * 1.15)
    for k in range(n): label(d, k, False)
    base = bg
    cards, frames, ticks = [], [], []
    total = int(7.0 * FPS)
    cache = {}
    last = None
    for fi in range(total):
        ang = -math.pi / 2 + 2 * math.pi * fi / FPS * 1.8   # 1秒に1.8周(2026-11-23に2倍速)
        k = round(((ang + math.pi / 2) / (2 * math.pi)) * n) % n
        key = (k, round(ang, 2))
        im = base.copy(); dd = ImageDraw.Draw(im)
        label(dd, k, True)
        # 針(中央から指す矢印)
        L = R - 120; tip = (cx + L * math.cos(ang), cy + L * math.sin(ang))
        nx, ny = -math.sin(ang), math.cos(ang)
        back = (cx - 60 * math.cos(ang), cy - 60 * math.sin(ang))
        dd.polygon([(back[0] + nx * 22, back[1] + ny * 22), (tip[0] - 70 * math.cos(ang) + nx * 22, tip[1] - 70 * math.sin(ang) + ny * 22),
                    (tip[0] - 70 * math.cos(ang) + nx * 52, tip[1] - 70 * math.sin(ang) + ny * 52), tip,
                    (tip[0] - 70 * math.cos(ang) - nx * 52, tip[1] - 70 * math.sin(ang) - ny * 52),
                    (tip[0] - 70 * math.cos(ang) - nx * 22, tip[1] - 70 * math.sin(ang) - ny * 22),
                    (back[0] - nx * 22, back[1] - ny * 22)], fill=(230, 40, 50, 255), outline=(255, 255, 255, 255))
        dd.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), fill=(255, 255, 255, 255), outline=(230, 40, 50, 255), width=10)
        cards.append(im.convert("RGB")); frames.append(fi)
        if k != last: ticks.append(fi); last = k
    return cards, frames, ticks


# ---------------- 音(切り替わるたびに「カチッ」) ----------------
def tick_wav(path, ticks, nframes):
    sr = 44100; n = int(nframes / FPS * sr); buf = [0.0] * n
    click = [math.sin(2 * math.pi * 2200 * i / sr) * math.exp(-i / (sr * 0.012)) * 0.5 for i in range(int(sr * 0.05))]
    for t in ticks:
        s = int(t / FPS * sr)
        for i, v in enumerate(click):
            if s + i < n: buf[s + i] += v
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 30000)) for v in buf))


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    src, out = sys.argv[1:]
    t = open(src, encoding="utf-8").read()
    fmt = re.search(r"^reel_format:\s*(\S+)", t, re.M)
    m = re.search(r"```json\s*(.*?)```", t, re.S)
    if not (fmt and m): sys.exit("台本に reel_format と ```json ブロックが必要です")
    spec = json.loads(m.group(1))
    if fmt.group(1) == "roulette_quote":
        cards, frames, ticks = build_quote(spec)
    elif fmt.group(1) == "roulette_action":
        cards, frames, ticks = build_action(spec)
    else:
        sys.exit(f"ルーレットの台本ではありません: {fmt.group(1)}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "tick.wav")
    tick_wav(wav, ticks, len(frames))
    pngs = {}
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png",
                             "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                             "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in frames:
        if i not in pngs:
            b = io.BytesIO(); cards[i].save(b, "PNG"); pngs[i] = b.getvalue()
        proc.stdin.write(pngs[i])
        if fmt.group(1) == "roulette_action": pngs.pop(i)   # 行動ルーレットは毎コマ違う画像
    proc.stdin.close()
    if proc.wait(): sys.exit("動画の書き出しに失敗しました")
    cards[frames[0]].save(out.removesuffix(".mp4") + "-cover.png")   # 投稿時のカバー用
    print(out, f"{len(frames) / FPS:.1f}秒")


if __name__ == "__main__":
    main()
