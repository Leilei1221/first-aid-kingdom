"""救援失敗（D4-2）：嚴重錯誤 → 救援失敗畫面 → 回到早上的存檔點（登入）或原地重選（沒登入）→ 扣救援費 → 記錄；一般錯誤維持解說後重選。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/rescue_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def boot(ctx, url):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.started = true; S.coins = 500; S.day = 4; document.getElementById('btnStart').click(); }")
    await page.wait_for_timeout(500)
    return page, errs
async def click_until_hidden(page, n=15):
    texts = []
    for _ in range(n):
        if await page.evaluate("() => document.getElementById('dialog').hidden"):
            await page.wait_for_timeout(500)
            if await page.evaluate("() => document.getElementById('dialog').hidden"): break
            continue
        texts.append(await page.inner_text('#dText')); await page.click('#dBtns button:first-child'); await page.wait_for_timeout(150)
    return texts
START = "() => { window.__r = 'pending'; window.__fa.quiz('hero', '測試題', ['錯A（嚴重）', '錯B（一般）', '對'], 2, '這是解說', undefined, {scenario: 'flood', bad: [0]}).then(() => window.__r = 'passed', e => window.__r = (e && e.rescueAbort) ? 'aborted' : 'error:' + e); }"
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # 1) 一般錯誤：解說後重選，最後答對
        page, errs = await boot(ctx, url)
        await page.evaluate(START); await page.wait_for_selector('#dBtns button')
        await page.locator('#dBtns button').nth(1).click(); await page.wait_for_timeout(200)
        txt = await page.inner_text('#dText')
        check('一般錯誤：顯示解說、可以再選一次', '這個做法不對' in txt and '這是解說' in txt and '救援失敗' not in txt, txt)
        await page.click('#dBtns button:first-child'); await page.wait_for_selector('#dBtns button')
        await page.locator('#dBtns button').nth(2).click(); await page.wait_for_timeout(200); await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
        check('答對後流程繼續（沒有中止、沒扣金幣）', await page.evaluate("() => window.__r") == 'passed' and await page.evaluate("() => window.__fa.S.coins") == 500)
        # 2) 嚴重錯誤、沒有存檔點（沒登入）：原地重選
        await page.evaluate(START); await page.wait_for_selector('#dBtns button')
        await page.locator('#dBtns button').nth(0).click(); await page.wait_for_timeout(250)
        texts = await click_until_hidden(page)
        allt = '\n'.join(texts)
        check('嚴重錯誤：顯示救援失敗與「在現實中…失去生命」', '救援失敗' in allt or '失去了意識' in allt, allt[:200])
        check('沒有存檔點：原地醒來重選、不倒回進度', '你在原地醒了過來' in allt, allt)
        check('扣救援費 200、整段流程被中止', await page.evaluate("() => window.__fa.S.coins") == 300 and await page.evaluate("() => window.__r") == 'aborted',
              str(await page.evaluate("() => [window.__fa.S.coins, window.__r]")))
        check('沒登入的失敗測試沒有頁面錯誤', not errs, str(errs)); await page.close()
        # 3) 嚴重錯誤、有存檔點（登入）：回到早上、記錄失敗
        page, errs = await boot(ctx, url)
        await page.evaluate("""() => { const snap = JSON.parse(JSON.stringify(window.__fa.S)); snap.coins = 900; snap.day = 4; snap.scene = 'home'; snap.pos = {x: 420, y: 660};
          window.__log = []; window.FACloud = { restore: async () => snap, failure: (s, c) => window.__log.push([s, c]), flush: () => {}, checkpoint: () => {}, queueSave: () => {}, status: () => 'ok', email: () => 'a@b.c', onStatus: () => {} }; }""")
        await page.evaluate(START); await page.wait_for_selector('#dBtns button')
        await page.locator('#dBtns button').nth(0).click(); await page.wait_for_timeout(250)
        texts = await click_until_hidden(page); allt = '\n'.join(texts)
        r = await page.evaluate("() => ({coins: window.__fa.S.coins, scene: window.__fa.S.scene, r: window.__r, log: window.__log})")
        check('有存檔點：回到早上的存檔（金幣 900）再扣救援費 200', r['coins'] == 700 and r['scene'] == 'home' and r['r'] == 'aborted', str(r))
        check('顯示「回到今天早上，重新做出選擇」', '回到今天早上' in allt, allt)
        check('失敗記錄：情境與學生選的選項', r['log'] == [['flood', '錯A（嚴重）']], str(r['log']))
        check('有存檔點的失敗測試沒有頁面錯誤', not errs, str(errs)); await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('救援失敗測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
