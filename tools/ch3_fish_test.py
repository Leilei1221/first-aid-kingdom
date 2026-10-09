"""第三章「藍堡的日常」E2（草稿）：釣魚、魚尺、保育類放回、魚攤買賣、大網。只有 #debug ?e1=1 或老師預覽才會出現。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_fish_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def boot(ctx, url, extra):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '?open=ch2,ch3' + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 300; S.sta = 60; S.day = 5; S.kitCap = 14; S.c.ch3_done = true; document.getElementById('btnStart').click(); }")
    await page.evaluate("() => { window.FACloud = { checkpoint: () => {}, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }")
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def goto(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(800)
async def hidden(page): return await page.evaluate("() => document.getElementById('dialog').hidden")
async def act_at(page, x, y):
    await page.evaluate(f"() => {{ window.__fa.S.pos = {{x: {x}, y: {y}}}; }}"); await page.wait_for_timeout(300)
    await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(400)
async def run(page, pick=None, max_steps=30):
    """對話走完。pick：{按鈕文字片段: 要按的} 依序比對；題目答案依 ANS；其餘按第一個"""
    out = []
    for _ in range(max_steps):
        if await hidden(page):
            await page.wait_for_timeout(450)
            if await hidden(page): return out
            continue
        txt = await page.inner_text('#dText'); out.append(txt)
        btns = page.locator('#dBtns button:not([disabled])'); labels = await btns.all_inner_texts()
        choice = None
        for q, a in ANS.items():
            if q in txt and len(labels) >= 3: choice = a
        if choice is None and pick:
            for k in pick:
                if any(k in l for l in labels): choice = next(i for i, l in enumerate(labels) if k in l); break
        if choice is None: choice = 0
        if labels: await btns.nth(choice).click()
        await page.wait_for_timeout(150)
    return out
ANS = {'釣到了綠蠵龜（海龜），你要怎麼做？': 2, '釣到了鬼蝠魟（蝠鱝），你要怎麼做？': 2, '要不要買這張大網？': 1}
def force(**k): return f"() => {{ window.__ch3FishForce = {json.dumps(k)}; }}"
async def to_menu(page):
    for _ in range(8):
        labels = await page.locator('#dBtns button').all_inner_texts()
        if any('賣出漁獲' in l for l in labels): return
        await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(300)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # --- 還沒完成章末演練：沒有魚攤；完成後（不需 e1）就有
        page, errs = await boot(ctx, url, '')
        await page.evaluate("() => { window.__fa.S.c.ch3_done = false; }")
        await goto(page, 'ch3_market', 830, 800); await act_at(page, 1150, 520)
        check('還沒完成章末演練：市集沒有魚攤', await hidden(page))
        await page.evaluate("() => { window.__fa.S.c.ch3_done = true; }")
        await goto(page, 'ch3_market', 830, 800); await act_at(page, 1150, 520)
        check('完成章末演練後（沒有 e1）：魚攤開放給所有人', not await hidden(page))
        await page.close()
        page, errs = await boot(ctx, url, '&e1=1')
        # --- 魚攤：買釣竿
        await goto(page, 'ch3_market', 830, 800); await act_at(page, 1150, 520)
        t = await page.inner_text('#dText'); labels = await page.locator('#dBtns button').all_inner_texts()
        check('魚攤：選單有買釣竿、賣出、烤魚、大網、離開；賣出與烤魚在魚簍空時不能按', any('買釣竿' in l for l in labels) and len(labels) == 5 and await page.locator('#dBtns button[disabled]').count() == 2, str(labels))
        coins0 = await st(page, 'S.coins')
        await page.locator('#dBtns button', has_text='買釣竿').click(); await page.wait_for_timeout(300)
        check('買釣竿：金幣 -60、有釣竿', await st(page, 'S.coins') == coins0 - 60 and await st(page, 'S.c.ch3_fish.rod === true'))
        await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        # --- 沒有釣竿的人不能釣（先暫時拿掉）
        await page.evaluate("() => { window.__fa.S.c.ch3_fish.rod = false; }")
        await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 720, 600)
        t = await page.inner_text('#dText'); check('沒有釣竿：說魚攤有賣', '沒有釣竿' in t, t); await run(page)
        await page.evaluate("() => { window.__fa.S.c.ch3_fish.rod = true; }")
        # --- 魚跑掉（體力照扣）
        sta0 = await st(page, 'S.sta'); await page.evaluate(force(hit=False))
        await act_at(page, 720, 600); t = '\n'.join(await run(page))
        check('沒有拉中：魚跑掉了、體力 -4、魚簍沒變', '魚跑掉了' in t and await st(page, 'S.sta') == sta0 - 4 and await st(page, 'Object.keys(S.c.ch3_fish.bag).length') == 0, t[:100])
        # --- 大小合適：留下
        await page.evaluate(force(hit=True, roll=.5, sp='snapper', size=70))
        await act_at(page, 720, 600); t = '\n'.join(await run(page, pick=['留下']))
        check('大小合適的鯛魚：留下、魚簍有 1 隻', '鯛魚' in t and await st(page, 'S.c.ch3_fish.bag.snapper') == 1, t[:160])
        # --- 小魚：選留下也會被攤販提醒並放回
        await page.evaluate(force(hit=True, roll=.5, sp='mackerel', size=20))
        await act_at(page, 720, 600); t = '\n'.join(await run(page, pick=['留下']))
        check('小魚選「留下」：攤販不收、放回、魚簍不變、拿到「小魚要放回」知識卡', '不收' in t and await st(page, 'S.c.ch3_fish.bag.mackerel || 0') == 0 and await st(page, 'S.cards.ch3_c_size === true'), t[:200])
        rep0 = await st(page, 'S.c.ch3_hb ? S.c.ch3_hb.rep : 0')
        for _ in range(2):
            await page.evaluate(force(hit=True, roll=.5, sp='mackerel', size=20)); await act_at(page, 720, 600); await run(page, pick=['放回'])
        check('小魚累計放回 3 次：港口信譽 +1', await st(page, 'S.c.ch3_fish.rel') == 3 and await st(page, 'S.c.ch3_hb.rep') == rep0 + 1, str(await st(page, 'JSON.stringify(S.c.ch3_fish)')))
        # --- 保育類：答對放回、信譽 +1、知識卡
        await page.evaluate(force(hit=True, roll=.01, pi=0)); rep1 = await st(page, 'S.c.ch3_hb.rep')
        await act_at(page, 720, 600); t = '\n'.join(await run(page))
        check('釣到海龜：題目答對放回、信譽 +1、拿到保育類知識卡、魚簍沒有海龜', '綠蠵龜' in t and await st(page, 'S.c.ch3_hb.rep') == rep1 + 1 and await st(page, 'S.cards.ch3_c_protected === true') and await st(page, "Object.keys(S.c.ch3_fish.bag).join() === 'snapper'"), t[:200])
        # --- 魚簍滿了
        await page.evaluate("() => { window.__fa.S.c.ch3_fish.bag = {grouper: 8}; }"); await page.evaluate(force(hit=True, roll=.5, sp='horse', size=80))
        await act_at(page, 720, 600); t = '\n'.join(await run(page, pick=['留下']))
        check('魚簍滿了：裝不下', '裝不下' in t and await st(page, 'S.c.ch3_fish.bag.horse || 0') == 0, t[-120:])
        # --- 賣魚、烤魚、大網
        await page.evaluate("() => { window.__fa.S.c.ch3_fish.bag = {grouper: 2, mackerel: 1}; window.__fa.S.sta = 50; }")
        await goto(page, 'ch3_market', 830, 800); await act_at(page, 1150, 520)
        coins1 = await st(page, 'S.coins')
        await page.locator('#dBtns button', has_text='烤一條魚').click(); await page.wait_for_timeout(400)
        t = await page.inner_text('#dText'); check('烤魚：體力 +12', await st(page, 'S.sta') == 62, t); await to_menu(page); check('烤魚：有「海鮮要煮熟」知識卡', await st(page, 'S.cards.ch3_c_cook === true')); await page.locator('#dBtns button', has_text='賣出漁獲').click(); await page.wait_for_timeout(400)
        left = await st(page, 'Object.values(S.c.ch3_fish.bag).reduce((a,b)=>a+b,0)')
        check('賣出漁獲：魚簍清空、金幣增加（石斑 70 與鯖魚 20 的總和扣掉烤掉的）', left == 0 and await st(page, 'S.coins') in (coins1 + 160, coins1 + 140, coins1 + 90, coins1 + 70), f'{coins1} -> {await st(page, "S.coins")}')
        await to_menu(page)
        await page.locator('#dBtns button', has_text='看看大網').click(); await page.wait_for_timeout(400)
        t = '\n'.join(await run(page, max_steps=12))
        check('大網：題目答對、拿到「流刺網不適用」知識卡', '要不要買這張大網' in t and await st(page, 'S.cards.ch3_c_gear === true'), t[:200])
        check('沒有新增頂層存檔欄位（只用 S.c.ch3_fish）', await st(page, "Object.keys(S).filter(k => k.toLowerCase().includes('fish')).length") == 0)
        check('E2 測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('藍堡日常 E2 測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
