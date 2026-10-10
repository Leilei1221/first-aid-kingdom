"""第二章鍛造鎮小店（老師 2026-10-10 同意第二章加玩法）：完成第二章後，廣場有「鍛造鎮小店」：急救用品、乾糧、開水、體力補給、哨子手電筒雨衣；同價、不賒帳。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch2_store_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
IT = json.load(open(ROOT / 'content/items.json', encoding='utf-8')); ITEMS = IT['ITEMS']
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.started = true; S.coins = 500; S.sta = 20; S.day = 5; S.kitCap = 6; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def at_store():
            await page.evaluate("() => { window.__fa.go('ch2_town', [330, 690]); }"); await page.wait_for_timeout(1000)
            await page.evaluate("() => { window.__fa.S.pos = {x: 330, y: 665}; }"); await page.wait_for_timeout(500)
            return await page.inner_text('#act')
        act = await at_store(); check('還沒完成第二章：廣場沒有小店', '小店' not in act, act)
        await page.evaluate("() => { window.__fa.S.c.done = true; window.__fa.refresh(); }")
        act = await at_store(); check('完成第二章後：廣場有「鍛造鎮小店」', '鍛造鎮小店' in act, act)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        t = await page.inner_text('#dText')
        med = IT['SHOP_MED']; extra = IT['SHOP_EXTRA']
        check('賣急救用品、乾糧 40、開水 30、點心、便當、防災小物，價格同雜貨店', all(ITEMS[k]['name'] in t and f"{ITEMS[k]['price']} 金幣" in t for k in med + extra) and '乾糧' in t and '40 金幣' in t and '開水' in t and '30 金幣' in t, t[:200])
        c0, k0 = await st('S.coins'), await st('S.kit.length')
        await page.locator('#dText button[data-a="gauze"]').click(); await page.wait_for_timeout(350)
        check(f'買無菌紗布：扣 {ITEMS["gauze"]["price"]}、背包 +1', await st('S.coins') == c0 - ITEMS['gauze']['price'] and await st('S.kit.length') == k0 + 1 and await st("S.kit.includes('gauze')"))
        await page.locator('#dText button[data-a="ration"]').click(); await page.wait_for_timeout(350)
        check('買乾糧：扣 40、有保存期限（ration@到期日）', await st("S.kit[S.kit.length-1].startsWith('ration@')") and await st('S.coins') == c0 - ITEMS['gauze']['price'] - 40)
        s0 = await st('S.sta'); await page.locator('#dText button[data-a="sta:snack"]').click(); await page.wait_for_timeout(350)
        check('買能量點心：體力 +40，不佔背包', await st('S.sta') == s0 + 40 and await st('S.kit.length') == k0 + 2)
        await page.evaluate("() => { const S = window.__fa.S; while (S.kit.length < S.kitCap) S.kit.push('bandaid'); window.__fa.refresh(); }")
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        check('背包滿了：不能再買（背包已滿）', await page.locator('#dText button[data-a="glove"]').is_disabled() and '背包已滿' in await page.inner_text('#dText'))
        await page.evaluate("() => { window.__fa.S.coins = 5; window.__fa.S.kit.length = 0; window.__fa.S.sta = 10; window.__fa.refresh(); }")
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        check('金幣不夠（5）：買不了，沒有賒帳', all([await page.locator(f'#dText button[data-a="{a}"]').is_disabled() for a in ['glove', 'ration', 'water', 'sta:snack', 'whistle']]))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
