import os, sys, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30
FONT=os.environ["REEL_FONT"]; FFMPEG=os.environ.get("REEL_FFMPEG","ffmpeg")
level, q, opts, out = sys.argv[1], sys.argv[2], sys.argv[3].split("|"), sys.argv[4]
COUNT=10; END=2.5
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
def endcard_bg():
    im=Image.new("RGB",(W,H),"#4472c4")
    if len(sys.argv)>5:
        ph=Image.open(sys.argv[5]).convert("RGB"); r=max(W/ph.width,H/ph.height)
        ph=ph.resize((int(ph.width*r),int(ph.height*r)),Image.LANCZOS).filter(ImageFilter.GaussianBlur(4)); l=(ph.width-W)//2; tp=(ph.height-H)//2
        im=Image.blend(ph.crop((l,tp,l+W,tp+H)),Image.new("RGB",(W,H),"black"),0.55)
    d=ImageDraw.Draw(im)
    bold(d,(540,820),"答え&解説は",f(100),"white","mm",3)
    bold(d,(540,970),"概要欄へ!",f(120),"white","mm",3)
    return im
def endcard_frame(bg,t):
    # 下矢印3つを、少しずつ位相をずらして上下に弾ませる(視線を下へ誘導するアニメーション)
    im=bg.copy(); d=ImageDraw.Draw(im)
    af=f(100); amp=22; freq=1.8
    for i in range(3):
        phase=i*0.75
        dy=amp*max(0.0, math.sin(2*math.pi*freq*t-phase))
        x=540+(i-1)*95
        bold(d,(x,1180+dy),"▼",af,"#ffd400","mm",2)
    return im
p=subprocess.Popen([FFMPEG,"-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out+".video.mp4"],stdin=subprocess.PIPE)
fr=0
for n in range(COUNT,0,-1):
    for _ in range(FPS):
        p.stdin.write(base(n,fr/FPS).tobytes()); fr+=1
for _ in range(FPS//2):
    p.stdin.write(base(0,fr/FPS).tobytes()); fr+=1
bg=endcard_bg()
for i in range(int(END*FPS)):
    p.stdin.write(endcard_frame(bg,i/FPS).tobytes())
p.stdin.close(); p.wait()
# 2026-10-18: カウントダウン効果音(カチカチ+チーン)を合成して重ねる
import importlib.util
_spec=importlib.util.spec_from_file_location("countdown_audio",os.path.join(os.path.dirname(os.path.abspath(__file__)),"countdown_audio.py"))
ca=importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ca)
total=fr/FPS+END
wav=out+".audio.wav"
ca.write(wav,ca.render(total,COUNT))
subprocess.run([FFMPEG,"-y","-v","error","-i",out+".video.mp4","-i",wav,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","128k","-shortest",out],check=True)
os.remove(out+".video.mp4"); os.remove(wav)
