"""體力耗盡：序章以外的地區（藍堡、鍛造鎮、雪嶺…）體力掛零要昏倒、送回該地區的住處、扣醫療費、體力恢復一部分；序章（綠葉谷）行為不變（體力歸零不自動昏倒）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/exhaust_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
CLOUD = "() => { window.FACloud = { checkpoint: () => {}, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }"
async def boot(ctx, url):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '?open=ch2,ch3,ch4&sv=0#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 1000; S.sta = 100; S.day = 30; S.kitCap = 14; S.c.ch3_done = true; S.c.ch3_e3 = { seen: { np: true }, frag: { jp: 1, au: 1, np: 1 }, own: {}, cnt: {}, wear: {} }; S.c.ch4 = { arrived: true }; document.getElementById('btnStart').click(); }")
    await page.evaluate(CLOUD); await page.wait_for_timeout(600)
    return page, errs
async def ev(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def text(page): return await page.inner_text('#dText')
async def hidden(page): return await page.evaluate("() => document.getElementById('dialog').hidden")
async def drain(page, n=14):
    for _ in range(n):
        await page.wait_for_timeout(350)
        if await hidden(page):
            await page.wait_for_timeout(900)
            if await hidden(page): return
            continue
        en = page.locator('#dBtns button:not([disabled])')
        if await en.count(): await en.first.click()
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        for scene, at, rid in [('ch3_harbor', [820, 640], 'ch3'), ('ch4_village', [880, 620], 'ch4')]:
            page, errs = await boot(ctx, url)
            await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, {json.dumps(at)}); }}"); await page.wait_for_timeout(1200)
            c0 = await ev(page, "S.coins"); d0 = await ev(page, "S.day")
            await page.evaluate("() => { window.__fa.S.sta = 0; }")
            await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, {json.dumps(at)}); }}"); await page.wait_for_timeout(1500)
            check(f'{scene}：體力 0、換場景時昏倒（出現昏倒對話）', not await hidden(page) and ('體力' in await text(page) or '倒' in await text(page) or '醒' in await text(page)), (await text(page))[:60] if not await hidden(page) else '沒有對話')
            await drain(page)
            check(f'{scene}：醒來後扣醫療費、天數 +1、體力恢復、回到該地區的住處', await ev(page, "S.coins") < c0 and await ev(page, "S.day") == d0 + 1 and await ev(page, "S.sta") > 0, f'{await ev(page, "S.coins")} {await ev(page, "S.day")} {await ev(page, "S.sta")} {await ev(page, "S.scene")}')
            home = await page.evaluate(f"() => window.__fa.REGIONS.{rid}.home.scene")
            check(f'{scene}：醒來在該地區的住處（{home}）', await ev(page, "S.scene") == home, await ev(page, "S.scene"))
            check(f'{scene}：沒有頁面錯誤', not errs, str(errs[:2])); await page.close()
        # 序章（綠葉谷）：體力歸零不自動昏倒（行為不變）
        page, errs = await boot(ctx, url)
        await page.evaluate("() => { window.__fa.go('village', [1045, 300]); }"); await page.wait_for_timeout(1200)
        c0 = await ev(page, "S.coins")
        await page.evaluate("() => { window.__fa.S.sta = 0; }")
        await page.evaluate("() => { window.__fa.go('village', [1045, 300]); }"); await page.wait_for_timeout(1500)
        check('序章：體力 0 換場景不會自動昏倒（沒有對話、沒扣錢）', await hidden(page) and await ev(page, "S.coins") == c0 and await ev(page, "S.scene") == 'village', f'{await ev(page, "S.coins")} {await ev(page, "S.scene")}')
        await page.close(); await b.close()
    print('\n失敗', fails, '項' if fails else '，全部通過'); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
