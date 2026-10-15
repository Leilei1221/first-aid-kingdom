"""新手引導第二階段：第一次靠近的功能提示（只出現一次）、第一次好感度說明（只一次）、點「目標」打開任務清單。
用法：python3 -m http.server 8765 之後 `python3 tools/guide_test.py http://localhost:8765/index.html`"""
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
        await page.evaluate("""() => { const S = window.__fa.S; S.step = 3; S.axe = true; S.scene = 'village'; S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        # 靠近委託板
        pos = await page.evaluate("() => { const o = window.__fa.SCENES.village.things.find(t => t.kind === 'board'); return [o.x, o.y]; }")
        await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {pos[0]}, y: {pos[1]}}}; }}")
        await page.wait_for_function("document.getElementById('toast').classList.contains('on')", timeout=5000)
        t = await page.inner_text('#toast')
        check('第一次靠近委託板出現功能提示', '委託板' in t, t)
        await page.evaluate("() => { document.getElementById('toast').classList.remove('on'); }")
        await page.evaluate("() => { const S = window.__fa.S; S.pos = {x: 10, y: 10}; }"); await page.wait_for_timeout(400)
        await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {pos[0]}, y: {pos[1]}}}; }}"); await page.wait_for_timeout(600)
        check('再靠近不會重複提示', not await page.evaluate("() => document.getElementById('toast').classList.contains('on')"))
        # 任務清單
        await page.click('#goal'); await page.wait_for_selector('#dialog:not([hidden])')
        t = await page.inner_text('#dText')
        check('點「目標」打開任務清單，有主線與委託板工作', '目標' in t and '委託板的工作' in t and '報酬' in t, t)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
        # 好感度說明
        await page.evaluate("() => { const S = window.__fa.S; S.mat.wood = 20; S.req = [0, 2, 1]; window.__fa.S.pos = {x: 10, y: 10}; }")
        await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {pos[0]}, y: {pos[1]}}}; }}"); await page.wait_for_timeout(400)
        await page.evaluate("() => { window.__fa.doAction(); }"); await page.wait_for_selector('#dText button[data-i]')
        await page.click('#dText button[data-i]:not([disabled])'); await page.wait_for_function("document.getElementById('dText').innerText.includes('好感度')", timeout=5000)
        check('第一次增加好感度時說明一次', '愛心' in await page.inner_text('#dText'))
        st = await page.evaluate("() => !!window.__fa.S.warned.heartTip")
        check('好感度說明只記一次', st)
        check('沒有頁面錯誤', not errs, str(errs))
        await b.close()
    print('新手引導第二階段測試全過' if not fails else f'有 {fails} 項失敗'); return fails
if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
