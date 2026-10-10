"""第四章裝備的作用（老師 2026-10-10：買的裝備要有用）：登山包少耗體力、雪線沒護目鏡／保暖襪多耗體力、營地過夜依保暖等級＋保暖毯＋頭燈決定恢復多少。
用法：python3 -u tools/ch4_gear_test.py http://localhost:8765/index.html"""
import asyncio, sys
from playwright.async_api import async_playwright
fails = 0
def check(n, ok, info=''):
    global fails; print(('✓' if ok else '✗'), n, '' if ok else info); fails += not ok
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1280, 'height': 800}); page = await ctx.new_page(); errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("localStorage.setItem('fa-debug','1')")
        await page.goto(url + '?preview=ch4_village#debug')
        await page.wait_for_function("window.__fa && window.__ch4Gear", timeout=60000)
        ev = lambda js: page.evaluate("() => { const S = window.__fa.S, G = window.__ch4Gear; " + js + " }")
        set_e3 = lambda own, cnt: ev(f"S.c.ch3_e3 = {{own: {own}, cnt: {cnt}, seen: {{}}, frag: {{}}, wear: {{}}}};")
        FULL = "{jacket:1,hat:1,pants:1,gloves:1,boots:1}"
        await ev("S.c.ch3_pack = 0;"); check('沒有登山包：爬山耗體力照舊（c2＝25）', await ev("return G.climbCost('c2');") == 25)
        await ev("S.c.ch3_pack = 1;"); check('登山包 1 級：少耗 5', await ev("return G.climbCost('c2');") == 20)
        await ev("S.c.ch3_pack = 2;"); check('登山包 2 級：少耗 10', await ev("return G.climbCost('c2');") == 15)
        await ev("S.c.ch3_pack = 0;")
        await set_e3(FULL, "{headlamp:1}"); mx = await ev("return window.__fa.staMax();")
        check('保暖齊全＋有頭燈：全回', await ev("return G.sleepRecover().sta;") == mx)
        await set_e3(FULL, "{}"); check('保暖齊全、沒頭燈：90%', await ev("return G.sleepRecover().sta;") == round(mx * .9))
        await set_e3("{jacket:1,hat:1,pants:1}", "{headlamp:1}"); check('缺一些（3 件）：80%', await ev("return G.sleepRecover().sta;") == round(mx * .8))
        await set_e3("{jacket:1}", "{headlamp:1}"); check('不足：50%', await ev("return G.sleepRecover().sta;") == round(mx * .5))
        await set_e3("{jacket:1}", "{headlamp:1, blanket:1}"); r = await ev("return G.sleepRecover();")
        check('不足＋保暖毯：70%，毯子用掉', r['sta'] == round(mx * .7) and await ev("return S.c.ch3_e3.cnt.blanket;") == 0, str(r))
        # 雪線：沒護目鏡 −15、沒保暖襪 −10、都有不扣
        await set_e3(FULL, "{socks:1}"); await ev("S.sta = 80; G.coldCheck();"); await page.wait_for_timeout(500)
        check('沒護目鏡：體力 −15', await ev("return S.sta;") == 65)
        await page.evaluate("() => { document.querySelectorAll('#dBtns button').forEach(b => b.click()); }"); await page.wait_for_timeout(300)
        await set_e3("{jacket:1, goggles:1}", "{}"); await ev("S.sta = 80; G.coldCheck();"); await page.wait_for_timeout(500)
        check('沒保暖襪：體力 −10', await ev("return S.sta;") == 70)
        await page.evaluate("() => { document.querySelectorAll('#dBtns button').forEach(b => b.click()); }"); await page.wait_for_timeout(300)
        await set_e3("{goggles:1}", "{socks:1}"); await ev("S.sta = 80; G.coldCheck();"); await page.wait_for_timeout(500)
        check('護目鏡和保暖襪都有：不扣體力', await ev("return S.sta;") == 80)
        check('沒有頁面錯誤', not errs, str(errs)); await b.close()
    print(f'\n失敗 {fails} 項' if fails else '\n第四章裝備測試全過'); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
