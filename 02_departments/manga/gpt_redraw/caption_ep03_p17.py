"""第3話17ページ: カメラの画面の白い帯に、字幕を横書きで入れる"""
import sys; sys.path.insert(0,'../tools'); import page_compose as pc
from PIL import Image,ImageDraw,ImageFont
pg=Image.open('ep03_p17_final.png').convert('L'); d=ImageDraw.Draw(pg)
k=889/1024; T=lambda x,y:(56+x*k,40+y*k)
x0,y0=T(178,644); x1,y1=T(928,682); d.rectangle([x0,y0,x1,y1],fill=255)
f=ImageFont.truetype(pc.FONT_B,24); t='〇〇大生の1日に密着してみた'; bb=d.textbbox((0,0),t,font=f)
d.text(((x0+x1-bb[2])/2,(y0+y1-bb[3])/2-2),t,font=f,fill=0); pg.save('ep03_p17_final.png')
