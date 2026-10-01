"""欠款時急救用品可賒帳（上限 DEBT_LIMIT），其他商品仍不能買。
用法：在專案根目錄 `python3 -m http.server 8765`，再 `python3 tools/credit_test.py http://localhost:8765/index.html`"""
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
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.scene = 'shop'; S.coins = -100; S.kit = []; S.kitCap = 8; S.mat.wood = 0;
          S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a="buy:glove"]')
        dis = lambda a: page.eval_on_selector(f'#dText button[data-a="{a}"]', 'b => b.disabled')
        txt = lambda a: page.eval_on_selector(f'#dText button[data-a="{a}"]', 'b => b.textContent')
        check('欠款 100：手套可賒帳購買', not await dis('buy:glove') and '賒帳' in await txt('buy:glove'), await txt('buy:glove'))
        check('欠款時小麥種子仍不能買', await dis('seed') if await page.query_selector('#dText button[data-a="seed"]') else True)
        await page.click('#dText button[data-a="buy:glove"]'); await page.wait_for_timeout(150)
        st = await page.evaluate("() => ({c: window.__fa.S.coins, kit: window.__fa.S.kit})")
        check('賒帳後金幣 -120、背包有手套', st == {'c': -120, 'kit': ['glove']}, str(st))
        await page.evaluate("() => { window.__fa.S.coins = -290; window.__fa.refresh(); }")
        await page.click('#dBtns button'); await page.wait_for_timeout(200)
        await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a="buy:glove"]')
        check('欠款 290：手套（20）超過上限，不能買', await dis('buy:glove') and '超過賒帳上限' in await txt('buy:glove'), await txt('buy:glove'))
        check('欠款 290：OK繃（10）剛好到上限，可買', not await dis('buy:bandaid'), await txt('buy:bandaid'))
        check('提示文字說明賒帳', '賒帳' in await page.inner_text('#dText'))
        await page.evaluate("() => { window.__fa.S.coins = 50; window.__fa.refresh(); }")
        await page.click('#dBtns button'); await page.wait_for_timeout(200)
        await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a="buy:glove"]')
        check('有錢時顯示一般「買 1 個」', await txt('buy:glove') == '買 1 個', await txt('buy:glove'))
        check('沒有頁面錯誤', not errs, str(errs)); await b.close()
    print('賒帳測試全過' if not fails else f'有 {fails} 項失敗'); return fails
if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
