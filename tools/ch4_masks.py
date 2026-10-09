"""雪嶺（第四章）場景的可行走遮罩：多邊形（可走）減去障礙物，輸出 chapters/ch4/walks.json（每格 8px，與 data/walks.json 同格式）。
座標直接用遊戲座標（1672×941）。疊圖輸出到 /tmp/ch4_mask_*.png 供目視檢查。用法：python3 tools/ch4_masks.py [場景key]"""
import json, os, sys
from PIL import Image, ImageDraw
W, H, C = 1672, 941, 8
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC = {
 'village': dict(
   walk=[[(300,520),(330,430),(450,350),(860,340),(1060,350),(1230,415),(1260,480),(1450,545),(1560,600),(1580,665),(1420,705),(1100,770),(900,800),(800,785),(770,730),(690,700),(480,690),(380,650),(300,610)],
         [(300,670),(430,640),(560,650),(700,700),(780,730),(770,780),(600,790),(420,770),(310,730)]],
   block=[('ell',590,800,170,70)]),
 'inn': dict(
   walk=[[(330,790),(290,640),(310,520),(450,470),(620,430),(1000,430),(1090,450),(1300,440),(1400,540),(1650,540),(1650,690),(1420,700),(1330,830),(1260,935),(330,935),(290,880)]],
   block=[('rect',640,430,1010,470),('rect',1420,420,1650,540)]),
 'camp1': dict(
   walk=[[(190,330),(330,290),(700,285),(880,290),(1000,295),(1250,300),(1390,335),(1450,385),(1500,470),(1600,520),(1620,660),(1500,760),(1250,840),(900,860),(780,810),(660,830),(520,830),(420,810),(340,860),(240,880),(160,830),(140,760),(220,700),(290,660),(280,560),(230,500),(180,420)]],
   block=[('rect',0,430,285,700),('ell',1160,260,90,40)]),
}
SC['camp1_night'] = SC['camp1']
def build(only=None):
    out = {}
    for k, s in SC.items():
        if only and k != only: continue
        m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
        for poly in s['walk']: d.polygon(poly, fill=255)
        for b in s['block']:
            if b[0] == 'ell': _, x, y, rx, ry = b; d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=0)
            elif b[0] == 'rect': _, x0, y0, x1, y1 = b; d.rectangle([x0, y0, x1, y1], fill=0)
            else: d.polygon(b[1], fill=0)
        px = m.load(); rows = []
        for j in range(H // C + 1):
            rows.append(''.join('1' if px[min(W - 1, i * C + 4), min(H - 1, j * C + 4)] > 127 else '0' for i in range(W // C + 1)))
        out['ch4_' + k] = rows
        im = Image.open(os.path.join(ROOT, f'chapters/ch4/assets/ch4_{k}.webp')).convert('RGBA'); ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c == '1': od.rectangle([i * C, j * C, i * C + C - 1, j * C + C - 1], fill=(0, 140, 255, 90))
        Image.alpha_composite(im, ov).convert('RGB').resize((1254, 706)).save(f'/tmp/ch4_mask_{k}.png')
    return out
if __name__ == '__main__':
    out = build(sys.argv[1] if len(sys.argv) > 1 else None)
    if len(sys.argv) <= 1: json.dump(out, open(os.path.join(ROOT, 'chapters/ch4/walks.json'), 'w'))
    print(len(out), '個場景')
