#!/usr/bin/env bash
# Kindle(KDP)用のEPUBを作る。
# 使い方: tools/ebook/build.sh <book-slug>
#   02_departments/ebook/drafts/<book-slug>/ の *.md をファイル名順に連結し
#   (plan.md は企画書なので除外)、build/<book-slug>.epub を出力する。
#   metadata.yml があればタイトル・著者名に使い、cover.jpg / cover.png があれば表紙にする。
set -euo pipefail

slug="${1:?book-slug を指定してください(例: tools/ebook/build.sh oyano-koekake)}"
root="$(cd "$(dirname "$0")/../.." && pwd)"
dir="$root/02_departments/ebook/drafts/$slug"
[ -d "$dir" ] || dir="$root/02_departments/ebook/review/$slug"
[ -d "$dir" ] || { echo "見つかりません: drafts/$slug または review/$slug" >&2; exit 1; }
command -v pandoc >/dev/null || { echo "pandoc が必要です(apt install pandoc 等)" >&2; exit 1; }

mapfile -t chapters < <(find "$dir" -maxdepth 1 -name '*.md' ! -name 'plan.md' | sort)
[ "${#chapters[@]}" -gt 0 ] || { echo "$dir に原稿(*.md)がありません" >&2; exit 1; }

args=(--from markdown-yaml_metadata_block --to epub3 --toc --toc-depth=1
      --split-level=1 --css "$root/tools/ebook/kindle.css")
[ -f "$dir/metadata.yml" ] && args+=(--metadata-file "$dir/metadata.yml")
for c in cover.jpg cover.png; do
  [ -f "$dir/$c" ] && { args+=(--epub-cover-image "$dir/$c"); break; }
done

mkdir -p "$dir/build"
out="$dir/build/$slug.epub"
pandoc "${args[@]}" -o "$out" "${chapters[@]}"
echo "作成しました: $out(${#chapters[@]}ファイル)"
grep -l '【要加筆' "${chapters[@]}" 2>/dev/null | sed 's/^/警告: 【要加筆】が残っています: /' >&2 || true
