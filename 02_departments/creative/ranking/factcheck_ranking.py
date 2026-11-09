#!/usr/bin/env python3
"""倍率ランキングのデータ(JSON)を、大学公式の出典と機械的に突き合わせる(2026-11-03追加)。

校正担当(.github/workflows/ranking-factcheck.yml)が毎回これを実行し、結果を見たうえで
行と資料の対応・年度・倍率の定義を目で確認して合否を付ける。描画スクリプトは
校正担当の合格(factcheck.status == "ok")が無いデータでは本番の動画を作らない。

チェック内容(行ごと):
  1. 出典URLが取得できる(PDFはテキスト化)
  2. 出典の本文に、データの年度(例「2026年度」)が書かれている
     (2026-11-09、益田さん承認: 出典PDFの本文に年度が無い場合は、データの source.year_page に
     大学公式の掲載ページを書けば、そのページに「2026年度」の記載と出典URLへのリンクの両方が
     あることを確認して年度の根拠とみなす。ページは出典と同じ大学のドメインに限る)
  3. 出典の本文に、志願者(または受験者)数と合格者数がそのまま載っている
     (「4,764」「4764」どちらの書き方でも可。看護医療の男女別のように合計が本文に無い
     場合や、学科・方式を合計した行・補欠合格を足した行は"parts"に内訳(examinees/applicants/passers それぞれのリスト)を書けば、内訳が本文にあり合計が一致することを確認する)
  4. 倍率 = 分子 ÷ 合格者数 を小数1桁に丸めた値と一致する
  5. 「非公開」の行は出典URLが空であること
使い方: python3 factcheck_ranking.py <data.json> [...]
"""
import json, os, re, subprocess, sys, tempfile, urllib.request
from decimal import Decimal, ROUND_HALF_UP

UA = "Mozilla/5.0 (compatible; gakugym-factcheck/1.0)"
_cache = {}


def text_of(url):
    if url in _cache:
        return _cache[url]
    ref = re.match(r"https?://[^/]+/", url).group(0)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": ref})
    raw = urllib.request.urlopen(req, timeout=60).read()
    if raw[:5] == b"%PDF-":
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(raw); f.flush()
            t = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
    else:
        t = re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "replace"))
    t = t.translate(str.maketrans("０１２３４５６７８９，", "0123456789,"))
    _cache[url] = t
    dump = os.environ.get("FACTCHECK_DUMP")
    if dump:  # 校正担当AIが同じ本文を読めるよう保存しておく(大学サイトはcurlだと弾かれることがある)
        os.makedirs(dump, exist_ok=True)
        idx = len(os.listdir(dump)) // 2 + 1
        open(f"{dump}/{idx}.txt", "w", encoding="utf-8").write(t)
        open(f"{dump}/{idx}.url", "w").write(url)
    return t


_raw = {}


def raw_of(url):
    if url in _raw:
        return _raw[url]
    ref = re.match(r"https?://[^/]+/", url).group(0)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": ref})
    _raw[url] = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    return _raw[url]


def year_page_ok(d, year, src_url):
    """出典本文に年度が無いとき、公式の掲載ページで年度を確かめる。理由を返す(OKならNone)"""
    page = (d.get("source") or {}).get("year_page")
    if not page:
        return "出典に「%s」の記載が無い(source.year_page も未指定)" % year
    host = lambda u: re.match(r"https?://([^/]+)/", u).group(1)
    if host(page) != host(src_url):
        return "year_page が出典と別のドメイン"
    try:
        raw = raw_of(page)
    except Exception as e:
        return "year_page を取得できない (%s)" % e
    flat = re.sub(r"\s+", "", re.sub(r"<[^>]+>", " ", raw)).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    path = re.sub(r"https?://[^/]+", "", src_url)
    if year not in flat:
        return "year_page に「%s」の記載が無い" % year
    if src_url not in raw and path not in raw:
        return "year_page に出典へのリンクが無い"
    return None


def has_num(t, n):
    pat = r"(?<![\d,])(%s|%s)(?![\d,])" % (re.escape(f"{n:,}"), re.escape(str(n)))
    return re.search(pat, t) is not None


def check(path):
    d = json.load(open(path, encoding="utf-8"))
    key = d.get("count_key", "examinees")
    year = f"{d['year']}年度"
    ok, lines = True, []
    for r in d["rows"]:
        name = r["name"]
        if r.get("ratio") is None and r.get("passers") == 0 and r.get("source_url"):
            # 2026-11-05: 合格者0人の入試は「非公開」ではなく倍率を出せないだけ。数字を出典と照合する
            try:
                t = text_of(r["source_url"])
                good = (year in re.sub(r"\s+", "", t) or year_page_ok(d, year, r["source_url"]) is None) and has_num(t, r[key])
            except Exception as e:
                good = False
            lines.append(f"{'OK ' if good else 'NG '} {name}: 合格者0人({key}={r.get(key)}、倍率は出せない)")
            ok &= good
            continue
        if r.get("ratio") is None:
            good = not r.get("source_url")
            lines.append(f"{'OK ' if good else 'NG '} {name}: 非公開(出典URLなし)")
            ok &= good
            continue
        try:
            t = text_of(r["source_url"])
        except Exception as e:
            lines.append(f"NG  {name}: 出典を取得できない ({e})"); ok = False; continue
        errs = []
        if year not in re.sub(r"\s+", "", t):
            why = year_page_ok(d, year, r["source_url"])
            if why:
                errs.append(why)
        n, p = r[key], r["passers"]
        parts = r.get("parts", {})
        if key in parts:
            if sum(parts[key]) != n or not all(has_num(t, x) for x in parts[key]):
                errs.append(f"{key}の内訳{parts[key]}が出典と合わない")
        elif not has_num(t, n):
            errs.append(f"{key}={n} が出典に無い")
        if "passers" in parts:
            if sum(parts["passers"]) != p or not all(has_num(t, x) for x in parts["passers"]):
                errs.append(f"passersの内訳{parts['passers']}が出典と合わない")
        elif not has_num(t, p):
            errs.append(f"passers={p} が出典に無い")
        # 四捨五入(Pythonのroundは2.25→2.2になるため使わない)
        if float((Decimal(n) / Decimal(p)).quantize(Decimal("0.1"), ROUND_HALF_UP)) != r["ratio"]:
            errs.append(f"倍率 {r['ratio']} ≠ {n}/{p}={n / p:.3f}")
        lines.append(("OK " if not errs else "NG ") + f" {name}: {n}/{p}={r['ratio']}倍" + ("" if not errs else " ← " + " / ".join(errs)))
        ok &= not errs
    return ok, lines


if __name__ == "__main__":
    all_ok = True
    for p in sys.argv[1:]:
        ok, lines = check(p)
        print(f"## {p}: {'機械チェック合格' if ok else '機械チェック不合格'}")
        print("\n".join(lines))
        all_ok &= ok
    sys.exit(0 if all_ok else 1)
