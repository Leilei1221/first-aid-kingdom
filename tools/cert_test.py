"""獎狀（老師 2026-10-14 決定）：四關最高星數合計、18 顆結業獎狀、20 顆優等獎狀、姓名確認、列印、舊存檔相容。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/cert_test.py http://localhost:8765/index.html`"""
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
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.day = 5; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        ev = lambda e, a=None: page.evaluate(e, a) if a is not None else page.evaluate(e)
        txt = lambda: page.inner_text('#dText')
        async def btn(label):
            await page.locator('#dBtns button', has_text=label).first.click(); await page.wait_for_timeout(200)
        async def closeAll():
            for _ in range(6):
                if await ev("() => document.getElementById('dialog').hidden"): return
                await page.locator('#dBtns button').last.click(); await page.wait_for_timeout(150)
        async def setStars(c, a, b_, d):
            await ev("([c,a,b,d]) => { const S = window.__fa.S; S.castleBest = c; S.c.stars = a; S.c.ch3_stars = b; S.c.ch4 = Object.assign(S.c.ch4 || {}, {stars: d}); window.__fa.refresh(); }", [c, a, b_, d])
        # ---------- 共用計算 ----------
        r = await ev("() => [FAStars.total({castleBest:5,c:{stars:5,ch3_stars:5,ch4:{stars:5}}}), FAStars.total({}), FAStars.total({castleBest:9,c:{stars:-2,ch3_stars:'x'}}), FAStars.tier(17), FAStars.tier(18), FAStars.tier(19), FAStars.tier(20)]")
        check('星數合計：滿星 20、空存檔 0、異常值被限制在 0～5', r[:3] == [20, 0, 5], r)
        check('等級：17 無、18～19 結業、20 優等', r[3:] == [None, 'grad', 'grad', 'honor'], r)
        # ---------- 舊存檔（沒有 S.c.cert）不出錯、少星時不發獎狀 ----------
        await setStars(3, 3, 3, 3)
        check('12 顆星：沒有獎狀紀錄', await ev("() => !window.__fa.S.c.cert || (!window.__fa.S.c.cert.grad && !window.__fa.S.c.cert.honor)"))
        # ---------- 設定選單有入口 ----------
        await page.click('#btnSettings') if await page.locator('#btnSettings').count() else await ev("() => window.__fa.settings && window.__fa.settings()")
        await page.wait_for_timeout(300)
        labels = await page.locator('#dBtns button').all_inner_texts()
        check('設定選單有「獎狀與筆試」', '獎狀與筆試' in labels, labels)
        await btn('獎狀與筆試')
        t = await txt()
        check('少於 18 顆：顯示總星數 12 / 20 與還差 6 顆', '12 / 20' in t and '還差 6 顆' in t, t)
        labels = await page.locator('#dBtns button').all_inner_texts()
        check('少於 18 顆：沒有領獎狀按鈕', not any('領' in x for x in labels), labels)
        await closeAll()
        # ---------- 18 顆：結業獎狀 ----------
        await setStars(5, 4, 5, 4)
        check('18 顆：記下達成日期（結業）', await ev("() => !!window.__fa.S.c.cert.grad && !window.__fa.S.c.cert.honor"))
        await ev("() => { window.FACloud && (window.FACloud.name = () => '王小明'); }")
        await ev("() => { window.__fa.certCenter(); }"); await page.wait_for_timeout(300)
        t = await txt()
        check('18 顆：中心顯示可領結業獎狀', '結業獎狀可以領取' in t, t)
        await btn('領結業獎狀')
        t = await txt(); nm = await page.input_value('#certNm')
        check('第一次領：先確認姓名，預填登入帳號的名字', nm == '王小明', nm)
        await page.fill('#certNm', '王小明'); await btn('確認')
        t = await txt()
        check('獎狀有姓名、結業獎狀、18 顆星與「不等同 BLS 證照」', '王小明' in t and '結業獎狀' in t and '18' in t and '不等同 BLS 急救證照' in t, t)
        check('姓名存進 S.c.cert', await ev("() => window.__fa.S.c.cert.name") == '王小明')
        async with ctx.expect_page() as pop:
            await btn('列印')
        w = await pop.value; await w.wait_for_load_state()
        pt = await w.inner_text('body')
        check('列印視窗有獎狀內容', '王小明' in pt and '結業獎狀' in pt, pt)
        await w.close()
        await btn('修改姓名'); await page.fill('#certNm', '王大明'); await btn('確認')
        check('可以修改姓名', '王大明' in await txt())
        await closeAll()
        # ---------- 20 顆：優等獎狀 ----------
        await setStars(5, 5, 5, 5)
        check('20 顆：記下優等日期', await ev("() => !!window.__fa.S.c.cert.honor && window.__fa.certTier()") == 'honor')
        await ev("() => { window.__fa.certCenter(); }"); await page.wait_for_timeout(300)
        check('20 顆：中心顯示優等', '優等獎狀已經可以領取' in await txt())
        await btn('領優等獎狀'); t = await txt()
        check('優等獎狀有「優等獎狀」與全部滿星', '優等獎狀' in t and '全部滿星' in t and '王大明' in t, t)
        await closeAll()
        # ---------- 星數降低不會收回已達成的獎狀 ----------
        await setStars(1, 1, 1, 1)
        check('星數事後變少：已達成的獎狀紀錄保留', await ev("() => window.__fa.certTier()") == 'honor')
        check('沒有 JS 錯誤', not errs, errs)
        await b.close()
    print('失敗', fails)
    sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
