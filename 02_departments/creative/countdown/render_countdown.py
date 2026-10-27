import os, sys, datetime
from PIL import Image, ImageDraw, ImageFont
# 2026-10-27追加: ③(習慣化メソッド発信アカウント、構想中)のストーリーズ用、
# 「共通テストまであと〇日」カウントダウン画像を日次生成するスクリプト。
# 英検はCBT化が進み単一の試験日訴求が弱くなったため、①向けに検討していた
# 「試験日カウントダウン企画」は撤回し、全受験生に刺さる共通テストの
# カウントダウンとして③に割り当てた(詳細: 01_HQ/roadmap.md 2026-10-27参照)。
# 学ジムのロゴ・サービス名は出さない(③は送客を狙わないため)。

W, H = 1080, 1920
FONT = os.environ["REEL_FONT"]
AVATAR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reel_quiz", "avatar.png")


def f(sz):
    return ImageFont.truetype(FONT, sz)


def bold(d, xy, t, font, fill, anchor="la", w=2):
    d.text(xy, t, font=font, fill=fill, anchor=anchor, stroke_width=w, stroke_fill=fill)


def dotted_bg():
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    step = 90
    for gy in range(-step, H + step, step):
        for gx in range(-step, W + step, step):
            d.ellipse((gx - 6, gy - 6, gx + 6, gy + 6), fill="#e3eafa")
    return im, d


def nth_weekday_of_month(year, month, weekday, n):
    d = datetime.date(year, month, 1)
    count = 0
    while True:
        if d.weekday() == weekday:
            count += 1
            if count == n:
                return d
        d += datetime.timedelta(days=1)


def next_kyotsu_test_date(today):
    # 共通テストは例年1月第2土曜日(直近の実施傾向に基づく仮定。
    # 大学入試センターの正式発表と異なる場合は、この関数の第2引数(月内の週番号)を
    # 要確認・要修正)
    SAT = 5
    candidate = nth_weekday_of_month(today.year, 1, SAT, 2)
    if today > candidate:
        candidate = nth_weekday_of_month(today.year + 1, 1, SAT, 2)
    return candidate


MESSAGES = [
    "今日の積み重ねが、本番の自分をつくる",
    "スマホを置いた分だけ、力になる",
    "焦らなくていい。今日やることをやるだけ",
    "本番まで、まだ仕込める時間がある",
    "小さな習慣が、一番強い",
]


def circular_avatar(size):
    if not os.path.exists(AVATAR_PATH):
        return None
    av = Image.open(AVATAR_PATH).convert("RGB").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size))
    out.paste(av, (0, 0), mask)
    return out


def main():
    out_path = sys.argv[1]
    today = datetime.date.today()
    target = next_kyotsu_test_date(today)
    days_left = (target - today).days
    msg = MESSAGES[today.toordinal() % len(MESSAGES)]

    im, d = dotted_bg()
    d.rounded_rectangle((80, 150, 560, 280), 10, fill="#4472c4")
    bold(d, (320, 215), "共通テストまで", f(52), "white", "mm", 1)

    bold(d, (540, 850), str(days_left), f(420), "#e60000", "mm", 6)
    bold(d, (540, 1150), "日", f(120), "#111111", "mm", 3)

    av = circular_avatar(140)
    if av is not None:
        im.paste(av, (W // 2 - 70, 1320), av)

    bold(d, (540, 1540), msg, f(44), "#111111", "mm", 1)
    bold(d, (540, 1620), target.strftime("%Y年%m月%d日(土)実施予定"), f(34), "#666666", "mm", 1)

    im.save(out_path)
    print(f"days_left={days_left} target={target.isoformat()}")


if __name__ == "__main__":
    main()
