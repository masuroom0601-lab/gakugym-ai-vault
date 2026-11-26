"""第3話5ページ: 最後のコマの左端に、イヅルが書いている地図(道順と注意書き)のアップを差しこむ(2026-11-26 益田さん指定)"""
import sys; sys.path.insert(0,'../tools'); import page_compose as pc
from PIL import Image,ImageDraw,ImageFont
pg=Image.open('ep03_p05_final.png').convert('L')
W,H=262,410; m=Image.new('L',(W,H),255); d=ImageDraw.Draw(m)
R=lambda n:ImageFont.truetype(pc.FONT,n); B=lambda n:ImageFont.truetype(pc.FONT_B,n)
d.text((12,8),'北の迷宮 第1層',font=B(17),fill=0); d.line([12,32,W-12,32],fill=0,width=2)
# 通路(二重線)と部屋
def cor(x0,y0,x1,y1,w=14):
    if x0==x1: d.rectangle([x0-w//2,min(y0,y1),x0+w//2,max(y0,y1)],outline=0,width=2,fill=255)
    else: d.rectangle([min(x0,x1),y0-w//2,max(x0,x1),y0+w//2],outline=0,width=2,fill=255)
cor(130,380,130,250); cor(130,250,60,250); cor(60,250,60,150); cor(130,250,200,250); cor(200,250,200,110); cor(60,150,130,150); cor(130,150,130,80); cor(200,110,130,110)
for x,y in [(130,250),(60,150),(200,110)]: d.rectangle([x-16,y-16,x+16,y+16],outline=0,width=2,fill=255)
d.rectangle([110,60,150,92],outline=0,width=3,fill=255)
# 道順(点線)と印
for y in range(372,258,-12): d.line([126,y,126,y-6],fill=0,width=2)
for x in range(122,206,12): d.line([x,246,x+6,246],fill=0,width=2)
for y in range(238,118,-12): d.line([196,y,196,y-6],fill=0,width=2)
d.line([52,142,68,158],fill=0,width=3); d.line([68,142,52,158],fill=0,width=3)   # ×(行き止まり)
d.ellipse([186,232,214,260],outline=0,width=2)                                     # 〇(罠)
f=R(12); fb=B(12)
d.text((140,368),'入口',font=fb,fill=0)
d.text((140,262),'分かれ道は右!',font=fb,fill=0)
d.text((74,168),'行き止まり',font=f,fill=0)
d.text((210,232),'罠',font=fb,fill=0); d.text((150,282),'※床のくぼみに注意',font=f,fill=0)
d.text((158,72),'第2層への',font=f,fill=0); d.text((158,86),'階段',font=f,fill=0)
d.text((12,300),'※休けいは',font=f,fill=0); d.text((12,314),'2つ目の部屋で',font=f,fill=0)
d.text((12,340),'※回復の薬 3本',font=f,fill=0); d.text((12,354),'※お弁当 4人分',font=f,fill=0)
im=Image.new('L',(W+8,H+8),0); im.paste(m,(4,4))
pg.paste(im,(62,930)); pg.save('ep03_p05_final.png')
