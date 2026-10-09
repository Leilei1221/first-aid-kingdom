"""把老師用 ChatGPT 生的雪嶺（E4）F1 圖轉成遊戲用的 WebP：山腳村、旅店內部、帕桑嚮導、老闆娘（全身＋頭像）。
用法：python3 tools/ch4_import_images.py "<原始圖檔資料夾>"
來源檔名見 MAP（兩張場景是 'Codex 圖像 …' 加時間）。沒有 numpy，只用 PIL；人物去背沿用 tools/ch3_import_e12_images.py 的 cutout。"""
import sys, pathlib, json, importlib.util
from PIL import Image
ROOT = pathlib.Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location('e12', ROOT / 'tools/ch3_import_e12_images.py'); e12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e12)
SRC = pathlib.Path(sys.argv[1]); OUT = ROOT / 'chapters/ch4/assets'; OUT.mkdir(parents=True, exist_ok=True)
MAP = [  # (來源檔名（含 * 的用結尾比對）, 輸出, 種類, 尺寸)
 ('*02_01_01', 'ch4_village', 'scene', None), ('*02_01_39', 'ch4_inn', 'scene', None),
 ('ch4_guide.png', 'ch4_guide', 'body', 520), ('ch4_innk.png', 'ch4_innk', 'body', 520),
 ('ch4_guide_face.png', 'ch4_guide_face', 'face', 160), ('ch4_innk_face.png', 'ch4_innk_face', 'face', 160)]
def find(n):
    if n.startswith('*'):
        r = [p for p in SRC.glob('Codex 圖像 2026年10月9日*') if p.stem.endswith(n[1:])]
        if len(r) != 1: raise SystemExit(f'找不到或有多個：{n} {r}')
        return r[0]
    return SRC / n
sizes = {}
for n, name, kind, size in MAP:
    im = Image.open(find(n))
    if kind == 'scene': out = im.convert('RGB').resize((1672, 941), Image.LANCZOS); dst = OUT / f'{name}.webp'; out.save(dst, 'WEBP', quality=82)
    else:
        cut = e12.cutout(im, enclosed=kind != 'face')
        if kind == 'face':
            s = min(cut.size); x0 = (cut.width - s) // 2; out = cut.crop((x0, 0, x0 + s, s)).resize((size, size), Image.LANCZOS)
        else: out = cut.copy(); out.thumbnail((size, size), Image.LANCZOS)
        dst = OUT / f'{name}.webp'; out.save(dst, 'WEBP', quality=90)
    if kind != 'scene': sizes[name] = round(out.width / out.height, 4)
    print(name, out.size, dst.stat().st_size // 1024, 'KB')
rp = ROOT / 'chapters/ch4/ratios.json'; r = json.load(open(rp, encoding='utf-8')) if rp.exists() else {'RATIO': {}}
r['RATIO'].update(sizes); json.dump(r, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
