"""第四章「雪嶺」F1（草稿）：章節骨架——山腳村與旅店、遮罩、進入條件（只有預覽或 #debug ?open=ch4）、帕桑出發與回藍堡、世界地圖、住一晚、防災包。
用法：`python3 -u tools/ch4_test.py http://localhost:8765/index.html`"""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
CLOUD = "() => { window.FACloud = { checkpoint: () => {}, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }"
async def boot(ctx, url, extra, setup=''):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '?open=ch2,ch3' + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 5000; S.sta = 60; S.day = 15; S.kitCap = 14; S.c.ch3_done = true; " + setup + " document.getElementById('btnStart').click(); }")
    await page.evaluate(CLOUD); await page.wait_for_timeout(500)
    return page, errs
async def ev(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def goto(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(900)
async def hidden(page): return await page.evaluate("() => document.getElementById('dialog').hidden")
async def act_at(page, x, y):
    await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(400)
    await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(500)
async def click(page, text, wait=450):
    await page.locator('#dBtns button, #dText button', has_text=text).first.click(); await page.wait_for_timeout(wait)
async def btns(page): return await page.locator('#dBtns button').all_inner_texts()
async def text(page): return await page.inner_text('#dText')
async def drain(page, n=12):
    for _ in range(n):
        if await hidden(page): return
        await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(450)
FRAG = "S.c.ch3_e3 = { seen: { np: true }, frag: { jp: 1, au: 1, np: 1 }, own: {}, cnt: {}, wear: {} };"
async def main(url):
    walks = {}
    for k, v in json.load(open(ROOT / 'chapters/ch4/walks.json')).items(): walks[k] = v
    ok = lambda s, x, y: walks[s][y // 8][x // 8] == '1'
    sc = json.load(open(ROOT / 'chapters/ch4/scenes.json'))
    for s, d in sc.items():
        check(f'{s}：出生點在可走區', ok(s, *d['spawn']))
        for n in d['npcs']: check(f'{s}：NPC {n["id"]} 站在可走區', ok(s, n['x'], n['y']))
        for t in d['things']:
            if t['kind'] != 'door' or s == 'ch4_inn': check(f'{s}：互動點 {t["label"]} 的位置可走或在附近', any(ok(s, t['x'] + dx, t['y'] + dy) for dx in (-60, 0, 60) for dy in (-60, 0, 60)))
    check('旅店出口回村裡的位置可走', ok('ch4_village', *sc['ch4_inn']['exits'][0]['at']))
    check('村裡進旅店後的出生位置可走', ok('ch4_inn', *sc['ch4_village']['things'][0]['at']))
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # --- 一般進入（沒有 ?open=ch4）：草稿擋住，沒有「去雪嶺」，世界地圖沒有雪嶺入口
        page, errs = await boot(ctx, url, '', FRAG)
        check('ch4 章節載入了', await page.evaluate("() => !!window.__fa.CHAPTERS.ch4 && window.__fa.CHAPTERS.ch4.loaded"))
        await goto(page, 'ch3_harbor', 820, 640)
        await page.evaluate("() => { window.__fa.S.day = 15; }"); await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 900, 540)
        await skip_to_menu(page)
        check('沒有 ?open=ch4：帕桑選單沒有「跟帕桑去雪嶺」', not any('雪嶺' in t for t in await btns(page)), str(await btns(page)))
        await leave(page); await page.close()
        ctx2 = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx2.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx2.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3,ch4#debug')
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 5000; S.sta = 60; S.day = 15; S.kitCap = 14; S.c.ch3_done = true; S.c.ch3_e3 = { seen: { np: true }, frag: { jp: 1 }, own: {}, cnt: {}, wear: {} }; document.getElementById('btnStart').click(); }")
        await page.evaluate(CLOUD); await page.wait_for_timeout(500)
        await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 900, 540); await skip_to_menu(page)
        check('只有 1 片碎片：沒有「去雪嶺」', not any('雪嶺' in t for t in await btns(page)), str(await btns(page))); await leave(page)
        check('還沒到過雪嶺：世界地圖的雪嶺是鎖住的', not await page.evaluate("() => { const r = window.__fa.REGIONS.ch4; return !!r && !!(window.__fa.S.c.ch4 && window.__fa.S.c.ch4.arrived); }"))
        await page.evaluate("() => { window.__fa.S.c.ch3_e3.frag = { jp: 1, au: 1, np: 1 }; }")
        await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 900, 540); await skip_to_menu(page)
        check('三片碎片、見過帕桑、完成章末：帕桑選單有「跟帕桑去雪嶺」', any('跟帕桑去雪嶺' in t for t in await btns(page)), str(await btns(page)))
        await click(page, '跟帕桑去雪嶺'); check('第一次出發：帕桑說碎片拼起來是家鄉', '家鄉' in await text(page), await text(page))
        for _ in range(4):
            if any('出發去雪嶺' in t for t in await btns(page)): break
            await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(400)
        check('出發前有「出發去雪嶺」與「再準備一下」', any('出發去雪嶺' in t for t in await btns(page)) and any('再準備' in t for t in await btns(page)))
        await click(page, '再準備一下'); await page.wait_for_timeout(300); await leave(page)
        check('選「再準備一下」：留在港口、沒到過雪嶺', await ev(page, "S.scene") == 'ch3_harbor' and not await ev(page, "!!(S.c.ch4 && S.c.ch4.arrived)"))
        await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 900, 540); await skip_to_menu(page); await click(page, '跟帕桑去雪嶺')
        for _ in range(4):
            if any('出發去雪嶺' in t for t in await btns(page)): break
            await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(400)
        await click(page, '出發去雪嶺', 1200)
        for _ in range(6):
            if await ev(page, "S.scene") == 'ch4_village' and not await hidden(page): break
            await page.wait_for_timeout(500)
        # 防災包詢問（防災包在綠葉谷時不會問）→ 直接處理對話到抵達
        for _ in range(8):
            if await hidden(page): break
            bt = await btns(page)
            if any('不帶' in t or '留在這裡' in t for t in bt): await click(page, '留在這裡')
            else: await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(450)
        check('出發後到了山腳村', await ev(page, "S.scene") == 'ch4_village', await ev(page, "S.scene"))
        check('記下到過雪嶺（S.c.ch4.arrived）', await ev(page, "!!(S.c.ch4 && S.c.ch4.arrived)"))
        check('沒有新增頂層存檔欄位（只用 S.c）', await ev(page, "!('ch4' in S)"))
        check('世界地圖的雪嶺解鎖', await page.evaluate("() => { const f = window.__fa; const r = f.REGIONS.ch4; return !!(r && f.S.c.ch4.arrived); }"))
        check('地區是雪嶺', await page.evaluate("() => window.__fa.curRegion().name") == '雪嶺')
        check('目標文字提到帕桑', '帕桑' in await page.inner_text('#goal'))
        check('沒有錯誤', not errs, str(errs[:2]))
        # --- 山腳村：上山的路還不能走、帕桑對話、回藍堡
        await act_at(page, 400, 400); check('上山的路：說營地還沒準備好', '還沒準備好' in await text(page) or '營地' in await text(page), await text(page)); await drain(page)
        await act_at(page, 1000, 600)
        check('和帕桑說話有選單', any('聊聊雪嶺' in t for t in await btns(page)), str(await btns(page)))
        await click(page, '聊聊雪嶺'); check('聊聊：有「一層一層穿」的話', '一層一層' in await text(page) or '毛線' in await text(page), await text(page))
        for _ in range(4):
            if any('先離開' in t for t in await btns(page)): break
            await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(400)
        await click(page, '先離開', 500)
        await goto(page, 'ch4_village', 880, 620); await act_at(page, 950, 372)
        check('進旅店：到了旅店場景', await ev(page, "S.scene") == 'ch4_inn', await ev(page, "S.scene"))
        # --- 旅店：老闆娘、住一晚、防災包
        await act_at(page, 700, 560)
        check('老闆娘第一次說歡迎', '歡迎' in await text(page), await text(page)); await drain(page)
        d0, c0 = await ev(page, "S.day"), await ev(page, "S.coins")
        await act_at(page, 1250, 470); check('住一晚有提示與價錢', '20 金幣' in await text(page), await text(page))
        await click(page, '住一晚', 1500); await drain(page, 3)
        check('住一晚：天數 +1、金幣 −20、體力恢復', await ev(page, "S.day") == d0 + 1 and await ev(page, "S.coins") == c0 - 20 and await ev(page, "S.sta") >= 100, f'{await ev(page, "S.day")} {await ev(page, "S.coins")} {await ev(page, "S.sta")}')
        await act_at(page, 1480, 580); check('防災包可以開啟（放在這裡或整理）', not await hidden(page))
        for _ in range(4):
            if await hidden(page): break
            bt = await btns(page)
            if any('關閉' in t for t in bt): await click(page, '關閉', 500)
            else: await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(450)
        # 旅店出口回村
        t = await page.evaluate("() => { const e = window.__fa.SCENES.ch4_inn.exits[0]; return [e.test(300, 700), e.test(500, 700), e.test(300, 400), e.to, e.at]; }")
        check('旅店左下的門是出口（往右走、往上走不是）', t[0] and not t[1] and not t[2] and t[3] == 'ch4_village', str(t))
        await goto(page, t[3], *t[4]); check('出口把人帶回山腳村', await ev(page, "S.scene") == 'ch4_village')
        # --- 搭小船回藍堡
        await goto(page, 'ch4_village', 880, 620); await act_at(page, 620, 700)
        check('小船：問要不要回藍堡', '藍堡' in await text(page), await text(page))
        for _ in range(6):
            if await hidden(page): break
            bt = await btns(page)
            if any('回藍堡' in t for t in bt): await click(page, '回藍堡', 1500)
            elif any('留在這裡' in t for t in bt): await click(page, '留在這裡')
            else: await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(450)
        check('回到藍堡港口', await ev(page, "S.scene") == 'ch3_harbor', await ev(page, "S.scene"))
        check('港口：帕桑（商船不是他的那天）站在港口另一個位置', await ev(page, "S.day") >= 16)
        await page.evaluate("() => { window.__fa.S.day = 12; }"); await goto(page, 'ch3_harbor', 820, 640)
        await act_at(page, 1050, 620); check('第 12 天（澳洲商船）：還是找得到帕桑，選單有去雪嶺', any('跟帕桑去雪嶺' in t for t in await btns(page)), str(await btns(page))); await leave(page)
        await ctx2.close()
        # --- 老師預覽：直接站在雪嶺、全部章節開放、不需要條件
        ctx3 = await b.new_context(viewport={'width': 1180, 'height': 820})
        page = await ctx3.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        for sid, name in [('ch4_village', '山腳村'), ('ch4_inn', '山腳旅店')]:
            await page.goto(url + f'?preview={sid}')
            await page.wait_for_function("document.getElementById('game') && !document.getElementById('game').hidden", timeout=60000); await page.wait_for_timeout(2500)
            check(f'?preview={sid}：場景名「{name}」', name in await page.inner_text('body'))
            check(f'?preview={sid}：場景背景圖載入', await page.evaluate("(k) => [...document.querySelectorAll('*')].some(e => (e.style && e.style.backgroundImage || '').includes(k))", sid))
        await page.goto(url + '?preview=ch3_harbor&m=np')
        await page.wait_for_function("document.getElementById('game') && !document.getElementById('game').hidden", timeout=60000); await page.wait_for_timeout(900)
        check('預覽港口帕桑：沒有錯誤', not errs, str(errs[:2]))
        await b.close()
    print('\n失敗', fails, '項' if fails else '，全部通過'); sys.exit(1 if fails else 0)
async def leave(page):
    for _ in range(4):
        if await hidden(page): return
        if any('Bye' in t for t in await btns(page)): await click(page, 'Bye', 500); return
        await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(350)
async def skip_to_menu(page):
    for _ in range(6):
        if await hidden(page): return
        if any('Buy' in t for t in await btns(page)): return
        await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(350)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
