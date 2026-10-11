#!/usr/bin/env python3
"""台本(task-<date>-quiz-001.md)から「今日の1問」リール動画を作る。

使い方: python3 make_reel_from_draft.py <台本md> [出力mp4]
出力を省略すると daily/reel-<date>.mp4 に書く。
"""
import os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_CANDIDATES = [  # 先頭ほど優先(IPAゴシックが無ければ他の日本語書体で代用)
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf",
    "/usr/share/fonts/truetype/vlgothic/VL-Gothic-Regular.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

def find_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p): return p
    r = subprocess.run(["fc-list", ":lang=ja", "file"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        p = line.split(":")[0].strip()
        if p.lower().endswith((".ttf", ".otf", ".ttc")): return p
    return None

def find_ffmpeg():
    if shutil.which("ffmpeg"): return "ffmpeg"
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg"], check=False)
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None

def die(msg):
    print("ERROR:", msg, file=sys.stderr); sys.exit(1)

def parse(path):
    t = open(path, encoding="utf-8").read()
    m = re.search(r"^level:\s*(\S+)", t, re.M)
    q = re.search(r"^## 問題\s*\n(.+?)\n\s*\n", t + "\n\n", re.M | re.S)
    sec = re.search(r"^## 選択肢\s*\n(.*?)(?=^## |\Z)", t, re.M | re.S)
    o = re.findall(r"^([①②③④])\s*(.+)$", sec.group(1) if sec else "", re.M)
    if not (m and q) or len(o) != 4:
        die("台本からlevel/問題/選択肢①〜④を読み取れません")
    return m.group(1), " ".join(q.group(1).split()), [(c, s.strip()) for c, s in o]

def main():
    if len(sys.argv) < 2: die("台本mdを指定してください")
    draft = sys.argv[1]
    date = re.search(r"task-(\d{4}-\d{2}-\d{2})-quiz", draft)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        HERE, "daily", f"reel-{date.group(1) if date else 'today'}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ffmpeg = find_ffmpeg()
    if not ffmpeg: die("ffmpegがありません(imageio-ffmpegの導入も失敗)")
    font = find_font()
    if not font: die("日本語フォントが見つかりません")
    print("font:", font, "ffmpeg:", ffmpeg)
    try:
        import PIL  # noqa
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pillow"], check=False)
        try:
            import PIL  # noqa
        except ImportError:
            die("Pillowを使えません")
    level, q, opts = parse(draft)
    letters = dict(zip("①②③④", "ABCD"))
    opt_txt = "|".join(f"{letters[c]}) {s}" for c, s in opts)
    env = dict(os.environ, REEL_FONT=font, REEL_FFMPEG=ffmpeg)
    r = subprocess.run([sys.executable, os.path.join(HERE, "render_reel.py"),
                        level, q, opt_txt, out, os.path.join(HERE, "end_bg_1.jpg")], env=env)
    if r.returncode or not os.path.exists(out): die("動画の生成に失敗しました")
    print(out)

main()
