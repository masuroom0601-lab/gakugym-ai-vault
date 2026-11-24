"""各話のシナリオ(scenarios/epXX_script.md)から、全話をまとめた scenarios/full_script.md を組み立てる。
手で同期すると食い違いが起きるため、各話のファイルを正として、全話版は必ずこのプログラムで作り直す。

使い方: python3 02_departments/manga/tools/build_full_script.py
- 各話の「本文」(≪page≫〜最後のページ)だけを載せる。各話の末尾の「決定事項」などのメモは載せない
- 書式の説明コメントは省き、「この話の役割」のコメントは残す
"""
import glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "..", "scenarios")
TITLE = "勇者サークルを追放されたけど、CAPSの人たちが温かく迎え入れてくれたのでそのまま幸せになります。ついでに強いガクチカも作ります"

eps = []
for p in sorted(glob.glob(os.path.join(SC, "ep[0-9][0-9]_script.md"))):
    t = open(p, encoding="utf-8").read()
    fm = dict(re.findall(r"^(\w+): (.*)$", t.split("---")[1], re.M))
    body = t.split("---", 2)[2]
    body = re.sub(r"<!-- 書式[^>]*?-->\n?", "", body)
    body = body.split("\n---\n")[0].strip("\n")
    body = re.sub(r"^≪page", "#### ≪page", body, flags=re.M)
    pages = int(re.match(r"\d+", fm["pages"]).group())
    eps.append((fm["title"], pages, os.path.basename(p), body))

out = [f"# {TITLE}", "", f"## シナリオ全文(全{len(eps)}話)", "",
       f"各話の元ファイルは `{eps[0][2]}`〜`{eps[-1][2]}`。このファイルは tools/build_full_script.py で自動で作る(手で直さない)。", ""]
out += [f"- {t}({n}ページ)" for t, n, _, _ in eps]
out += ["", f"**合計 {sum(n for _, n, _, _ in eps)}ページ**", ""]
for t, n, _, body in eps:
    out += ["", "---", "", f"## {t}", "", body]
open(os.path.join(SC, "full_script.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"全{len(eps)}話・合計{sum(n for _, n, _, _ in eps)}ページで、full_script.md を作り直しました")
