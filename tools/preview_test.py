"""老師預覽（preview.html → index.html?preview=場景id）：直接站在指定場景、全部章節開放、不碰一般存檔、不連雲端；沒有 ?preview= 時完全不受影響。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/preview_test.py http://localhost:8765/index.html`"""
import asyncio, json, re, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
SENTINEL = json.dumps({'v': 1, 'sentinel': 'student-save', 'scene': 'home', 'coins': 7})
async def main(url):
    root = url.rsplit('/', 1)[0]
    html = (pathlib.Path(__file__).parent.parent / 'preview.html').read_text(encoding='utf-8')
    links = re.findall(r'href="index\.html\?preview=([a-z0-9_]+)[&"]', html)
    check('preview.html：有場景連結且包含市集、救生站', len(links) >= 6 and {'ch3_market', 'ch3_rescue'} <= set(links), str(links))
    check('preview.html 不被搜尋引擎收錄（noindex）', 'name="robots" content="noindex"' in html)
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        # --- 每個連結都能進去：站在該場景、遊戲已開始、沒有錯誤
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script(f"localStorage.setItem('fa-kingdom-p1-v1', {json.dumps(SENTINEL)});")   # 假裝這台已有一份學生存檔
        await page.goto(f'{root}/preview.html'); await page.wait_for_selector('a.go')
        check('preview.html 能開、有連結', await page.locator('a.go').count() == len(links))
        for sid in links:
            await page.goto(f'{root}/index.html?preview={sid}')
            await page.wait_for_function("document.getElementById('game') && !document.getElementById('game').hidden", timeout=60000)
            await page.wait_for_timeout(700)
            r = await page.evaluate("() => ({title: document.getElementById('title').hidden, banner: document.body.innerText.includes('老師預覽'), cloud: typeof window.FACloud, sceneName: document.getElementById('where') ? document.getElementById('where').textContent : null})")
            check(f'?preview={sid}：直接開始遊戲、顯示預覽標示、沒有雲端', r['title'] and r['banner'] and r['cloud'] == 'undefined', str(r))
        # --- 站在對的場景（用市集與救生站驗證場景名稱，其餘看遊戲內的場景名牌）
        for sid, name in [('ch3_market', '港口市集'), ('ch3_rescue', '救生站')]:
            await page.goto(f'{root}/index.html?preview={sid}')
            await page.wait_for_function("document.getElementById('game') && !document.getElementById('game').hidden", timeout=60000); await page.wait_for_timeout(700)
            body = await page.inner_text('body')
            check(f'?preview={sid}：場景名「{name}」', name in body, body[:80])
        # --- 預覽進場景時，章節的圖與互動點要出得來（章節程式要先掛上去才開始）
        for sid, img in [('ch3_market', 'ch3_fisher_down'), ('ch3_rescue', 'ch3_cpr_manikin'), ('ch3_rescue', 'ch3_face_shield')]:
            await page.goto(f'{root}/index.html?preview={sid}')
            await page.wait_for_function("document.getElementById('game') && !document.getElementById('game').hidden", timeout=60000); await page.wait_for_timeout(900)
            check(f'?preview={sid}：場景裡有 {img} 的圖', await page.evaluate("(k) => !!document.querySelector('img[src*=' + JSON.stringify(k) + ']')", img))
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page2 = await ctx.new_page(); page2.on('pageerror', lambda e: errs.append(str(e)))
        await page2.goto(f'{root}/index.html?preview=ch3_market#debug')
        page, page_old = page2, page
        await page.wait_for_function("window.__fa && !document.getElementById('game').hidden", timeout=60000); await page.wait_for_timeout(900)
        await page.evaluate("() => { window.__fa.S.pos = {x: 790, y: 650}; }"); await page.wait_for_timeout(300)
        check('?preview=ch3_market：走近倒地者有「查看倒地的人」', await page.inner_text('#act') == '查看倒地的人')
        await page.evaluate("() => { window.__fa.S.pos = {x: 747, y: 725}; }"); await page.wait_for_timeout(300)
        check('走近路人：互動鈕「對話」', await page.inner_text('#act') == '對話', await page.inner_text('#act'))
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(500)
        txt = await page.inner_text('#dText') if not await page.evaluate("() => document.getElementById('dialog').hidden") else ''
        check('跟沒有對白的路人說話：會出現對話框（……、之後才會加入），不是沒反應', '……' in txt and '之後才會加入' in txt, txt)
        # --- 野外項目、救災物資、天災（預覽參數）
        async def preview(q):
            pg = await ctx.new_page(); await pg.goto(f'{root}/index.html?preview={q}#debug')
            await pg.wait_for_function("window.__fa && !document.getElementById('game').hidden", timeout=60000); await pg.wait_for_timeout(700); return pg
        pg = await preview('river&wild=1')
        await pg.evaluate("() => { window.__fa.S.pos = {x: 560, y: 520}; }"); await pg.wait_for_timeout(300)
        check('?preview=river&wild=1：河邊有「裝溪水」（野外項目開啟）', await pg.inner_text('#act') == '裝溪水', await pg.inner_text('#act'))
        await pg.close()
        pg = await preview('river')
        await pg.evaluate("() => { window.__fa.S.pos = {x: 560, y: 520}; }"); await pg.wait_for_timeout(300)
        check('?preview=river（沒有 wild=1）：河邊沒有「裝溪水」', await pg.inner_text('#act') != '裝溪水')
        await pg.close()
        pg = await preview('home&wx=typhoon')
        r = await pg.evaluate("() => { const S = window.__fa.S, d = S.day; const next = JSON.stringify(S.wxNext); window.__fa.nextDay(); return {next, d, day: S.day, wx: S.wx && S.wx.type}; }")
        check('?preview=home&wx=typhoon：排了明天的颱風，睡一覺（換日）就發生', r['wx'] == 'typhoon' and f'"day":{r["d"] + 1}' in r['next'], str(r))
        await pg.close()
        pg = await preview('home&wx=flood&relief=1')
        r = await pg.evaluate("() => { const S = window.__fa.S; window.__fa.nextDay(); return {wx: S.wx && S.wx.type, relief: !!S.relief}; }")
        check('?preview=home&wx=flood&relief=1：山洪來襲後啟動村長救災物資', r == {'wx': 'flood', 'relief': True}, str(r))
        await pg.close()
        pg = await preview('home&wx=flood')
        r = await pg.evaluate("() => { const S = window.__fa.S; window.__fa.nextDay(); return {wx: S.wx && S.wx.type, relief: !!S.relief}; }")
        check('?preview=home&wx=flood（沒有 relief=1）：山洪會來，但不啟動救災物資', r == {'wx': 'flood', 'relief': False}, str(r))
        await pg.close()
        pg = await preview('home&wx=bogus')
        check('?preview=home&wx=不存在的天災：不排任何天災', await pg.evaluate("() => window.__fa.S.wxNext == null"))
        await pg.close()
        # --- 不碰一般存檔
        saved = await page.evaluate("() => localStorage.getItem('fa-kingdom-p1-v1')")
        check('預覽後，一般存檔（含學生進度）原封不動', saved == SENTINEL, str(saved)[:80])
        check('預覽用自己的存檔 key', await page.evaluate("() => localStorage.getItem('fa-kingdom-preview') !== null"))
        check('預覽沒有頁面錯誤', not errs, str(errs))
        await page.close()
        # --- 沒有 ?preview= 時，完全不受影響：第三章仍然關閉、遊戲停在標題畫面、沒有預覽標示
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(f'{root}/index.html'); await page.wait_for_function("!document.getElementById('btnStart').disabled", timeout=60000)
        r = await page.evaluate("() => ({title: !document.getElementById('title').hidden, banner: document.body.innerText.includes('老師預覽'), cloud: typeof window.FACloud})")
        check('一般進入：停在標題畫面、沒有預覽標示、雲端模組仍在', r['title'] and not r['banner'] and r['cloud'] == 'object', str(r))
        await page.close()
        # 一般進入時第三章仍關閉（用 debug 掛鉤看）
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); await page.goto(f'{root}/index.html#debug'); await page.wait_for_function("window.__fa", timeout=60000)
        check('一般進入：第三章仍然關閉、第二章開放', await page.evaluate("() => ({c3: window.__fa.CHAPTERS.ch3.open, c2: window.__fa.CHAPTERS.ch2.open})") == {'c3': False, 'c2': True})
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('老師預覽測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
