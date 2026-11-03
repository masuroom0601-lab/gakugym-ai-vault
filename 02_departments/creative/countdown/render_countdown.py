import os, sys, datetime, random
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


def first_saturday_on_or_after_jan13(year):
    # 2026-10-27修正: 大学入試センターの公式ルールは「1月13日以降の最初の
    # 土曜日及びその翌日の2日間」。以前は誤って「1月第2土曜日」で計算して
    # おり、2027年の場合に1月9日(誤り)と算出していた。正しくは1月13日
    # (2027年は水曜日)以降最初の土曜日である1月16日(益田さんのご指摘で
    # 判明・修正)。
    d = datetime.date(year, 1, 13)
    while d.weekday() != 5:  # 5 = 土曜日
        d += datetime.timedelta(days=1)
    return d


def next_kyotsu_test_date(today):
    candidate = first_saturday_on_or_after_jan13(today.year)
    if today > candidate:
        candidate = first_saturday_on_or_after_jan13(today.year + 1)
    return candidate


MESSAGES = [
    # 2026-10-27更新: 益田さんの指示により、固定の日替わりローテーション(1周5日)
    # から、プールの中からランダムに選ぶ方式に変更。毎日違うメッセージが出る
    # 体感を作るため、プールも拡充した(詳細: 01_HQ/roadmap.md参照)。
    "今日の積み重ねが、本番の自分をつくる",
    "スマホを置いた分だけ、力になる",
    "焦らなくていい。今日やることをやるだけ",
    "本番まで、まだ仕込める時間がある",
    "小さな習慣が、一番強い",
    "意志が弱いんじゃない。仕組みが無いだけ",
    "スマホを遠ざけた10分が、合否を分ける",
    "今日サボった分は、明日の自分が払う",
    "不安なら、不安なまま机に向かえばいい",
    "一番の近道は、今日を本気でやること",
    "通知を切った瞬間から、集中が始まる",
    "完璧じゃなくていい。昨日より1問多く",
    "周りと比べなくていい。昨日の自分とだけ比べる",
    "今日の1時間は、来年の自分への投資",
    "疲れた日は休んでいい。サボった日じゃなければ",
    "本番は、今日の積み重ねでしか作れない",
    "スマホを見た時間だけ、机に向かう時間が減る",
    "迷う時間があるなら、1問でも解こう",
    "自分を信じられないなら、今日の努力で信じさせればいい",
    "焦りは敵じゃない。それだけ本気な証拠",
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


def fit_font(d, text, size, min_size=28):
    # 長い一言は画面幅(左右60pxの余白)に収まるまで文字を小さくする
    while size > min_size and d.textlength(text, font=f(size)) > W - 120:
        size -= 2
    return f(size)


def draw_classic(im, d, days_left, msg, target):
    # 2026-11-03以前の「中央を空けない」デザイン(ca47ad6の直前の版を復元)
    bold(d, (540, 300), "共通テスト", fm(104), "white", "mm", 1)
    bold(d, (540, 430), "C O U N T D O W N", f(48), "white", "mm", 1)

    box_w, box_h = 760, 480
    box = (W // 2 - box_w // 2, 640, W // 2 + box_w // 2, 640 + box_h)
    d.rounded_rectangle(box, 40, fill="white")
    bold(d, (W // 2, 640 + box_h // 2), str(days_left), f(300), "#e60000", "mm", 4)

    bold(d, (540, 1200), "あと何日?", f(64), "white", "mm", 2)

    av = circular_avatar(150)
    if av is not None:
        im.paste(av, (W // 2 - 75, 1340), av)

    bold(d, (540, 1580), msg, fit_font(d, msg, 42), "white", "mm", 1)
    bold(d, (540, 1660), target.strftime("%Y年%m月%d日(土)午前9時30分開始予定"), f(32), "#aab4d6", "mm", 1)


def draw_lyrics(im, d, days_left, msg, target):
    # 2026-11-03レイアウト変更: ストーリーズで音源の「歌詞スタンプ」を載せると
    # 見出しと数字の間に入り込んで窮屈になる、との指摘を受け、画面中央
    # (y=LYRIC_TOP〜LYRIC_BOTTOM)を歌詞用の空きスペースとして何も置かないようにした。
    # 上は見出し+数字、下はアイコン+一言にまとめる。上端・下端はストーリーズの
    # UI(プロフィール名・返信欄)と重ならないよう余白を取る。
    # 2026-11-03調整: 空きが広すぎるとの指摘で、上を80px下げ下を150px上げた(空き約430px)
    LYRIC_TOP, LYRIC_BOTTOM = 860, 1250
    T = 80  # 上ブロックの下げ幅

    bold(d, (540, 270 + T), "共通テスト", fm(96), "white", "mm", 1)
    bold(d, (540, 375 + T), "C O U N T D O W N", f(44), "white", "mm", 1)

    # 白箱の中に「あと [数字] 日」を1行で収める
    box_w, box_h = 820, 320
    by0 = 450 + T
    d.rounded_rectangle((W // 2 - box_w // 2, by0, W // 2 + box_w // 2, by0 + box_h), 40, fill="white")
    num = str(days_left)
    fa, fn, fd = f(64), f(250), f(96)
    wa, wn, wd = d.textlength("あと", font=fa), d.textlength(num, font=fn), d.textlength("日", font=fd)
    gap = 18
    x = W // 2 - (wa + gap + wn + gap + wd) / 2
    cy = by0 + box_h // 2
    bold(d, (x, cy + 70), "あと", fa, "#16235c", "ls", 2)
    bold(d, (x + wa + gap + wn / 2, cy), num, fn, "#e60000", "mm", 4)
    bold(d, (x + wa + gap + wn + gap, cy + 70), "日", fd, "#16235c", "ls", 2)

    av = circular_avatar(120)
    if av is not None:
        im.paste(av, (W // 2 - 60, LYRIC_BOTTOM + 40), av)

    bold(d, (540, LYRIC_BOTTOM + 220), msg, fit_font(d, msg, 42), "white", "mm", 1)
    bold(d, (540, LYRIC_BOTTOM + 290), target.strftime("%Y年%m月%d日(土)午前9時30分開始予定"), f(32), "#aab4d6", "mm", 1)


def main():
    out_path = sys.argv[1]
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    # 第2引数(YYYY-MM-DD)で投稿日を指定可能(予約投稿用に先の日付分をまとめて作るため)
    today = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
    target = next_kyotsu_test_date(today)
    days_left = (target - today).days
    # 2026-11-03変更: 日ごとの独立ランダムだと連続する日で同じ文言が出たため、
    # 固定シードでシャッフルした並びを日付順に1つずつ使う方式にした
    # (ランダムな並びのまま、20日間は同じ文言が出ない)
    order = MESSAGES[:]
    random.Random("gakugym-countdown").shuffle(order)
    msg = order[today.toordinal() % len(order)]

    im, d = navy_bg()

    # 2026-11-03: デザインを2種類に分けた(益田さんの指示)。
    # - classic: 中央を空けない従来デザイン。ストーリーズの予約投稿は
    #   音源なしでしかできないため、予約投稿用はこちらを使う(daily_classic/に保存)
    # - lyrics: 中央に歌詞スタンプ用の空きを作ったデザイン(daily/に保存)
    style = os.environ.get("COUNTDOWN_STYLE", "lyrics")
    if style == "classic":
        draw_classic(im, d, days_left, msg, target)
    else:
        draw_lyrics(im, d, days_left, msg, target)

    im.save(out_path)
    print(f"days_left={days_left} target={target.isoformat()}")


if __name__ == "__main__":
    main()
