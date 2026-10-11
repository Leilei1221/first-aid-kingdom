"""新手引導：第一次賣木材後的提示、目標欄指向阿木、委託板提示（只在第 3 步出現，且只提示一次）。
用法：python3 -m http.server 8765 之後 `python3 tools/first_hint_test.py http://localhost:8765/index.html`"""
import asyncio, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def txt(page): return await page.evaluate("() => document.getElementById('dText').innerText")
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(url + '#debug')
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 2; S.axe = true; S.mat.wood = 3; S.scene = 'village'; S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        await page.evaluate("() => { window.__fa.talk('shopkeeper'); }")
        await page.wait_for_selector('#dialog:not([hidden])')
        await page.click('#dBtns button:first-child'); await page.wait_for_selector('#dText button[data-a="sell:wood"]')   # 老闆的開場話 → 商店
        await page.click('#dText button[data-a="sell:wood"]'); await page.wait_for_timeout(300)
        goal = await page.inner_text('#goal')
        check('賣完後目標欄指向阿木', '阿木' in goal and '60' in goal, goal)
        await page.click('#dBtns button:first-child')      # 離開商店
        await page.wait_for_function("document.getElementById('dText').innerText.includes('賣掉第一批木材')", timeout=5000)
        t = await txt(page)
        check('賣完離開後有提示（委託板、60 金幣、阿木、看目標）', all(k in t for k in ['委託板', '60', '阿木', '目標']), t)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(400)
        st = await page.evaluate("() => ({step: window.__fa.S.step, w: !!window.__fa.S.warned.afterSell})")
        check('步驟進到 3、提示只記一次', st['step'] == 3 and st['w'], str(st))
        await page.evaluate("() => { window.__fa.talk('shopkeeper'); }")
        await page.wait_for_selector('#dText button[data-a]')
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(500)
        check('再進商店離開不會重複提示', not await page.is_visible('#dialog:not([hidden])'))
        await page.evaluate("() => { window.__fa.board && window.__fa.board(); }")
        has = await page.evaluate("() => typeof window.__fa.board")
        if has == 'function':
            await page.wait_for_selector('#dialog:not([hidden])')
            check('第 3 步委託板有阿木提示', '阿木' in await txt(page))
        check('沒有頁面錯誤', not errs, str(errs))
        await b.close()
    print('新手引導測試全過' if not fails else f'有 {fails} 項失敗'); return fails
if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
