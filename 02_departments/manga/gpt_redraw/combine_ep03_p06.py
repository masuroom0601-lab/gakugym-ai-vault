"""第3話6ページ: 1コマ目は1枚目(バツ印の傷がある)、ほかは2枚目(タマキを直した)を使う"""
from PIL import Image
a=Image.open('ep03_p06_rawA.webp').convert('RGB').resize((1024,1536)); b=Image.open('ep03_p06_rawB.webp').convert('RGB').resize((1024,1536))
p=a.crop((20,16,1004,384)); H=512-16; W=int(p.width*H/p.height); p=p.resize((W,H),Image.LANCZOS)
x=(W-984)//2; p=p.crop((x,0,x+984,H)); b.paste(p,(20,16)); b.save('ep03_p06_raw.png')
