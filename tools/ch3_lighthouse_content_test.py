"""藍堡燈塔（老師 2026-10-09 要求）：港口信譽 3 以上，夜間求助（每天一件，和港口那件不同）與新釣魚點（岩邊，保育類機率較高）；信譽不夠時只有燈塔日誌說明條件。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_lighthouse_content_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
EV = json.load(open(ROOT / 'chapters/ch3/harbor.json', encoding='utf-8'))['EVENTS']
ORDER = ['ch3_h_octopus', 'ch3_h_jelly', 'ch3_h_cut', 'ch3_h_vibrio']
hb_id = lambda d: ORDER[(d * 3) % 4]; lh_id = lambda d: ORDER[(d * 3 + 2) % 4]
QA = {q['q']: q for e in EV.values() for q in e['qs']}
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.c.ch3_done = true; S.started = true; S.coins = 100; S.sta = 100; S.day = 6; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(600)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def enter():
            await page.evaluate("() => { window.__fa.go('ch3_lighthouse', [900, 880]); }"); await page.wait_for_timeout(1000)
        async def things(): return await page.evaluate("() => window.__fa.SCENES.ch3_lighthouse && 0") if False else None
        async def act_at(x, y):
            await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(350)
            return await page.inner_text('#act')
        async def click_act():
            await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(450)
        async def finish(n=60):
            out = []
            for _ in range(n):
                if await page.evaluate("() => document.getElementById('dialog').hidden"):
                    await page.wait_for_timeout(600)
                    if await page.evaluate("() => document.getElementById('dialog').hidden"): return out
                    continue
                t = await page.inner_text('#dText'); out.append(t)
                btns = page.locator('#dBtns button:not([disabled])'); z = next((v for q, v in QA.items() if q in t), None)
                if z and await btns.count() == len(z['opts']): await btns.nth(z['ans']).click()
                elif '釣到了' in t and '你要怎麼做' in t and await btns.count() == 3: await btns.nth(2).click()   # 保育類題：放回海裡
                elif await btns.count(): await btns.nth(0).click()
                await page.wait_for_timeout(150)
            return out
        # --- 港口信譽不夠：只有燈塔日誌
        await page.evaluate("() => { window.__fa.S.c.ch3_hb = {rep: 0, done: 0, n: 0}; }"); await enter()
        check('信譽 0：燈塔只有「燈塔日誌」，沒有求助與釣魚', await act_at(1120, 585) == '燈塔日誌' and await act_at(900, 700) != '求助' and '釣魚' not in await act_at(820, 830))
        await act_at(1120, 585); await click_act(); t = '\n'.join(await finish())
        check('燈塔日誌說明條件（信譽 3、港口志工）與目前信譽', '3' in t and '港口志工' in t and '燈塔夜裡有人需要幫忙' in t and '你現在的港口信譽：0' in t, t)
        # --- 信譽夠：夜間求助與釣魚點
        await page.evaluate("() => { window.__fa.S.c.ch3_hb = {rep: 3, done: 0, n: 0}; window.__fa.S.day = 6; }"); await enter()
        e = EV[lh_id(6)]
        check('燈塔今天的求助和港口今天的不同', lh_id(6) != hb_id(6) and all(lh_id(d) != hb_id(d) for d in range(40)))
        a = await act_at(900, 705); check('信譽 3：長椅旁出現「求助：…」', a.startswith('求助') and e['name'] in a, a)
        check('信譽 3：岩邊有「釣魚（燈塔岩邊）」', '釣魚（燈塔岩邊）' in await act_at(820, 830))
        # 做完求助（備齊用品）
        await page.evaluate("(n) => { const S = window.__fa.S; Object.entries(n).forEach(([k, c]) => { for (let i = 0; i < c; i++) S.kit.push(k); }); }", e['needs'])
        coins, rep = await st('S.coins'), await st('S.c.ch3_hb.rep')
        await act_at(900, 705); await click_act(); t = '\n'.join(await finish())
        check('夜間求助：有開場句、題目答完、獲得 30 金幣、港口信譽 +1', '夕陽照在燈塔上' in t and await st('S.coins') == coins + 30 and await st('S.c.ch3_hb.rep') == rep + 1, t[:200])
        check(f'獲得知識卡 {e["card"]}、記在 S.c.ch3_hb.lh（沒有新增頂層欄位）', await st(f"!!S.cards.{e['card']}") and await st('S.c.ch3_hb.lh.done') == 6 and await st('S.c.ch3_hb.lh.n') == 1 and await page.evaluate("() => !('lh' in window.__fa.S)"))
        check('做完後今晚沒有第二次求助', not (await act_at(900, 705)).startswith('求助'))
        await click_act() if False else None
        await act_at(1120, 585); await click_act(); t = '\n'.join(await finish())
        check('燈塔日誌：今晚的求助都處理好了', '今晚的求助都處理好了' in t, t)
        await page.evaluate("() => { window.__fa.S.day = 7; window.__fa.refresh(); }"); await enter()
        check('隔天又有新的求助，而且是不同的事件', (await act_at(900, 705)).startswith('求助') and EV[lh_id(7)]['name'] in await page.inner_text('#act') and lh_id(7) != lh_id(6))
        # --- 釣魚：燈塔岩邊保育類機率較高（15%），碼頭 8%
        await page.evaluate("() => { const S = window.__fa.S; S.c.ch3_fish = {rod: true, bag: {}, rel: 0, n: 0}; S.sta = 100; window.__ch3FishForce = {hit: true, roll: 0.1, pi: 0}; }")
        await act_at(820, 830); await click_act(); t = '\n'.join(await finish())
        check('燈塔岩邊 roll=0.1：遇到保育類（綠蠵龜），要放回', '綠蠵龜' in t, t[:200])
        await page.evaluate("() => { const S = window.__fa.S; S.sta = 100; }")
        await page.evaluate("() => { window.__fa.go('ch3_harbor', [720, 640]); }"); await page.wait_for_timeout(900)
        await act_at(720, 630); await click_act(); t = '\n'.join(await finish())
        check('碼頭同樣 roll=0.1：不是保育類（碼頭是 8%，沒有改）', '綠蠵龜' not in t and '鬼蝠魟' not in t, t[:200])
        await page.evaluate("() => { window.__ch3FishForce = {hit: true, roll: 0.5, sp: 'grouper', size: 70}; window.__fa.S.sta = 100; }")
        await page.evaluate("() => { window.__fa.S.c.ch3_fish.bag = {}; }")   # 前面碼頭那次是隨機魚種，先清空魚簍再算
        await enter(); await act_at(820, 830); sta = await st('S.sta'); await click_act(); await finish()
        check('燈塔岩邊釣到石斑魚：進魚簍、耗體力', await st('S.c.ch3_fish.bag.grouper') == 1 and await st('S.sta') < sta, str(await st('S.c.ch3_fish')))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
