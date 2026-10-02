"""營火露營與打火石（D4-4）：礦坑掉打火石、背包露營鈕、營火位置題與熄火題、睡一晚恢復體力、建立存檔點；WILD 關閉時整套不出現。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/camp_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def boot(ctx, url, extra='', rand=None):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    if rand is not None: await page.add_init_script(f"Math.random = () => {rand};")
    MOCK = "window.__cp = 0; window.FACloud = { checkpoint: () => { window.__cp++; }, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {} };"
    await page.goto(url + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.started = true; S.coins = 100; S.sta = 40; S.day = 5; S.tools.pick = true; document.getElementById('btnStart').click(); }")
    await page.evaluate("() => { " + MOCK + " }")  # cloud.js 載入後再換成假的雲端，才算得到存檔點
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def wait_dialog(page, text, t=8000):
    await page.wait_for_function("(tx) => !document.getElementById('dialog').hidden && document.getElementById('dText').innerText.includes(tx)", arg=text, timeout=t)
async def pick(page, i):
    await page.locator('#dBtns button:not([disabled])').nth(i).click(); await page.wait_for_timeout(200)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # 預設（WILD 關閉）：礦坑不掉打火石、背包沒有露營鈕
        page, errs = await boot(ctx, url, rand=0)
        await page.evaluate("() => { window.__fa.go('mine_in', [860, 650]); }"); await page.wait_for_timeout(800)
        for _ in range(3): await page.evaluate("() => { window.__fa.mine(0); }"); await page.wait_for_timeout(450)
        check('預設：敲礦石不會掉打火石', await st(page, '!(S.mat.flint)'), await st(page, 'JSON.stringify(S.mat)'))
        await page.evaluate("() => { window.__fa.S.mat.flint = 1; window.__fa.S.mat.wood = 3; }")
        await page.click('#btnBag'); await page.wait_for_selector('#dText')
        check('預設：背包的打火石沒有「露營」鈕', await page.locator('#dText button[data-m="camp"]').count() == 0)
        await pick(page, 0); await page.close()
        # WILD：礦坑掉打火石
        page, errs = await boot(ctx, url, '?wild=1', rand=0)
        await page.evaluate("() => { window.__fa.go('mine_in', [860, 650]); }"); await page.wait_for_timeout(800)
        for _ in range(3): await page.evaluate("() => { window.__fa.mine(0); }"); await page.wait_for_timeout(450)
        check('WILD：敲礦石掉出打火石', await st(page, '(S.mat.flint || 0) >= 1'), await st(page, 'JSON.stringify(S.mat)'))
        # 露營：不適合的地方
        await page.evaluate("() => { window.__fa.go('village', [1045, 330]); }"); await page.wait_for_timeout(800)
        await page.evaluate("() => { window.__fa.camp(); }"); await wait_dialog(page, '不適合生火露營'); await pick(page, 0)
        # 森林露營：位置題（答對）→ 睡一晚 → 熄火題（答對）
        await page.evaluate("() => { const S = window.__fa.S; S.mat.flint = 1; S.mat.wood = 3; S.sta = 40; window.__fa.go('forest', [950, 300]); }"); await page.wait_for_timeout(900)
        d0 = await st(page, 'S.day'); cp0 = await page.evaluate("() => window.__cp")
        await page.evaluate("() => { window.__fa.camp(); }"); await wait_dialog(page, '營火要生在哪裡'); await pick(page, 1)
        await wait_dialog(page, '處置正確'); await pick(page, 0)
        await wait_dialog(page, '用打火石點燃了營火'); await pick(page, 0)
        await wait_dialog(page, '在營火旁醒來', 12000); await pick(page, 0)
        await wait_dialog(page, '營火要怎麼處理'); await pick(page, 2)
        await wait_dialog(page, '處理正確'); await pick(page, 0); await page.wait_for_timeout(500)
        r = await page.evaluate("() => ({day: window.__fa.S.day, sta: window.__fa.S.sta, flint: window.__fa.S.mat.flint, wood: window.__fa.S.mat.wood, card: !!window.__fa.S.cards.campfire, cp: window.__cp})")
        check('露營一晚：進入下一天、體力至少 70、用掉打火石 1 和木材 3、得到知識卡', r['day'] == d0 + 1 and r['sta'] >= 70 and r['flint'] == 0 and r['wood'] == 0 and r['card'], str(r))
        check('露營睡醒建立每日存檔點', r['cp'] == cp0 + 1, str(r))
        # 熄火答錯不會失敗，只是重新處理（一般錯誤）
        await page.evaluate("() => { const S = window.__fa.S; S.mat.flint = 1; S.mat.wood = 3; S.warned.campQuiz = true; }")
        await page.evaluate("() => { window.__fa.camp(); }"); await wait_dialog(page, '用打火石點燃了營火'); await pick(page, 0)
        await wait_dialog(page, '在營火旁醒來', 12000); await pick(page, 0)
        await wait_dialog(page, '營火要怎麼處理'); await pick(page, 0)
        await wait_dialog(page, '這樣不夠安全'); await pick(page, 0); await page.wait_for_timeout(500)
        check('熄火答錯：解說後仍完成露營（不是救援失敗）', await st(page, 'S.mat.flint') == 0 and await st(page, 'S.day') == d0 + 2)
        await page.evaluate("() => { const S = window.__fa.S; S.mat.flint = 1; S.mat.wood = 1; }")
        await page.click('#btnBag'); await page.wait_for_selector('#dText')
        check('WILD：背包的打火石有「露營」鈕', await page.locator('#dText button[data-m="camp"]').count() == 1)
        await page.locator('#dText button[data-m="camp"]').click(); await wait_dialog(page, '生火需要木材 3 份'); await pick(page, 0)
        check('木材不足：提示需要 3 份', True)
        check('營火測試沒有頁面錯誤', not errs, str(errs)); await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('營火測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
