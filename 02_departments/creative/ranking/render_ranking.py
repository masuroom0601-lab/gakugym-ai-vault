#!/usr/bin/env python3
"""「○○大学 学部別倍率ランキング」リール(②総合型選抜アカウント)を作る。

2026-11-03追加(益田さんの企画)。データは各大学の公式発表(入試結果ページ・PDF)から
作ったJSON(02_departments/sougou/ranking/data/*.json)だけを使う。パスナビは利用規約上
商用の二次利用ができないため使わない(01_HQ/roadmap.md参照)。

構成(約19秒): 表紙 → 下位から順に棒グラフで発表 → 1位を強調 → フォロー誘導。
出典は各シーンの下端に小さく入れる。

使い方: python3 render_ranking.py <data.json> <out.mp4>
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
# 2026-11-03: 投稿先は③massu_smartphone(益田さんの指示)。CTAは③のアバター・IDを使う
AVATAR_PATH = os.path.join(HERE, "..", "reel_quiz", "avatar.png")
HANDLE = "@massu_smartphone"
STUDY_VIDEO = os.path.join(ASSETS, "study_bg.mp4")  # CTAの背景(勉強風景の動画)

W, H, FPS = 1080, 1920, 30
FONT = os.environ["REEL_FONT"]
FFMPEG = os.environ.get("REEL_FFMPEG", "ffmpeg")
NAVY, GOLD, RED, GRAY = "#14245a", "#f2b200", "#e60000", "#8a93ad"
COVER, STEP, HOLD, TOP1, PROMO, CTA = 2.2, 1.0, 1.8, 2.8, 3.0, 3.0  # 2026-11-03: 棒の出方が速いとの指摘で STEP 0.62→1.0秒

data = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]
YEAR = int(data["year"])
# 2025年度以前のデータは絶対に使わない(益田さんの指示)。一般選抜は2026年度に統一。
# 総合型は2026-11-03の益田さんの判断で「最終結果がそろった最新の年度」(2026年度以降)を使う
assert YEAR >= 2026, "2025年度以前のデータは使わない"
if data["selection"] == "一般選抜":
    assert YEAR == 2026, "一般選抜は2026年度で統一"
# 2026-11-03: 校正担当のファクトチェック(ranking-factcheck.yml)に合格したデータでしか
# 本番の動画を作らない。見本づくりの時だけ RANKING_ALLOW_UNCHECKED=1 で通す
if data.get("factcheck", {}).get("status") != "ok" and os.environ.get("RANKING_ALLOW_UNCHECKED") != "1":
    sys.exit(f"ファクトチェック未合格のため作成しない: {sys.argv[1]} (factcheck={data.get('factcheck')})")
# 分母・分子の種類(総合型は受験者数が公表されないことが多いので志願者数で割る)
COUNT_KEY = data.get("count_key", "examinees")
COUNT_LABEL = {"examinees": "受験者", "applicants": "志願者"}[COUNT_KEY]


def f(sz):
    return ImageFont.truetype(FONT, sz)


def bold(d, xy, t, font, fill, anchor="la", w=2):
    d.text(xy, t, font=font, fill=fill, anchor=anchor, stroke_width=w, stroke_fill=fill)


def fit(d, t, size, maxw, min_size=24):
    while size > min_size and d.textlength(t, font=f(size)) > maxw:
        size -= 2
    return f(size)


# 順位: 倍率の高い順。非公開は最下段にまとめる。表示上の倍率(小数1桁)が同じなら同順位
rows = data["rows"]
pub = sorted([r for r in rows if r.get("ratio") is not None], key=lambda r: -r[COUNT_KEY] / r["passers"])
hidden = [r for r in rows if r.get("ratio") is None]
ranked, prev, rank = [], None, 0
for i, r in enumerate(pub):
    if r["ratio"] != prev:
        rank = i + 1
    prev = r["ratio"]
    ranked.append((rank, r))
for r in hidden:
    ranked.append((None, r))
N = len(ranked)
maxr = max([r["ratio"] for _, r in ranked if r.get("ratio")] or [1])

SRC = data["source"].get("footer") or f"出典:{data['source']['publisher']}「{data['source']['title']}」({data['source']['published'].replace('-', '/')}公表)"
FORMULA = f"倍率={COUNT_LABEL}数÷合格者数"


def footer(d, light=False, col=None):
    col = col or ("#c5cbe0" if light else GRAY)
    fs = fit(d, SRC, 24, W - 80)
    d.text((W // 2, 1845), SRC, font=fs, fill=col, anchor="mm")
    d.text((W // 2, 1878), FORMULA, font=f(22), fill=col, anchor="mm")


def base(dark=False):
    im = Image.new("RGB", (W, H), NAVY if dark else "#f6f7fb")
    return im, ImageDraw.Draw(im)


def _hex(c):
    c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _shade(c, k):
    r, g, b = _hex(c)
    if k >= 0:
        return "#%02x%02x%02x" % tuple(int(v + (255 - v) * k) for v in (r, g, b))
    return "#%02x%02x%02x" % tuple(int(v * (1 + k)) for v in (r, g, b))


def _is_light(c):
    r, g, b = _hex(c)
    return 0.299 * r + 0.587 * g + 0.114 * b > 150


# 2026-11-03: 表紙の背景は各大学のスクールカラー(益田さんの指示)。色はデータJSONの
# "school_color"に、大学公式の表記を確認した上で入れる(未設定なら紺)
SCHOOL = data.get("school_color", {}).get("hex", NAVY)


def cover(t):
    im = Image.new("RGB", (W, H), SCHOOL); d = ImageDraw.Draw(im)
    light = _is_light(SCHOOL)
    stripe = _shade(SCHOOL, -0.12 if light else 0.10)
    # 斜めのストライプで動きを出す
    off = int(t * 40) % 120
    for x in range(-H, W + H, 120):
        d.polygon([(x + off, 0), (x + off + 50, 0), (x + off + 50 - H * 0.4, H), (x + off - H * 0.4, H)], fill=stripe)
    ink = "#111111"  # 文字のフチ(明るい色の背景でも読めるように)
    d.rounded_rectangle((250, 470, 830, 570), 50, fill="white", outline=ink, width=6)
    bold(d, (540, 520), f"{YEAR}年度 {data['selection']}", f(54), ink, "mm", 2)
    uni = data["university"]
    # 背景と金色の明るさが近い(オレンジ・黄・水色など)ときは金色をやめて白にする
    lum = lambda c: 0.299 * _hex(c)[0] + 0.587 * _hex(c)[1] + 0.114 * _hex(c)[2]
    accent = GOLD if abs(lum(GOLD) - lum(SCHOOL)) > 70 else "white"
    for txt, y, font, col in [(uni, 760, fit(d, uni, 130, 960), "white"), ("学部別", 930, f(110), accent), ("倍率ランキング", 1080, f(120), accent)]:
        d.text((540, y), txt, font=font, fill=col, anchor="mm", stroke_width=10, stroke_fill=ink)
    d.rounded_rectangle((170, 1250, 910, 1360), 55, fill="white", outline=ink, width=6)
    bold(d, (540, 1305), "あなたの志望学部は何倍?", f(54), RED, "mm", 2)
    footer(d, col="#1a1a1a" if light else "#e6e9f2")
    return im


# 項目が少ない大学でも上に寄らないよう、行間を広げて縦方向の中央に配置する
ROW_H = min(150, int(1460 / max(N, 1)))
ROW_TOP = 300 + max(0, (1460 - N * ROW_H) // 2)
LABEL_X, BAR_X0, BAR_X1 = 165, 520, 830  # 2桁倍率(19.0倍等)と重ならない幅


def ranking(t):
    """下位から1行ずつ棒が伸びて表示される"""
    im, d = base()
    bold(d, (540, 130), f"{data['short']} {data['selection']} 倍率ランキング", fit(d, f"{data['short']} {data['selection']} 倍率ランキング", 62, 980), NAVY, "mm", 2)
    d.text((540, 205), f"{YEAR}年度入試結果", font=f(38), fill=GRAY, anchor="mm")
    shown = int(t / STEP) + 1  # 下から何行出ているか
    for i, (rk, r) in enumerate(ranked):
        order_from_bottom = N - 1 - i
        y = ROW_TOP + i * ROW_H + ROW_H // 2
        visible = order_from_bottom < shown
        top3 = rk is not None and rk <= 3
        if top3:
            d.rounded_rectangle((40, y - ROW_H // 2 + 6, W - 40, y + ROW_H // 2 - 6), 18, fill="#fff3c4")
        if not visible:
            d.text((LABEL_X - 60, y), "?", font=f(40), fill="#c9cfdd", anchor="mm")
            d.rounded_rectangle((BAR_X0, y - 16, BAR_X1, y + 16), 16, fill="#e4e7f0")
            continue
        k = min(1.0, (t - order_from_bottom * STEP) / 0.6)
        k = 1 - (1 - k) ** 3
        rcol = RED if rk == 1 else (NAVY if rk else GRAY)
        bold(d, (LABEL_X - 60, y), f"{rk}" if rk else "-", f(46 if top3 else 40), rcol, "mm", 2)
        d.text((LABEL_X - 30, y + 18), "位" if rk else "", font=f(22), fill=rcol, anchor="lm")
        bold(d, (LABEL_X, y), r["name"], fit(d, r["name"], 40, BAR_X0 - LABEL_X - 20), "#111111", "lm", 1)
        d.rounded_rectangle((BAR_X0, y - 16, BAR_X1, y + 16), 16, fill="#e4e7f0")
        if r.get("ratio") is not None:
            bw = int((BAR_X1 - BAR_X0) * (r["ratio"] / maxr) * k)
            if bw > 32:
                d.rounded_rectangle((BAR_X0, y - 16, BAR_X0 + bw, y + 16), 16, fill=RED if rk == 1 else (GOLD if top3 else "#4472c4"))
            bold(d, (W - 50, y), f"{r['ratio']:.1f}倍", f(44 if top3 else 40), RED if top3 else "#111111", "rm", 2)
        else:
            bold(d, (W - 50, y), "非公開", f(38), GRAY, "rm", 1)
    footer(d)
    return im


def photo_bg(path, dim=0.55, blur=2):
    ph = Image.open(path).convert("RGB")
    r = max(W / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1), Image.LANCZOS)
    l, tp = (ph.width - W) // 2, (ph.height - H) // 2
    ph = ph.crop((l, tp, l + W, tp + H))
    if blur:
        ph = ph.filter(ImageFilter.GaussianBlur(blur))
    return Image.blend(ph, Image.new("RGB", (W, H), "black"), dim)


CAMPUS = data.get("campus_photo") or {}
CAMPUS_IMG = photo_bg(os.path.join(HERE, CAMPUS["path"])) if CAMPUS.get("path") else None


def top1(t):
    # 2026-11-03: 背景に大学キャンパスの写真(ライセンス確認済みのもの)を使う
    if CAMPUS_IMG is not None:
        im = CAMPUS_IMG.copy(); d = ImageDraw.Draw(im)
        if CAMPUS.get("credit"):
            fc = fit(d, CAMPUS["credit"], 22, W - 80)
            d.text((W // 2, 1800), CAMPUS["credit"], font=fc, fill="#c5cbe0", anchor="mm")
    else:
        im, d = base(dark=True)
    firsts = [r for rk, r in ranked if rk == 1]
    s = 1.0 + 0.08 * max(0.0, math.sin(math.pi * min(1.0, t / 0.35)))
    bold(d, (540, 520), "倍率 第1位", f(int(80 * s)), GOLD, "mm", 3)
    # 王冠
    cx, cy = 540, 360
    d.polygon([(cx - 110, cy + 60), (cx - 110, cy - 30), (cx - 55, cy + 15), (cx, cy - 60), (cx + 55, cy + 15), (cx + 110, cy - 30), (cx + 110, cy + 60)], fill=GOLD)
    y = 760
    for r in firsts:
        bold(d, (540, y), r["name"], fit(d, r["name"], 100, 960), "white", "mm", 3)
        y += 170
    ratio = firsts[0]["ratio"]
    # 写真の上でも読めるよう、倍率は黒いフチ付きで描く
    d.text((540, y + 80), f"{ratio:.1f}倍", font=f(int(200 * s)), fill=RED, anchor="mm", stroke_width=10, stroke_fill="#111111")
    r0 = firsts[0]
    d.text((540, y + 260), f"{COUNT_LABEL}{r0[COUNT_KEY]:,}人 / 合格者{r0['passers']:,}人", font=f(44), fill="#c5cbe0", anchor="mm")
    footer(d, light=True)
    return im


def circular_avatar(size):
    av = Image.open(AVATAR_PATH).convert("RGB").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    o = Image.new("RGBA", (size, size)); o.paste(av, (0, 0), mask)
    return o


AV = circular_avatar(204)


def study_frames():
    """CTA背景の勉強風景動画を1フレームずつ返す(足りなければループ)"""
    if not os.path.exists(STUDY_VIDEO):
        while True:
            yield None
    cmd = [FFMPEG, "-v", "error", "-stream_loop", "-1", "-i", STUDY_VIDEO, "-vf",
           f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    dark = Image.new("RGB", (W, H), "black")
    try:
        while True:
            buf = pr.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                yield None; continue
            yield Image.blend(Image.frombytes("RGB", (W, H), buf), dark, 0.55)
    finally:
        pr.kill()


def promo(t):
    """学部研究シート配布の告知(2026-11-03追加、益田さんの指示)。
    ③は本来送客しないアカウントだが、倍率ランキング投稿だけは例外として告知を入れる。
    「学ジム」の名前は出さず「オープンチャット」とだけ書く。リールにはリンクを貼れないため
    プロフィールのリンクから参加するよう案内する"""
    im = Image.new("RGB", (W, H), "#fff6d6"); d = ImageDraw.Draw(im)
    off = int(t * 30) % 90
    for gy in range(-90, H + 90, 90):
        for gx in range(-90, W + 90, 90):
            d.ellipse((gx + off - 6, gy + off - 6, gx + off + 6, gy + off + 6), fill="#f6e3a3")
    pop = 1.0 + 0.06 * max(0.0, math.sin(math.pi * min(1.0, t / 0.35)))
    # 学部研究シートのイラスト(紙+チェック欄)
    cx, cy, sw, sh = 540, 560, int(300 * pop), int(380 * pop)
    d.rounded_rectangle((cx - sw // 2 + 14, cy - sh // 2 + 14, cx + sw // 2 + 14, cy + sh // 2 + 14), 24, fill="#d9c27a")
    d.rounded_rectangle((cx - sw // 2, cy - sh // 2, cx + sw // 2, cy + sh // 2), 24, fill="white", outline=NAVY, width=8)
    d.rectangle((cx - sw // 2 + 30, cy - sh // 2 + 34, cx + sw // 2 - 30, cy - sh // 2 + 80), fill=NAVY)
    d.text((cx, cy - sh // 2 + 57), "学部研究シート", font=f(int(34 * pop)), fill="white", anchor="mm")
    for i in range(4):
        yy = cy - sh // 2 + 130 + i * 58
        d.rounded_rectangle((cx - sw // 2 + 34, yy - 16, cx - sw // 2 + 66, yy + 16), 6, outline=NAVY, width=5)
        d.line([(cx - sw // 2 + 84, yy), (cx + sw // 2 - 34, yy)], fill="#c9cfdd", width=10)
    ink = "#111111"
    bold(d, (540, 900), "オープンチャットで", f(68), NAVY, "mm", 2)
    d.text((540, 1030), "学部研究シート", font=f(104), fill=RED, anchor="mm", stroke_width=8, stroke_fill="white")
    bold(d, (540, 1150), "配布中!", f(90), NAVY, "mm", 3)
    bold(d, (540, 1290), "志望校選びや総合型対策に", f(52), ink, "mm", 1)
    d.rounded_rectangle((110, 1390, 970, 1520), 65, fill=NAVY)
    bold(d, (540, 1455), "プロフィールのリンクから参加", f(56), "white", "mm", 2)
    # 上向きの矢印(プロフィールへ誘導)
    ay = 1610 - int(18 * max(0.0, math.sin(2 * math.pi * 1.6 * t)))
    d.polygon([(540, ay - 60), (490, ay), (590, ay)], fill=RED)
    footer(d)
    return im


def draw_icon(d, kind, x, y, r):
    if kind == "follow":
        w = max(6, int(r * 0.16)); a = int(r * 0.48)
        d.rounded_rectangle((x - a, y - w // 2, x + a, y + w // 2), w // 2, fill="white")
        d.rounded_rectangle((x - w // 2, y - a, x + w // 2, y + a), w // 2, fill="white")
    elif kind == "save":
        # Instagramの保存マーク(しおり形の白抜き)
        bw, bh = r * 0.78, r * 1.0
        x0, x1, y0, y1 = x - bw / 2, x + bw / 2, y - bh / 2, y + bh / 2
        d.line([(x0, y1), (x0, y0), (x1, y0), (x1, y1), (x, y1 - bh * 0.3), (x0, y1)], fill="white", width=max(5, int(r * 0.12)), joint="curve")
    elif kind == "share":
        # 紙飛行機(DM送信のマーク)
        s = r * 0.62
        tip, left, bottom, fold = (x + s, y - s * 0.95), (x - s, y - s * 0.25), (x + s * 0.2, y + s), (x - s * 0.05, y + s * 0.05)
        d.line([left, tip, bottom, fold, left], fill="white", width=max(5, int(r * 0.11)), joint="curve")
        d.line([fold, tip], fill="white", width=max(4, int(r * 0.09)))


def cta(t, bg):
    # 2026-11-03: ③のセルフチェックリールと同じCTA(アバター+ID)。「毎日発信中」は
    # 毎日出すとは限らないため使わない(益田さんの指示)
    if bg is None:
        im, d = base(dark=True)
    else:
        im = bg; d = ImageDraw.Draw(im)
    bold(d, (540, 210), "まっすー", f(72), "white", "mm", 2)
    bold(d, (540, 300), HANDLE, f(48), GOLD, "mm", 1)
    r = 110; cx, cy = 540, 520
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="white", outline=GOLD, width=8)
    im.paste(AV, (cx - AV.width // 2, cy - AV.height // 2), AV)
    bd = 46; bx, by = cx + r - 10, cy + r - 10
    d.ellipse((bx - bd, by - bd, bx + bd, by + bd), fill=GOLD, outline="white", width=6)
    bold(d, (bx, by - 6), "+", f(70), "#4472c4", "mm", 2)
    bold(d, (540, 730), "フォロー&保存で", f(58), "white", "mm", 2)
    bold(d, (540, 805), "受験情報を見逃さない!", f(58), "white", "mm", 2)
    # 2026-11-03: マークを味気なくしないよう、保存=Instagramの保存マーク、シェア=紙飛行機にし、
    # 色もボタンごとに分けた(益田さんの指示)
    icons = [("フォロー", "follow", "#4472c4"), ("保存", "save", "#f2b200"), ("シェア", "share", "#e8457c")]
    for i, (lab, kind, col) in enumerate(icons):
        x, y = 270 + i * 270, 1150
        sc = 1.0 + 0.15 * max(0.0, math.sin(2 * math.pi * 1.5 * t - i * 0.6))
        rr = int(80 * sc)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col, outline="white", width=6)
        draw_icon(d, kind, x, y, rr)
        bold(d, (x, y + 150), lab, f(48), "white", "mm", 2)
    footer(d, light=True)
    return im


p = subprocess.Popen([FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
for i in range(int(COVER * FPS)):
    p.stdin.write(cover(i / FPS).tobytes())
for i in range(int((N * STEP + HOLD) * FPS)):
    p.stdin.write(ranking(i / FPS).tobytes())
for i in range(int(TOP1 * FPS)):
    p.stdin.write(top1(i / FPS).tobytes())
for i in range(int(PROMO * FPS)):
    p.stdin.write(promo(i / FPS).tobytes())
frames = study_frames()
for i in range(int(CTA * FPS)):
    p.stdin.write(cta(i / FPS, next(frames)).tobytes())
p.stdin.close()
p.wait()
print(out)
