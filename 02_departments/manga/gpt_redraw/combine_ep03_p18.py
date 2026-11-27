"""第3話18ページ: 2枚目(D助が見本どおり)をもとに、1枚目の椎菜の顔と上半身を重ねる(益田さん選択)"""
from PIL import Image, ImageDraw, ImageFilter
a=Image.open('ep03_p18_rawA.webp').convert('RGB').resize((1024,1536)); b=Image.open('ep03_p18_rawB.webp').convert('RGB').resize((1024,1536))
m=Image.new('L',(1024,1536),0); ImageDraw.Draw(m).ellipse([318,55,520,330],fill=255); m=m.filter(ImageFilter.GaussianBlur(10))
b.paste(a,(0,0),m); b.save('ep03_p18_raw.png')
