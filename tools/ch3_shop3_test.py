"""藍堡的港口小店（老師 2026-10-09 同意）：港口市集的水果攤，賣乾糧、開水、體能點心與便當、哨子／手電筒／雨衣；一開始就能用（不用完成章末）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_shop3_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
IT = json.load(open(ROOT / 'content/items.json', encoding='utf-8')); ITEMS = IT['ITEMS']; EXTRA = IT['SHOP_EXTRA']
BAL = json.load(open(ROOT / 'content/balance.json', encoding='utf-8')); FOOD = {f['id']: f for f in BAL['STAMINA_SHOP']['food']}; LIFE = BAL.get('RATION_LIFE', 10)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 500; S.sta = 20; S.day = 5; S.kitCap = 6; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        await page.evaluate("() => { window.__fa.go('ch3_market', [650, 470]); }"); await page.wait_for_timeout(900)
        await page.evaluate("() => { window.__fa.S.pos = {x: 650, y: 440}; }"); await page.wait_for_timeout(500)
        act = await page.inner_text('#act'); check('港口市集水果攤前有「港口小店」（還沒完成章末也有）', '港口小店' in act, act)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        t = await page.inner_text('#dText')
        check('列出乾糧 40、開水 30、點心、便當、哨子、手電筒、雨衣，價格正確', all(x in t for x in ['乾糧', '40 金幣', '開水', '30 金幣', FOOD['snack']['name'], FOOD['meal']['name']]) and all(ITEMS[k]['name'] in t and f"{ITEMS[k]['price']} 金幣" in t for k in EXTRA), t[:300])
        c0, k0 = await st('S.coins'), await st('S.kit.length')
        await page.locator('#dText button[data-a="ration"]').click(); await page.wait_for_timeout(350)
        check('買乾糧：扣 40、背包多一包有保存期限的乾糧（ration@到期日）', await st('S.coins') == c0 - 40 and await st('S.kit.length') == k0 + 1 and await st("S.kit[S.kit.length-1].startsWith('ration@')"), await st('JSON.stringify(S.kit)'))
        exp = int((await st("S.kit[S.kit.length-1]")).split('@')[1]); day = await st('S.day')
        check('乾糧的保存期限是今天起算的壽命天數', exp - day == LIFE or exp - day > 0, f'{exp} {day} {LIFE}')
        await page.locator('#dText button[data-a="water"]').click(); await page.wait_for_timeout(350)
        check('買開水：扣 30、背包多一瓶 water', await st('S.coins') == c0 - 70 and await st("S.kit[S.kit.length-1]") == 'water')
        s0 = await st('S.sta'); await page.locator('#dText button[data-a="sta:snack"]').click(); await page.wait_for_timeout(350)
        check(f'買能量點心：馬上吃下，體力 +{FOOD["snack"]["restore"]}，不佔背包', await st('S.sta') == s0 + FOOD['snack']['restore'] and await st('S.coins') == c0 - 70 - FOOD['snack']['cost'] and await st('S.kit.length') == k0 + 2)
        await page.locator('#dText button[data-a="sta:meal"]').click(); await page.wait_for_timeout(350)
        check('買便當後體力補到上限；之後點心、便當都不能再買（體力已滿）', await st('S.sta') == await page.evaluate("() => window.__fa.staMax()") and await page.locator('#dText button[data-a="sta:snack"]').is_disabled())
        c1 = await st('S.coins'); await page.locator('#dText button[data-a="flashlight"]').click(); await page.wait_for_timeout(350)
        check(f'買手電筒：扣 {ITEMS["flashlight"]["price"]}、進背包', await st('S.coins') == c1 - ITEMS['flashlight']['price'] and await st("S.kit.includes('flashlight')"))
        await page.evaluate("() => { const S = window.__fa.S; while (S.kit.length < S.kitCap) S.kit.push('bandaid'); window.__fa.refresh(); }")
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        check('背包滿了：乾糧、開水、用品都買不了（顯示背包已滿）', await page.locator('#dText button[data-a="ration"]').is_disabled() and '背包已滿' in await page.inner_text('#dText'))
        await page.evaluate("() => { window.__fa.S.coins = 5; window.__fa.S.kit.length = 0; window.__fa.S.sta = 10; window.__fa.refresh(); }")
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000)
        check('金幣不夠（5）：全部買不了，沒有賒帳', all([await page.locator(f'#dText button[data-a="{a}"]').is_disabled() for a in ['ration', 'water', 'sta:snack', 'whistle']]))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
