"""藍堡港口的走路範圍：主角不能走到藍色屋頂上（老師 2026-10-09 試玩發現）。不需要瀏覽器。
用法：python3 tools/ch3_roof_test.py"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = json.load(open(os.path.join(ROOT, 'chapters/ch3/walks.json'), encoding='utf-8'))['ch3_harbor']
ok = lambda x, y: 0 <= int(y // 8) < len(W) and 0 <= int(x // 8) < len(W[0]) and W[int(y // 8)][int(x // 8)] == '1'
fails = 0
def check(name, cond):
    global fails
    print(('✓' if cond else '✗'), name)
    if not cond: fails += 1
# 預覽圖座標（1254×706）換算成遊戲座標：×1.3397
g = lambda px, py: (px * 1.3397, py * 1.3397)
roof = {'救生站塔頂': g(1075, 290), '救生站屋頂（左）': g(950, 385), '救生站屋頂（右）': g(1120, 420), '救生站屋頂（中）': g(1030, 395),
        '下方中間的藍屋頂': g(930, 672), '下方中間的藍屋頂（左）': g(915, 682), '右下角的藍屋頂': g(1150, 630), '右下角的藍屋頂（下）': g(1200, 680)}
for name, (x, y) in roof.items(): check(f'{name} 不能走上去', not ok(x, y))
walk = {'出生點': (820, 640), '廣場中間': (1000, 600), '救生站門前的空地': g(930, 610), '搭船處': (830, 440), '燈塔入口': (695, 236), }
for name, (x, y) in walk.items(): check(f'{name} 還是走得到', ok(x, y))
import math
near = lambda x, y, r=120: any(ok(x + dx, y + dy) for dx in range(-r, r + 1, 8) for dy in range(-r, r + 1, 8) if math.hypot(dx, dy) <= r)
check('往市集的門（1490,290）120px 內還是有可走處', near(1490, 290))
check('進入救生站的門（1390,790）120px 內還是有可走處', near(1390, 790))
print('失敗', fails); sys.exit(1 if fails else 0)
