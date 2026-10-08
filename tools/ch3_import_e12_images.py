"""把老師用 ChatGPT 生的 E1、E2 圖轉成遊戲用的 WebP：傷口圖（420×420 白底）、物件圖（灰底去背）。
用法：python3 tools/ch3_import_e12_images.py "<圖卡資料夾>"
檔名對應（以檔名裡的時間辨認，2026-10-08 晚上那一批）：見 MAP。沒有 numpy，只用 PIL。"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFilter
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
ROOT = pathlib.Path(__file__).parent.parent
MAP = [  # (檔名結尾時間, 輸出, 種類, 最長邊)
 ('11_56_57', 'w_octopus', 'wound', 420), ('11_57_31', 'w_jelly', 'wound', 420), ('11_57_37', 'w_rockcut', 'wound', 420), ('11_57_42', 'w_vibrio', 'wound', 420),
 ('11_57_47', 'ch3_hb_board', 'obj', 460), ('11_57_51', 'ch3_fish_spot', 'obj', 480), ('11_57_56', 'ch3_fish_stall', 'obj', 560),
 ('11_58_04', 'ch3_f_mackerel', 'obj', 420), ('11_58_09', 'ch3_f_horse', 'obj', 420), ('11_58_15', 'ch3_f_snapper', 'obj', 420), ('11_58_19', 'ch3_f_grouper', 'obj', 420),
 ('11_58_23', 'ch3_p_turtle', 'obj', 420), ('11_58_27', 'ch3_p_ray', 'obj', 420), ('11_58_33', 'ch3_rod', 'obj', 420)]
def find(t):
    r = [p for p in SRC.glob('Codex 圖像 2026年10月8日*') if p.stem.endswith(t)]
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
if __name__ == '__main__':
    for t, name, kind, size in MAP:
        im = Image.open(find(t))
        if kind == 'wound':
            out = im.convert('RGB').resize((size, size), Image.LANCZOS); dst = ROOT / 'assets' / f'{name}.webp'; out.save(dst, 'WEBP', quality=88)
        else:
            out = cutout(im, enclosed=name in ('ch3_hb_board', 'ch3_fish_spot', 'ch3_fish_stall', 'ch3_rod')); out.thumbnail((size, size), Image.LANCZOS); dst = ROOT / 'chapters/ch3/assets' / f'{name}.webp'; out.save(dst, 'WEBP', quality=90)
            print(name, out.size, round(out.size[0] / out.size[1], 4))
        print('→', dst.relative_to(ROOT), dst.stat().st_size // 1024, 'KB')
