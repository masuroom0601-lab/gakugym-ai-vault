#!/usr/bin/env python3
"""英検クイズ台本の問題文が、リール動画の画面で何行になるかを数える(2026-11-13追加)。

益田さんの分析: 問題文が2行の投稿は伸び(12.5万回・4.6万回)、3行は1万回台、
4行以上は1000回未満もある。そのため「問題文は動画上で2行以内」をルールにした。
台本担当(x-threads-daily-draft.yml)と校正担当(proofreading-daily-check.yml)が
このスクリプトで機械的に行数を確かめる。

使い方:
  python3 check_question_lines.py <台本md>         # 台本の「## 問題」を数える
  python3 check_question_lines.py --text "英文"     # 作成中の英文を数える
3行以上なら終了コード1。

折り返しの計算は render_reel.py の wrap()(フォント58px・幅920px・単語単位)と同じ。
render_reel.py の文字サイズや幅を変えたら、ここの FONT_SIZE / MAX_WIDTH も合わせること。
"""
import os, re, sys

MAX_LINES = 2
FONT_SIZE = 58
MAX_WIDTH = 920
FONT_CANDIDATES = [  # make_reel_from_draft.py と同じ順(動画と同じ書体で測るため)
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def question_of(path):
    t = open(path, encoding="utf-8").read()
    m = re.search(r"^## 問題\s*\n(.+?)\n\s*\n", t + "\n\n", re.M | re.S)
    if not m:
        sys.exit("台本から「## 問題」を読み取れません: " + path)
    return " ".join(m.group(1).split())


def wrap(text):
    from PIL import Image, ImageDraw, ImageFont
    font_path = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
    if not font_path:
        sys.exit("日本語フォントがありません(apt-get install fonts-ipafont-gothic)")
    font = ImageFont.truetype(font_path, FONT_SIZE)
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines, cur = [], ""
    for word in text.split(" "):
        test = (cur + " " + word).strip()
        if d.textlength(test, font=font) <= MAX_WIDTH:
            cur = test
        else:
            lines.append(cur); cur = word
    lines.append(cur)
    return lines


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--text":
        q = " ".join(sys.argv[2].split())
    elif len(sys.argv) == 2:
        q = question_of(sys.argv[1])
    else:
        sys.exit(__doc__)
    lines = wrap(q)
    for i, l in enumerate(lines, 1):
        print(f"{i}行目: {l}")
    ok = len(lines) <= MAX_LINES
    print(f"動画上の行数: {len(lines)}行 → {'OK' if ok else f'NG({MAX_LINES}行以内にすること)'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
