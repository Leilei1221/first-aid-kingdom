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
 ('ch4_guide_face.png', 'ch4_guide_face', 'face', 160), ('ch4_innk_face.png', 'ch4_innk_face', 'face', 160),
 # F2：營地 1（白天、夜晚）、同行登山客、山上版的帕桑
 ('喜馬拉雅中山營地.png', 'ch4_camp1', 'scene', None), ('喜馬拉雅中山營地_夜景.png', 'ch4_camp1_night', 'scene', None),
 ('ch4_young_hiker.png', 'ch4_hiker', 'body', 520), ('ch4_young_hiker_portrait.png', 'ch4_hiker_face', 'face', 160),
 ('ch4_guide_mountain.png', 'ch4_guide_up', 'body', 520), ('ch4_guide_portrait.png', 'ch4_guide_up_face', 'face', 160),
 ('ch4_young_hiker_cold.png', 'ch4_hiker_cold', 'body', 520),
 # F3：營地 2（白天、夜晚）、資深登山客老周（站立、不適、頭像）
 ('喜馬拉雅高山營地.png', 'ch4_camp2', 'scene', None), ('喜馬拉雅高山營地_夜景.png', 'ch4_camp2_night', 'scene', None),
 ('ch4_elder.png', 'ch4_elder', 'body', 520), ('ch4_elder_face.png', 'ch4_elder_face', 'face', 160), ('ch4_elder_sick.png', 'ch4_elder_sick', 'body', 520),
 # F4：雪線、登山攝影師（站立、雪盲、凍傷、頭像）、三張傷口圖（放在 assets/，key 由章節程式註冊）
 ('喜馬拉雅雪線雪原.png', 'ch4_snowline', 'scene', None),
 ('ch4_photog.png', 'ch4_photog', 'body', 520), ('ch4_photog_face.png', 'ch4_photog_face', 'face', 160),
 ('ch4_photog_snowblind.png', 'ch4_photog_snowblind', 'body', 520), ('ch4_photog_cold.png', 'ch4_photog_cold', 'body', 520),
 ('w_frostbite.png', 'w_frostbite', 'wound', 420), ('w_frostface.png', 'w_frostface', 'wound', 420), ('w_snowblind.png', 'w_snowblind', 'wound', 420),
 # F5：山屋室外（白天）、山屋室內、管理員、暴風雪情境圖、求救訊號圖示（夜晚版『喜馬拉雅高山山莊_夜景.png』還沒用到，之後的階段才接）
 ('喜馬拉雅高山山莊.png', 'ch4_lodge', 'scene', None), ('喜馬拉雅山屋室內.png', 'ch4_lodge_in', 'scene', None), ('喜馬拉雅白茫風雪.png', 'ch4_whiteout', 'scene', None),
 ('ch4_keeper.png', 'ch4_keeper', 'body', 520), ('ch4_keeper_face.png', 'ch4_keeper_face', 'face', 160),
 ('ch4_i_whistle.png', 'ch4_i_whistle', 'obj', 256), ('ch4_i_mirro.png', 'ch4_i_mirror', 'obj', 256), ('ch4_i_torch.png', 'ch4_i_torch', 'obj', 256)]
def find(n):
    if n.startswith('*'):
        r = [p for p in SRC.glob('Codex 圖像 2026年10月9日*') if p.stem.endswith(n[1:])]
        if len(r) != 1: raise SystemExit(f'找不到或有多個：{n} {r}')
        return r[0]
    return SRC / n
sizes = {}
for n, name, kind, size in MAP:
    im = Image.open(find(n))
    if kind == 'wound': out = im.convert('RGB').resize((size, size), Image.LANCZOS); dst = ROOT / 'assets' / f'{name}.webp'; out.save(dst, 'WEBP', quality=88)
    elif kind == 'scene': out = im.convert('RGB').resize((1672, 941), Image.LANCZOS); dst = OUT / f'{name}.webp'; out.save(dst, 'WEBP', quality=82)
    else:
        cut = e12.cutout(im, enclosed=kind != 'face')
        if kind == 'face':
            s = min(cut.size); x0 = (cut.width - s) // 2; out = cut.crop((x0, 0, x0 + s, s)).resize((size, size), Image.LANCZOS)
        else: out = cut.copy(); out.thumbnail((size, size), Image.LANCZOS)
        dst = OUT / f'{name}.webp'; out.save(dst, 'WEBP', quality=90)
    if kind not in ('scene', 'wound'): sizes[name] = round(out.width / out.height, 4)
    print(name, out.size, dst.stat().st_size // 1024, 'KB')
rp = ROOT / 'chapters/ch4/ratios.json'; r = json.load(open(rp, encoding='utf-8')) if rp.exists() else {'RATIO': {}}
r['RATIO'].update(sizes); json.dump(r, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
