#!/usr/bin/env python3
"""倍率ランキング動画のキャプションを、読みやすいMarkdownファイルに書き出す(2026-11-06追加)。
使い方: python3 write_caption.py <data.json> <out.md> <動画のパス>
キャプション本文はデータJSONの "caption" をそのまま使う(数字はファクトチェック済みのデータ由来)。
"""
import json, sys

data, out, video = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(data, encoding="utf-8"))
fc = d.get("factcheck", {})
hidden = [r["name"] for r in d["rows"] if r.get("ratio") is None]
lines = [
    f"# {d['university']} {d['selection']} 倍率ランキング({d['year']}年度)",
    "",
    f"- 動画: `{video}`",
    f"- データ: `{data}`",
    f"- ファクトチェック: {'合格' if fc.get('status') == 'ok' else fc.get('status', '未実施')}({fc.get('checked_at', '')})",
]
if hidden:
    lines.append(f"- 倍率を出していない行: {'、'.join(hidden)}")
lines += ["", "## 投稿用キャプション(そのままコピーして使う)", "", "```", d.get("caption", "(キャプション未作成)").strip(), "```", ""]
open(out, "w", encoding="utf-8").write("\n".join(lines))
print(out)
