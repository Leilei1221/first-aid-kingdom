"""商店「體能補給」（老師 2026-10-07 決定）：完成第三章後開啟；能量點心／豐盛便當補體力、體能訓練永久提高體力上限（最多 3 次，價格依序遞增）；上限變高後睡醒、吃乾糧、體力條都跟著用新上限。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/stamina_shop_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
CFG = json.load(open(pathlib.Path(__file__).parent.parent / 'content/balance.json', encoding='utf-8'))['STAMINA_SHOP']
SNACK, MEAL = CFG['food'][0], CFG['food'][1]
UP = CFG['up']
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 5000; S.sta = 50; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def open_shop():
            await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000); await page.wait_for_timeout(200)
        async def shop_text(): return await page.inner_text('#dText')
        async def click(a):
            await page.locator(f'#dText button[data-a="{a}"]').click(); await page.wait_for_timeout(350)
        async def dis(a): return await page.locator(f'#dText button[data-a="{a}"]').is_disabled()
        async def close_shop():
            await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        # --- 完成第三章之前：沒有這一區
        await open_shop(); t = await shop_text()
        check('還沒完成第三章：商店沒有「體能補給」', '體能補給' not in t and await page.locator('#dText button[data-a="staup"]').count() == 0)
        await close_shop()
        await page.evaluate("() => { window.__fa.S.c.ch3_done = true; }")
        await open_shop(); t = await shop_text()
        check('完成第三章後：商店出現「體能補給」（能量點心、豐盛便當、體能訓練）', all(k in t for k in ['體能補給', SNACK['name'], MEAL['name'], '體能訓練']), t[-400:])
        # --- 補給
        b4 = await st('S.coins'); s4 = await st('S.sta')
        await click('sta:snack')
        check(f'能量點心：花 {SNACK["cost"]} 金幣、體力 +{SNACK["restore"]}（50 → 90）', await st('S.coins') == b4 - SNACK['cost'] and await st('S.sta') == min(100, s4 + SNACK['restore']), f'{await st("S.coins")} {await st("S.sta")}')
        await click('sta:meal')
        check('豐盛便當：補到上限（100），超出的不浪費也不超過上限', await st('S.sta') == 100, str(await st('S.sta')))
        check('體力已滿：兩種補給按鈕都不能按', await dis('sta:snack') and await dis('sta:meal'))
        coins = await st('S.coins'); await page.evaluate("() => { document.querySelector('#dText button[data-a=\"sta:snack\"]').disabled = false; }")
        await click('sta:snack'); check('就算硬按（體力已滿）：不扣錢、不變', await st('S.coins') == coins and await st('S.sta') == 100)
        # --- 體能訓練：三次、價格遞增、上限逐次提高
        for i, cost in enumerate(UP['costs']):
            b4 = await st('S.coins'); sta4 = await st('S.sta')
            check(f'體能訓練第 {i+1} 次：標示價格 {cost}、上限 {100 + i*UP["step"]} → {100 + (i+1)*UP["step"]}', f'{cost} 金幣' in await shop_text() and f'{100 + i*UP["step"]} → {100 + (i+1)*UP["step"]}' in await shop_text(), (await shop_text())[-300:])
            await click('staup')
            check(f'體能訓練第 {i+1} 次：扣 {cost}、體力上限 {100 + (i+1)*UP["step"]}、體力 +{UP["step"]}', await st('S.coins') == b4 - cost and await page.evaluate("() => window.__fa.staMax()") == 100 + (i+1)*UP['step'] and await st('S.sta') == sta4 + UP['step'], f'{await st("S.coins")} {await page.evaluate("() => window.__fa.staMax()")} {await st("S.sta")}')
        t = await shop_text()
        check('練滿 3 次：顯示「已達上限」、沒有購買鈕', '已達上限' in t and await page.locator('#dText button[data-a="staup"]').count() == 0, t[-300:])
        check('記錄在既有的 S.c.staUp（3 次），沒有新增頂層存檔欄位', await st('S.c.staUp') == 3 and await page.evaluate("() => !('staUp' in window.__fa.S)"))
        await close_shop()
        # --- 上限變高之後
        mx = await page.evaluate("() => window.__fa.staMax()")
        check('體力條：滿體力時顯示 100%（用新上限算）', await page.evaluate("([m]) => { const S = window.__fa.S; S.sta = m; window.__fa.refresh(); return document.getElementById('staBar').style.width; }", [mx]) == '100%')
        check('體力一半時體力條約 50%', await page.evaluate("([m]) => { const S = window.__fa.S; S.sta = m / 2; window.__fa.refresh(); return Math.round(parseFloat(document.getElementById('staBar').style.width)); }", [mx]) == 50)
        # 睡醒：回到新上限
        await page.evaluate("() => { const S = window.__fa.S; S.sta = 10; window.__fa.go('home', [840, 770]); }"); await page.wait_for_timeout(800)
        await page.evaluate("() => { window.__fa.bed(); }")
        for _ in range(30):
            if await page.evaluate("() => document.getElementById('dialog').hidden"):
                await page.wait_for_timeout(500)
                if await page.evaluate("() => document.getElementById('dialog').hidden"): break
                continue
            btns = page.locator('#dBtns button:not([disabled])')
            if await btns.count(): await btns.nth(0).click()
            await page.wait_for_timeout(200)
        check('睡一覺：體力回到新上限（130）', await st('S.sta') == mx, f'{await st("S.sta")} vs {mx}')
        # 欠債時不能買
        await page.evaluate("() => { window.__fa.S.hearts.shopkeeper = 0; }")   # 買體能訓練會增加老闆的好感度，3 顆心起有折扣；這裡要測原價的邊界
        await page.evaluate("() => { window.__fa.S.coins = -50; window.__fa.S.sta = 20; }")
        await page.evaluate("() => { window.__fa.S.c.staUp = 0; }")
        await open_shop()
        check('欠款時（金幣為負）：補給與體能訓練都不能買', await dis('sta:snack') and await dis('sta:meal') and await dis('staup'))
        await close_shop()
        await page.evaluate("(c) => { window.__fa.S.coins = c; }", SNACK['cost'] - 1)
        await open_shop(); check('金幣差 1：能量點心不能買', await dis('sta:snack')); await close_shop()
        check('體能補給測試沒有頁面錯誤', not errs, str(errs))
        await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('體能補給測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
