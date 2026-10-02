"""第三章（港口藍堡）D1：從礦坑南邊石階到南岸漁港、航行（船票、補給、防災包、停航、存檔點）、各場景之間的門（網址自動加 ?open=ch3）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def boot(ctx, url, extra=''):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.add_init_script("window.__cp = 0;")
    await page.goto(url + '?open=ch2,ch3' + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 300; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
    await page.evaluate("() => { window.FACloud = { checkpoint: () => { window.__cp++; }, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }")
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def goto(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(800)
async def finish(page, n=30, pick=0):
    out = []
    for _ in range(n):
        if await page.evaluate("() => document.getElementById('dialog').hidden"):
            await page.wait_for_timeout(1000)
            if await page.evaluate("() => document.getElementById('dialog').hidden"): return out
            continue
        out.append(await page.inner_text('#dText'))
        await page.locator('#dBtns button:not([disabled])').nth(0).click(); await page.wait_for_timeout(150)
    return out
async def act_at(page, x, y):
    await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(300)
    await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(300)
async def board(page):
    """買票上船並處理防災包詢問；回傳看到的文字"""
    await act_at(page, 1230, 600)
    await page.wait_for_selector('#dBtns button')
    return await finish(page)
async def sail(page, nights=2):
    for _ in range(nights):
        await page.evaluate("() => { document.getElementById('act').click(); }") if False else None
        await act_at(page, 1080, 580)       # 甲板上的艙口
        await page.wait_for_function("() => window.__fa.S.scene === 'ch3_ship_cabin'", timeout=8000)
        await act_at(page, 1200, 560)       # 船艙的床
        await finish(page, n=12)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # --- 序章接點：礦坑入口南邊的石階
        page, errs = await boot(ctx, url)
        r = await page.evaluate("() => ({ch: window.__fa.CHAPTERS.ch3.open, n: Object.keys(window.__fa.SCENES).filter(k => k.startsWith('ch3_')).length})")
        check('?open=ch3：第三章開放、8 個場景', r == {'ch': True, 'n': 8}, str(r))
        await goto(page, 'mine_out', 800, 600)
        await page.evaluate("() => { window.__fa.S.pos = {x: 800, y: 880}; }"); await page.keyboard.down('ArrowDown'); await page.wait_for_timeout(1800); await page.keyboard.up('ArrowDown'); await page.wait_for_timeout(1200)
        check('完成第二章後：從礦坑入口南邊石階走到南岸漁港', await st(page, 'S.scene') == 'ch3_fishport', await st(page, 'S.scene'))
        # 沒完成第二章：被擋下
        await page.evaluate("() => { window.__fa.S.c.done = false; }")
        await goto(page, 'mine_out', 800, 600)
        await page.evaluate("() => { window.__fa.S.pos = {x: 800, y: 880}; }"); await page.keyboard.down('ArrowDown'); await page.wait_for_timeout(1800); await page.keyboard.up('ArrowDown'); await page.wait_for_timeout(600)
        txt = await page.inner_text('#dText') if not await page.evaluate("() => document.getElementById('dialog').hidden") else ''
        check('還沒完成第二章：石階被擋下並提示', '等完成第二章再去吧' in txt and await st(page, 'S.scene') == 'mine_out', txt)
        await finish(page, 3)
        await page.evaluate("() => { window.__fa.S.c.done = true; }")
        # --- 航行：不帶補給
        await page.evaluate("() => { const S = window.__fa.S; S.kit = []; S.stash = []; S.coins = 200; S.stashAt = 'base'; }")
        await goto(page, 'ch3_fishport', 760, 110)
        await page.evaluate("() => { window.__fa.S.pos = {x: 1230, y: 600}; }"); await page.wait_for_timeout(300)
        t = await board(page)
        check('船長：船票 30、乾糧 40、開水 30', any('30 金幣' in x and '乾糧 40' in x and '開水 30' in x for x in t), str(t)[:200])
        check('買票上船：到白天甲板、兩晚、金幣 -30', await st(page, "S.scene") == 'ch3_ship_day' and await st(page, "S.voyage && S.voyage.left === 2 && S.voyage.to === 'ch3_harbor'") and await st(page, 'S.coins') == 170, await st(page, 'JSON.stringify([S.scene,S.voyage,S.coins])'))
        cp0 = await page.evaluate("() => window.__cp")
        await act_at(page, 1080, 580)
        await page.wait_for_function("() => window.__fa.S.scene === 'ch3_ship_cabin'", timeout=8000)
        check('甲板艙口 → 船艙', True)
        await act_at(page, 1200, 560); t = await finish(page, 12)
        check('第一晚：自己沒帶補給 → 向船長買乾糧與開水（70 金幣）', await st(page, 'S.coins') == 100 and any('跟船長買了乾糧' in x for x in t), await st(page, 'S.coins'))
        check('睡醒建立存檔點、剩 1 晚', await page.evaluate("() => window.__cp") == cp0 + 1 and await st(page, 'S.voyage.left') == 1)
        await act_at(page, 910, 408); await page.wait_for_timeout(900)
        check('船艙爬梯 → 回到甲板（第二天是黃昏的甲板）', await st(page, 'S.scene') == 'ch3_ship_dusk', await st(page, 'S.scene'))
        await act_at(page, 1080, 580); await page.wait_for_function("() => window.__fa.S.scene === 'ch3_ship_cabin'", timeout=8000)
        await act_at(page, 1200, 560); await finish(page, 12)
        check('第二晚：再向船長買補給（70 金幣）→ 剩 30 金幣', await st(page, 'S.coins') == 30, await st(page, 'S.coins'))
        check('兩晚後抵達港口藍堡、航行結束', await st(page, 'S.scene') == 'ch3_harbor' and await st(page, '!S.voyage'), await st(page, 'JSON.stringify([S.scene,S.voyage])'))
        # --- 防災包當旅行行李＋回程
        await page.evaluate("() => { const S = window.__fa.S; S.kit = []; S.stash = ['ration@50', 'ration@50', 'water', 'water']; S.stashAt = 'ch3'; S.coins = 200; }")
        await goto(page, 'ch3_harbor', 820, 640)
        await page.evaluate("() => { window.__fa.S.stashAt = 'carry'; }")
        await page.evaluate("() => { window.__fa.S.pos = {x: 830, y: 440}; }"); await page.wait_for_timeout(300)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dBtns button')
        await finish(page)
        check('回程：藍堡港口搭船回綠葉谷', await st(page, "S.scene") == 'ch3_ship_day' and await st(page, "S.voyage.to") == 'ch3_fishport', await st(page, 'JSON.stringify([S.scene,S.voyage])'))
        await sail(page, 2)
        r = await st(page, "({scene: S.scene, stash: S.stash.length, coins: S.coins})")
        check('回程兩晚：自己帶的 2 乾糧＋2 水取自防災包、沒買補給；回到南岸漁港', r == {'scene': 'ch3_fishport', 'stash': 0, 'coins': 170}, str(r))
        # --- 停航
        await page.evaluate("() => { window.__fa.scheduleWx('typhoon'); }")
        await page.evaluate("() => { window.__fa.S.pos = {x: 1230, y: 600}; }"); await page.wait_for_timeout(300)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_selector('#dText')
        txt = await page.inner_text('#dText')
        check('颱風預報：船長說今天停航、沒有賣票', '今天停航' in txt and await page.locator('#dBtns button').count() == 1, txt)
        await finish(page, 3)
        # --- 其他場景之間的門
        await page.evaluate("() => { window.__fa.S.wxNext = null; }")
        await goto(page, 'ch3_harbor', 820, 640)
        for (label, x, y, dest) in [('市集', 1490, 290, 'ch3_market'), ('救生站', 1390, 790, 'ch3_rescue'), ('燈塔', 716, 508, 'ch3_lighthouse')]:
            await goto(page, 'ch3_harbor', 820, 640); await act_at(page, x, y); await page.wait_for_timeout(900)
            check(f'港口 → {label}', await st(page, 'S.scene') == dest, await st(page, 'S.scene'))
        check('第三章測試沒有頁面錯誤', not errs, str(errs)); await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
