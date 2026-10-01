"""背包裡的乾糧：沒過期可以吃（體力 +RATION_EAT），過期只能丟，體力滿時不吃。
用法：`python3 -m http.server 8765` 之後 `python3 tools/ration_test.py http://localhost:8765/index.html`"""
import asyncio, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(url + '#debug')
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.scene = 'village'; S.day = 20; S.sta = 50;
          S.kit = ['ration@25','ration@10']; S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        await page.click('#btnBag'); await page.wait_for_selector('#dText button[data-i]')
        n = await page.locator('#dText button[data-r]').count()
        check('沒過期的乾糧有「吃」鈕，過期的沒有', n == 1, f'吃鈕 {n} 個')
        await page.click('#dText button[data-r]'); await page.wait_for_timeout(200)
        st = await page.evaluate("() => ({sta: window.__fa.S.sta, kit: window.__fa.S.kit})")
        check('吃乾糧：體力 +20、乾糧用掉、過期的還在', st == {'sta': 70, 'kit': ['ration@10']}, str(st))
        check('過期乾糧沒有「吃」鈕', await page.locator('#dText button[data-r]').count() == 0)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(200)
        await page.evaluate("() => { const S = window.__fa.S; S.sta = 100; S.kit = ['ration@25']; }")
        await page.click('#btnBag'); await page.wait_for_selector('#dText button[data-r]')
        await page.click('#dText button[data-r]'); await page.wait_for_timeout(200)
        st = await page.evaluate("() => ({sta: window.__fa.S.sta, kit: window.__fa.S.kit})")
        check('體力滿時乾糧不會被吃掉', st == {'sta': 100, 'kit': ['ration@25']}, str(st))
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(200)
        await page.evaluate("() => { const S = window.__fa.S; S.sta = 90; S.kit = ['ration@25']; }")
        await page.click('#btnBag'); await page.wait_for_selector('#dText button[data-r]')
        await page.click('#dText button[data-r]'); await page.wait_for_timeout(200)
        check('體力不滿 20 時最多補到 100', await page.evaluate("() => window.__fa.S.sta") == 100)
        # 劇情第 9 步：唯一一包乾糧要留給爺爺
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(200)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 9; S.sta = 40; S.kit = ['ration@25']; }")
        await page.click('#btnBag'); await page.wait_for_selector('#dText button[data-r]')
        await page.click('#dText button[data-r]'); await page.wait_for_timeout(200)
        st = await page.evaluate("() => ({sta: window.__fa.S.sta, kit: window.__fa.S.kit})")
        check('第 9 步：唯一一包乾糧不能吃', st == {'sta': 40, 'kit': ['ration@25']}, str(st))
        check('沒有頁面錯誤', not errs, str(errs)); await b.close()
    print('乾糧測試全過' if not fails else f'有 {fails} 項失敗'); return fails
if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
