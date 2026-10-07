"""第三章 NPC 對話：港口救生員（選單、聊聊依進度）、救生站救生員、港口水手、南岸水手（選單與四個話題）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_npc_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
QZ = json.load(open(pathlib.Path(__file__).parent.parent / 'chapters/ch3/dialogues.json', encoding='utf-8'))['quizzes']
ByQ = {z['q']: z for z in QZ.values() if 'q' in z}
async def boot(ctx, url, opened=True):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + ('?open=ch2,ch3' if opened else '') + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 300; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
    await page.evaluate("() => { window.FACloud = { checkpoint: () => {}, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }")
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def goto(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(800)
async def act(page):
    await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(300)
async def hidden(page): return await page.evaluate("() => document.getElementById('dialog').hidden")
async def drive(page, wrong_first=False, log=None):
    """走完整個第 1 節：題目答對（wrong_first=True 時每題先選一個錯的），其他一律按第一個按鈕；回傳看過的所有文字"""
    texts = []; seen_wrong = set()
    for _ in range(120):
        if await hidden(page):
            await page.wait_for_timeout(450)
            if await hidden(page): return texts
            continue
        if await page.locator('#oq').count():              # 排序題：依正確順序點
            texts.append('[排序]')
            steps = QZ['ch3_q1_7']['steps']
            for s in steps:
                await page.locator('#oq button:not([disabled])', has_text=s).first.click(); await page.wait_for_timeout(120)
            await page.wait_for_timeout(700); continue
        txt = await page.inner_text('#dText'); texts.append(txt)
        z = next((v for q, v in ByQ.items() if q in txt), None)
        btns = page.locator('#dBtns button:not([disabled])')
        if z and await btns.count() == len(z['opts']):
            pick = z['ans']
            if wrong_first and z['q'] not in seen_wrong:
                seen_wrong.add(z['q']); pick = (z['ans'] + 1) % len(z['opts'])
            await btns.nth(pick).click()
        else:
            await btns.nth(0).click()
        await page.wait_for_timeout(150)
    return texts
async def answer_until(page, stop_selector, max_steps=80):
    """答題直到出現 stop_selector（或對話結束）；回傳看過的文字"""
    texts = []
    for _ in range(max_steps):
        if await page.locator(stop_selector).count(): return texts
        if await hidden(page):
            await page.wait_for_timeout(450)
            if await hidden(page): return texts
            continue
        txt = await page.inner_text('#dText'); texts.append(txt)
        z = next((v for q, v in ByQ.items() if q in txt), None)
        btns = page.locator('#dBtns button:not([disabled])')
        if z and await btns.count() == len(z['opts']): await btns.nth(z['ans']).click()
        elif await btns.count(): await btns.nth(0).click()
        await page.wait_for_timeout(150)
    return texts
async def answer_until(page, stop_selector, max_steps=100):
    texts = []
    for _ in range(max_steps):
        if await page.locator(stop_selector).count(): return texts
        if await hidden(page):
            await page.wait_for_timeout(450)
            if await hidden(page): return texts
            continue
        if await page.locator('#oq').count():
            texts.append('[排序]')
            for s in QZ['ch3_q4_5']['steps']:
                await page.locator('#oq button:not([disabled])', has_text=s).first.click(); await page.wait_for_timeout(120)
            await page.wait_for_timeout(700); continue
        txt = await page.inner_text('#dText'); texts.append(txt)
        z = next((v for q, v in ByQ.items() if q in txt), None)
        btns = page.locator('#dBtns button:not([disabled])')
        if z and await btns.count() == len(z['opts']): await btns.nth(z['ans']).click()
        elif await btns.count(): await btns.nth(0).click()
        await page.wait_for_timeout(150)
    return texts
async def say_text(page):
    """目前對話框的文字（空字串＝沒有對話）"""
    return '' if await hidden(page) else await page.inner_text('#dText')
async def talk_at(page, scene, x, y):
    await goto(page, scene, x, y)
    await page.evaluate("([x, y]) => { window.__fa.S.pos = {x, y}; }", [x, y]); await page.wait_for_timeout(300)
    await act(page); await page.wait_for_selector('#dBtns button')
async def next_btn(page, label=None):
    btns = page.locator('#dBtns button:not([disabled])')
    if label: await page.locator('#dBtns button', has_text=label).first.click()
    else: await btns.nth(0).click()
    await page.wait_for_timeout(250)
async def collect_lines(page, n):
    """連續按「繼續」，收集 n 句"""
    out = []
    for _ in range(n):
        out.append(await say_text(page)); await next_btn(page)
    return out
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url)
        # --- 港口救生員：選單與「聊聊」
        for label, c3 in [('還沒做章末演練', None), ('章末完成、5 顆星', {'ch3_done': True, 'ch3_stars': 5}), ('章末完成、3 顆星', {'ch3_done': True, 'ch3_stars': 3})]:
            await page.evaluate("(c) => { const S = window.__fa.S; delete S.c.ch3_done; delete S.c.ch3_stars; if (c) Object.assign(S.c, c); }", c3)
            await talk_at(page, 'ch3_harbor', 1250, 800)
            menu = await page.locator('#dBtns button').all_inner_texts()
            check(f'港口救生員（{label}）：選單「請教救生員（第 4 節）／聊聊／先離開」', menu == ['請教救生員（第 4 節）', '聊聊', '先離開'], str(menu))
            await next_btn(page, '聊聊'); t1 = await say_text(page)
            if label == '還沒做章末演練':
                check('聊聊（還沒做章末）：別當那個只看著的人', '別當那個只看著的人' in t1, t1)
                await next_btn(page); t2 = await say_text(page)
                check('聊聊（還沒做章末）：救生站有假人和 AED', '假人和 AED' in t2, t2)
                await next_btn(page)
            elif c3['ch3_stars'] == 5:
                check('聊聊（4 顆星以上）：處理得很好、心跳之匣', '處理得很好' in t1 and '心跳之匣' in t1, t1); await next_btn(page)
            else:
                check('聊聊（3 顆星以下）：再練幾次', '再練幾次' in t1, t1); await next_btn(page)
            await page.wait_for_selector('#dBtns button')
            check('聊完回到選單', await page.locator('#dBtns button').all_inner_texts() == ['請教救生員（第 4 節）', '聊聊', '先離開'])
            await next_btn(page, '先離開'); await page.wait_for_timeout(300)
            check('先離開：對話關閉', await hidden(page))
        # --- 救生站的救生員
        await talk_at(page, 'ch3_rescue', 693, 690)
        t = await collect_lines(page, 2)
        check('救生站救生員：假人、別怕弄壞它', '假人是給大家練習用的' in t[0] and '別怕弄壞它' in t[1], str(t))
        await page.wait_for_timeout(400); check('救生站救生員：兩句後結束', await hidden(page))
        # --- 港口水手
        await talk_at(page, 'ch3_harbor', 1000, 480)
        t = await collect_lines(page, 2)
        check('港口水手：天氣停航、告示牌搭船', '會停航' in t[0] and '告示牌' in t[1], str(t))
        # --- 南岸水手：選單與四個話題
        sailor = await page.evaluate("() => { const n = window.__fa.SCENES.ch3_fishport.npcs.find(n => n.id === 'ch3_sailor'); return [n.x, n.y]; }")
        await talk_at(page, 'ch3_fishport', sailor[0], sailor[1] + 50)
        menu = await page.locator('#dBtns button').all_inner_texts()
        check('南岸水手：選單五項', menu == ['去藍堡怎麼走', '看浪況', '天氣與颱風季', '救生衣與落水', '先離開'], str(menu))
        expect = {'去藍堡怎麼走': (['找老船長買票', '乾糧和水自己帶比較划算'], 1),
                  '看浪況': (['白色浪花', '寧可多等一天'], 2),
                  '天氣與颱風季': (['天氣預報', '停航就是停航', '看起來沒事', '只是暫時的'], 2),
                  '救生衣與落水': (['穿好救生衣', '自己不要跳下去', '打 118 找海巡'], 2)}
        for topic, (keys, n) in expect.items():
            await next_btn(page, topic)
            t = '\n'.join(await collect_lines(page, n))
            check(f'南岸水手「{topic}」：台詞完整（{len(keys)} 個關鍵句）', all(k in t for k in keys), t)
            await page.wait_for_selector('#dBtns button')
            check(f'「{topic}」說完回到選單', await page.locator('#dBtns button').count() == 5)
        await next_btn(page, '先離開'); await page.wait_for_timeout(300)
        check('南岸水手：先離開，對話關閉', await hidden(page))
        check('NPC 對話測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章 NPC 對話測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
