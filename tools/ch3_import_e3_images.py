"""把老師用 ChatGPT 生的 E3 圖（商人、商船、海圖碎片、登山裝備、整套造型）轉成遊戲用的 WebP。
用法：python3 tools/ch3_import_e3_images.py "<圖卡資料夾>"
檔名以 2026-10-09 凌晨的時間辨認（見 MAP）。沒有 numpy，只用 PIL。"""
import sys, pathlib, importlib.util
from PIL import Image, ImageFilter
ROOT = pathlib.Path(__file__).parent.parent
spec = importlib.util.spec_from_file_location('e12', ROOT / 'tools/ch3_import_e12_images.py'); e12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(e12)
SRC = pathlib.Path(sys.argv[1]); OUT = ROOT / 'chapters/ch3/assets'
MAP = [  # (時間, 輸出, 種類, 尺寸)
 ('12_22_59', 'ch3_m_jp', 'body', 520), ('12_23_39', 'ch3_m_au', 'body', 520), ('12_23_42', 'ch3_m_np', 'body', 520),
 ('12_29_40', 'ch3_m_jp_face', 'face', 160), ('12_29_44', 'ch3_m_au_face', 'face', 160), ('12_29_49', 'ch3_m_np_face', 'face', 160),
 ('12_29_53', 'ch3_ship_jp', 'obj', 520), ('12_29_57', 'ch3_ship_au', 'obj', 520), ('12_30_02', 'ch3_ship_np', 'obj', 520),
 ('12_38_47', 'ch3_map_frag', 'obj', 300),
 ('12_38_51', 'ch3_g_jacket', 'obj', 420), ('12_38_57', 'ch3_g_hat', 'obj', 360), ('12_39_01', 'ch3_g_pants', 'obj', 420), ('12_39_05', 'ch3_g_gloves', 'obj', 420),
 ('12_39_09', 'ch3_g_boots', 'obj', 420), ('12_39_14', 'ch3_g_goggles', 'obj', 360), ('12_39_19', 'ch3_g_pack1', 'obj', 420), ('12_39_23', 'ch3_g_pack2', 'obj', 420),
 ('12_39_27', 'ch3_i_warmer', 'obj', 260), ('12_39_31', 'ch3_i_blanket', 'obj', 260), ('12_39_36', 'ch3_i_headlamp', 'obj', 260), ('12_39_40', 'ch3_i_socks', 'obj', 260)
]
HERO = (330, 520)
def find(t):
    r = [p for p in SRC.glob('Codex 圖像 2026年10月9日*') if p.stem.endswith(t)]
    if len(r) != 1: raise SystemExit(f'找不到或有多個：{t} {r}')
    return r[0]
def defringe(im, px=2):
    a = im.getchannel('A').filter(ImageFilter.MinFilter(2 * px + 1)).filter(ImageFilter.GaussianBlur(0.8)); im = im.copy(); im.putalpha(a); return im
sizes = {}
for t, name, kind, size in MAP:
    im = Image.open(find(t))
    if im.mode == 'RGBA' and im.getchannel('A').getextrema()[0] == 0: cut = defringe(im).crop(im.getchannel('A').getbbox())  # 已經去背的（日本頭像）：去掉邊緣的紅色雜邊
    else: cut = e12.cutout(im, enclosed=kind != 'face')
    if kind == 'face':
        s = min(cut.size); x0 = (cut.width - s) // 2; out = cut.crop((x0, 0, x0 + s, s)).resize((size, size), Image.LANCZOS)  # 取上方、左右置中的正方形，臉才夠大
    elif kind == 'outfit':  # 放到和主角一樣大小的畫布，腳底對齊、左右置中，這樣直接換圖不會變形
        k = min(HERO[0] / cut.width, HERO[1] / cut.height); c = cut.resize((round(cut.width * k), round(cut.height * k)), Image.LANCZOS)
        out = Image.new('RGBA', HERO, (0, 0, 0, 0)); out.paste(c, ((HERO[0] - c.width) // 2, HERO[1] - c.height), c)
    elif kind == 'body':
        out = cut.copy(); out.thumbnail((size, size), Image.LANCZOS)
    else:
        out = cut.copy(); out.thumbnail((size, size), Image.LANCZOS)
    dst = OUT / f'{name}.webp'; out.save(dst, 'WEBP', quality=90)
    sizes[name] = round(out.width / out.height, 4)
    print(name, out.size, sizes[name], dst.stat().st_size // 1024, 'KB')
import json
rp = ROOT / 'chapters/ch3/ratios.json'; r = json.load(open(rp, encoding='utf-8')); r['RATIO'].update(sizes); json.dump(r, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
cp = ROOT / 'chapters/ch3/chapter.json'; m = json.load(open(cp, encoding='utf-8')); m['assets'] = sorted(set(m['assets']) | set(sizes)); json.dump(m, open(cp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
