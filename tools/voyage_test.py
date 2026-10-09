"""航行共用程式（chapters/voyage.js）：第二章、第三章的停航、往返與抵達。整理前後行為必須相同。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/voyage_test.py http://localhost:8765/index.html`"""
import asyncio, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.c.intro = true; S.cards.ch2_lifejacket = true; S.started = true; S.coins = 500; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def goto(scene, x, y):
            await page.evaluate(f"() => {{ window.__fa.go('{scene}', [{x}, {y}]); }}"); await page.wait_for_timeout(800)
        async def act_at(x, y):
            await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(300)
            await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(400)
        async def finish(n=40):
            out = []
            for _ in range(n):
                if await page.evaluate("() => document.getElementById('dialog').hidden"):
                    await page.wait_for_timeout(900)
                    if await page.evaluate("() => document.getElementById('dialog').hidden"): return out
                    continue
                out.append(await page.inner_text('#dText'))
                await page.locator('#dBtns button:not([disabled])').nth(0).click(); await page.wait_for_timeout(150)
            return out
        # 颱風：兩章的船長都停航，不收錢、不開航
        await page.evaluate("() => { window.__fa.scheduleWx('typhoon'); }")
        for scene, x, y, capt in [('ch2_port', 1240, 590, 'ch2'), ('ch3_fishport', 1230, 600, 'ch3')]:
            await goto(scene, x, y); c0 = await st('S.coins'); await act_at(x, y); t = '\n'.join(await finish())
            check(f'{capt}：颱風前一天停航，不收錢、不開航', '停航' in t and await st('S.coins') == c0 and await st('!S.voyage'), t[:200])
        await page.evaluate("() => { window.__fa.S.wxNext = null; }")
        # 第二章回程：從綠葉谷碼頭搭船到鍛造鎮；已經看過迎接就不再重複
        await goto('ch2_port', 1240, 590); await act_at(1240, 590)
        t = await finish(); await page.wait_for_timeout(300)
        check('第二章：買票上船到甲板，兩晚', await st('S.scene') == 'ch2_deck' and await st('S.voyage && S.voyage.left === 2 && S.voyage.to === "ch2_vport"'), str(await st('JSON.stringify([S.scene,S.voyage])')))
        await page.evaluate("() => { Object.assign(window.__fa.S.voyage, {sick: true, mob: true}); window.__fa.S.kit.push('ration', 'ration', 'water', 'water'); }")
        for _ in range(2):
            await act_at(1000, 590); await finish(12)
        check('第二章：兩晚後抵達鍛造鎮碼頭、航行結束', await st('S.scene') == 'ch2_vport' and await st('!S.voyage'), str(await st('JSON.stringify([S.scene,S.voyage])')))
        check('第二章：已看過迎接（S.c.intro），抵達不重複', await st('S.c.intro === true'))
        # 第二章回程：鍛造鎮碼頭搭回綠葉谷，抵達 ch2_port
        await act_at(520, 700); await finish(); 
        check('第二章回程：到甲板、目的地綠葉谷碼頭', await st('S.voyage && S.voyage.to === "ch2_port"'), str(await st('JSON.stringify(S.voyage)')))
        await page.evaluate("() => { Object.assign(window.__fa.S.voyage, {sick: true, mob: true}); window.__fa.S.kit.push('ration', 'ration', 'water', 'water'); }")
        for _ in range(2):
            await act_at(1000, 590); await finish(12)
        check('第二章回程：兩晚後回到綠葉谷碼頭（ch2_port）', await st('S.scene') == 'ch2_port' and await st('!S.voyage'), await st('S.scene'))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
