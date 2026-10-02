"""班級控制（D5-1）：遊戲讀取老師端設定（功能開關、天災公告）、本機快取、讀不到時的退路。
用「模擬的雲端」（window.__faRemote）驗證遊戲端邏輯；真正的 Supabase 函式要等老師執行 SQL 後另外實測。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/control_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
def mock(email, control):
    """control：dict＝回傳這個；'error'＝丟錯（模擬沒網路）；None＝這個帳號不是在學學生（RPC 回傳空設定）"""
    c = json.dumps(control)
    return f"""
    window.__faRemote = {{
      async user() {{ return {json.dumps({'email': email}) if email else 'null'}; }}, async signIn() {{}}, async signOut() {{}},
      async load() {{ return null; }}, async insert() {{ return '2026-01-01T00:00:00.000001+00:00'; }}, async update() {{ return '2026-01-01T00:00:00.000002+00:00'; }},
      async checkpoint() {{}}, async loadCheckpoint() {{ return null; }}, async clearCheckpoints() {{}}, async failure() {{}},
      async control() {{ const c = {c}; if (c === 'error') throw new Error('offline'); window.__ctrlCalls = (window.__ctrlCalls || 0) + 1; return c; }}
    }};"""
async def open_page(ctx, url, email, control):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script(mock(email, control))
    await page.goto(url + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.wait_for_timeout(300)
    return page, errs
async def ev(page, expr): return await page.evaluate(expr)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("if(!localStorage.getItem('keep')){localStorage.clear();localStorage.setItem('keep','1');}localStorage.setItem('fa-debug','1')")
        # 1) 沒登入：用程式預設
        page, errs = await open_page(ctx, url, None, {'class_id': 'c1', 'flags': {'wild': True}, 'weather': None})
        check('沒登入：不讀班級設定，野外與救災都用預設（關閉）', await ev(page, "() => window.__fa.CONTROL === null && !window.__fa.flagOn('wild', false) && !window.__fa.flagOn('relief', false)"))
        await page.close()
        # 2) 登入、班級開了 wild 和 relief
        ctrl = {'class_id': 'c1', 'flags': {'wild': True, 'relief': True, 'ch2': False}, 'weather': {'id': 7, 'type': 'typhoon'}}
        page, errs = await open_page(ctx, url, 's1@hlhs.hlc.edu.tw', ctrl)
        r = await ev(page, "() => ({c: window.__fa.CONTROL, wild: window.__fa.flagOn('wild', false), relief: window.__fa.flagOn('relief', false), ch2: window.__fa.flagOn('ch2', true), none: window.__fa.flagOn('zzz', true)})")
        check('登入後讀到班級設定（wild、relief 開、ch2 關、沒設定的用預設）', r['wild'] and r['relief'] and r['ch2'] is False and r['none'] is True and r['c']['weather']['type'] == 'typhoon', str(r))
        check('設定存進本機快取', await ev(page, "() => { try { const c = JSON.parse(localStorage.getItem('fa-kingdom-ctrl-v1')); return c.email === 's1@hlhs.hlc.edu.tw' && c.data.flags.wild === true; } catch (e) { return false; } }"))
        # 老師端的 wild 開關真的控制遊戲：沒有 ?wild=1 也能掉打火石的判斷（用 camp 的守門條件間接驗證：背包露營鈕）
        await ev(page, "() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.started = true; S.mat.flint = 1; document.getElementById('btnStart').click(); }"); await page.wait_for_timeout(500)
        await page.click('#btnBag'); await page.wait_for_selector('#dText')
        check('老師開了 wild：背包的打火石有「露營」鈕（沒加 ?wild=1）', await page.locator('#dText button[data-m="camp"]').count() == 1)
        await page.click('#dBtns button:last-child'); await page.wait_for_timeout(200)
        # 每天早上更新設定
        n0 = await ev(page, "() => window.__ctrlCalls || 0"); await ev(page, "() => window.__fa.nextDay()"); await page.wait_for_timeout(300)
        check('每天早上（nextDay）會再讀一次設定', await ev(page, "() => window.__ctrlCalls || 0") == n0 + 1, str(n0))
        await page.close()
        # 3) 讀不到（沒網路）：用上次的快取
        page, errs = await open_page(ctx, url, 's1@hlhs.hlc.edu.tw', 'error')
        check('讀不到設定時沿用本機快取（wild 仍開）', await ev(page, "() => window.__fa.flagOn('wild', false) === true && window.__fa.CONTROL.flags.relief === true"))
        await page.close()
        # 4) 換一個帳號：不能用上一個人的快取
        page, errs = await open_page(ctx, url, 'other@hlhs.hlc.edu.tw', 'error')
        check('換帳號且讀不到：不使用別人的快取（回到預設）', await ev(page, "() => window.__fa.flagOn('wild', false) === false"))
        await page.close()
        # 5) 非在學學生（老師、訪客）：空設定 → 預設
        page, errs = await open_page(ctx, url, 'guest@gmail.com', {'class_id': None, 'flags': {}, 'weather': None})
        check('訪客／老師：class_id 空、flags 空 → 全部用預設', await ev(page, "() => window.__fa.flagOn('wild', false) === false && window.__fa.flagOn('ch2', true) === true"))
        check('班級控制測試沒有頁面錯誤', not errs, str(errs)); await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('班級控制測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
