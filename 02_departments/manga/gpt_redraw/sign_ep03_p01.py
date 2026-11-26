"""第3話1ページ: 網点の後で、立て札(元の絵 x96-186, y325-406)を白く塗り、文字を入れる"""
import sys; sys.path.insert(0,'../tools'); import page_compose as pc
from PIL import Image,ImageDraw,ImageFont
pg=Image.open('ep03_p01_final.png').convert('L'); d=ImageDraw.Draw(pg)
k=889/1024; T=lambda x,y:(56+x*k,40+y*k)
x0,y0=T(99,328); x1,y1=T(183,403); d.rectangle([x0,y0,x1,y1],fill=255)
f=ImageFont.truetype(pc.FONT_B,15); fs=ImageFont.truetype(pc.FONT,8)
w=d.textbbox((0,0),'北の迷宮',font=f)[2]; d.text(((x0+x1-w)/2,y0+6),'北の迷宮',font=f,fill=0)
for i,t in enumerate(['※入場には、大学の','冒険許可書が必要です']):
    w=d.textbbox((0,0),t,font=fs)[2]; d.text(((x0+x1-w)/2,y0+30+i*12),t,font=fs,fill=0)
pg.save('ep03_p01_final.png')
