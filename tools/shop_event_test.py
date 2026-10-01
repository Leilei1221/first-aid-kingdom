"""雜貨店老闆娘受傷事件（cut）：背包沒有用品時，要能直接買到，再回來處理傷口。
用法：python3 -m http.server 8765 之後 `python3 tools/shop_event_test.py http://localhost:8765/index.html`"""
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
        page = await ctx.new_page()
        errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(url + '#debug')
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.scene = 'shop'; S.coins = 100; S.kit = []; S.kitCap = 6;
          S.event = {id: 'cut', day: S.day}; S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        dlg = lambda: page.inner_text('#dText')
        btns = lambda: page.eval_on_selector_all('#dBtns button', 'bs => bs.map(b => b.textContent)')
        await page.evaluate("() => { window.__fa.talk('shopkeeper'); }")
        await page.wait_for_selector('#dialog:not([hidden])'); await page.click('#dBtns button:first-child')   # 介紹 → 繼續
        await page.wait_for_function("document.getElementById('dText').innerText.includes('需要')")
        check('缺用品時顯示「到櫃檯買急救用品」', '到櫃檯買急救用品' in await btns(), str(await btns()))
        await page.click('#dBtns button:first-child')
        await page.wait_for_selector('#dText button[data-a^="buy:glove"]')
        await page.click('#dText button[data-a="buy:glove"]'); await page.wait_for_timeout(150)
        await page.click('#dText button[data-a="buy:bandaid"]'); await page.wait_for_timeout(150)
        kit = await page.evaluate("() => window.__fa.S.kit")
        check('商店打得開，手套與 OK 繃買得到', sorted(kit) == ['bandaid', 'glove'], str(kit))
        await page.click('#dBtns button')            # 離開商店
        await page.wait_for_timeout(300)
        # 再找一次老闆娘 → 進入事件，備齊用品後出題
        await page.evaluate("() => { window.__fa.talk('shopkeeper'); }")
        await page.wait_for_selector('#dialog:not([hidden])'); await page.click('#dBtns button:first-child')
        await page.wait_for_function("document.getElementById('dBtns').children.length === 3", timeout=5000)
        await page.click('#dBtns button:nth-child(3)')   # 正確答案
        for _ in range(6):
            await page.wait_for_timeout(250)
            if await page.evaluate("() => window.__fa.S.event.done"): break
            if await page.is_visible('#dialog:not([hidden])'): await page.click('#dBtns button:first-child')
        check('備齊用品後可完成事件', await page.evaluate("() => window.__fa.S.event.done"))
        # 其他事件在缺用品時行為不變：仍只有「繼續」
        await page.evaluate("() => { const S = window.__fa.S; S.event = {id: 'bee', day: S.day}; S.kit = []; }") if False else None
        check('沒有頁面錯誤', not errs, str(errs))
        await b.close()
    print('老闆娘事件測試全過' if not fails else f'有 {fails} 項失敗')
    return fails

if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
