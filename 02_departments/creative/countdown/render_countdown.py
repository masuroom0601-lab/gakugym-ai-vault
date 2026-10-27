import os, sys, datetime
from PIL import Image, ImageDraw, ImageFont
# 2026-10-27追加: ③(習慣化メソッド発信アカウント、構想中)のストーリーズ用、
# 「共通テストまであと〇日」カウントダウン画像を日次生成するスクリプト。
# 英検はCBT化が進み単一の試験日訴求が弱くなったため、①向けに検討していた
# 「試験日カウントダウン企画」は撤回し、全受験生に刺さる共通テストの
# カウントダウンとして③に割り当てた(詳細: 01_HQ/roadmap.md 2026-10-27参照)。
# 学ジムのロゴ・サービス名は出さない(③は送客を狙わないため)。
#
# 【2026-10-27デザイン変更】益田さんが参考として共有してくれた、他塾(Z会東大
# コース)のXアカウントのカウントダウン投稿(紺地+ミンチョ体見出し+白箱に赤字の
# 大きな数字、というデザイン)を参考に、英検クイズリールと見た目が被らないよう
# 配色・フォント・レイアウトを一新した。ただし元投稿そのものの模倣にならない
# よう、アカウントの透かし文字(@ハンドルの縦書き)は入れない、配色は独自の紺、
# ボックスは角丸にする、など差別化した上で、ストーリーズの縦長(1080x1920)に
# 合わせてレイアウトを再構成している。

W, H = 1080, 1920
FONT = os.environ["REEL_FONT"]
MINCHO_FONT = os.environ.get("REEL_MINCHO_FONT", FONT)
BG_COLOR = "#16235c"
AVATAR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reel_quiz", "avatar.png")


def f(sz):
    return ImageFont.truetype(FONT, sz)


def fm(sz):
    return ImageFont.truetype(MINCHO_FONT, sz)


def bold(d, xy, t, font, fill, anchor="la", w=2):
    d.text(xy, t, font=font, fill=fill, anchor=anchor, stroke_width=w, stroke_fill=fill)


def navy_bg():
    im = Image.new("RGB", (W, H), BG_COLOR)
    d = ImageDraw.Draw(im)
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

    im, d = navy_bg()

    # 見出し(ミンチョ体で「共通テスト」、下にアルファベットで「COUNTDOWN」)
    bold(d, (540, 300), "共通テスト", fm(104), "white", "mm", 1)
    bold(d, (540, 430), "C O U N T D O W N", f(48), "white", "mm", 1)

    # 白箱+赤字の大きな数字(角丸にして元ネタの直角ボックスと差別化)
    box_w, box_h = 760, 480
    box = (W // 2 - box_w // 2, 640, W // 2 + box_w // 2, 640 + box_h)
    d.rounded_rectangle(box, 40, fill="white")
    bold(d, (W // 2, 640 + box_h // 2), str(days_left), f(300), "#e60000", "mm", 4)

    bold(d, (540, 1200), "あと何日?", f(64), "white", "mm", 2)

    av = circular_avatar(150)
    if av is not None:
        im.paste(av, (W // 2 - 75, 1340), av)

    bold(d, (540, 1580), msg, f(42), "white", "mm", 1)
    bold(d, (540, 1660), target.strftime("%Y年%m月%d日(土)実施予定"), f(32), "#aab4d6", "mm", 1)

    im.save(out_path)
    print(f"days_left={days_left} target={target.isoformat()}")


if __name__ == "__main__":
    main()
