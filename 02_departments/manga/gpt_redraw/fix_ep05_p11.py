"""第5話11ページ: 網点の仕上げのあとで、貼り紙の文字とスマホのSNS画面を、絵の白い部分の中だけに重ねる"""
import sys,cv2,numpy as np
sys.path.insert(0,'../tools'); import page_compose as pc
from PIL import Image,ImageDraw,ImageFont
raw=np.array(Image.open('ep05_p11_raw.webp').convert('L').resize((1024,1536)))
pg=np.array(Image.open('ep05_p11_final.png').convert('L'))
k=889/1024; H0,W0=pg.shape
A=np.float32([[k,0,56],[0,k,40]])
def white_mask(x0,y0,x1,y1):
    b=(raw[y0:y1,x0:x1]>232).astype(np.uint8); n,l,st,_=cv2.connectedComponentsWithStats(b,4)
    i=1+np.argmax(st[1:,4]); m=np.zeros(raw.shape,np.uint8); m[y0:y1,x0:x1]=(l==i)*255
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    return cv2.erode(cv2.warpAffine(m,A,(W0,H0)),np.ones((3,3),np.uint8))
# 貼り紙は、手前に向いた斜めの四角(上の辺は右上がり、下の辺は右下がり)。平らな紙に文字を書いてから、その四角にはめこむ
PW,PH=180,360; pl=Image.new('L',(PW,PH),255); d=ImageDraw.Draw(pl)
f=ImageFont.truetype(pc.FONT_B,44); pc.vcols.rubies={}
pc.draw_vtext(d,[[(c,None) for c in '目指せ'],[(c,None) for c in '魔王討伐!']],PW-22,70,f,gap=10)
q=np.float32([[882,85],[974,27],[975,270],[882,251]]); q=(np.c_[q,np.ones(4)]@A.T).astype(np.float32)
Mp=cv2.getPerspectiveTransform(np.float32([[0,0],[PW,0],[PW,PH],[0,PH]]),q)
L=cv2.warpPerspective(np.array(pl),Mp,(W0,H0),flags=cv2.INTER_AREA,borderValue=255)
pm=white_mask(850,0,1010,300); pg[pm>0]=255; pg[(pm>0)&(L<140)]=0
W,H=300,520; s=Image.new('L',(W,H),255); sd=ImageDraw.Draw(s)
B=lambda n:ImageFont.truetype(pc.FONT_B,n); R=lambda n:ImageFont.truetype(pc.FONT,n)
# 見出しは黒い帯にせず、文字と下線だけにする(画面の角の形と帯がずれて台形に見えたため)
sd.text((18,22),'勇者サークル 公式',font=B(24),fill=0)
sd.ellipse([14,74,64,124],outline=0,width=3); sd.text((76,78),'@yusha_circle',font=R(18),fill=0); sd.text((76,102),'最後の投稿: 半年前',font=B(18),fill=0)
sd.line([0,138,W,138],fill=0,width=2)
sd.rounded_rectangle([14,152,W-14,400],radius=10,outline=0,width=3)
sd.text((28,166),'冒険の記録',font=B(26),fill=0); sd.text((28,204),'第3層到達!',font=B(34),fill=0)
sd.rectangle([28,256,W-28,380],outline=0,width=2); sd.line([28,380,120,300,180,350,230,310,W-28,380],fill=0,width=2)
dst=np.float32([[637,859],[804,793],[927,1105],[760,1171]]); dst=(np.c_[dst,np.ones(4)]@A.T).astype(np.float32)
Mx=cv2.getPerspectiveTransform(np.float32([[0,0],[W,0],[W,H],[0,H]]),dst)
w=cv2.warpPerspective(np.array(s),Mx,(W0,H0),flags=cv2.INTER_AREA,borderValue=255)
sm=white_mask(600,780,990,1140); pg[sm>0]=w[sm>0]
Image.fromarray(pg).save('ep05_p11_final.png')
