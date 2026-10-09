"""第三章「藍堡的日常」E1（草稿）：港口公告板、每天輪一件海洋傷害求助（藍環章魚、水母、割傷、海洋弧菌）、港口信譽。
老師 2026-10-09 審核通過：完成第三章章末演練（S.c.ch3_done）後對所有人開放，不再需要 ?e1=1（參數留著不影響）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_harbor_test.py http://localhost:8765/index.html`"""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
EV = json.load(open(ROOT / 'chapters/ch3/harbor.json', encoding='utf-8'))['EVENTS']
QS = {q['q']: q for e in EV.values() for q in e['qs']}
ORDER = ['ch3_h_octopus', 'ch3_h_jelly', 'ch3_h_cut', 'ch3_h_vibrio']
async def boot(ctx, url, extra):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '?open=ch2,ch3' + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 300; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
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
async def run(page, max_steps=40):
    """把對話走完：遇到題目按正解，其他按第一個按鈕；回傳看過的文字"""
    out = []
    for _ in range(max_steps):
        if await hidden(page):
            await page.wait_for_timeout(450)
            if await hidden(page): return out
            continue
        txt = await page.inner_text('#dText'); out.append(txt)
        btns = page.locator('#dBtns button:not([disabled])')
        q = next((v for k, v in QS.items() if k in txt), None)
        if q and await btns.count() == len(q['opts']): await btns.nth(q['ans']).click()
        elif await btns.count(): await btns.nth(0).click()
        await page.wait_for_timeout(150)
    return out
def day_for(evid, after=4):
    d = after + 1
    while ORDER[(d * 3) % 4] != evid: d += 1
    return d
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # --- 還沒完成章末演練：沒有公告板；完成後不需要 e1 就有
        page, errs = await boot(ctx, url, '')
        await page.evaluate("() => { window.__fa.S.c.ch3_done = false; }")
        await goto(page, 'ch3_harbor', 820, 640)
        await act_at(page, 1050, 640)
        check('還沒完成章末演練：港口沒有公告板', await hidden(page))
        check('還沒完成章末演練：目標不提公告板', '公告板' not in await page.inner_text('#goal'))
        await page.evaluate("() => { window.__fa.S.c.ch3_done = true; }")
        await goto(page, 'ch3_harbor', 820, 640); await act_at(page, 1050, 640)
        check('完成章末演練後（沒有 e1）：公告板開放給所有人', not await hidden(page))
        await page.close()
        # --- ?e1=1
        page, errs = await boot(ctx, url, '&e1=1')
        await goto(page, 'ch3_harbor', 820, 640)
        await act_at(page, 1050, 640)
        check('還沒完成第三章（章末）：e1 也看不到公告板', await hidden(page))
        await page.evaluate("() => { const S = window.__fa.S; S.c.ch3_done = true; S.kit = []; ['ch3_k1_3','ch3_k2_3','ch3_k3_1','ch3_k3_3','ch3_k4_4'].forEach(k => S.cards[k] = true); }")
        await goto(page, 'ch3_harbor', 820, 640)
        check('完成第三章後：目標指向港口公告板', '公告板' in await page.inner_text('#goal'), await page.inner_text('#goal'))
        await act_at(page, 1050, 640)
        t = await page.inner_text('#dText')
        check('公告板：見習志工、信譽 0、今天的求助', '見習志工' in t and '信譽 0' in t and '今天的求助' in t, t)
        await run(page)
        # --- 缺用品：不算處理
        d = day_for('ch3_h_octopus'); await page.evaluate(f"() => {{ window.__fa.S.day = {d}; }}")
        await goto(page, 'ch3_harbor', 820, 640)
        await act_at(page, 880, 785)
        t = '\n'.join(await run(page))
        check('藍環章魚（缺彈性繃帶）：說明還缺什麼、不算處理', '還缺' in t and await st(page, 'S.c.ch3_hb.done') == 0, t[:200])
        # --- 四件事各走一遍
        rep = 0; coins = await st(page, 'S.coins')
        for k, evid in enumerate(ORDER):
            d = day_for(evid, await st(page, 'S.day'))
            e = EV[evid]
            await page.evaluate("([d, n]) => { const S = window.__fa.S; S.day = d; S.kit = []; for (const [key, c] of Object.entries(n)) for (let i = 0; i < c; i++) S.kit.push(key); }", [d, e['needs']])
            await goto(page, 'ch3_harbor', 820, 640)
            await act_at(page, 880, 785)
            t = '\n'.join(await run(page))
            rep += 1
            check(f'{e["name"]}：題目都出現', all(q['q'] in t for q in e['qs']), t[:150])
            check(f'{e["name"]}：獲得知識卡、金幣 +30、信譽 +1、用品用掉', await st(page, f"S.cards.{e['card']} === true") and await st(page, 'S.coins') == coins + 30 * rep and await st(page, 'S.c.ch3_hb.rep') == rep and await st(page, 'S.kit.length') == 0)
            if e.get('emph'): check('海洋弧菌：特別強調「一定要先就醫」', t.count('一定要先就醫') >= 2, t[-300:])
            await act_at(page, 880, 785)
            check(f'{e["name"]}：同一天不能重複處理', await hidden(page))
        check('四件事都做完：已幫忙 4 件、信譽 4', await st(page, 'S.c.ch3_hb.n') == 4 and await st(page, 'S.c.ch3_hb.rep') == 4)
        await act_at(page, 1050, 640); t = await page.inner_text('#dText'); await run(page)
        check('公告板：稱號港口志工', '港口志工' in t and '今天的求助都處理好了' in t, t)
        check('沒有新增頂層存檔欄位（只用 S.c.ch3_hb）', await st(page, "Object.keys(S).filter(k => k.toLowerCase().includes('ch3') || k.toLowerCase().includes('harbor')).length") == 0)
        # --- 老師預覽：?ev=4 直接看海洋弧菌，不用準備用品、不存進度
        pv = await ctx.new_page(); perrs = []; pv.on('pageerror', lambda e: perrs.append(str(e)))
        await pv.goto(url + '?preview=ch3_harbor&ev=4#debug')
        await pv.wait_for_function("window.__fa && document.getElementById('dialog')", timeout=60000); await pv.wait_for_timeout(1500)
        await act_at(pv, 880, 785)
        t = '\n'.join(await run(pv))
        check('預覽 ?ev=4：海洋弧菌求助，沒有備好用品也能看到題目與「一定要先就醫」', EV['ch3_h_vibrio']['qs'][0]['q'] in t and t.count('一定要先就醫') >= 2, t[:200])
        check('預覽沒有頁面錯誤', not perrs, str(perrs)); await pv.close()
        check('E1 測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('藍堡日常 E1 測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
