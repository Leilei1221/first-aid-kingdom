"""防災包場景標記圖（老師 2026-10-28 生圖，灰底）：去背、最長邊縮到 400，存 assets/escape_bag.webp。
用法：python3 tools/stash_bag_import.py <圖檔>"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFilter
ROOT = pathlib.Path(__file__).parent.parent
def cutout(im, tol=22, enclosed=True):
    im = im.convert('RGB'); w, h = im.size
    border = [im.getpixel((x, 0)) for x in range(0, w, 7)] + [im.getpixel((x, h - 1)) for x in range(0, w, 7)] + [im.getpixel((0, y)) for y in range(0, h, 7)] + [im.getpixel((w - 1, y)) for y in range(0, h, 7)]
    bg = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))
    work = im.copy(); S = (255, 0, 255)
    near = lambda c: all(abs(c[i] - bg[i]) <= tol for i in range(3))
    for x in range(0, w, 9):
        for y in (0, h - 1):
            if work.getpixel((x, y)) != S and near(work.getpixel((x, y))): ImageDraw.floodfill(work, (x, y), S, thresh=tol * 1.6)
    for y in range(0, h, 9):
        for x in (0, w - 1):
            if work.getpixel((x, y)) != S and near(work.getpixel((x, y))): ImageDraw.floodfill(work, (x, y), S, thresh=tol * 1.6)
    mask = Image.new('L', (w, h), 255)
    mask.putdata([0 if p == S else 255 for p in work.getdata()])
    # 第二輪：被物件圍住、沒被外面填到的灰底（釣竿線圈裡、兩支竿之間）。找「顏色跟背景很像」的大塊區域才去掉，細小的灰色（石頭、反光）留著
    tight = Image.new('L', (w, h), 0)
    tight.putdata([255 if all(abs(c[i] - bg[i]) <= 14 for i in range(3)) else 0 for c in im.getdata()])
    blobs = tight.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(11))
    if enclosed: mask = Image.composite(Image.new('L', (w, h), 0), mask, blobs)  # 魚、動物身上有灰色反光，不做這一輪
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    out = im.convert('RGBA'); out.putalpha(mask)
    return out.crop(out.getbbox() or (0, 0, w, h))


out = cutout(Image.open(sys.argv[1]), tol=22, enclosed=False); out.thumbnail((400, 400), Image.LANCZOS)
dst = ROOT / 'assets' / 'escape_bag.webp'; out.save(dst, 'WEBP', quality=90)
print(out.size, '→', dst.relative_to(ROOT), dst.stat().st_size // 1024, 'KB')
