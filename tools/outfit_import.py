"""把老師用 ChatGPT 生的主角裝扮圖（灰底、1024×1536）轉成遊戲用的 WebP：去背、縮成 330×520 的透明畫布（和 hero.webp 同尺寸，腳底貼齊、水平置中）。
用法：python3 tools/outfit_import.py "<圖卡資料夾>"
檔名對應（以檔名裡的時間辨認，2026-10-09 凌晨 12:50～12:51 那一批）：見 MAP。沒有 numpy，只用 PIL。"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFilter
SRC = pathlib.Path(sys.argv[1])
ROOT = pathlib.Path(__file__).parent.parent
CW, CH = 330, 520
MAP = [('12_50_55', 'outfit_sailor'), ('12_51_04', 'outfit_mountain'), ('12_51_09', 'outfit_lifeguard'), ('12_51_36', 'outfit_guardian')]
def find(t):
    r = [p for p in SRC.glob('Codex 圖像 2026年10月9日*') if p.stem.endswith(t)]
    if len(r) != 1: raise SystemExit(f'找不到或有多個：{t} {r}')
    return r[0]
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

for t, name in MAP:
    out = cutout(Image.open(find(t)), tol=22, enclosed=True)
    s = min(CW / out.size[0], CH / out.size[1]); out = out.resize((round(out.size[0] * s), round(out.size[1] * s)), Image.LANCZOS)
    canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); canvas.alpha_composite(out, ((CW - out.size[0]) // 2, CH - out.size[1]))
    dst = ROOT / 'assets' / f'{name}.webp'; canvas.save(dst, 'WEBP', quality=90)
    print(name, out.size, '→', dst.relative_to(ROOT), dst.stat().st_size // 1024, 'KB')
