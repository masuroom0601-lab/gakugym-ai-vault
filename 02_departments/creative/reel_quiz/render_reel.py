import os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FONT=os.environ["REEL_FONT"]; FFMPEG=os.environ.get("REEL_FFMPEG","ffmpeg")
level, q, opts, out = sys.argv[1], sys.argv[2], sys.argv[3].split("|"), sys.argv[4]
COUNT=10; END=2.5; CTA=3.0
AVATAR_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"avatar.png")
def circular_avatar(size):
    # 2026-10-22追加: CTAシーンのアバターに、益田さん提供のまっすーイラストを丸く切り抜いて使う
    if not os.path.exists(AVATAR_PATH): return None
    av=Image.open(AVATAR_PATH).convert("RGB").resize((size,size),Image.LANCZOS)
    mask=Image.new("L",(size,size),0); ImageDraw.Draw(mask).ellipse((0,0,size,size),fill=255)
    out=Image.new("RGBA",(size,size)); out.paste(av,(0,0),mask)
    return out
def f(sz): return ImageFont.truetype(FONT, sz)
def bold(d,xy,t,font,fill,anchor="la",w=2):
    d.text(xy,t,font=font,fill=fill,anchor=anchor,stroke_width=w,stroke_fill=fill)
def wrap(d,t,font,maxw):
    lines,cur=[],""
    for word in t.split(" "):
        test=(cur+" "+word).strip()
        if d.textlength(test,font=font)<=maxw: cur=test
        else: lines.append(cur); cur=word
    lines.append(cur); return lines
def base(n,t=0.0):
    im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im)
    step=90; off=(t*30)%step
    for gy in range(-step,H+step,step):
        for gx in range(-step,W+step,step):
            x=gx+off; y=gy+off
            d.ellipse((x-6,y-6,x+6,y+6),fill="#e3eafa")
    for k in range(-H,W,360):
        x=k+((t*60)%360)
        d.polygon([(x,H),(x+120,H),(x+120+H*0.0+0,H),(x,H)],fill="white")
    d.rounded_rectangle((80,110,350,240),10,fill="#4472c4")
    bold(d,(215,175),"英検",f(60),"white","mm",1)
    bold(d,(380,175),level+"レベル",f(78),"#e60000","lm",2)
    bold(d,(80,330),"受験英語",f(64),"#111111","la",2)
    bold(d,(80,420),"10秒で解けないと",f(76),"#111111","la",2)
    bold(d,(80,520),"英検キツイ",f(110),"#e60000","la",3)
    d.line((80,660,1000,660),fill="#cccccc",width=4)
    y=720
    for l in wrap(d,q,f(58),920):
        bold(d,(80,y),l,f(58),"#111111","la",2); y+=84
    y=max(y+50,1000); oy=y
    for o in opts:
        bold(d,(110,y),o,f(54),"#111111","la",2); y+=100
    # countdown badge
    by=oy  # カウントダウン枠は選択肢と同じ高さ(問題文が長くても重ならない)
    d.rounded_rectangle((720,by,1000,by+300),24,fill="#e8eefc",outline="#4472c4",width=6)
    d.ellipse((770,by+50,950,by+230),outline="#4472c4",width=6)
    bold(d,(860,by+140),str(n),f(120),"#111111","mm",3)
    d.rounded_rectangle((80,1620,780,1740),40,fill="#4472c4")
    bold(d,(430,1680),"答えをコメント欄へ!",f(54),"white","mm",1)
    return im
def plain_bg():
    # 2026-10-22: endcard_bg()から文字描画を分離(endcard_frame/cta_frameの両方が
    # 同じ背景を使い回すため、背景そのものには何も文字を焼き込まない)
    im=Image.new("RGB",(W,H),"#4472c4")
    if len(sys.argv)>5:
        ph=Image.open(sys.argv[5]).convert("RGB"); r=max(W/ph.width,H/ph.height)
        ph=ph.resize((int(ph.width*r),int(ph.height*r)),Image.LANCZOS).filter(ImageFilter.GaussianBlur(4)); l=(ph.width-W)//2; tp=(ph.height-H)//2
        im=Image.blend(ph.crop((l,tp,l+W,tp+H)),Image.new("RGB",(W,H),"black"),0.55)
    return im
def endcard_frame(bg,t):
    # 下矢印3つを、少しずつ位相をずらして上下に弾ませる(視線を下へ誘導するアニメーション)
    im=bg.copy(); d=ImageDraw.Draw(im)
    bold(d,(540,820),"答え&解説は",f(100),"white","mm",3)
    bold(d,(540,970),"概要欄へ!",f(120),"white","mm",3)
    af=f(100); amp=22; freq=1.8
    for i in range(3):
        phase=i*0.75
        dy=amp*max(0.0, math.sin(2*math.pi*freq*t-phase))
        x=540+(i-1)*95
        bold(d,(x,1180+dy),"▼",af,"#ffd400","mm",2)
    return im
def heart(d,cx,cy,r,fill):
    d.ellipse((cx-r,cy-r,cx,cy),fill=fill); d.ellipse((cx,cy-r,cx+r,cy),fill=fill)
    d.polygon([(cx-r,cy-r*0.15),(cx+r,cy-r*0.15),(cx,cy+r*1.3)],fill=fill)
def bookmark(d,cx,cy,w,h,fill):
    x0,x1,y0,y1=cx-w/2,cx+w/2,cy-h/2,cy+h/2
    d.polygon([(x0,y0),(x1,y0),(x1,y1),(cx,y1-h*0.32),(x0,y1)],fill=fill)
def cta_frame(bg,t):
    # 2026-10-22追加: エンドカードの後に、まっすーのアカウントフォロー・いいね・保存を
    # 促すCTAシーンを追加(益田さん提供の参考動画の構成を、本リールの画風に合わせて再現)
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
    bold(d,(540,805),"毎日の英検対策を見逃さない!",f(58),"white","mm",2)
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
fr=0
for n in range(COUNT,0,-1):
    for _ in range(FPS):
        p.stdin.write(base(n,fr/FPS).tobytes()); fr+=1
for _ in range(FPS//2):
    p.stdin.write(base(0,fr/FPS).tobytes()); fr+=1
bg=plain_bg()
for i in range(int(END*FPS)):
    p.stdin.write(endcard_frame(bg,i/FPS).tobytes())
for i in range(int(CTA*FPS)):
    p.stdin.write(cta_frame(bg,i/FPS).tobytes())
p.stdin.close(); p.wait()
# 2026-10-18: カウントダウン効果音(カチカチ+チーン)を合成して重ねる
import importlib.util
_spec=importlib.util.spec_from_file_location("countdown_audio",os.path.join(os.path.dirname(os.path.abspath(__file__)),"countdown_audio.py"))
ca=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ca)
total=fr/FPS+END+CTA
wav=out+".audio.wav"
ca.write(wav,ca.render(total,COUNT))
subprocess.run([FFMPEG,"-y","-v","error","-i",out+".video.mp4","-i",wav,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","128k","-shortest",out],check=True)
os.remove(out+".video.mp4"); os.remove(wav)
