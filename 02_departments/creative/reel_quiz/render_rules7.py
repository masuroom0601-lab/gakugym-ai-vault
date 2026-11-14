#!/usr/bin/env python3
"""③の「7選」リール(15秒)を台本から作る(2026-11-14追加)。

Canvaの「スマホに負けない7ルール」(DAHZo1v-V_M、2026-11-01)と同じ形:
勉強風景の動画を背景に、白いカードにタイトルと①〜⑦を1つずつ出し、最後に
「詳細な解説はキャプションをcheck!!」「ここから積み上げていこう!」を出す。
Canvaの自動流し込み(有料のブランドテンプレート機能)が使えなくなったため、自前で描く。

使い方: python3 render_rules7.py <台本 task-<日付>-sumaho-001.md> <出力mp4>
背景: creative/ranking/assets/study_bg.mp4(Mixkit Free License・商用可・表記不要)
"""
import os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 15.0
HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "..", "ranking", "assets", "study_bg.mp4")
FD = ["/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/noto"]
T_TITLE, T_FIRST, T_STEP, T_CTA = 0.3, 1.6, 1.15, 10.4  # 秒


def F(s, w="Bold"):
    for d in FD:
        p = os.path.join(d, f"NotoSansCJK-{w}.ttc")
        if os.path.exists(p): return ImageFont.truetype(p, s)
    sys.exit("フォントがありません(fonts-noto-cjk)")


def parse(md):
    t = open(md, encoding="utf-8").read()
    sec = re.search(r"^## リール台本.*?(?=^## )", t + "\n## ", re.M | re.S)  # キャプション内の①〜⑦は拾わない
    t = sec.group(0) if sec else t
    m = re.search(r"\*\*タイトル\*\*[:：]\s*(.+)", t)
    items = re.findall(r"^([①②③④⑤⑥⑦].+)$", t, re.M)
    if not m or len(items) != 7:
        sys.exit("台本からタイトルと①〜⑦の7項目を読み取れません")
    return m.group(1).strip(), [i.strip() for i in items]


def title_lines(d, title, f, width):
    """タイトルを2行までに分ける(「の」「を」の直後など自然な位置を優先)"""
    if d.textlength(title, font=f) <= width: return [title]
    best = None
    for k in range(2, len(title) - 1):
        a, b = title[:k], title[k:]
        if max(d.textlength(a, font=f), d.textlength(b, font=f)) > width: continue
        cost = abs(len(a) - len(b)) - (6 if a[-1] in "のをにはがでと" else 0)
        if best is None or cost < best[0]: best = (cost, [a, b])
    return best[1] if best else [title]


def overlay(title, items, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if t < T_TITLE: return im
    a = min(1.0, (t - T_TITLE) / 0.35)
    card = (60, 300, 1020, 1640)
    d.rounded_rectangle(card, 8, fill=(255, 255, 255, int(245 * a)))
    # 上の飾り(手描き風のくるくる)
    for k in range(4):
        x = 360 + k * 90
        d.arc((x, 205, x + 90, 265), 200, 520, fill=(255, 255, 255, int(255 * a)), width=10)
    tf = F(84, "Bold"); lines = title_lines(d, title, tf, 860)
    y = 430 if len(lines) == 2 else 470
    for ln in lines:
        d.text((W // 2, y), ln, font=tf, fill=(17, 17, 17, int(255 * a)), anchor="mm"); y += 110
    y0 = 700
    for i, it in enumerate(items):
        ti = T_FIRST + i * T_STEP
        if t < ti: break
        b = min(1.0, (t - ti) / 0.25); dx = int((1 - b) * 40)
        f = F(56, "Bold")
        while d.textlength(it, font=f) > 860 and f.size > 36: f = F(f.size - 2, "Bold")
        d.text((110 - dx, y0 + i * 108), it, font=f, fill=(17, 17, 17, int(255 * b)), anchor="lm")
    if t >= T_CTA:
        c = min(1.0, (t - T_CTA) / 0.4)
        d.rounded_rectangle((110, 1480, 970, 1600), 60, fill=(17, 17, 17, int(235 * c)))
        d.text((W // 2, 1540), "詳細な解説はキャプションをcheck!!", font=F(48, "Black"), fill=(255, 255, 255, int(255 * c)), anchor="mm")
        d.text((W // 2, 1730), "ここから積み上げていこう！", font=F(64, "Black"), fill=(255, 255, 255, int(255 * c)),
               anchor="mm", stroke_width=8, stroke_fill=(17, 17, 17, int(255 * c)))
    return im


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    title, items = parse(sys.argv[1]); out = sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    vf = (f"[0:v]scale=-2:{H},crop={W}:{H},boxblur=6:1,eq=brightness=-0.08,fps={FPS}[bg];"
          f"[bg][1:v]overlay=0:0:format=auto,format=yuv420p[v]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", BG,
           "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
           "-f", "lavfi", "-t", str(DUR), "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", vf, "-map", "[v]", "-map", "2:a",
           "-c:v", "libx264", "-c:a", "aac", "-t", str(DUR), "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    import io
    cache = {}
    for n in range(int(DUR * FPS)):
        t = n / FPS
        key = round(t, 2) if any(abs(t - x) < 0.5 for x in [T_TITLE, T_CTA] + [T_FIRST + i * T_STEP for i in range(7)]) else "static" + str(sum(t >= T_FIRST + i * T_STEP for i in range(7))) + str(t >= T_CTA)
        if key not in cache:
            b = io.BytesIO(); overlay(title, items, t).save(b, "PNG"); cache[key] = b.getvalue()
        p.stdin.write(cache[key])
    p.stdin.close()
    if p.wait(): sys.exit("動画の書き出しに失敗しました")
    print(out)


if __name__ == "__main__":
    main()
