"""第3話9ページ: 受付の机のメモ(石の下の紙)に「先に帰ります」を、紙の傾きに合わせて入れる"""
import sys; sys.path.insert(0,'../tools'); import page_compose as pc
from PIL import Image,ImageDraw,ImageFont
pg=Image.open('ep03_p09_final.png').convert('L')
k=889/1024; T=lambda x,y:(int(56+x*k),int(40+y*k))
f=ImageFont.truetype(pc.FONT_B,14); t='先に帰ります'; bb=f.getbbox(t)
lay=Image.new('L',(bb[2]+8,bb[3]+8),0); ImageDraw.Draw(lay).text((4,2),t,font=f,fill=255)
lay=lay.rotate(-14,expand=True,resample=Image.BICUBIC)
pg.paste(0,T(262,745),lay); pg.save('ep03_p09_final.png')
