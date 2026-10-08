"""裝扮（老師 2026-10-09 決定）：完成第三章後，雜貨店買水手裝、登山裝；第三章 5 顆星送救生員裝、累計簽到 30 天送守護者裝；背包「裝扮」換上，只改外觀。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/outfit_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
O = {o['id']: o for o in json.load(open(pathlib.Path(__file__).parent.parent / 'content/balance.json', encoding='utf-8'))['OUTFITS']['list']}
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 20000; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        heroSrc = lambda: page.evaluate("() => document.querySelector('#hero img').getAttribute('src')")
        async def open_shop():
            await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a]', timeout=8000); await page.wait_for_timeout(200)
        async def close_dlg():
            await page.locator('#dBtns button', has_text='離開').or_(page.locator('#dBtns button', has_text='關閉')).first.click(); await page.wait_for_timeout(300)
        async def click(sel):
            await page.locator(sel).first.click(); await page.wait_for_timeout(350)
        # 完成第三章之前
        await open_shop(); check('還沒完成第三章：商店沒有「裝扮」', '裝扮' not in await page.inner_text('#dText')); await close_dlg()
        await page.evaluate("() => { const S = window.__fa.S; S.c.ch3_done = true; S.hearts.shopkeeper = 0; window.__fa.refresh(); }")
        check('完成第三章但沒達成條件：沒有任何裝扮', await st('S.c.outfits || []') == [])
        await open_shop(); t = await page.inner_text('#dText')
        check('商店有「裝扮」：水手裝、登山裝；救生員裝、守護者裝不在商店', O['sailor']['name'] in t and O['mountain']['name'] in t and O['lifeguard']['name'] not in t and O['guardian']['name'] not in t, t[-300:])
        b4 = await st('S.coins'); await click('#dText button[data-a="out:sailor"]')
        check(f'買水手裝：扣 {O["sailor"]["cost"]}、記在 S.c.outfits，沒有新增頂層欄位', await st('S.coins') == b4 - O['sailor']['cost'] and await st('S.c.outfits') == ['sailor'] and await page.evaluate("() => !('outfits' in window.__fa.S)"))
        check('買過：顯示已擁有、不能再按', await page.locator('#dText button[data-a="out:sailor"]').is_disabled())
        c = await st('S.coins'); await page.evaluate("() => { document.querySelector('#dText button[data-a=\"out:sailor\"]').disabled = false; }"); await click('#dText button[data-a="out:sailor"]')
        check('硬按已擁有的：不扣錢、不重複', await st('S.coins') == c and await st('S.c.outfits') == ['sailor'])
        await close_dlg()
        # 背包換裝
        check('一開始穿預設（hero.webp）', (await heroSrc()).endswith('hero.webp'), await heroSrc())
        await page.evaluate("() => { window.__fa.bag(); }"); await page.wait_for_selector('#dText button[data-w]', timeout=8000)
        t = await page.inner_text('#dText'); check('背包有「裝扮」：預設（穿著中）、水手裝', '裝扮' in t and '預設裝扮' in t and '穿著中' in t and O['sailor']['name'] in t, t[:400])
        await click('#dText button[data-w="sailor"]'); await page.wait_for_selector('#dText button[data-w]', timeout=8000)
        check('換上水手裝：主角圖換成 outfit_sailor、記在 S.c.outfit', 'outfit_sailor' in await heroSrc() and await st('S.c.outfit') == 'sailor', await heroSrc())
        check('水手裝只改外觀：體力與金幣不變', await st('S.sta') == 100)
        await close_dlg()
        await page.evaluate("() => { window.__fa.go('home', [840, 770]); }"); await page.wait_for_timeout(900)
        check('換場景後仍穿著水手裝', 'outfit_sailor' in await heroSrc(), await heroSrc())
        # 存檔與重新載入
        await page.evaluate("() => { window.__fa.save(); }")
        # 條件送：第三章 5 顆星
        await page.evaluate("() => { window.__fa.S.c.ch3_stars = 4; window.__fa.refresh(); }")
        check('4 顆星：還沒有救生員裝', 'lifeguard' not in await st('S.c.outfits'))
        await page.evaluate("() => { window.__fa.S.c.ch3_stars = 5; window.__fa.refresh(); }")
        check('5 顆星：獲得救生員裝', 'lifeguard' in await st('S.c.outfits'))
        await page.evaluate("() => { window.__fa.refresh(); window.__fa.refresh(); }")
        check('重複 refresh 不會重複給', (await st('S.c.outfits')).count('lifeguard') == 1)
        # 累計簽到 30 天
        await page.evaluate("() => { const S = window.__fa.S; S.c.daily = S.c.daily || {days: 0, done: {}, got: {}, titles: []}; S.c.daily.got = S.c.daily.got || {}; S.c.daily.got[30] = true; window.__fa.refresh(); }")
        check('累計簽到 30 天：獲得守護者裝', 'guardian' in await st('S.c.outfits'))
        # 換其他、換回預設
        await page.evaluate("() => { window.__fa.wearOutfit('guardian'); }"); check('換成守護者裝', 'outfit_guardian' in await heroSrc())
        await page.evaluate("() => { window.__fa.wearOutfit(''); }"); check('換回預設', (await heroSrc()).endswith('hero.webp') and await st('S.c.outfit') == None)
        # 沒擁有的編號不能穿（存檔被改過）
        await page.evaluate("() => { window.__fa.S.c.outfit = 'mountain'; window.__fa.S.c.outfits = ['sailor']; window.__fa.go('home', [840, 770]); }"); await page.wait_for_timeout(900)
        check('存檔裡穿著沒擁有的裝扮：退回預設，不壞圖', (await heroSrc()).endswith('hero.webp'), await heroSrc())
        # 還沒完成第三章：不送
        await page.evaluate("() => { const S = window.__fa.S; S.c.ch3_done = false; S.c.outfits = []; S.c.ch3_stars = 5; window.__fa.refresh(); }")
        check('沒完成第三章：條件裝扮不會自動送', await st('S.c.outfits') == [])
        # 圖檔都存在、330x520
        info = await page.evaluate("""async () => Promise.all(['sailor','mountain','lifeguard','guardian'].map(id => new Promise(r => { const i = new Image(); i.onload = () => r([id, i.naturalWidth, i.naturalHeight]); i.onerror = () => r([id, 0, 0]); i.src = 'assets/outfit_' + id + '.webp'; })))""")
        check('四張裝扮圖都能載入且是 330×520', all(w == 330 and h == 520 for _, w, h in info), str(info))
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
