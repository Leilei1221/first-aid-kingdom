"""交通工具（老師 2026-10-08 決定）：完成第三章後雜貨店可買熱氣球等四種；世界地圖點其他地區就能搭乘（不過夜、不用食水、耗體力；颱風豪雨不能飛、濃霧只有無人機能飛）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/vehicle_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
V = json.load(open(pathlib.Path(__file__).parent.parent / 'content/balance.json', encoding='utf-8'))['VEHICLES']
L = {v['id']: v for v in V['list']}
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 30000; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def open_shop():
            await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000); await page.wait_for_timeout(200)
        async def click(a):
            await page.locator(f'#dText button[data-a="{a}"]').click(); await page.wait_for_timeout(350)
        async def dis(a): return await page.locator(f'#dText button[data-a="{a}"]').is_disabled()
        async def close_shop():
            await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        async def dlg_text(): return await page.inner_text('#dText')
        async def pick_btn(label):
            await page.locator('#dBtns button', has_text=label).first.click(); await page.wait_for_timeout(350)
        async def finish_dialogs():
            for _ in range(20):
                if await page.evaluate("() => document.getElementById('dialog').hidden"):
                    await page.wait_for_timeout(500)
                    if await page.evaluate("() => document.getElementById('dialog').hidden"): return
                    continue
                btns = page.locator('#dBtns button:not([disabled])')
                if await btns.count(): await btns.nth(0).click()
                await page.wait_for_timeout(200)
        async def open_map_click(region_idx):
            await page.evaluate("() => { window.__fa.worldMap(); }"); await page.wait_for_selector('button[data-r]', timeout=8000)
            await page.locator(f'button[data-r="{region_idx}"]').click(); await page.wait_for_timeout(500)
        # --- 完成第三章之前：商店沒有、地圖照舊只顯示提示
        await page.evaluate("() => { window.__fa.S.c.ch3_done = false; }")
        await open_shop(); check('還沒完成第三章：商店沒有「交通工具」', '交通工具' not in await dlg_text()); await close_shop()
        await page.evaluate("() => { window.__fa.S.c.ch3_done = true; window.__fa.S.hearts.shopkeeper = 0; }")
        await open_shop(); t = await dlg_text()
        check('完成第三章後：商店出現「交通工具」四種', all(v['name'] in t for v in V['list']) and '交通工具' in t, t[-500:])
        # --- 買：價格、扣款、已擁有、記在 S.c.air
        b4 = await st('S.coins'); await click('air:balloon')
        check(f'買熱氣球：扣 {L["balloon"]["cost"]} 金幣、記在 S.c.air，沒有新增頂層欄位', await st('S.coins') == b4 - L['balloon']['cost'] and await st('S.c.air') == ['balloon'] and await page.evaluate("() => !('air' in window.__fa.S)"))
        check('買過的：按鈕變「已擁有」且不能再按', await dis('air:balloon') and '已擁有' in await dlg_text())
        c = await st('S.coins'); await page.evaluate("() => { document.querySelector('#dText button[data-a=\"air:balloon\"]').disabled = false; }"); await click('air:balloon')
        check('硬按已擁有的：不再扣錢、不重複記錄', await st('S.coins') == c and await st('S.c.air') == ['balloon'])
        await page.evaluate("(c) => { window.__fa.S.coins = c; }", L['drone']['cost'] - 1)
        await close_shop(); await open_shop(); check('金幣差 1：無人機不能買', await dis('air:drone')); await close_shop()
        # --- 世界地圖搭乘
        regs = await page.evaluate("() => window.__fa.REGIONS && Object.keys(window.__fa.REGIONS)"); print('  地區', regs)
        idx = await page.evaluate("""() => { const r = Object.values(window.__fa.REGIONS); return r.map(x => x.id); }""")
        await page.evaluate("() => { const S = window.__fa.S; S.sta = 100; S.coins = 2000; window.__fa.go('farm', [600, 600]); }"); await page.wait_for_timeout(900)
        # 地圖 pin 順序＝[BASE].concat(Object.values(REGIONS))
        ch2 = 1 + idx.index(next(i for i in idx if 'ch2' in i)); ch3 = 1 + idx.index(next(i for i in idx if 'ch3' in i))
        day, coins, sta = await st('S.day'), await st('S.coins'), await st('S.sta')
        await open_map_click(ch3); t = await dlg_text()
        check('地圖點港口藍堡：跳出「搭乘熱氣球」，列出耗體力', '熱氣球' in t and str(L['balloon']['sta']) in t and '港口藍堡' in t, t)
        await pick_btn('搭熱氣球出發'); await finish_dialogs()
        check('抵達港口藍堡的中心場景', (await st('S.scene')).startswith('ch3_'), await st('S.scene'))
        check(f'耗體力 {L["balloon"]["sta"]}、沒過夜、沒花錢、不是航行中', await st('S.sta') == sta - L['balloon']['sta'] and await st('S.day') == day and await st('S.coins') == coins and await st('!S.voyage'), f'{await st("S.sta")} {await st("S.day")}')
        # 再從藍堡飛回綠葉谷（基地）
        await open_map_click(0); await pick_btn('搭熱氣球出發'); await finish_dialogs()
        check('可以飛回綠葉谷（基地）', not (await st('S.scene')).startswith('ch3_'), await st('S.scene'))
        # --- 選擇：擁有多種時選最省體力且能飛的
        await page.evaluate("() => { const S = window.__fa.S; S.c.air = ['bamboo', 'balloon', 'glider']; S.sta = 100; }")
        check('三種都有：自動選最省體力的復古滑翔機', await page.evaluate("() => window.__fa.airPick().v.id") == 'glider')
        # 體力不夠：滑翔機 10 + minLeft
        await page.evaluate("(m) => { window.__fa.S.sta = 10 + m - 1; }", V['minLeft'])
        check('體力不夠（飛完會低於保留量）：提示體力不夠', await page.evaluate("() => window.__fa.airPick().why") == 'tired')
        await open_map_click(ch3); t = await dlg_text(); check('體力不夠：顯示提示、不出發', '體力不夠' in t, t); await finish_dialogs()
        check('體力沒被扣、場景沒變', await st('S.sta') == 10 + V['minLeft'] - 1 and not (await st('S.scene')).startswith('ch3_'))
        # --- 天氣
        await page.evaluate("() => { const S = window.__fa.S; S.sta = 100; window.__fa.scheduleWx('typhoon'); }")   # 明天颱風
        check('明天颱風：不能飛', await page.evaluate("() => window.__fa.airPick().why") == 'storm')
        await open_map_click(ch3); t = await dlg_text(); check('颱風：地圖顯示不能飛', '不能飛' in t, t); await finish_dialogs()
        await page.evaluate("() => { const S = window.__fa.S; S.wxNext = null; S.wx = {type: 'fog', day: S.day}; }")
        check('濃霧：只有三種手動交通工具 → 不能飛', await page.evaluate("() => window.__fa.airPick().why") == 'fog')
        await page.evaluate("() => { window.__fa.S.c.air.push('drone'); }")
        check('濃霧＋有無人機：選無人機（耗體力 0）', await page.evaluate("() => window.__fa.airPick().v.id") == 'drone')
        sta = await st('S.sta'); await open_map_click(ch3); await pick_btn('搭無人機出發'); await finish_dialogs()
        check('無人機：濃霧能飛、體力不變', (await st('S.scene')).startswith('ch3_') and await st('S.sta') == sta, f'{await st("S.scene")} {await st("S.sta")}')
        # --- 沒有交通工具：維持原本提示
        await page.evaluate("() => { const S = window.__fa.S; S.wx = null; S.c.air = []; window.__fa.go('farm', [600, 600]); }"); await page.wait_for_timeout(900)
        await open_map_click(ch3); t = await dlg_text(); check('沒有交通工具：仍顯示原本的旅行提示（搭船）', '熱氣球' not in t and '搭' in t or '船' in t, t); await finish_dialogs()
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
