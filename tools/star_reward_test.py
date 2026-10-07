"""星級獎勵（老師 2026-10-07 決定）：3、4、5 顆星報酬不同、每個新達成的星級只領一次；落石之城要先完成第三章才開啟；第三章章末由 ch3_finale_test 驗證。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/star_reward_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
BAL = json.load(open(pathlib.Path(__file__).parent.parent / 'content/balance.json', encoding='utf-8'))['STAR_REWARD']
CAS, CH3 = BAL['castle'], BAL['ch3']
async def main(url):
    check('設定：星級報酬 3 < 4 < 5（兩個大關卡都是）', CAS['3'] < CAS['4'] < CAS['5'] and CH3['3'] < CH3['4'] < CH3['5'], str(BAL))
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        async def fresh():
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
            await pg.goto(url + '#debug'); await pg.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
            await pg.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 100; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
            await pg.wait_for_timeout(400); return pg, errs
        pg, errs = await fresh()
        sr = lambda kind, stars: pg.evaluate("([k, s]) => { const r = window.__fa.starReward(k, s); return {r, coins: window.__fa.S.coins}; }", [kind, stars])
        # --- 落石之城：還沒完成第三章，不適用
        o = await sr('castle', 5)
        check('落石之城：還沒完成第三章 → 不給獎勵（null）、金幣不變、不記錄', o['r'] is None and o['coins'] == 100 and await pg.evaluate("() => !(window.__fa.S.c.starPaid)"), str(o))
        # --- 第三章章末：星級逐級領
        o = await sr('ch3', 2); check('第三章 2 顆星：沒有獎勵、提示下一級 3 顆星', o['r'] == {'gain': 0, 'next': {'tier': 3, 'coins': CH3['3']}} and o['coins'] == 100, str(o))
        o = await sr('ch3', 3); check('第三章 3 顆星：領 3 星的報酬、提示 4 星', o['r'] == {'gain': CH3['3'], 'next': {'tier': 4, 'coins': CH3['4']}} and o['coins'] == 100 + CH3['3'], str(o))
        c = o['coins']
        o = await sr('ch3', 3); check('再打 3 顆星：不重複領', o['r']['gain'] == 0 and o['coins'] == c, str(o))
        o = await sr('ch3', 2); check('打退步（2 顆星）：不扣、不影響已領的等級', o['r']['gain'] == 0 and o['coins'] == c and o['r']['next']['tier'] == 4, str(o))
        o = await sr('ch3', 5); check('再打 5 顆星：只補 4、5 星的差額（跳過 3 星）', o['r'] == {'gain': CH3['4'] + CH3['5'], 'next': None} and o['coins'] == c + CH3['4'] + CH3['5'], str(o))
        c = o['coins']
        o = await sr('ch3', 5); check('已拿滿 5 星：再打不再給', o['r'] == {'gain': 0, 'next': None} and o['coins'] == c, str(o))
        # --- 落石之城：完成第三章後
        await pg.evaluate("() => { const S = window.__fa.S; S.c.ch3_done = true; S.coins = 0; }")
        o = await sr('castle', 4); check('落石之城（完成第三章後）：第一次 4 顆星＝3 星加 4 星報酬', o['r'] == {'gain': CAS['3'] + CAS['4'], 'next': {'tier': 5, 'coins': CAS['5']}} and o['coins'] == CAS['3'] + CAS['4'], str(o))
        o = await sr('castle', 5); check('落石之城：再挑戰 5 顆星＝只補 5 星報酬', o['r']['gain'] == CAS['5'] and o['r']['next'] is None, str(o))
        await pg.evaluate("() => { window.__fa.S.c.starPaid = {}; window.__fa.S.coins = 0; }")
        o = await sr('castle', 5); check('落石之城：一次跳到 5 顆星＝3、4、5 星報酬全領', o['r']['gain'] == CAS['3'] + CAS['4'] + CAS['5'], str(o))
        check('記錄在既有的 S.c.starPaid，沒有新增頂層存檔欄位', await pg.evaluate("() => !('starPaid' in window.__fa.S) && !('starReward' in window.__fa.S)") and await pg.evaluate("() => window.__fa.S.c.starPaid.castle") == 5)
        check('星級獎勵測試（函式）沒有頁面錯誤', not errs, str(errs)); await pg.close()
        # --- 落石之城結算畫面
        async def castle_report(ch3_done):
            pg, errs = await fresh()
            await pg.evaluate("(d) => { const S = window.__fa.S; S.c.ch3_done = d; S.coins = 0; S.rescue = {guard: 'ok', cook: 'ok', soldier: 'ok'}; S.kit = ['ration@99', 'ration@99', 'ration@99', 'water', 'water', 'water']; S.castleBest = 0; S.scene = 'ruin'; }", ch3_done)
            await pg.evaluate("() => { window.__fa.rationPhase(); }")
            texts = []
            for _ in range(60):
                if await pg.evaluate("() => document.getElementById('dialog').hidden"):
                    await pg.wait_for_timeout(500)
                    if await pg.evaluate("() => document.getElementById('dialog').hidden"): break
                    continue
                texts.append(await pg.inner_text('#dText'))
                btns = pg.locator('#dBtns button:not([disabled])')
                if await btns.count(): await btns.nth(0).click()
                await pg.wait_for_timeout(150)
            coins = await pg.evaluate("() => window.__fa.S.coins"); await pg.close(); return '\n'.join(texts), coins, errs
        t, coins, e1 = await castle_report(True)
        check('落石之城結算（完成第三章後、5 顆星）：顯示「星級獎勵：+%d 金幣」並實際加錢' % (CAS['3'] + CAS['4'] + CAS['5']), '星級獎勵：+%d 金幣' % (CAS['3'] + CAS['4'] + CAS['5']) in t and coins == CAS['3'] + CAS['4'] + CAS['5'], str((coins, t[-200:])))
        t, coins, e2 = await castle_report(False)
        check('落石之城結算（還沒完成第三章）：沒有任何獎勵字樣、金幣不變（序章維持原樣）', '星級獎勵' not in t and '下次達成' not in t and coins == 0, str((coins, t[-200:])))
        check('落石之城結算測試沒有頁面錯誤', not e1 and not e2, str((e1, e2)))
        await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('星級獎勵測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
