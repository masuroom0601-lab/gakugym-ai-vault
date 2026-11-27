"""第3話13ページ: 一番上の段は新しい絵(キャンディーをくわえたアイミ)、2段目から下は前の絵(鼻で笑うシロ)を使う"""
from PIL import Image
a=Image.open('ep03_p13_rawB.webp').convert('RGB').resize((1024,1536)); b=Image.open('ep03_p13_raw.webp').convert('RGB').resize((1024,1536))
c=b.copy(); c.paste((255,255,255),(0,500,1024,520)); c.paste(a.crop((0,0,1024,502)),(0,0)); c.save('ep03_p13_raw_mix.png')
