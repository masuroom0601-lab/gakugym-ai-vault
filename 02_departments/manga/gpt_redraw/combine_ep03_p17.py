"""第3話17ページ: 2枚目(椎菜とD助を直した)をもとに、1枚目のヒサ(ヘッドホン)の頭と肩を重ねる"""
from PIL import Image, ImageDraw, ImageFilter
a=Image.open('ep03_p17_rawA.webp').convert('RGB').resize((1024,1536)); b=Image.open('ep03_p17_rawB.webp').convert('RGB').resize((1024,1536))
m=Image.new('L',(1024,1536),0); ImageDraw.Draw(m).rounded_rectangle([472,16,648,238],radius=40,fill=255); m=m.filter(ImageFilter.GaussianBlur(6))
b.paste(a,(0,0),m); b.save('ep03_p17_raw.png')
