"""村長與災後救災物資（D4-5）：預設關閉；開啟後地震／山洪災後當天與隔天村長發放乾糧與開水、有上限、救災物資不能賣、過後收回。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/relief_test.py http://localhost:8765/index.html`"""
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
    # 有班級、後台沒設定的學生：野外項目預設關（不屬於任何班的人野外預設是開的，選單會多一項打火石）；救災物資用 ?relief=1 開
    await page.add_init_script("localStorage.setItem('fa-kingdom-ctrl-v1', JSON.stringify({email: 's1@hlhs.hlc.edu.tw', data: {class_id: 'c1', flags: {}, weather: null}, at: Date.now()}));")
    await page.goto(url + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.started = true; S.coins = 100; S.day = 8; S.kitCap = 10; S.kit = []; document.getElementById('btnStart').click(); }")
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def go_village(page):
    await page.evaluate("() => { window.__fa.go('village', [1045, 330]); }"); await page.wait_for_timeout(900)
async def wait_dialog(page, text, t=8000):
    await page.wait_for_function("(tx) => !document.getElementById('dialog').hidden && document.getElementById('dText').innerText.includes(tx)", arg=text, timeout=t)
async def pick(page, i):
    await page.locator('#dBtns button:not([disabled])').nth(i).click(); await page.wait_for_timeout(200)
async def npc_names(page): return await page.evaluate("() => [...document.querySelectorAll('.npc .tag')].map(e => e.textContent.replace('!', ''))")
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # 預設：關閉
        page, errs = await boot(ctx, url)
        await page.evaluate("() => { window.__fa.startRelief('quake'); }"); await go_village(page)
        check('預設（RELIEF 關閉）：不會啟動救災、村莊沒有村長', await st(page, '!S.relief') and '村長' not in await npc_names(page), str(await npc_names(page)))
        await page.close()
        # 開啟
        page, errs = await boot(ctx, url, '?relief=1')
        await page.evaluate("() => { window.__fa.startRelief('quake'); }"); await go_village(page)
        check('災後：村莊出現村長（S.relief 有效 2 天）', '村長' in await npc_names(page) and await st(page, 'S.relief.until === S.day + 1'), str(await npc_names(page)))
        await page.evaluate("() => { window.__fa.chiefTalk(); }"); await wait_dialog(page, '我是這裡的村長'); await pick(page, 0)
        await wait_dialog(page, '乾糧、開水'); await pick(page, 0); await wait_dialog(page, '乾糧、開水'); await pick(page, 0)   # 乾糧 ×2
        await wait_dialog(page, '乾糧、開水')
        btn = await page.locator('#dBtns button').all_inner_texts()
        check('乾糧領滿 2 份後按鈕變灰', '還能領 0' in btn[0] and await page.locator('#dBtns button').first.is_disabled(), str(btn))
        await pick(page, 0); await wait_dialog(page, '乾糧、開水')   # 開水 ×1（跳過灰掉的乾糧，第 0 個可按的是開水）
        r = await st(page, "({kit: S.kit, taken: S.relief.taken})")
        check('領了乾糧 ×2（標記 @r 的救災物資）與開水 ×1', r['kit'].count('water') == 1 and sum(1 for k in r['kit'] if k.startswith('ration@') and k.endswith('@r')) == 2 and r['taken'] == {'ration': 2, 'water': 1}, str(r))
        check('救災乾糧的保存期限照一般乾糧計（到第 18 天）', 'ration@18@r' in r['kit'], str(r['kit']))
        await pick(page, 1)  # 離開
        await wait_dialog(page, '不能拿去換錢'); await pick(page, 0)
        # 背包滿了
        await page.evaluate("() => { const S = window.__fa.S; S.kit = ['glove','glove','glove','glove','glove','glove','glove','glove','glove','glove']; window.__fa.chiefTalk(); }")
        await wait_dialog(page, '乾糧、開水'); await pick(page, 0); await wait_dialog(page, '背包已經滿了'); await pick(page, 0)
        await wait_dialog(page, '乾糧、開水'); await pick(page, 1)  # 離開
        await page.wait_for_timeout(400)
        if not await page.evaluate("() => document.getElementById('dialog').hidden"): await pick(page, 0)
        # 商店不收救災乾糧
        await page.evaluate("() => { const S = window.__fa.S; S.kit = ['ration@18@r', 'ration@18@r']; S.step = 8; window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText')
        t1 = await page.inner_text('#dText'); await pick(page, 0)
        await page.evaluate("() => { const S = window.__fa.S; S.kit = ['ration@18@r', 'ration@19']; window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText')
        t2 = await page.inner_text('#dText'); await pick(page, 0)
        check('商店：只有救災乾糧時沒有「賣乾糧」', '賣 1 包' not in t1 and '急救背包裡有' not in t1.split('乾糧')[1][:40] if '乾糧' in t1 else True, t1[:200])
        check('商店：自己做的乾糧可以賣（只算 1 包）', '急救背包裡有 1 包' in t2, t2[:300])
        # 時間：當天與隔天有、之後收回
        await page.evaluate("() => { window.__fa.nextDay(); }"); await go_village(page)
        check('隔天村長還在', '村長' in await npc_names(page) and await st(page, '!!S.relief'))
        msg = await page.evaluate("() => window.__fa.nextDay()")
        check('再隔天：救災物資收回、早上訊息說明、存檔清掉 S.relief', '收回倉庫' in msg and await st(page, '!S.relief'), msg)
        await go_village(page)
        check('收回後村莊沒有村長', '村長' not in await npc_names(page), str(await npc_names(page)))
        # 山洪
        await page.evaluate("() => { window.__fa.scheduleWx('flood'); window.__fa.nextDay(); }")
        check('山洪當天也啟動救災（類型 flood）', await st(page, "S.relief && S.relief.type === 'flood'"))
        check('救災測試沒有頁面錯誤', not errs, str(errs)); await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('救災測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
