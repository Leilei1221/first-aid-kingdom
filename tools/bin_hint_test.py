"""起床訊息的收納箱提醒：有自動收割機、收納箱裡有小麥時，訊息要提醒「到農田最右邊的收納箱拿」；沒有收割機或箱子是空的就不出現。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/bin_hint_test.py http://localhost:8765/index.html`"""
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
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.started = true; document.getElementById('btnStart').click(); }"); await page.wait_for_timeout(500)
        async def morning(harvester, bin_, plots):
            return await page.evaluate("([h, b, pl]) => { const S = window.__fa.S; S.harvester = h; S.bin = b; S.plots = pl; return window.__fa.nextDay(); }", [harvester, bin_, plots])
        ripe = {'0': {'st': 'planted', 'g': 99, 'wet': False}}
        html = await morning(True, 0, ripe)
        check('今天收成：訊息有「收了小麥」與收納箱提醒（共 3 份）', '自動收割機收了小麥 ×3' in html and '收納箱裡現在有小麥 ×3' in html and '農田最右邊的收納箱' in html and '素材袋' in html, html)
        html = await morning(True, 5, {})
        check('今天沒收成、但箱子裡還有 5 份：仍然提醒', '收納箱裡現在有小麥 ×5' in html and '自動收割機收了小麥' not in html, html)
        html = await morning(True, 0, {})
        check('有收割機但箱子是空的：沒有提醒', '收納箱裡現在有' not in html, html)
        html = await morning(False, 7, {})
        check('沒有收割機：沒有提醒', '收納箱裡現在有' not in html, html)
        check('收納箱提醒測試沒有頁面錯誤', not errs, str(errs))
        await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('收納箱提醒測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
