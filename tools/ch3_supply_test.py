"""藍堡的急救用品補給點（老師 2026-10-09 同意加）：救生站的急救用品櫃，賣和綠葉谷雜貨店一樣的基本急救用品（同價、不打折、不賒帳）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_supply_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
IT = json.load(open(pathlib.Path(__file__).parent.parent / 'content/items.json', encoding='utf-8'))
MED = IT['SHOP_MED']; ITEMS = IT['ITEMS']
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 100; S.sta = 100; S.day = 5; S.kitCap = 6; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        await page.evaluate("() => { window.__fa.go('ch3_rescue', [990, 530]); }"); await page.wait_for_timeout(900)
        await page.evaluate("() => { window.__fa.S.pos = {x: 990, y: 505}; }"); await page.wait_for_timeout(400)
        act = await page.inner_text('#act'); check('救生站有「急救用品櫃」互動鈕（不是 AED 或休息）', '急救用品櫃' in act, act)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        t = await page.inner_text('#dText')
        check('列出雜貨店的全部基本急救用品，價格與雜貨店相同', all(ITEMS[k]['name'] in t and f"{ITEMS[k]['price']} 金幣" in t for k in MED), t[:300])
        b4 = await st('S.coins'); n4 = await st('S.kit.length')
        await page.locator('#dText button[data-a="gauze"]').click(); await page.wait_for_timeout(350)
        check(f'買無菌紗布：扣 {ITEMS["gauze"]["price"]} 金幣、背包 +1', await st('S.coins') == b4 - ITEMS['gauze']['price'] and await st('S.kit.length') == n4 + 1 and await st("S.kit.includes('gauze')"))
        await page.evaluate("() => { window.__fa.S.coins = 9; window.__fa.refresh(); }")
        await page.locator('#dText button[data-a="glove"]').evaluate("b => { b.disabled = false; }"); c = await st('S.coins'); await page.locator('#dText button[data-a="glove"]').click(); await page.wait_for_timeout(300)
        check('金幣不夠（沒有賒帳）：硬按也買不到、不扣錢', await st('S.coins') == c and await st('S.kit.length') == n4 + 1)
        await page.evaluate("() => { const S = window.__fa.S; S.coins = 500; while (S.kit.length < S.kitCap) S.kit.push('bandaid'); window.__fa.refresh(); }")
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        check('背包滿了：購買鈕顯示「背包已滿」且不能按', await page.locator('#dText button[data-a="glove"]').is_disabled() and '背包已滿' in await page.inner_text('#dText'))
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
