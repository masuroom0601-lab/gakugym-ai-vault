#!/bin/bash
# 全7話の原稿を、今の文字入れの仕組みで組み直し、PDFを作る(2026-11-26)
# 1) Kaggleの絵のページ: page_compose.py で組み直す(絵は作業フォルダ S の中)
# 2) GPTで描いたページ: gpt_redraw/rebuild_gpt.sh で文字を入れ直し、names/epNN/gpt/ に置く(build_pdf.py はこちらを優先する)
M=/home/user/gakugym-ai-vault/02_departments/manga
S=${S:-/tmp/claude-0/-home-user-gakugym-ai-vault/95c9f1fa-8794-5a83-b244-1f63d9e3d53d/scratchpad}
cd $M
pk() { python3 -c "import sys; sys.path.insert(0,'$S'); from $1 import P; print(','.join(f'{k}={v}' for k,v in P[$2].items()))"; }
comp() { python3 tools/page_compose.py names/ep0$1_name.py $2 $3 names/ep0$1/pages/p$(printf %02d $2).png --pick $4 >/dev/null 2>>$S/rebuild_err.txt || echo "第$1話 $2ページ 失敗"; }
gptpage() { [ -f names/ep0$1/gpt/p$(printf %02d $2).png ]; }
: > $S/rebuild_err.txt
# 第1話
for pg in $(seq 1 33); do
  gptpage 1 $pg && continue
  case $pg in
    2) comp 1 2 $S/ep1fix 1=s1,2=c,3=s2,4=c ;;
    13) comp 1 13 $S/ep1fix 1=s1,2=s2,3=s1,4=s32,5=s2,6=e,7=s2 ;;
    33) comp 1 33 $S/ep1p33 1=s1,2=s2 ;;
    *) comp 1 $pg $S/ep1v3 $(pk picks_v3 $pg) ;;
  esac
done; echo "第1話 組み直し済み"
# 第2話
for pg in $(seq 1 20); do gptpage 2 $pg && continue; comp 2 $pg $S/ep2final $(pk ep2picks2 $pg); done; echo "第2話 組み直し済み"
# 第3〜7話
for ep in 3 4 5 6 7; do
  while read pg p; do [ -z "$pg" ] && continue; gptpage $ep $pg && continue; comp $ep $pg $S/ep${ep}final $p; done < names/ep0${ep}_picks.txt
  echo "第${ep}話 組み直し済み"
done
# GPTのページ
bash gpt_redraw/rebuild_gpt.sh
python3 tools/build_pdf.py
