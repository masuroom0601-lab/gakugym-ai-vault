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
def wrap(d,t,font,maxw):
    # 日本語は単語間にスペースが無いため、英語用の単語区切りではなく1文字ずつ詰めて折り返す
    lines,cur=[],""
    for ch in t:
        test=cur+ch
        if d.textlength(test,font=font)<=maxw: cur=test
        else: lines.append(cur); cur=ch
    lines.append(cur); return lines
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
def intro_frame(t):
    # 2026-10-24: 文字数が少ない(タイトルが短い)とブロック全体が画面上部に
    # 偏って見える、という指摘を受け、内容量に応じてブロック全体を画面中央寄りに
    # 配置するよう変更(固定y座標の積み上げをやめ、ブロック高さから逆算する)
    im,d=dotted_bg(t)
    badge(d,"スマホ習慣")
    title_font=f(84)
    title_lines=wrap(d,title,title_font,920)
    sub_h,gap1,line_h,gap2,foot_h=84,50,118,60,70
    n=len(title_lines)
    block_h=sub_h+gap1+line_h*n+gap2+foot_h
    y0=1060-block_h/2
    bold(d,(80,y0),"あなたは何個当てはまる?",f(60),"#111111","la",2)
    ty=y0+sub_h+gap1
    for i,l in enumerate(title_lines):
        bold(d,(80,ty+i*line_h),l,title_font,"#e60000","la",3)
    fy=ty+line_h*n+gap2
    bold(d,(80,fy),"正直にチェックしてみて!",f(54),"#111111","la",2)
    return im
def checkbox(d,cx,cy,size,checked,scale):
    s=size*scale
    d.rounded_rectangle((cx-s/2,cy-s/2,cx+s/2,cy+s/2),16,outline="#4472c4",width=8,fill="white")
    if checked:
        p=[(cx-s*0.28,cy+s*0.02),(cx-s*0.06,cy+s*0.26),(cx+s*0.32,cy-s*0.26)]
        d.line(p,fill="#e60000",width=int(s*0.12),joint="curve")
def item_frame(idx,total,text,t_local):
    # 2026-10-24: 項目の文字数が少ない(1行で収まる)ときに、チェックボックス+文章の
    # ブロックが画面上部に偏って見える、という指摘を受け、ブロック高さに応じて
    # 画面中央寄りに配置するよう変更
    im,d=dotted_bg()
    badge(d,"スマホ習慣")
    bold(d,(1000,175),f"{idx}/{total}",f(50),"#4472c4","rm",1)
    checked = t_local>0.35
    scale = min(1.0, 0.7+0.3*min(1.0,t_local/0.35)) if checked else 1.0
    lines=wrap(d,text,f(66),760)
    line_h=92
    block_h=line_h*len(lines)
    ty=1060-block_h/2
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
    bold(d,(540,300),"@massu_gakugym",f(48),"#ffd400","mm",1)
    r=110; cx,cy=540,520
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill="white",outline="#ffd400",width=8)
    av=circular_avatar(2*(r-8))
    if av: im.paste(av,(cx-av.width//2,cy-av.height//2),av)
    else: bold(d,(cx,cy),"ま",f(100),"#4472c4","mm",2)
    bd=46; bx,by=cx+r-10,cy+r-10
    d.ellipse((bx-bd,by-bd,bx+bd,by+bd),fill="#ffd400",outline="white",width=6)
    bold(d,(bx,by-6),"+",f(70),"#4472c4","mm",2)
    bold(d,(540,730),"フォロー&いいね&保存で",f(58),"white","mm",2)
    bold(d,(540,805),"スマホ対策も見逃さない!",f(58),"white","mm",2)
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
