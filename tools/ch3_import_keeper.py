"""把老師用 ChatGPT 生的燈塔管理員圖（灰底）轉成遊戲用的 WebP：全身圖去背、高 520；大頭貼去背、放進 160×160（和其他 NPC 一樣）。
用法：python3 tools/ch3_import_keeper.py "<圖卡資料夾>"
檔名對應（以檔名裡的時間辨認，2026-10-10 上午 11:34～11:35 那一批）：見 MAP。沒有 numpy，只用 PIL。"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFilter
SRC = pathlib.Path(sys.argv[1])
ROOT = pathlib.Path(__file__).parent.parent
MAP = [('上午11_34_47', 'ch3_keeper', 'body'), ('上午11_35_33', 'ch3_keeper_face', 'face')]
def find(t):
    r = [p for p in SRC.glob('Codex 圖像 2026年10月10日*') if p.stem.endswith(t)]
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

for t, name, kind in MAP:
    out = cutout(Image.open(find(t)), tol=22, enclosed=True)
    if kind == 'body':
        out = out.resize((round(out.size[0] * 520 / out.size[1]), 520), Image.LANCZOS); print(name, out.size, 'RATIO', round(out.size[0] / 520, 3))
    else:
        s = 160 / max(out.size); out = out.resize((round(out.size[0] * s), round(out.size[1] * s)), Image.LANCZOS)
        cv = Image.new('RGBA', (160, 160), (0, 0, 0, 0)); cv.alpha_composite(out, ((160 - out.size[0]) // 2, (160 - out.size[1]) // 2)); out = cv
    dst = ROOT / 'chapters/ch3/assets' / f'{name}.webp'; out.save(dst, 'WEBP', quality=90)
    print('→', dst.relative_to(ROOT), dst.stat().st_size // 1024, 'KB')
