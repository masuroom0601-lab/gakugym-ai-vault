"""第3話8ページ: 1コマ目は1枚目(シロの顔が整っている)、ほかは2枚目(最後のコマをシロに直した)を使う。2枚はコマ割りが同じ"""
from PIL import Image
a=Image.open('ep03_p08_rawA.webp').convert('RGB').resize((1024,1536)); b=Image.open('ep03_p08_rawB.webp').convert('RGB').resize((1024,1536))
b.paste(a.crop((0,0,1024,438)),(0,0)); b.save('ep03_p08_raw.png')
