import os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
# 2026-10-24追加: 「スマホ対策」コンテンツ用の参加型(セルフチェック)リール生成スクリプト。
# 英検クイズ(render_reel.py)がTips形式のCanvaリールより大幅に再生数が高いことが
# vidIQでの実測で判明したため、同じ「参加させる・一瞬で理解できる・テンポよく進む」
# 構造を流用し、スマホ習慣のセルフチェック形式で作る(詳細: 01_HQ/roadmap.md参照)。
W,H,FPS=1080,1920,30
FONT=os.environ["REEL_FONT"]; FFMPEG=os.environ.get("REEL_FFMPEG","ffmpeg")
title, items, verdict, out = sys.argv[1], sys.argv[2].split("|"), sys.argv[3], sys.argv[4]
ITEM=2.2; INTRO=1.8; VERDICT=2.8; CTA=3.0
# 2026-11-03追加: 診断の切り口を2種類で交互にA/Bテストする(益田さんの指示)。
# standard=スマホ依存度、dopamine=「ドーパミン中毒」(ゲーム・動画・集中力まで広げた版)
VARIANT=os.environ.get("CHECKUP_VARIANT","standard")
LABELS={
    "standard":{"badge":"スマホ習慣","meter":"スマホ依存 危険度","cta":"スマホ対策も見逃さない!"},
    "dopamine":{"badge":"ドーパミン","meter":"ドーパミン中毒 危険度","cta":"集中力の戻し方も見逃さない!"},
}[VARIANT if VARIANT in ("standard","dopamine") else "standard"]
AVATAR_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"avatar.png")
def circular_avatar(size):
    if not os.path.exists(AVATAR_PATH): return None
    av=Image.open(AVATAR_PATH).convert("RGB").resize((size,size),Image.LANCZOS)
    mask=Image.new("L",(size,size),0); ImageDraw.Draw(mask).ellipse((0,0,size,size),fill=255)
    out=Image.new("RGBA",(size,size)); out.paste(av,(0,0),mask)
    return out
def f(sz): return ImageFont.truetype(FONT, sz)
def bold(d,xy,t,font,fill,anchor="la",w=2):
    d.text(xy,t,font=font,fill=fill,anchor=anchor,stroke_width=w,stroke_fill=fill)
CLOSE="、。,.!?!?」』”)ー"
def _kata(c): return "ァ"<=c<="ヺ" or c=="ー"
def _kanji(c): return "一"<=c<="鿿"
def _hira(c): return "ぁ"<=c<="ゖ"
QUOTES='"“”「」『』'
def _break_cost(s,k):
    # s[:k] と s[k:] の間で改行するコスト(小さいほど自然)
    a,b=s[k-1],s[k]
    if b in CLOSE or a in "「『“(": return 10**6
    q=sum(1 for c in s[:k] if c in '"“”')
    if q%2==1 or s[:k].count("「")>s[:k].count("」"): return 60  # "…"や「…」の途中
    if b in "をがにでとはのもへや" and not _hira(a): return 35  # 行頭に助詞が来る
    if a in "、。!?!?」』”)" or (a=='"' and q%2==0): return 0
    if b in "「『“(" or b=='"': return 0
    if b in "をがにでとはのもへや" and not _hira(a): return 35  # 行頭に助詞が来る
    if s[k:].startswith(("あなた","きみ")): return 2
    if a in "はがをにでもと" and not _hira(b): return 2
    if (_kata(a) and _kanji(b)) or (_kanji(a) and _hira(b)) or (_hira(a) and _kanji(b)): return 10
    if (_kanji(a) and _kanji(b)) or (_kata(a) and _kata(b)) or (a.isdigit() and b.isdigit()): return 40
    if _hira(a) and _hira(b): return 35
    return 20
def wrap(d,t,font,maxw):
    # 日本語は単語間にスペースが無いため、2026-11-03に「改行位置を文全体で最適化」
    # する方式に変更: 熟語や"…"の途中・行頭の句読点を避け、句読点や助詞の後などの
    # 自然な位置で、なるべく行の長さが揃うように改行する
    n=len(t); INF=float("inf")
    best=[INF]*(n+1); prev=[-1]*(n+1); best[0]=0
    for j in range(1,n+1):
        for i in range(j-1,-1,-1):
            w=d.textlength(t[i:j],font=font)
            if w>maxw and j-i>1: break
            if best[i]==INF: continue
            c=best[i]+20
            if j<n:
                c+=_break_cost(t,j)+10*((maxw-w)/maxw)**2
            elif j-i<=3 and i>0:
                c+=25  # 最終行が2〜3文字だけになるのを避ける
            if c<best[j]: best[j]=c; prev[j]=i
    lines=[]; j=n
    while j>0: lines.append(t[prev[j]:j]); j=prev[j]
    return lines[::-1]
def dotted_bg(t=0.0):
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im)
    step=90; off=(t*30)%step
    for gy in range(-step,H+step,step):
        for gx in range(-step,W+step,step):
            x=gx+off; y=gy+off
            d.ellipse((x-6,y-6,x+6,y+6),fill="#e3eafa")
    return im,d
def badge(d,text):
    d.rounded_rectangle((80,110,430,240),10,fill="#4472c4")
    bold(d,(255,175),text,f(56),"white","mm",1)
def outline(d,xy,t,font,fill,stroke,w,anchor="mm"):
    d.text(xy,t,font=font,fill=fill,anchor=anchor,stroke_width=w,stroke_fill=stroke)
def sunburst_bg(t):
    im=Image.new("RGB",(W,H),"#ffd400"); d=ImageDraw.Draw(im)
    cx,cy,R,n=540,940,2400,24
    rot=t*6
    for k in range(n):
        if k%2: continue
        a0=math.radians(rot+k*360/n); a1=math.radians(rot+(k+1)*360/n)
        d.polygon([(cx,cy),(cx+R*math.cos(a0),cy+R*math.sin(a0)),(cx+R*math.cos(a1),cy+R*math.sin(a1))],fill="#ffa400")
    return im,d
def title_lines(d,text,maxw):
    # 1行ずつ別サイズで最大化する。末尾の「チェック」は独立した行にし、
    # 残りが長い場合は「の」の直後など自然な位置で2行に分ける
    segs=[text]
    if text.endswith("チェック") and len(text)>4: segs=[text[:-4],"チェック"]
    head=segs[0]
    if len(head)>7:
        mid=len(head)//2
        cuts=[i+1 for i,ch in enumerate(head[:-1]) if ((ch in "のなをにとでがはい" and not ("ぁ"<=head[i+1]<="ゖ")) or (_kata(ch) and _kanji(head[i+1]))) and abs(i+1-mid)<=3]
        cut=min(cuts,key=lambda c:abs(c-mid)) if cuts else mid
        segs=[head[:cut],head[cut:]]+segs[1:]
    out=[]
    for s in segs:
        sz=210
        while sz>90 and d.textlength(s,font=f(sz))>maxw: sz-=5
        out.append((s,sz))
    return out
def intro_frame(t):
    # 2026-11-03: 表紙=プロフィール一覧のサムネイルになるため、文字が小さく
    # インパクトが弱いとの指摘を受け全面刷新。黄色×オレンジの集中線背景+
    # 白枠の中に特大の赤文字タイトル。プロフィール一覧は縦長動画の中央(3:4)
    # しか表示されないので、要素はすべて y=300〜1600 の範囲に収める。
    im,d=sunburst_bg(t)
    lines=title_lines(d,title,860)
    total=sum(int(sz*1.12) for _,sz in lines)
    # バッジ上端(top)〜フッター下端までの全体を画面中央(y=960)に寄せる
    top=int(960-(430+total+90+185)/2)
    d.rounded_rectangle((300,top,780,top+120),60,fill="#4472c4",outline="#111111",width=8)
    outline(d,(540,top+60),LABELS["badge"],f(66),"white","#111111",3)
    outline(d,(540,top+230),"あなたは何個",f(92),"white","#111111",9)
    outline(d,(540,top+340),"当てはまる?",f(92),"white","#111111",9)
    by0=top+430; by1=by0+total+90
    d.rounded_rectangle((60,by0+14,1020,by1+14),40,fill="#111111")
    d.rounded_rectangle((50,by0,1010,by1),40,fill="white",outline="#111111",width=10)
    y=by0+45
    for l,sz in lines:
        lh=int(sz*1.12)
        outline(d,(530,y+lh//2),l,f(sz),"#e60000","#111111",5)
        y+=lh
    fy=by1+115
    d.rounded_rectangle((90,fy-70,990,fy+70),70,fill="#e60000",outline="#111111",width=8)
    outline(d,(540,fy),"正直にチェックしてみて!",f(70),"white","#111111",3)
    return im
def checkbox(d,cx,cy,size,checked,scale):
    s=size*scale
    d.rounded_rectangle((cx-s/2,cy-s/2,cx+s/2,cy+s/2),16,outline="#4472c4",width=8,fill="white")
    if checked:
        p=[(cx-s*0.28,cy+s*0.02),(cx-s*0.06,cy+s*0.26),(cx+s*0.32,cy-s*0.26)]
        d.line(p,fill="#e60000",width=int(s*0.12),joint="curve")
# 2026-11-03追加: 本編シーンの余白を活かすため、上部に大きなアバターを置き、
# 項目が進むごとに表情が段階的に深刻になる演出(笑顔→苦笑い→焦り→ショック→青ざめ)と、
# 下部に「スマホ依存 危険度」メーターを追加した(益田さんの提案)。
# 表情差分はCanvaの画像生成で作成(avatar_expr/stage1〜4.png、stage0は通常のavatar.png)。
EXPR_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)),"avatar_expr")
_expr_cache={}
def expr_avatar(stage,size):
    key=(stage,size)
    if key not in _expr_cache:
        path=AVATAR_PATH if stage==0 else os.path.join(EXPR_DIR,f"stage{stage}.png")
        if not os.path.exists(path): path=AVATAR_PATH
        av=Image.open(path).convert("RGB").resize((size,size),Image.LANCZOS)
        mask=Image.new("L",(size,size),0); ImageDraw.Draw(mask).ellipse((0,0,size,size),fill=255)
        o=Image.new("RGBA",(size,size)); o.paste(av,(0,0),mask); _expr_cache[key]=o
    return _expr_cache[key]
def expr_stage(idx,total):
    return 0 if total<=1 else round((idx-1)*4/(total-1))
def danger_meter(d,idx,total,t_local):
    # 前の項目の位置から今の項目の位置まで、最初の0.4秒でゲージが伸びる
    prev,cur=(idx-1)/total,idx/total
    k=min(1.0,t_local/0.4); k=1-(1-k)**3
    v=prev+(cur-prev)*k
    x0,x1,y0,y1=140,940,1560,1630
    bold(d,(540,1500),LABELS["meter"],f(54),"#111111","mm",2)
    d.rounded_rectangle((x0,y0,x1,y1),35,fill="#e6e9f2",outline="#c9cfdd",width=4)
    fw=int((x1-x0)*v)
    if fw>40:
        col="#2db84d" if v<0.34 else ("#ffb400" if v<0.67 else "#e60000")
        d.rounded_rectangle((x0,y0,x0+fw,y1),35,fill=col)
    bold(d,(x1,y1+55),f"{int(round(v*100))}%",f(50),"#e60000" if v>=0.67 else "#111111","rm",2)
def item_frame(idx,total,text,t_local):
    # 2026-10-24: 項目の文字数が少ない(1行で収まる)ときに、チェックボックス+文章の
    # ブロックが画面上部に偏って見える、という指摘を受け、ブロック高さに応じて
    # 画面中央寄りに配置するよう変更
    im,d=dotted_bg()
    badge(d,LABELS["badge"])
    bold(d,(1000,175),f"{idx}/{total}",f(50),"#4472c4","rm",1)
    st=expr_stage(idx,total); prev_st=expr_stage(idx-1,total) if idx>1 else st
    sz=440
    if st!=prev_st and t_local<0.3:
        sz=int(440*(1+0.12*math.sin(math.pi*t_local/0.3)))  # 表情が変わる瞬間だけ軽く弾ませる
    cy=560
    ring="#4472c4" if st<2 else ("#ffb400" if st<4 else "#e60000")
    d.ellipse((540-sz//2-12,cy-sz//2-12,540+sz//2+12,cy+sz//2+12),fill=ring)
    av=expr_avatar(st,sz); im.paste(av,(540-sz//2,cy-sz//2),av)
    danger_meter(d,idx,total,t_local)
    checked = t_local>0.35
    scale = min(1.0, 0.7+0.3*min(1.0,t_local/0.35)) if checked else 1.0
    lines=wrap(d,text,f(66),760)
    line_h=92
    block_h=line_h*len(lines)
    ty=1130-block_h/2
    for i,l in enumerate(lines):
        bold(d,(280,ty+i*line_h),l,f(66),"#111111","la",2)
    checkbox(d,180,ty+block_h/2-18,140,checked,scale)
    return im
def verdict_bg():
    im=Image.new("RGB",(W,H),"#4472c4")
    if len(sys.argv)>5:
        ph=Image.open(sys.argv[5]).convert("RGB"); r=max(W/ph.width,H/ph.height)
        ph=ph.resize((int(ph.width*r),int(ph.height*r)),Image.LANCZOS).filter(ImageFilter.GaussianBlur(4)); l=(ph.width-W)//2; tp=(ph.height-H)//2
        im=Image.blend(ph.crop((l,tp,l+W,tp+H)),Image.new("RGB",(W,H),"black"),0.55)
    return im
def verdict_frame(bg,t):
    # 2026-10-24: 診断ラインが短いと画面上部に偏って見える指摘を受け、ブロック高さに
    # 応じて中央寄りに配置するよう変更
    im=bg.copy(); d=ImageDraw.Draw(im)
    lines=wrap(d,verdict,f(76),920)
    line_h,gap1,cta_h,gap2=108,80,90,180
    n=len(lines)
    block_h=line_h*n+gap1+cta_h+gap2
    y0=1040-block_h/2
    for i,l in enumerate(lines):
        bold(d,(540,y0+i*line_h),l,f(76),"white","mm",3)
    cta_y=y0+line_h*n+gap1
    bold(d,(540,cta_y),"改善法は概要欄へ!",f(90),"#ffd400","mm",3)
    arrow_y=cta_y+gap2
    af=f(100); amp=22; freq=1.8
    for i in range(3):
        phase=i*0.75
        dy=amp*max(0.0, math.sin(2*math.pi*freq*t-phase))
        x=540+(i-1)*95
        bold(d,(x,arrow_y+dy),"▼",af,"#ffd400","mm",2)
    return im
def heart(d,cx,cy,r,fill):
    d.ellipse((cx-r,cy-r,cx,cy),fill=fill); d.ellipse((cx,cy-r,cx+r,cy),fill=fill)
    d.polygon([(cx-r,cy-r*0.15),(cx+r,cy-r*0.15),(cx,cy+r*1.3)],fill=fill)
def bookmark(d,cx,cy,w,h,fill):
    x0,x1,y0,y1=cx-w/2,cx+w/2,cy-h/2,cy+h/2
    d.polygon([(x0,y0),(x1,y0),(x1,y1),(cx,y1-h*0.32),(x0,y1)],fill=fill)
def cta_frame(bg,t):
    im=bg.copy(); d=ImageDraw.Draw(im)
    bold(d,(540,210),"まっすー",f(72),"white","mm",2)
    bold(d,(540,300),"@massu_smartphone",f(48),"#ffd400","mm",1)
    r=110; cx,cy=540,520
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill="white",outline="#ffd400",width=8)
    av=circular_avatar(2*(r-8))
    if av: im.paste(av,(cx-av.width//2,cy-av.height//2),av)
    else: bold(d,(cx,cy),"ま",f(100),"#4472c4","mm",2)
    bd=46; bx,by=cx+r-10,cy+r-10
    d.ellipse((bx-bd,by-bd,bx+bd,by+bd),fill="#ffd400",outline="white",width=6)
    bold(d,(bx,by-6),"+",f(70),"#4472c4","mm",2)
    bold(d,(540,730),"フォロー&いいね&保存で",f(58),"white","mm",2)
    bold(d,(540,805),LABELS["cta"],f(58),"white","mm",2)
    icons=[("フォロー","follow"),("いいね","heart"),("保存","bookmark")]
    for i,(label,kind) in enumerate(icons):
        ix=270+i*270; iy=1150
        scale=1.0+0.18*max(0.0,math.sin(2*math.pi*1.6*t-i*0.5))
        ir=int(80*scale)
        if kind=="follow":
            d.ellipse((ix-ir,iy-ir,ix+ir,iy+ir),fill="white")
            bold(d,(ix,iy-6),"+",f(int(100*scale)),"#4472c4","mm",3)
        elif kind=="heart":
            heart(d,ix,iy-ir*0.2,ir,"#ff4d4d")
        else:
            bookmark(d,ix,iy,ir*1.5,ir*1.9,"#ffd400")
        bold(d,(ix,iy+150),label,f(50),"white","mm",2)
    return im
p=subprocess.Popen([FFMPEG,"-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out+".video.mp4"],stdin=subprocess.PIPE)
for i in range(int(INTRO*FPS)):
    p.stdin.write(intro_frame(i/FPS).tobytes())
total_items=len(items)
for idx,text in enumerate(items,start=1):
    for i in range(int(ITEM*FPS)):
        p.stdin.write(item_frame(idx,total_items,text,i/FPS).tobytes())
bg=verdict_bg()
for i in range(int(VERDICT*FPS)):
    p.stdin.write(verdict_frame(bg,i/FPS).tobytes())
for i in range(int(CTA*FPS)):
    p.stdin.write(cta_frame(bg,i/FPS).tobytes())
p.stdin.close(); p.wait()
subprocess.run([FFMPEG,"-y","-v","error","-i",out+".video.mp4","-c:v","copy","-an",out],check=True)
os.remove(out+".video.mp4")
