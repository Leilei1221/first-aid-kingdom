"""第三章「藍堡的日常」E3（草稿）：各國商人（商船輪流靠岸、買賣、中英雙語、海圖碎片）、登山裝備與登山包（格數與負重門檻）、換裝（整套造型與疊件）。
只有 #debug ?e1=1 或老師預覽才會出現。用法：`python3 -u tools/ch3_e3_test.py http://localhost:8765/index.html`"""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
async def boot(ctx, url, extra):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '?open=ch2,ch3' + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 5000; S.sta = 60; S.day = 15; S.kitCap = 14; S.c.ch3_done = true; document.getElementById('btnStart').click(); }")
    await page.evaluate("() => { window.FACloud = { checkpoint: () => {}, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }")
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def goto(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(900)
async def hidden(page): return await page.evaluate("() => document.getElementById('dialog').hidden")
async def act_at(page, x, y):
    await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(400)
    await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(500)
async def click(page, text, wait=350):
    await page.locator('#dBtns button, #dText button', has_text=text).first.click(); await page.wait_for_timeout(wait)
async def text(page): return await page.inner_text('#dText')
async def skip_to(page, label, n=8):
    for _ in range(n):
        if await hidden(page): return False
        if any(label in l for l in await page.locator('#dBtns button').all_inner_texts()): return True
        await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(300)
    return False
async def meet(page, day):
    await page.evaluate(f"() => {{ window.__fa.S.day = {day}; }}"); await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 900, 540)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url, '')
        await page.evaluate("() => { window.__fa.S.c.ch3_done = false; }")
        await meet(page, 15); check('還沒完成章末演練：港口沒有商人、沒有換裝鈕', await hidden(page) and await page.evaluate("() => document.getElementById('btnWear').hidden"))
        await page.evaluate("() => { window.__fa.S.c.ch3_done = true; }")
        await meet(page, 15); check('完成章末演練後（沒有 e1）：商人開放給所有人', not await hidden(page)); await page.close()
        page, errs = await boot(ctx, url, '&e1=1')
        # --- 商船輪流：第 9、10 天日本、11 天沒有、12、13 澳洲、15 尼泊爾
        # --- 尼泊爾（第 15 天）：第一次見面、海圖碎片、買東西
        await meet(page, 15)
        t = await text(page); check('第一次見到尼泊爾商人：英文招呼（Hello! 你好！）', 'Hello!' in t and '帕桑' in t, t)
        await click(page, '繼續'); await click(page, '繼續'); t = await text(page)
        check('第一次見面：獲得海圖碎片 1/3', '碎片' in t and '1/3' in t, t); await click(page, '繼續')
        check('選單：買、賣、聊聊、離開（中英並列）', await skip_to(page, '買東西 Buy'))
        await click(page, '買東西'); t = await text(page)
        check('買東西：登山外套等裝備、中英名稱並列', 'parka' in t and '登山包 backpack' in t and 'wool hat' in t, t[:200])
        c0 = await st(page, 'S.coins')
        await page.locator('button[data-a="jacket"]').click(); await page.wait_for_timeout(300)
        check('買防寒外套：金幣 -400、擁有', await st(page, 'S.coins') == c0 - 400 and await st(page, 'S.c.ch3_e3.own.jacket === 1'))
        await page.locator('button[data-a="hat"]').click(); await page.wait_for_timeout(300)
        check('買毛帽：擁有', await st(page, 'S.c.ch3_e3.own.hat === 1'))
        check('先買小登山包才能買大的（大型登山包按鈕不能按）', await page.locator('button[data-a="pack2"]').is_disabled())
        # 負重門檻：沒登山包時 9 件手套（重量見 items.json）會變慢，買了登山包就不會
        W = json.load(open(ROOT / 'content/items.json', encoding='utf-8'))['ITEMS']['glove']['w']
        await page.evaluate("(n) => { const S = window.__fa.S; S.kitCap = 30; S.kit = Array(n).fill('glove'); }", int(9 / W) + 1)
        m0 = await page.evaluate("() => window.__fa.speedMul()")
        await page.locator('button[data-a="pack1"]').click(); await page.wait_for_timeout(300)
        m1 = await page.evaluate("() => window.__fa.speedMul()")
        check('買登山包：急救背包 18 格、等級 1、負重門檻提高（原本太重走得慢，現在不會）', await st(page, 'S.kitCap') == 18 and await st(page, 'S.c.ch3_pack') == 1 and m0 < 1 and m1 == 1, f'{m0} {m1}')
        await page.locator('button[data-a="pack2"]').click(); await page.wait_for_timeout(300)
        check('再買大型登山包：22 格、等級 2', await st(page, 'S.kitCap') == 22 and await st(page, 'S.c.ch3_pack') == 2)
        await page.locator('button[data-a="warmer"]').click(); await page.wait_for_timeout(300)
        check('暖暖包可以重複買（現有 1）', await st(page, 'S.c.ch3_e3.cnt.warmer') == 1)
        await page.locator('#dBtns button', has_text='回上一頁').click(); await page.wait_for_timeout(300)
        # 賣藥品
        await page.evaluate("() => { window.__fa.S.kit = ['gauze', 'gauze', 'elastic']; }")
        await click(page, '賣東西'); await click(page, '繼續')
        t = await text(page); c1 = await st(page, 'S.coins')
        await page.locator('button[data-a="gauze"]').click(); await page.wait_for_timeout(300)
        check('賣紗布：+7（平常買價 15 的一半，不再有賺價差）、少 1 個', await st(page, 'S.coins') == c1 + 7 and await st(page, 'S.kit.length') == 2)
        # 一天最多收 6 件：賣滿之後按鈕顯示「今天收滿了」，硬按也賣不了
        await page.evaluate("() => { window.__fa.S.kit = Array(10).fill('bandaid'); }"); c2 = await st(page, 'S.coins'); n = 0
        await page.locator('#dBtns button', has_text='回上一頁').click(); await page.wait_for_timeout(300)
        await click(page, '賣東西'); await click(page, '繼續'); await page.wait_for_selector('button[data-a="bandaid"]', timeout=5000)
        for _ in range(9):
            btn = page.locator('button[data-a="bandaid"]')
            if await btn.count() == 0 or await btn.is_disabled(): break
            await btn.click(); await page.wait_for_timeout(250); n += 1
        check('一天最多再收到上限（6 件含剛賣的紗布 1 件，所以 OK 繃只能再賣 5 件）', n == 5 and await st(page, 'S.kit.length') == 5, f'{n} {await st(page, "S.kit.length")}')
        check('收滿後按鈕顯示「今天收滿了」', '今天收滿了' in await page.inner_text('#dText'))
        check('OK 繃一個只付 5（買價 10 的一半）：5 件共 25 金幣', await st(page, 'S.coins') == c2 + 25, str(await st(page, 'S.coins') - c2))
        await page.locator('#dBtns button', has_text='回上一頁').click(); await page.wait_for_timeout(300)
        await click(page, '聊聊'); t = await text(page); check('聊聊：英文小教室（Warm clothes）', 'Warm clothes' in t or '保暖' in t, t)
        await skip_to(page, '離開 Bye'); await click(page, '離開 Bye', 500)
        check('離開後對話關閉', await hidden(page))
        # --- 換裝鈕與換裝
        check('擁有裝備後出現「換裝」鈕', not await page.evaluate("() => document.getElementById('btnWear').hidden"))
        await page.evaluate("() => document.getElementById('btnWear').click()"); await page.wait_for_selector('#wv'); await page.wait_for_timeout(400)
        t = await text(page); check('換裝：疊件（外套、毛帽）；整套裝扮到背包換', '外套' in t and '毛帽' in t and '背包' in t, t)
        await page.locator('button[data-t="jacket"]').click(); await page.wait_for_timeout(700)
        await page.locator('button[data-c="jacket:5"]').click(); await page.wait_for_timeout(700)
        await page.locator('#dBtns button', has_text='完成').click(); await page.wait_for_timeout(1200)
        src = await page.evaluate("() => document.getElementById('hero').querySelector('img').src")
        check('換裝完成：主角的圖換成合成的圖（data URL）、記錄在 S.c.ch3_e3', src.startswith('data:image/png') and await st(page, "S.c.ch3_e3.wear.jacket.on === true && S.c.ch3_e3.wear.jacket.c === 5"), src[:40])
        # 與核心的「整套裝扮」並存：換成水手裝後，疊件重新合成在水手裝上
        await page.evaluate("() => { const S = window.__fa.S; S.c.outfits = ['sailor']; window.__fa.wearOutfit('sailor'); }"); await page.wait_for_timeout(1500)
        src2 = await page.evaluate("() => document.getElementById('hero').querySelector('img').src")
        check('換整套裝扮（水手裝）：疊件仍在、重新合成', src2.startswith('data:image/png') and src2 != src, src2[:40])
        await page.evaluate("() => { window.__fa.wearOutfit(''); window.__fa.S.c.ch3_e3.wear = {}; }"); await page.wait_for_timeout(1200)
        src3 = await page.evaluate("() => document.getElementById('hero').querySelector('img').src")
        check('脫掉疊件、換回預設裝扮：回到原圖（不是 data URL）', not src3.startswith('data:'), src3[:60])
        # --- 日本（第 9 天）：賣魚多三成、加大魚簍
        await page.evaluate("() => { const S = window.__fa.S; S.c.ch3_fish = {rod: true, bag: {grouper: 2}, rel: 0, n: 0}; }")
        await meet(page, 9); await skip_to(page, '買東西 Buy'); await click(page, '賣東西'); await click(page, '繼續'); await page.wait_for_selector('button[data-a="grouper"]')
        c2 = await st(page, 'S.coins'); await page.locator('button[data-a="grouper"]').click(); await page.wait_for_timeout(300)
        check('日本商人收魚：石斑魚 70 × 1.3 ＝ 91', await st(page, 'S.coins') == c2 + 91 and await st(page, 'S.c.ch3_fish.bag.grouper') == 1)
        await page.locator('#dBtns button', has_text='回上一頁').click(); await page.wait_for_timeout(300)
        await click(page, '買東西'); await page.locator('button[data-a="bagplus"]').click(); await page.wait_for_timeout(300)
        check('加大魚簍：魚簍多 4 格', await st(page, 'S.c.ch3_fish.plus') == 4)
        await skip_to(page, '離開 Bye'); await click(page, '離開 Bye', 500)
        # --- 澳洲（第 12 天）：買繃帶、賣乾糧；三片碎片集滿
        await page.evaluate("() => { const S = window.__fa.S; S.kit = ['ration@99', 'ration@99']; S.kitCap = 22; }")
        await meet(page, 12); t = await text(page); await skip_to(page, '買東西 Buy')
        check('澳洲商人：英文招呼', 'Welcome' in t, t)
        await click(page, '賣東西'); await click(page, '繼續'); await page.wait_for_selector('button[data-a="ration"]'); c3 = await st(page, 'S.coins')
        await page.locator('button[data-a="ration"]').click(); await page.wait_for_timeout(300)
        check('賣乾糧：+40', await st(page, 'S.coins') == c3 + 40)
        await page.locator('#dBtns button', has_text='回上一頁').click(); await page.wait_for_timeout(300)
        await click(page, '買東西'); n0 = await st(page, 'S.kit.length'); await page.locator('button[data-a="elastic"]').click(); await page.wait_for_timeout(300)
        check('買彈性繃帶：進急救背包', await st(page, 'S.kit.length') == n0 + 1)
        await skip_to(page, '離開 Bye'); await click(page, '離開 Bye', 500)
        check('三位商人都見過：海圖碎片 3/3', await st(page, 'Object.keys(S.c.ch3_e3.frag).length') == 3)
        # --- 公告板與沒有商船的日子
        await page.evaluate("() => { window.__fa.S.day = 11; }"); await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 1050, 640)
        t = await text(page); check('公告板：沒有商船靠岸的日子，顯示下一艘', '今天沒有商船靠岸' in t and '下一艘' in t, t)
        await page.evaluate("() => document.getElementById('dBtns').querySelector('button').click()"); await page.wait_for_timeout(300)
        await act_at(page, 900, 540); check('沒有商船的日子：港口沒有商人', await hidden(page))
        check('沒有新增頂層存檔欄位', await st(page, "Object.keys(S).filter(k => /e3|pack|wear|frag/i.test(k)).length") == 0)
        check('E3 測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('藍堡日常 E3 測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
