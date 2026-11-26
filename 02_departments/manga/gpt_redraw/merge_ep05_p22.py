"""第5話22ページ: 上2段は明るめ、最後のコマ(迷宮の影)は暗めの仕上げを使う"""
import sys
from PIL import Image
a=Image.open('ep05_p22_final.png'); b=Image.open(sys.argv[1])
y=int(40+915*889/1024); a.paste(b.crop((0,y,1000,1414)),(0,y)); a.save('ep05_p22_final.png')
