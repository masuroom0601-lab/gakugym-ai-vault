#!/usr/bin/env python3
"""台本(instagram_tiktokのスマホ対策枠draft)から「スマホ習慣セルフチェック」リールを作る。

2026-10-24追加: Tips形式のCanvaリールより英検クイズ形式の方が大幅に再生数が
高かった実測(vidIQ)を受け、スマホ対策枠も参加型(セルフチェック)形式で作る。

使い方: python3 make_checkup_from_draft.py <台本md> [出力mp4]
出力を省略すると checkup-daily/reel-<date>.mp4 に書く。
"""
import os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_CANDIDATES = [
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
    title = re.search(r"\*\*タイトル\*\*:\s*(.+)", t)
    items = re.findall(r"^\d+\.\s*(.+)$", t, re.M)
    verdict = re.search(r"\*\*診断ライン\*\*:\s*(.+)", t)
    if not (title and items and verdict):
        die("台本からタイトル/チェック項目/診断ラインを読み取れません(「## リール台本(スマホ習慣セルフチェック形式)」節の記法を確認してください)")
    if not (4 <= len(items) <= 8):
        die(f"チェック項目は4〜8個を想定していますが{len(items)}個でした")
    return title.group(1).strip(), [i.strip() for i in items], verdict.group(1).strip()

def main():
    if len(sys.argv) < 2: die("台本mdを指定してください")
    draft = sys.argv[1]
    date = re.search(r"task-(\d{4}-\d{2}-\d{2})-ig", draft)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        HERE, "checkup-daily", f"reel-{date.group(1) if date else 'today'}.mp4")
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
    title, items, verdict = parse(draft)
    env = dict(os.environ, REEL_FONT=font, REEL_FFMPEG=ffmpeg)
    bg = os.path.join(HERE, "end_bg_2.jpg")
    r = subprocess.run([sys.executable, os.path.join(HERE, "render_checkup.py"),
                        title, "|".join(items), verdict, out, bg], env=env)
    if r.returncode or not os.path.exists(out): die("動画の生成に失敗しました")
    print(out)

main()
