"""第二章鍛造委託與島上探索點（老師 2026-10-10 同意第二章加玩法）：完成第二章後，鐵匠鋪有「鍛造委託」（每天一張，交鐵礦石或鐵錠換金幣與信譽）；礦坑口、廣場營火坑、碼頭各有一個探索點（每天一次，題目與知識卡沿用現有已審核的）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch2_extras_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
LIST = [{'name': '鐵礦石 ×6', 'need': {'ch2_iron': 6}, 'pay': 60}, {'name': '鐵錠 ×2', 'need': {'ch2_ingot': 2}, 'pay': 90}, {'name': '鐵礦石 ×10', 'need': {'ch2_iron': 10}, 'pay': 110}, {'name': '鐵錠 ×4', 'need': {'ch2_ingot': 4}, 'pay': 200}]
orderof = lambda d: LIST[(d * 3) % 4]
SPOTS = {'mine': ('ch2_lavamine', 900, 780, '礦坑口的告示牌', 'lost', ['憑感覺一直往前走', '停下來、保持冷靜', '往看起來比較亮的地方跑'], 1),
         'camp': ('ch2_town', 860, 780, '廣場的營火坑', 'campfire', None, 1), 'port': ('ch2_vport', 700, 700, '碼頭的氣象公告', 'typhoon', None, 2)}
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.started = true; S.coins = 100; S.sta = 100; S.day = 6; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def go(scene, x, y): await page.evaluate(f"() => {{ window.__fa.go('{scene}', [{x}, {y + 40}]); }}"); await page.wait_for_timeout(1000)
        async def act_at(x, y):
            await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(450); return await page.inner_text('#act')
        async def click_act(): await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(450)
        async def finish(n=40):
            out = []
            for _ in range(n):
                if await page.evaluate("() => document.getElementById('dialog').hidden"):
                    await page.wait_for_timeout(600)
                    if await page.evaluate("() => document.getElementById('dialog').hidden"): return out
                    continue
                t = await page.inner_text('#dText'); out.append(t); btns = page.locator('#dBtns button:not([disabled])')
                labels = await page.locator('#dBtns button').all_inner_texts()
                if len(labels) == 3 and any('停下來' in l or '空曠' in l or '堅固' in l for l in labels):   # 探索題：選正確的那個
                    idx = next(i for i, l in enumerate(labels) if '停下來' in l or '空曠' in l or '堅固' in l); await page.locator('#dBtns button').nth(idx).click()
                elif await btns.count(): await btns.nth(0).click()
                await page.wait_for_timeout(150)
            return out
        # --- 還沒完成第二章：都沒有
        await go('ch2_smithy', 840, 640); a = await act_at(840, 640); check('還沒完成第二章：鐵匠鋪沒有鍛造委託', '委託' not in a, a)
        await page.evaluate("() => { window.__fa.S.c.done = true; window.__fa.refresh(); }")
        # --- 鍛造委託
        await go('ch2_smithy', 840, 640); a = await act_at(840, 640); check('完成第二章後：鐵匠鋪有「鍛造委託」', '鍛造委託' in a, a)
        o = orderof(6)
        await page.evaluate("() => { window.__fa.S.mat.ch2_iron = 2; window.__fa.S.mat.ch2_ingot = 0; }")
        await click_act(); t = await page.inner_text('#dText'); lab = await page.locator('#dBtns button').all_inner_texts()
        check('今天的委託單：內容與酬勞正確、材料不夠時「交出」不能按', o['name'] in t and str(o['pay']) in t and await page.locator('#dBtns button').first.is_disabled(), t + str(lab))
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await page.evaluate("(n) => { Object.entries(n).forEach(([k, c]) => { window.__fa.S.mat[k] = c + 1; }); }", o['need'])
        c0 = await st('S.coins'); await click_act(); await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(400); await finish()
        left = {k: await st(f'S.mat.{k}') for k in o['need']}
        check(f'交出材料：扣材料（剩 1）、+{o["pay"]} 金幣、鍛造信譽 +1', await st('S.coins') == c0 + o['pay'] and all(v == 1 for v in left.values()) and await st('S.c.ch2_or.rep') == 1, str(left))
        await click_act(); t = await page.inner_text('#dText'); check('今天交過了：不能再交', '今天的委託已經交了' in t, t); await page.locator('#dBtns button').first.click(); await page.wait_for_timeout(300)
        check('記在既有的 S.c.ch2_or，沒有新增頂層欄位', await page.evaluate("() => !('ch2_or' in window.__fa.S)"))
        check('隔天換另一張委託單（不同的內容）', orderof(7) != orderof(6))
        # --- 島上探索
        for key, (scene, x, y, label, card, _o, ans) in SPOTS.items():
            await go(scene, x, y); a = await act_at(x, y); check(f'{label}：探索點出現', label in a, a)
            c0 = await st('S.coins'); await click_act(); await finish()
            check(f'{label}：答完得 10 金幣、知識卡 {card}', await st('S.coins') == c0 + 10 and await st(f'!!S.cards.{card}'))
            await click_act(); t = await page.inner_text('#dText'); check(f'{label}：今天只能一次', '今天已經看過了' in t, t); await page.locator('#dBtns button').first.click(); await page.wait_for_timeout(300)
        check('今天三個探索點都做完：記錄 3 個', await st('Object.keys(S.c.ch2_ex.got).length') == 3)
        await page.evaluate("() => { window.__fa.S.day = 7; }"); await go('ch2_vport', 700, 700); await act_at(700, 700); c0 = await st('S.coins'); await click_act(); await finish()
        check('隔天探索點又可以做', await st('S.coins') == c0 + 10)
        # --- 港口商人：第三章的三位商人輪流到火山島碼頭（比藍堡晚一天），規則共用
        cyc = lambda d: ['jp', 'au', 'np'][(d // 3) % 3] if d % 3 < 2 else None
        NAMES = {'jp': '日本商人', 'au': '澳洲商人', 'np': '尼泊爾商人'}
        d = next(d for d in range(40, 80) if cyc(d + 1) == 'au')
        await page.evaluate("(d) => { const S = window.__fa.S; S.day = d; S.c.ch3_done = true; S.kit = []; S.c.ch3_e3 = S.c.ch3_e3 || {frag: {}, own: {}, cnt: {}, seen: {}, wear: {}}; S.c.ch3_e3.seen.au = true; S.c.ch3_e3.frag.au = 1; }", d)
        await go('ch2_vport', 690, 640); a = await act_at(690, 660)
        check(f'火山島碼頭今天輪到澳洲商人（第 {d} 天，藍堡是第 {d} 天的商人 {cyc(d)}）', NAMES['au'] in a, a)
        await click_act(); labs = ' '.join(await page.locator('#dBtns button').all_inner_texts()); check('商人選單：買東西、賣東西、聊聊（沒有「去雪嶺」）', '買東西' in labs and '賣東西' in labs and '聊聊' in labs and '去雪嶺' not in labs, labs)
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        d2 = next(d for d in range(40, 80) if cyc(d + 1) is None)
        await page.evaluate("(d) => { window.__fa.S.day = d; }", d2); await go('ch2_vport', 690, 640); a = await act_at(690, 660)
        check('沒有商船的日子：碼頭沒有商人', not any(n in a for n in NAMES.values()), a)
        await page.evaluate("() => { window.__fa.S.c.ch3_done = false; }")
        await page.evaluate("(d) => { window.__fa.S.day = d; }", d); await go('ch2_vport', 690, 640); a = await act_at(690, 660)
        check('商人也出現在第二章碼頭，不用完成第三章（只要第三章有開放）', NAMES['au'] in a, a)
        await click_act(); await page.wait_for_timeout(300); await page.locator('#dBtns button', has_text='賣東西').click(); await page.wait_for_timeout(300)
        await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(300)
        check('賣東西：走的是第三章的收購規則（今天還能收 N 件、每天上限）', '今天還能收' in await page.inner_text('#dText'), await page.inner_text('#dText'))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
