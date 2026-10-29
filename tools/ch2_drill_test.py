"""第二章火災演練（老師 2026-10-29 同意）：完成第二章後找消防隊長可重打火災救援，補星數；星數只升不降、不給金幣、不影響 c.done。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch2_drill_test.py http://localhost:8765/index.html`"""
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
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.intro = true; S.started = true; S.coins = 100; S.sta = 100; S.day = 6; S.kitCap = 14;
          Object.assign(S.c, {smith: true, appr: true, cap: true, inn: true, elec: true, clue: true, fire: true, done: true, stars: 3, r_119: 'ok', r_ext: 'ok', r_clothes: 'wrong', r_smith: 'missing', r_guest: 'wrong'});
          S.scene = 'ch2_town'; S.pos = {x: 860, y: 860}; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def click_btn(i):
            await page.wait_for_selector('#dialog:not([hidden])'); await page.locator('#dBtns button:not([disabled])').nth(i).click(); await page.wait_for_timeout(350)
        coins0 = await st('S.coins')
        await page.evaluate("() => { window.__fa.talk('ch2_cap'); }")
        await page.wait_for_selector('#dialog:not([hidden])')
        t = await page.inner_text('#dText')
        check('完成後找消防隊長有「火災演練」選項', '再練習' in t, t)
        await click_btn(0)   # 火災演練
        t = await page.inner_text('#dText'); check('開始前說明規則（紗布、無金幣）', '無菌紗布' in t and '沒有金幣獎勵' in t, t)
        await click_btn(1)   # 先不要
        check('選「先不要」不會重置', await st('S.c.r_119') == 'ok' and not await st('!!S.c.redo'))
        await page.evaluate("() => { window.__fa.talk('ch2_cap'); }"); await click_btn(0); await click_btn(0)   # 開始演練
        await page.wait_for_timeout(1200)
        s = await st("({scene: S.scene, redo: !!S.c.redo, done: !!S.c.done, r: ['r_119','r_ext','r_clothes','r_smith','r_guest'].map(k => S.c[k] || null), ext: S.kit.includes('ch2_extinguisher')})")
        check('進入火場、五項歸零、c.done 不動、有滅火器', s['scene'] == 'ch2_townfire' and s['redo'] and s['done'] and all(x is None for x in s['r']) and s['ext'], str(s))
        await page.wait_for_selector('#dialog:not([hidden])'); await click_btn(0)
        g = await page.inner_text('#goal'); check('目標欄回到火場', '大火' in g, g)
        # 演練中全部處理完（直接設定結果）→ 找隊長以外的人觸發報告
        await page.evaluate("() => { Object.assign(window.__fa.S.c, {r_119: 'ok', r_ext: 'ok', r_clothes: 'ok', r_smith: 'ok', r_guest: 'ok'}); window.__fa.talk('ch2_appr'); }")
        await page.wait_for_function("document.getElementById('dText').innerText.includes('火災演練完成')", timeout=10000) if False else None
        for _ in range(8):
            if await page.evaluate("() => document.getElementById('dialog').hidden"): break
            t = await page.inner_text('#dText')
            if '火災演練完成' in t: break
            await page.locator('#dBtns button:not([disabled])').nth(0).click(); await page.wait_for_timeout(300)
        check('報告顯示「火災演練完成」與最高星數', '火災演練完成' in t and '5' in t, t)
        await click_btn(0); await page.wait_for_timeout(800)
        s = await st("({stars: S.c.stars, redo: !!S.c.redo, done: !!S.c.done, coins: S.coins, scene: S.scene})")
        check('星數升到 5、演練結束、沒有金幣獎勵、回到鎮上', s['stars'] == 5 and not s['redo'] and s['done'] and s['coins'] == coins0 and s['scene'] == 'ch2_town', str(s))
        # 星數只升不降：再打一次全錯
        await page.evaluate("() => { window.__fa.talk('ch2_cap'); }"); await click_btn(0); await click_btn(0); await page.wait_for_timeout(1000)
        await page.evaluate("() => { Object.assign(window.__fa.S.c, {r_119: 'wrong', r_ext: 'ok', r_clothes: 'wrong', r_smith: 'wrong', r_guest: 'wrong'}); window.__fa.talk('ch2_appr'); }")
        for _ in range(8):
            if await page.evaluate("() => document.getElementById('dialog').hidden"): break
            await page.locator('#dBtns button:not([disabled])').nth(0).click(); await page.wait_for_timeout(300)
        await page.wait_for_timeout(600)
        check('星數只升不降（再打 1 星仍是 5）', await st('S.c.stars') == 5, str(await st('S.c.stars')))
        check('沒有頁面錯誤', not errs, str(errs))
        await b.close()
    print('第二章火災演練測試全過' if not fails else f'有 {fails} 項失敗'); return fails
if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
