# -*- coding: utf-8 -*-
"""Калибровочная линейка: печатает шкалу в мм, чтобы измерить реальный размер этикетки.
   python3 ruler.py [ширина_мм] [высота_мм]
"""
from PIL import Image, ImageDraw, ImageFont
import sys
DPI = 203; MM = DPI/25.4
px = lambda mm: int(round(mm*MM))
W_MM = int(sys.argv[1]) if len(sys.argv) > 1 else 65
H_MM = int(sys.argv[2]) if len(sys.argv) > 2 else 50
W, H = px(W_MM), px(H_MM)
img = Image.new("L", (W, H), 255); d = ImageDraw.Draw(img)
f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf", px(2.6))
# горизонтальная шкала сверху
for mm in range(0, W_MM+1):
    x = px(mm)
    big = mm % 10 == 0
    d.line([(x,0),(x, px(4 if big else 2 if mm%5==0 else 1.2))], fill=0, width=1)
    if big and mm: d.text((x+2, px(4.2)), str(mm), font=f, fill=0)
# вертикальная шкала слева
for mm in range(0, H_MM+1):
    y = px(mm)
    big = mm % 10 == 0
    d.line([(0,y),(px(4 if big else 2 if mm%5==0 else 1.2), y)], fill=0, width=1)
    if big and mm: d.text((px(4.2), y+1), str(mm), font=f, fill=0)
d.rectangle([0,0,W-1,H-1], outline=0, width=1)
d.text((px(12), px(12)), f"задано {W_MM}x{H_MM} мм", font=f, fill=0)
d.text((px(12), px(16)), "смотри, на каком числе", font=f, fill=0)
d.text((px(12), px(20)), "обрывается шкала", font=f, fill=0)
img.save(f"ruler-{W_MM}x{H_MM}.png", dpi=(DPI,DPI))
print(f"ruler-{W_MM}x{H_MM}.png")
