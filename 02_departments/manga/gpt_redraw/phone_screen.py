"""網点の仕上げのあとで、スマホの白い画面に、勇者サークル公式SNSの画面をはめこむ(画面の傾きに合わせる)。
使い方: python3 phone_screen.py 元の絵 仕上げた原稿 x0 y0 x1 y1 種類(post=投稿画面 / old=半年前の投稿)
x0..y1 は、元の絵(1024x1536)の上で、スマホの画面をふくむ範囲"""
import sys,cv2,numpy as np
sys.path.insert(0,'../tools'); import page_compose as pc
from PIL import Image,ImageDraw,ImageFont
rawp,outp=sys.argv[1],sys.argv[2]; x0,y0,x1,y1=map(int,sys.argv[3:7]); kind=sys.argv[7]
raw=np.array(Image.open(rawp).convert('L').resize((1024,1536)))
pg=np.array(Image.open(outp).convert('L')); H0,W0=pg.shape
k=889/1024; A=np.float32([[k,0,56],[0,k,40]])
b=(raw[y0:y1,x0:x1]>232).astype(np.uint8); n,l,st,_=cv2.connectedComponentsWithStats(b,4)
i=1+np.argmax(st[1:,4]); m=np.zeros(raw.shape,np.uint8); m[y0:y1,x0:x1]=(l==i)*255
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
cnt,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
box=cv2.boxPoints(cv2.minAreaRect(max(cnt,key=cv2.contourArea)))
c=box.mean(0); ang=np.arctan2(box[:,1]-c[1],box[:,0]-c[0])
tl,tr,br,bl=[box[np.argmin(np.abs(((ang-a+np.pi)%(2*np.pi))-np.pi))] for a in (-2.4,-0.7,0.7,2.4)]
W,H=300,int(300*np.linalg.norm(bl-tl)/np.linalg.norm(tr-tl))
s=Image.new('L',(W,H),255); d=ImageDraw.Draw(s)
B=lambda n:ImageFont.truetype(pc.FONT_B,n); R=lambda n:ImageFont.truetype(pc.FONT,n)
d.text((18,20),'勇者サークル 公式',font=B(24),fill=0); d.line([0,62,W,62],fill=0,width=2)
if kind=='post':
    d.text((18,80),'新しい投稿',font=B(22),fill=0)
    d.rectangle([18,120,W-18,320],outline=0,width=2); d.line([18,320,110,230,170,280,220,240,W-18,320],fill=0,width=2)
    d.text((18,336),'今日の冒険 第2層へ!',font=R(20),fill=0)
    d.rounded_rectangle([W-130,H-70,W-18,H-26],radius=10,fill=40); d.text((W-112,H-62),'投稿する',font=B(20),fill=255)
if kind=='login':
    d.text((18,90),'ログイン',font=B(26),fill=0)
    d.rectangle([18,140,W-18,186],outline=0,width=2); d.text((28,150),'yusha_circle',font=R(20),fill=0)
    d.rectangle([18,206,W-18,252],outline=0,width=2); d.text((28,216),'●●●●●●',font=R(20),fill=0)
    d.text((18,266),'パスワードが違います',font=B(20),fill=0)
    d.rounded_rectangle([18,316,W-18,366],radius=10,fill=40); d.text((W//2-44,326),'ログイン',font=B(22),fill=255)
if kind=='selfie':  # シロの個人アカウントの投稿(元の絵の1コマ目の自撮りを写真に使う)
    s=Image.new('L',(W,H),255); d=ImageDraw.Draw(s)
    d.ellipse([10,8,38,36],outline=0,width=2); d.text((46,12),'shiro_hero',font=B(16),fill=0); d.line([0,44,W,44],fill=0,width=2)
    ph=Image.fromarray(raw[30:330,480:820]).resize((136,120)); s.paste(ph,(10,52)); d.rectangle([10,52,146,172],outline=0,width=2)
    d.text((156,60),'第1層、',font=B(17),fill=0); d.text((156,82),'余裕だった',font=B(17),fill=0)
    d.text((156,140),'♡ 2',font=B(18),fill=0)
    d.line([0,182,W,182],fill=0,width=1)
    d.text((60,190),'髪、なんかついてない?',font=R(15),fill=0)
    d.text((70,214),'第1層で?',font=R(15),fill=0)
dst=(np.c_[np.float32([tl,tr,br,bl]),np.ones(4)]@A.T).astype(np.float32)
Mx=cv2.getPerspectiveTransform(np.float32([[0,0],[W,0],[W,H],[0,H]]),dst)
w=cv2.warpPerspective(np.array(s),Mx,(W0,H0),flags=cv2.INTER_AREA,borderValue=255)
mm=cv2.erode(cv2.warpAffine(m,A,(W0,H0)),np.ones((3,3),np.uint8)); pg[mm>0]=w[mm>0]
Image.fromarray(pg).save(outp)
