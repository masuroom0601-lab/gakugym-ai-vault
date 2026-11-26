"""第3話5ページ: 最後のコマ左の地図のアップ(GPTが描いた)に、手書き風の短い注意書きを、紙の傾きに合わせて入れる(2026-11-26 益田さん指定)"""
import sys; sys.path.insert(0,'../tools'); import page_compose as pc
from PIL import Image,ImageDraw,ImageFont
pg=Image.open('ep03_p05_final.png').convert('L')
k=889/1024; T=lambda x,y:(int(56+x*k),int(40+y*k))
def note(text,x,y,size=15,ang=8,white=False):
    f=ImageFont.truetype(pc.FONT_B,size); bb=f.getbbox(text); w,h=bb[2]+8,bb[3]+8
    t=Image.new('L',(w,h),0); m=Image.new('L',(w,h),0); dt=ImageDraw.Draw(t); dm=ImageDraw.Draw(m)
    dm.text((4,2),text,font=f,fill=255,stroke_width=3 if white else 2,stroke_fill=255); dt.text((4,2),text,font=f,fill=255)
    t=t.rotate(ang,expand=True,resample=Image.BICUBIC); m=m.rotate(ang,expand=True,resample=Image.BICUBIC)
    X,Y=T(x,y); pg.paste(255,(X,Y),m); pg.paste(0,(X,Y),t)
note('分かれ道は右!',245,1080,15,8,True)
note('行き止まり',150,1135,13,8)
note('罠! 床に注意',70,1270,14,8,True)
note('薬3本・お弁当4人分',220,1395,13,8,True)
pg.save('ep03_p05_final.png')
