"""第三章第 4 節（專線、防災、分工決策題）：港口救生員入口、題目、知識卡、嚴重錯誤只標記。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_lesson4_test.py http://localhost:8765/index.html`"""
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
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url)
        c4 = ['ch3_k4_1', 'ch3_k4_2', 'ch3_k4_4']
        cards = json.load(open(pathlib.Path(__file__).parent.parent / 'chapters/ch3/cards.json', encoding='utf-8'))['CARDS']
        check('資料：沒有海嘯警報（K4-3、Q4-4）', 'ch3_k4_3' not in cards and 'ch3_q4_4' not in QZ)
        check('資料：第 4 節題目與分工題都在（Q4-1、2、3、5、6、D-1～3）', all(k in QZ for k in ['ch3_q4_1', 'ch3_q4_2', 'ch3_q4_3', 'ch3_q4_5', 'ch3_q4_6', 'ch3_d1', 'ch3_d2', 'ch3_d3']))
        check('嚴重錯誤只標記：Q4-1 E1、D-1 E1、E2、D-2 E4、D-3 E1', QZ['ch3_q4_1']['severe'] == 'E1' and QZ['ch3_d1']['severe'] == 'E1、E2' and QZ['ch3_d2']['severe'] == 'E4' and QZ['ch3_d3']['severe'] == 'E1')
        await goto(page, 'ch3_harbor', 1250, 800)
        await page.evaluate("() => { window.__fa.S.pos = {x: 1250, y: 800}; }"); await page.wait_for_timeout(300)
        lab = await page.inner_text('#act'); check('港口走近救生員：互動鈕「對話」', lab == '對話', lab)
        coins = await st(page, 'S.coins')
        await act(page); await page.wait_for_selector('#dBtns button')
        first = await page.inner_text('#dText'); check('開場：救生員，可選「先離開」', '救生員' in first and await page.locator('#dBtns button').count() == 2, first)
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(500)
        check('選先離開：沒有第 4 節知識卡', await st(page, "Object.keys(S.cards).filter(k => k.startsWith('ch3_k4')).length") == 0)
        await act(page); await page.wait_for_selector('#dBtns button')
        t = '\n'.join(await answer_until(page, '#nothing'))
        for key in ['ch3_q4_1', 'ch3_q4_2', 'ch3_q4_3', 'ch3_d1', 'ch3_d2', 'ch3_d3', 'ch3_q4_6']: check(f'{key} 題目出現', QZ[key]['q'] in t)
        check('排序題 Q4-5 出現並答對', '[排序]' in t and '順序完全正確' in t)
        check('三張知識卡都獲得', await st(page, "%s.every(k => S.cards[k])" % json.dumps(c4)))
        check('第 4 節完成、指向整合演練', '第 4 節完成' in t and '整合演練' in t)
        check('E1／E2／E4 本階段只標記：金幣不變、仍在港口', await st(page, 'S.coins') == coins and await st(page, 'S.scene') == 'ch3_harbor')
        await goto(page, 'ch3_rescue', 760, 840)
        await page.evaluate("() => { window.__fa.S.pos = {x: 693, y: 690}; }"); await page.wait_for_timeout(300)
        await act(page); await page.wait_for_selector('#dText')
        txt = await page.inner_text('#dText'); check('救生站裡的救生員：沒有第 4 節，只有「之後才會加入」', '之後才會加入' in txt and '第 4 節' not in txt, txt)
        check('第 4 節測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章第 4 節測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
