"""把老師用 ChatGPT 生的寵物圖（小貓、貓頭鷹、信封、送信插圖）轉成遊戲用的 WebP，放在 assets/。
用法：python3 tools/pets_import_images.py "<原始圖檔資料夾>"；跑完會印出各圖的寬高比（填進 content/balance.json 的 PETS）。
沒有 numpy，只用 PIL；去背沿用 tools/ch3_import_e12_images.py 的 cutout。"""
import sys, pathlib, importlib.util
from PIL import Image
ROOT = pathlib.Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location('e12', ROOT / 'tools/ch3_import_e12_images.py'); e12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e12)
SRC = pathlib.Path(sys.argv[1]); OUT = ROOT / 'assets'
MAP = [('pet_cat.png', 'pet_cat', 'body', 420), ('pet_owl.png', 'pet_owl', 'body', 420),
 ('pet_cat_face.png', 'pet_cat_face', 'face', 160), ('pet_owl_face.png', 'pet_owl_face', 'face', 160),
 ('pet_i_letter.png', 'pet_i_letter', 'obj', 256),
 ('pet_cat_deliver.png', 'pet_cat_deliver', 'pic', 520), ('pet_owl_deliver.png', 'pet_owl_deliver', 'pic', 520)]
for n, name, kind, size in MAP:
    im = Image.open(SRC / n)
    if kind == 'pic': out = im.convert('RGB'); out.thumbnail((size, size), Image.LANCZOS)
    else:
        cut = e12.cutout(im, enclosed=False)
        if kind == 'face':
            s = min(cut.size); x0 = (cut.width - s) // 2; out = cut.crop((x0, 0, x0 + s, s)).resize((size, size), Image.LANCZOS)
        else: out = cut.copy(); out.thumbnail((size, size), Image.LANCZOS)
    dst = OUT / f'{name}.webp'; out.save(dst, 'WEBP', quality=88)
    print(name, out.size, 'ratio', round(out.width / out.height, 4), dst.stat().st_size // 1024, 'KB')
