"""背包裡的方糖：體力低於門檻時可以直接吃（不必等跨過門檻當下的提示）。
用法：python3 -m http.server 8765 之後 `python3 tools/sugar_test.py http://localhost:8765/index.html`"""
import asyncio, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(url + '#debug')
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.scene = 'village'; S.sta = 12; S.kit = ['sugar','glove']; S.cards = {}; S.hypoDay = S.day;
          S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        await page.click('#btnBag'); await page.wait_for_selector('#dText button[data-g]')
        check('背包裡的方糖有「吃」鈕', await page.is_visible('#dText button[data-g]'))
        await page.click('#dText button[data-g]'); await page.wait_for_selector('#dialog:not([hidden])')
        await page.wait_for_function("document.getElementById('dText').innerText.includes('體力恢復 30')", timeout=5000)
        st = await page.evaluate("() => ({sta: window.__fa.S.sta, kit: window.__fa.S.kit, hypo: !!window.__fa.S.cards.hypo})")
        check('吃了方糖：體力 +30、方糖用掉、拿到知識卡', st['sta'] == 42 and st['kit'] == ['glove'] and st['hypo'], str(st))
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)   # 吃完回到背包畫面，關閉
        # 體力夠時不能浪費
        await page.evaluate("() => { const S = window.__fa.S; S.sta = 80; S.kit = ['sugar']; }")
        await page.click('#btnBag'); await page.wait_for_selector('#dText button[data-g]')
        await page.click('#dText button[data-g]'); await page.wait_for_timeout(300)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(200)
        st = await page.evaluate("() => ({sta: window.__fa.S.sta, kit: window.__fa.S.kit})")
        check('體力夠時方糖不會被吃掉', st['sta'] == 80 and st['kit'] == ['sugar'], str(st))
        check('沒有頁面錯誤', not errs, str(errs))
        await b.close()
    print('方糖測試全過' if not fails else f'有 {fails} 項失敗'); return fails
if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
