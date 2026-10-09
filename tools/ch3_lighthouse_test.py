"""藍堡「前往燈塔」的入口（老師 2026-10-09 要求移到防波堤起點的紅色記號處）：入口在棧橋起點、從廣場走得到（走路遮罩連通）、進燈塔再出來落在入口旁。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_lighthouse_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from collections import deque
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
SC = json.load(open(ROOT / 'chapters/ch3/scenes.json', encoding='utf-8'))
W = json.load(open(ROOT / 'chapters/ch3/walks.json', encoding='utf-8'))['ch3_harbor']
door = next(t for t in SC['ch3_harbor']['things'] if t['label'] == '前往燈塔')
back = SC['ch3_lighthouse']['exits'][0]['at']
ok = lambda x, y: 0 <= int(y // 8) < len(W) and 0 <= int(x // 8) < len(W[0]) and W[int(y // 8)][int(x // 8)] == '1'
def eroded(k):  # 把可走範圍往內縮 k 格（一格 8px），模擬主角有身體寬度：通道不夠寬就會斷
    H, Wd = len(W), len(W[0]); g = [[W[j][i] == '1' for i in range(Wd)] for j in range(H)]
    for _ in range(k):
        g = [[g[j][i] and all(0 <= j + dj < H and 0 <= i + di < Wd and g[j + dj][i + di] for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))) for i in range(Wd)] for j in range(H)]
    return g
def reach_g(g, a, b):
    s = (int(a[0] // 8), int(a[1] // 8)); t = (int(b[0] // 8), int(b[1] // 8))
    if not g[s[1]][s[0]]: return False
    seen = {s}; q = deque([s])
    while q:
        i, j = q.popleft()
        if abs(i - t[0]) <= 3 and abs(j - t[1]) <= 3: return True
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (i + di, j + dj)
            if n not in seen and 0 <= n[1] < len(g) and 0 <= n[0] < len(g[0]) and g[n[1]][n[0]]: seen.add(n); q.append(n)
    return False
def reachable(a, b):
    s = (int(a[0] // 8), int(a[1] // 8)); t = (int(b[0] // 8), int(b[1] // 8)); seen = {s}; q = deque([s])
    while q:
        i, j = q.popleft()
        if (i, j) == t: return True
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (i + di, j + dj)
            if n not in seen and 0 <= n[1] < len(W) and 0 <= n[0] < len(W[0]) and W[n[1]][n[0]] == '1': seen.add(n); q.append(n)
    return False
check('入口在棧橋起點（x 600～800、y 150～300，不再貼著石牆邊）', 600 <= door['x'] <= 800 and 150 <= door['y'] <= 300, str(door))
check('入口位置與回來的落點都是可走的', ok(door['x'], door['y']) and ok(*back), f"{door} {back}")
for name, pt in [('出生點', SC['ch3_harbor']['spawn']), ('搭船處', (830, 440)), ('港口救生員', (1250, 760)), ('市集門口', (1490, 290))]:
    check(f'從{name}走得到燈塔入口（走路遮罩連通）', reachable(pt, (door['x'], door['y'])), str(pt))
G = eroded(4)   # 往內縮 32px：通道要夠寬，主角才走得過
check('通道夠寬：可走範圍往內縮 32px 後，從出生點仍走得到入口附近', reach_g(G, SC['ch3_harbor']['spawn'], (door['x'], door['y'] + 20)))
check('通道夠寬：從上層平台（水手後面）也走得到入口附近', reach_g(G, (960, 340), (door['x'], door['y'] + 20)) or reach_g(G, (900, 420), (door['x'], door['y'] + 20)))
check('入口有自己的觸發範圍（r）比一般互動點大，並且優先於附近的「搭船」（pri）', door.get('r', 0) >= 200 and door.get('pri', 0) >= 1, str(door))
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        await page.evaluate("() => { window.__fa.go('ch3_harbor', [820, 640]); }"); await page.wait_for_timeout(900)
        await page.evaluate("([x, y]) => { window.__fa.S.pos = {x, y}; }", [door['x'], door['y'] + 20]); await page.wait_for_timeout(400)
        act = await page.inner_text('#act'); check('走到入口：互動鈕「前往燈塔」', '燈塔' in act, act)
        await page.evaluate("() => { window.__fa.S.pos = {x: 800, y: 380}; }"); await page.wait_for_timeout(400)
        act = await page.inner_text('#act'); check('離入口 200px 左右（在石階中段，離搭船處更近）也優先出現「前往燈塔」', '燈塔' in act, act)
        await page.evaluate("() => { window.__fa.S.pos = {x: 1100, y: 520}; }"); await page.wait_for_timeout(400)
        act = await page.inner_text('#act'); check('離得太遠（廣場中間）不會出現', '燈塔' not in act, act)
        await page.evaluate("() => { window.__fa.S.pos = {x: 830, y: 470}; }"); await page.wait_for_timeout(400)
        act = await page.inner_text('#act'); check('站在搭船處：還是「搭船回綠葉谷」（沒有被搶走）', '搭船' in act, act)
        await page.evaluate("([x, y]) => { window.__fa.S.pos = {x, y}; }", [door['x'], door['y'] + 20]); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(1200)
        check('進到燈塔場景', await st('S.scene') == 'ch3_lighthouse', await st('S.scene'))
        check('從燈塔出來的落點在新入口旁（80px 內），不在原本的石牆邊', abs(back[0] - door['x']) < 80 and abs(back[1] - door['y']) < 80, str(back))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
