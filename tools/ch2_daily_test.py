"""第二章鍛造鎮日常求助（老師 2026-10-10 同意第二章加玩法）：完成第二章後，廣場有公告板與每天一件求助（5 件輪流，題目是第二章故事裡原本就有的）；信譽、稱號、金幣、知識卡。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch2_daily_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
EV = json.load(open(ROOT / 'chapters/ch2/daily.json', encoding='utf-8'))['EVENTS']
ORDER = ['hot', 'chem', 'blister', 'elec', 'ext']
evof = lambda d: ORDER[(d * 3) % 5]
CARDS = json.load(open(ROOT / 'chapters/ch2/cards.json', encoding='utf-8')); CARDS = CARDS.get('CARDS', CARDS)
QA = {}
for e in EV.values():
    for q in e['qs']:
        if q.get('order'): QA[q['title']] = q
        else: QA[q['q']] = q
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.started = true; S.coins = 100; S.sta = 100; S.day = 6; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def town(): await page.evaluate("() => { window.__fa.go('ch2_town', [700, 760]); }"); await page.wait_for_timeout(1000)
        async def act_at(x, y):
            await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(450)
            return await page.inner_text('#act')
        async def click_act(): await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(450)
        async def finish(n=60):
            out = []
            for _ in range(n):
                if await page.evaluate("() => document.getElementById('dialog').hidden"):
                    await page.wait_for_timeout(600)
                    if await page.evaluate("() => document.getElementById('dialog').hidden"): return out
                    continue
                t = await page.inner_text('#dText'); out.append(t)
                btns = page.locator('#dBtns button:not([disabled])'); z = next((v for q, v in QA.items() if q in t), None)
                if await page.locator('#oq').count():
                    for s_ in EV['ext']['qs'][0]['steps']: await page.locator('#oq button:not([disabled])', has_text=s_).first.click(); await page.wait_for_timeout(120)
                    await page.wait_for_timeout(700)
                elif z and not z.get('order') and await btns.count() == len(z['opts']): await btns.nth(z['ans']).click()
                elif await btns.count(): await btns.nth(0).click()
                await page.wait_for_timeout(150)
            return out
        await town(); a = await act_at(580, 725); check('還沒完成第二章：沒有公告板', '公告' not in a, a)
        await page.evaluate("() => { window.__fa.S.c.done = true; window.__fa.refresh(); }"); await town()
        a = await act_at(580, 725); check('完成第二章後：廣場有「鍛造鎮公告板」', '公告板' in a, a)
        await click_act(); t = '\n'.join(await finish()); e = EV[evof(6)]
        check('公告板：稱號「見習學徒」、信譽 0、今天的求助名稱', '見習學徒' in t and e['name'] in t, t)
        a = await act_at(960, 690); check('廣場上有「求助：…」', a.startswith('求助') and e['name'] in a, a)
        # 備齊用品（水泡那件要紗布）
        await page.evaluate("(n) => { const S = window.__fa.S; Object.entries(n).forEach(([k, c]) => { for (let i = 0; i < c; i++) S.kit.push(k); }); }", e['needs'])
        coins, rep = await st('S.coins'), await st('(S.c.ch2_hb||{rep:0}).rep')
        await act_at(960, 690); await click_act(); t = '\n'.join(await finish())
        check('做完求助：獲得 30 金幣、信譽 +1、知識卡', await st('S.coins') == coins + 30 and await st('S.c.ch2_hb.rep') == rep + 1 and await st(f"!!S.cards.{e['card']}"), t[:200])
        check('記在既有的 S.c.ch2_hb，沒有新增頂層欄位', await st('S.c.ch2_hb.done') == 6 and await page.evaluate("() => !('ch2_hb' in window.__fa.S)"))
        check('今天沒有第二次求助', not (await act_at(960, 690)).startswith('求助'))
        await page.evaluate("() => { window.__fa.S.day = 7; window.__fa.refresh(); }"); await town()
        e2 = EV[evof(7)]; a = await act_at(960, 690); check('隔天換成不同的求助', a.startswith('求助') and e2['name'] in a and evof(7) != evof(6), a)
        # 5 天輪完不重複
        check('5 天內五件各出現一次', len({evof(d) for d in range(6, 11)}) == 5)
        # 缺用品：水泡那天（要紗布）沒帶不能做
        day = next(d for d in range(8, 20) if evof(d) == 'blister')
        await page.evaluate("(d) => { const S = window.__fa.S; S.day = d; S.kit = []; window.__fa.refresh(); }", day); await town()
        a = await act_at(960, 690); await click_act(); t = '\n'.join(await finish())
        check('水泡那天沒帶紗布：說還缺無菌紗布，不能完成（不算做完）', '無菌紗布' in t and await st('S.c.ch2_hb.done') != day, t[:200])
        # 五件都能完整做完（題目逐題答對、滅火器排序題也過）
        for ev in ORDER:
            d = next(d for d in range(30, 60) if evof(d) == ev); e = EV[ev]
            await page.evaluate("([d, n]) => { const S = window.__fa.S; S.day = d; S.kit = []; Object.entries(n).forEach(([k, c]) => { for (let i = 0; i < c; i++) S.kit.push(k); }); window.__fa.refresh(); }", [d, e['needs']]); await town()
            c0 = await st('S.coins'); await act_at(960, 690); await click_act(); await finish()
            check(f'{ev}（{e["name"]}）：整件做完、+30 金幣、拿到知識卡 {e["card"]}', await st('S.c.ch2_hb.done') == d and await st('S.coins') == c0 + 30 and await st(f"!!S.cards.{e['card']}"))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
