#!/usr/bin/env python3
"""②総合型・③スマホ対策のフィードを今日作るか、作るなら一覧型(list)か実話型(story)かを返す(2026-11-14追加)。

益田さんの決定(2026-11-14): 一覧型は2日に1本、実話型は週1本。
- 実話型は③(sumaho_habit)だけ、毎週土曜(実話は益田さん自身の話で、総合型の内容ではないため②では作らない)
- 一覧型は 2026-11-16 を起点に1日おき(②③とも同じ日)。③の土曜は実話型を優先する
使い方: python3 feed_kind.py <sumaho_habit|sougou> [YYYY-MM-DD]  → list / story / none
"""
import datetime as dt, sys

START = dt.date(2026, 11, 16)


def kind(dept, day):
    if day < START:
        return "none"
    if dept == "sumaho_habit" and day.weekday() == 5:
        return "story"
    return "list" if (day - START).days % 2 == 0 else "none"


if __name__ == "__main__":
    dept = sys.argv[1]
    d = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=9)).date()
    print(kind(dept, d))
