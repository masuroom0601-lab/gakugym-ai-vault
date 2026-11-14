#!/usr/bin/env python3
"""「爆速英単語」リールを単語リスト(JSON)から作る(2026-11-14追加)。

1語1.5秒で英単語→0.5秒後に日本語訳を表示し、英単語の読み上げ音声を重ねる。
40語なら本編60秒(+冒頭1.5秒・締め2.5秒)。

使い方:
  python3 make_vocab_reel.py lists/pre1-001.json out/pre1-001.mp4            # 読み上げ音声あり(edge-tts)
  python3 make_vocab_reel.py lists/pre1-001.json out/pre1-001.mp4 --no-audio # 音声なし(見た目の確認用)

必要なもの: Pillow、ffmpeg、日本語フォント(fonts-noto-cjk)、音声ありなら edge-tts(ネット接続が必要)
"""
import json, os, subprocess, sys, tempfile

W, H = 1080, 1920
INTRO, PER, REVEAL, OUTRO = 1.5, 1.5, 0.5, 2.5
VOICE = "en-US-AriaNeural"
BLUE, RED, INK, SUB = "#4472c4", "#e60000", "#111111", "#555555"
FONT_DIRS = ["/usr/share/fonts/opentype/noto", "/usr/share/fonts/truetype/noto"]


def font_path(weight):
    for d in FONT_DIRS:
        p = os.path.join(d, f"NotoSansCJK-{weight}.ttc")
        if os.path.exists(p):
            return p
    for d in FONT_DIRS:  # Black が無い環境では Bold で代用
        p = os.path.join(d, "NotoSansCJK-Bold.ttc")
        if os.path.exists(p):
            return p
    sys.exit("日本語フォントがありません(apt-get install fonts-noto-cjk)")


def F(size, weight="Black"):
    from PIL import ImageFont
    return ImageFont.truetype(font_path(weight), size)


def fit(d, text, weight, max_size, max_w):
    s = max_size
    while s > 40 and d.textlength(text, font=F(s, weight)) > max_w:
        s -= 4
    return F(s, weight)


def background():
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    for y in range(0, H + 90, 90):  # 英検クイズのリールと同じ水玉の地
        for x in range(0, W + 90, 90):
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill="#e3eafa")
    return im, d


def header(d, level, sub):
    d.rounded_rectangle((70, 120, 470, 230), 16, fill=BLUE)
    d.text((270, 175), level, font=F(64), fill="white", anchor="mm")
    d.text((W // 2, 360), "爆速英単語", font=F(150), fill=RED, anchor="mm",
           stroke_width=4, stroke_fill="white")
    d.text((W // 2, 500), sub, font=F(60, "Bold"), fill=INK, anchor="mm")
    d.line((70, 580, W - 70, 580), fill="#cccccc", width=4)


def word_frame(level, sub, i, n, en, ja):
    im, d = background()
    header(d, level, sub)
    d.text((W // 2, 660), f"{i} / {n}", font=F(56, "Bold"), fill=SUB, anchor="mm")
    d.rounded_rectangle((60, 720, W - 60, 1300), 40, fill="white", outline=BLUE, width=8)
    d.text((W // 2, 900), en, font=fit(d, en, "Bold", 150, W - 260), fill=INK, anchor="mm")
    if ja:
        d.line((200, 1020, W - 200, 1020), fill="#dddddd", width=4)
        d.text((W // 2, 1150), ja, font=fit(d, ja, "Black", 110, W - 260), fill=RED, anchor="mm")
    # 進み具合のバー。下端はInstagramのキャプション等に隠れるため、文字は1600px より上に置く
    d.rounded_rectangle((90, 1360, W - 90, 1400), 20, fill="#e3eafa")
    d.rounded_rectangle((90, 1360, 90 + (W - 180) * i // n, 1400), 20, fill=BLUE)
    d.rounded_rectangle((140, 1460, W - 140, 1580), 60, fill=BLUE)
    d.text((W // 2, 1520), "保存して何度も見返そう!", font=F(56), fill="white", anchor="mm")
    return im


def intro_frame(level, sub):
    im, d = background()
    d.rounded_rectangle((W // 2 - 220, 560, W // 2 + 220, 680), 20, fill=BLUE)
    d.text((W // 2, 620), level, font=F(72), fill="white", anchor="mm")
    d.text((W // 2, 860), "爆速英単語", font=F(190), fill=RED, anchor="mm",
           stroke_width=5, stroke_fill="white")
    d.text((W // 2, 1060), sub, font=F(96), fill=INK, anchor="mm")
    d.text((W // 2, 1240), "全部わかるかな?", font=F(72, "Bold"), fill=SUB, anchor="mm")
    return im


def outro_frame(level, n):
    im, d = background()
    d.text((W // 2, 640), f"{level}の{n}語", font=F(84), fill=INK, anchor="mm")
    d.text((W // 2, 800), "全部わかった?", font=F(140), fill=RED, anchor="mm",
           stroke_width=4, stroke_fill="white")
    d.text((W // 2, 1020), "保存して試験前に", font=F(88), fill=INK, anchor="mm")
    d.text((W // 2, 1140), "もう1回見よう!", font=F(88), fill=INK, anchor="mm")
    d.rounded_rectangle((150, 1300, W - 150, 1440), 70, fill=BLUE)
    d.text((W // 2, 1370), "フォローで続きも見られるよ", font=F(52), fill="white", anchor="mm")
    return im


def tts(words, outdir):
    import asyncio, edge_tts

    async def run():
        for k, w in enumerate(words):
            await edge_tts.Communicate(w, VOICE, rate="+10%").save(os.path.join(outdir, f"{k:03d}.mp3"))
    asyncio.run(run())


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    src, out = args
    audio = "--no-audio" not in sys.argv
    data = json.load(open(src, encoding="utf-8"))
    level, words = data["level"], data["words"]
    n = len(words)
    sub = f"{round(n * PER)}秒で{n}単語"
    tmp = tempfile.mkdtemp()

    # 画面(同じ画面が続く区間は同じ画像を使う)
    seq = [(intro_frame(level, sub), INTRO)]
    for i, (en, ja) in enumerate(words, 1):
        seq.append((word_frame(level, sub, i, n, en, None), REVEAL))
        seq.append((word_frame(level, sub, i, n, en, ja), PER - REVEAL))
    seq.append((outro_frame(level, n), OUTRO))
    total = INTRO + n * PER + OUTRO
    FPS = 30
    # 2026-11-14: ffmpeg の concat(画像+長さ指定)は最後の画面が欠けて動画が1.5秒短くなったため、
    # 30fpsの全コマ分のPNGを順に流し込む方式にした(同じ画面は同じPNGを繰り返し送るだけ)
    pngs = []
    for im, dur in seq:
        import io
        b = io.BytesIO(); im.save(b, "PNG"); pngs.append((b.getvalue(), dur))

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
           "-c:v", "png", "-i", "-"]
    if audio:
        tts([w for w, _ in words], tmp)
        for k in range(n):
            cmd += ["-i", os.path.join(tmp, f"{k:03d}.mp3")]
        parts = []
        for k in range(n):
            ms = int((INTRO + k * PER + 0.05) * 1000)
            parts.append(f"[{k + 1}:a]adelay={ms}|{ms}[a{k}]")
        mix = "".join(f"[a{k}]" for k in range(n))
        fc = ";".join(parts) + f";{mix}amix=inputs={n}:normalize=0,apad,atrim=0:{total}[aout]"
        cmd += ["-filter_complex", fc, "-map", "0:v", "-map", "[aout]"]
    else:
        cmd += ["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a"]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-t", str(total), "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    done = 0.0; frames = 0
    for data, dur in pngs:
        done += dur
        while frames < round(done * FPS):
            proc.stdin.write(data); frames += 1
    proc.stdin.close()
    if proc.wait():
        sys.exit("動画の書き出しに失敗しました")
    print(out, f"{total}秒")


if __name__ == "__main__":
    main()
