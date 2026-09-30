"""穿牆測試：把主角放在「不可走」的位置（牆、屋頂），按住方向鍵一秒，確認最後停在可走的格子上。
用法：python3 tools/wall_test.py http://localhost:8765/index.html
舊版（自由移動的脫困邏輯）會失敗，新版（snapFree）應全部通過。"""
import asyncio, json, os, random, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALKS = json.load(open(os.path.join(ROOT, 'data/walks.json')))
CELL = 8

def blocked_points(rows, n=3):
    rnd = random.Random(7); H, W = len(rows), len(rows[0]); out = []
    while len(out) < n:
        x, y = rnd.randrange(W), rnd.randrange(H)
        if rows[y][x] != '1':
            out.append((x * CELL + 4, y * CELL + 4))
    return out

async def main(url):
    bad = 0; total = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for sid, rows in WALKS.items():
            for (x, y) in blocked_points(rows):
                ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
                await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
                page = await ctx.new_page()
                await page.goto(url + '#debug')
                await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
                await page.evaluate(f"""() => {{ const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.scene = {json.dumps(sid)};
                  S.pos = {{x: {x}, y: {y}}}; S.started = true; document.getElementById('btnStart').click(); }}""")
                await page.wait_for_timeout(500)
                await page.keyboard.down('ArrowRight'); await page.keyboard.down('ArrowDown')
                await page.wait_for_timeout(1000)
                await page.keyboard.up('ArrowRight'); await page.keyboard.up('ArrowDown')
                pos = await page.evaluate("() => ({scene: window.__fa.S.scene, x: window.__fa.S.pos.x, y: window.__fa.S.pos.y})")
                r = WALKS.get(pos['scene'])
                ok = pos['scene'] != sid or (r[int(pos['y'] // CELL)][int(pos['x'] // CELL)] == '1')
                total += 1; bad += 0 if ok else 1
                if not ok: print('✗', sid, '起點', (x, y), '→', pos)
                await ctx.close()
        await b.close()
    print(f'{total} 個測試點，穿牆 {bad} 個')
    return bad

if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
