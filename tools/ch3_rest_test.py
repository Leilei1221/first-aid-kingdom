"""藍堡的休息處（老師 2026-10-09 同意加）：救生站的休息區，免費睡一晚（進入下一天、體力完全恢復、建立存檔點）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_rest_test.py http://localhost:8765/index.html`"""
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
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}window.__cp=0;")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 300; S.sta = 30; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.evaluate("() => { window.FACloud = { checkpoint: () => { window.__cp++; }, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null, reload: () => {} }; }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        await page.evaluate("() => { window.__fa.go('ch3_rescue', [800, 520]); }"); await page.wait_for_timeout(900)
        await page.evaluate("() => { window.__fa.S.pos = {x: 800, y: 470}; }"); await page.wait_for_timeout(400)
        act = await page.inner_text('#act')
        check('救生站有「休息」的互動鈕', '休息' in act, act)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(400)
        t = await page.inner_text('#dText'); check('救生員說可以休息一晚（免費）', '休息一晚' in t and '金幣' not in t.replace('體力完全恢復', ''), t)
        await page.locator('#dBtns button', has_text='先不用').click(); await page.wait_for_timeout(300)
        check('先不用：沒睡、天數與體力不變', await st('S.day') == 5 and await st('S.sta') == 30)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(400)
        coins = await st('S.coins'); cp = await page.evaluate("() => window.__cp")
        await page.locator('#dBtns button', has_text='睡一晚').click(); await page.wait_for_timeout(900)
        t = await page.inner_text('#dText')
        check('睡一晚：進入下一天（第 6 天）、體力回到上限、不扣金幣', await st('S.day') == 6 and await st('S.sta') == await page.evaluate("() => window.__fa.staMax()") and await st('S.coins') == coins, f'{await st("S.day")} {await st("S.sta")}')
        check('早上訊息顯示「睡了一覺」', '睡了一覺' in t, t)
        check('建立存檔點', await page.evaluate("() => window.__cp") == cp + 1)
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
