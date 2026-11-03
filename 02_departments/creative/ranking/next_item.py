#!/usr/bin/env python3
"""作成順(queue.json)から、まだ動画になっていない次の1本を選ぶ(2026-11-03追加)。
出力(GITHUB_OUTPUT形式): slug / university / short / type / kind / data(データJSONのパス)
"""
import glob, json, os

ROOT = "02_departments"
q = json.load(open(f"{ROOT}/sougou/ranking/queue.json", encoding="utf-8"))["items"]
for it in q:
    if it.get("done"):
        continue
    if glob.glob(f"{ROOT}/creative/ranking/daily/*-{it['slug']}-{it['kind']}.mp4"):
        continue
    data = f"{ROOT}/sougou/ranking/data/{it['slug']}-{it['kind']}.json"
    for k in ("slug", "university", "short", "type", "kind"):
        print(f"{k}={it[k]}")
    print(f"data={data}")
    break
else:
    print("slug=")
