"""天氣引擎（D4-1）：排定天災 → 預報 → 當天效果 → 隔天消失；停航；沒有排定時不作用。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/weather_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def boot(ctx, url, extra=''):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.started = true; S.coins = 200; document.getElementById('btnStart').click(); }")
    await page.wait_for_timeout(500)
    return page, errs
async def go(page, scene, x, y):
    await page.evaluate(f"() => window.__fa.go({json.dumps(scene)}, [{x}, {y}])"); await page.wait_for_timeout(700)
    await page.evaluate("() => window.__fa.refresh()")
async def cls(page): return await page.evaluate("() => [...document.getElementById('view').classList].filter(c => ['rain','storm','fog'].includes(c)).sort()")
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url, '?open=ch2')
        msg = await page.evaluate("() => window.__fa.nextDay()")
        check('沒有排定天災：隔天訊息沒有天氣、效果關閉', '天氣' not in msg and '來襲' not in msg and await cls(page) == [] and await page.evaluate("() => window.__fa.wxToday()") is None, msg)
        # 颱風：排定 → 預報 → 當天
        await page.evaluate("() => window.__fa.scheduleWx('typhoon')")
        check('排定颱風後：明天有颱風、停航成立', await page.evaluate("() => window.__fa.stormy()") is True)
        msg = await page.evaluate("() => window.__fa.nextDay()")
        check('隔天早上訊息：今天颱風來襲', '今天颱風來襲' in msg, msg)
        check('今天是颱風', await page.evaluate("() => window.__fa.wxToday()") == 'typhoon')
        await go(page, 'village', 1045, 330)
        check('戶外（村莊）：下雨＋強風效果', await cls(page) == ['rain', 'storm'], str(await cls(page)))
        await go(page, 'home', 840, 770)
        check('室內（爺爺家）：沒有雨', await cls(page) == [], str(await cls(page)))
        await go(page, 'ch2_town', 120, 610)
        check('章節戶外場景（鍛造鎮廣場）也有雨', await cls(page) == ['rain', 'storm'], str(await cls(page)))
        # 停航：颱風當天
        await go(page, 'ch2_port', 1000, 600)
        await page.evaluate("() => { window.__fa.talk('ch2_capt'); }"); await page.wait_for_selector('#dText')
        txt = await page.inner_text('#dText')
        check('颱風當天：船長說今天停航，沒有賣票', '今天停航' in txt and await page.locator('#dBtns button').count() == 1, txt)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
        # 隔天天氣消失
        await page.evaluate("() => window.__fa.nextDay()")
        check('再隔一天：颱風結束', await page.evaluate("() => window.__fa.wxToday()") is None)
        await go(page, 'village', 1045, 330)
        check('颱風結束後效果關閉', await cls(page) == [], str(await cls(page)))
        await page.evaluate("() => window.__fa.go('ch2_port', [1000, 600])"); await page.wait_for_timeout(700)
        await page.evaluate("() => { window.__fa.talk('ch2_capt'); }"); await page.wait_for_selector('#dText')
        txt = await page.inner_text('#dText')
        check('天氣好了：船長賣票', '買票上船' in await page.inner_text('#dBtns'), txt)
        await page.click('#dBtns button:last-child'); await page.wait_for_timeout(300)
        # 豪雨：下雨但沒有強風；預報訊息
        await page.evaluate("() => window.__fa.scheduleWx('flood')")
        msg = await page.evaluate("() => window.__fa.nextDay()")
        check('豪雨：隔天訊息今天豪雨來襲', '今天豪雨來襲' in msg, msg)
        await go(page, 'river', 60, 440)
        check('豪雨：河谷下雨、沒有強風', await cls(page) == ['rain'], str(await cls(page)))
        # 濃霧：只有森林
        await page.evaluate("() => { window.__fa.scheduleWx('fog'); }")
        await page.evaluate("() => window.__fa.nextDay()")
        await go(page, 'forest', 950, 300)
        a = await cls(page); await go(page, 'village', 1045, 330); c = await cls(page)
        check('濃霧：只在森林出現', a == ['fog'] and c == [], f'{a} {c}')
        # 預報：排定後隔天早上先預報
        await page.evaluate("() => window.__fa.scheduleWx('typhoon')")
        st = await page.evaluate("() => JSON.stringify(window.__fa.S.wxNext)")
        check('排定的天災存在存檔狀態裡（重新整理也在）', 'typhoon' in st)
        check('天氣測試沒有頁面錯誤', not errs, str(errs)); await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('天氣測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
