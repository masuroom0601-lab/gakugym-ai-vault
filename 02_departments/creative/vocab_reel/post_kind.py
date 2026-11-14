#!/usr/bin/env python3
"""①英検アカウントの今日の投稿が「英検クイズ」か「爆速英単語」かを返す(2026-11-14追加、益田さん指示)。

2つのリールを1日おきに交互に投稿する。2026-11-14(クイズ)を起点に、
偶数日目=quiz、奇数日目=vocab。日付はJSTで判定する。

使い方: python3 post_kind.py [YYYY-MM-DD]  → quiz または vocab を出力
"""
import datetime as dt, sys

START = dt.date(2026, 11, 14)  # この日は英検クイズ


def kind(day):
    return "quiz" if (day - START).days % 2 == 0 else "vocab"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        d = dt.date.fromisoformat(sys.argv[1])
    else:
        d = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)).date()
    print(kind(d))
