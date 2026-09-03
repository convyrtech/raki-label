# -*- coding: utf-8 -*-
"""Печать PNG-этикетки напрямую в термопринтер по TSPL (АТОЛ BP41 и совместимые).

  python3 print_tspl.py label-50x30-1.png              — показать, что будет отправлено
  python3 print_tspl.py label-50x30-1.png /dev/usb/lp0 — напечатать
  python3 print_tspl.py label-50x30-1.png /dev/usb/lp0 3   — 3 копии

Размер этикетки берётся из имени файла (label-50x30-...) или из --size 50x30.
"""
from PIL import Image
import sys, re, os

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opts = {a.split("=")[0]: a.split("=")[-1] for a in sys.argv[1:] if a.startswith("--")}
if not args:
    sys.exit(__doc__)

src = args[0]
dev = args[1] if len(args) > 1 else None
copies = int(args[2]) if len(args) > 2 else 1

DPI = 203
m = re.search(r"(\d+)x(\d+)", opts.get("--size", "") or os.path.basename(src))
if not m:
    sys.exit("не понял размер этикетки — добавь --size=50x30")
w_mm, h_mm = int(m.group(1)), int(m.group(2))

im = Image.open(src).convert("L")
target = (round(w_mm * DPI / 25.4), round(h_mm * DPI / 25.4))
if im.size != target:
    print(f"* размер {im.size} != {target}, масштабирую", file=sys.stderr)
    im = im.resize(target, Image.LANCZOS)
im = im.point(lambda p: 0 if p < 128 else 255).convert("1")

W, H = im.size
row_bytes = (W + 7) // 8
px = im.load()
data = bytearray()
for y in range(H):
    for bx in range(row_bytes):
        b = 0
        for bit in range(8):
            x = bx * 8 + bit
            # в TSPL 1 — не печатать, 0 — чёрная точка
            white = 1 if (x >= W or px[x, y] != 0) else 0
            b = (b << 1) | white
        data.append(b)

cmd = bytearray()
cmd += f"SIZE {w_mm} mm,{h_mm} mm\r\n".encode()
cmd += b"GAP 2 mm,0 mm\r\n"       # зазор между этикетками; для чёрной метки — BLINE
cmd += b"REFERENCE 0,0\r\n"   # сбросить смещение начала печати
cmd += b"OFFSET 0 mm\r\n"
cmd += b"SHIFT 0\r\n"
cmd += b"DIRECTION 1\r\n"
cmd += b"DENSITY 10\r\n"
cmd += b"SPEED 3\r\n"
cmd += b"CLS\r\n"
cmd += f"BITMAP 0,0,{row_bytes},{H},0,".encode() + bytes(data) + b"\r\n"
cmd += f"PRINT {copies},1\r\n".encode()

if dev:
    with open(dev, "wb") as f:
        f.write(cmd)
    print(f"отправлено {len(cmd)} байт в {dev}")
else:
    out = os.path.splitext(src)[0] + ".tspl.bin"
    open(out, "wb").write(cmd)
    print(f"устройство не указано, задание сохранено в {out} ({len(cmd)} байт)")
    print(f"печать: python3 print_tspl.py {src} /dev/usb/lp0")
