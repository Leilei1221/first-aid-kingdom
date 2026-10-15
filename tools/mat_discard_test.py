"""素材袋：每種素材都能丟棄（有確認）；打火石、鐵礦石、鐵錠可在雜貨店賣出。
用法：python3 -m http.server 8765 之後 `python3 tools/mat_discard_test.py http://localhost:8765/index.html`"""
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
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.scene = 'village'; S.mat.flint = 2; S.mat.ch2_iron = 4; S.mat.ch2_ingot = 1; S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        await page.click('#btnBag'); await page.wait_for_selector('#dText button[data-m^="drop:"]')
        n = await page.locator('#dText button[data-m^="drop:"]').count()
        check('打火石、鐵礦石、鐵錠都有丟棄鈕', n >= 3, str(n))
        await page.click('#dText button[data-m="drop:ch2_iron"]'); await page.wait_for_selector('#dBtns button')
        t = await page.inner_text('#dText')
        check('丟棄前有確認、寫出品名與數量', '鐵礦石' in t and '4' in t, t)
        await page.click('#dBtns button:nth-child(2)'); await page.wait_for_timeout(300)   # 先留著
        check('選「先留著」不會丟', await page.evaluate("() => window.__fa.S.mat.ch2_iron") == 4)
        await page.click('#dText button[data-m="drop:ch2_iron"]'); await page.wait_for_selector('#dBtns button')
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(400)
        check('丟掉後鐵礦石歸零', await page.evaluate("() => window.__fa.S.mat.ch2_iron") == 0)
        await page.click('#dText button[data-m="drop:flint"]'); await page.wait_for_selector('#dBtns button')
        check('丟打火石時提醒之後會用到', '之後' in await page.inner_text('#dText'))
        await page.click('#dBtns button:nth-child(2)'); await page.wait_for_timeout(300)
        await page.click('#dBtns button:last-child'); await page.wait_for_timeout(300)   # 關閉背包
        # 賣
        await page.evaluate("() => { const S = window.__fa.S; S.coins = 0; S.mat.flint = 2; S.mat.ch2_iron = 4; S.mat.ch2_ingot = 1; window.__fa.talk('shopkeeper'); }")
        await page.wait_for_selector('#dText button[data-a="sell:flint"]', timeout=5000) if await page.locator('#dText button[data-a="sell:flint"]').count() else None
        if not await page.locator('#dText button[data-a="sell:flint"]').count():
            await page.click('#dBtns button:first-child'); await page.wait_for_selector('#dText button[data-a="sell:flint"]')
        for k in ('flint', 'ch2_iron', 'ch2_ingot'):
            await page.click(f'#dText button[data-a="sell:{k}"]'); await page.wait_for_timeout(250)
        c = await page.evaluate("() => window.__fa.S.coins")
        check('賣出打火石 2×5＋鐵礦石 4×3＋鐵錠 1×10＝32 金幣', c == 32, str(c))
        check('沒有頁面錯誤', not errs, str(errs))
        await b.close()
    print('素材丟棄與販售測試全過' if not fails else f'有 {fails} 項失敗'); return fails
if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
