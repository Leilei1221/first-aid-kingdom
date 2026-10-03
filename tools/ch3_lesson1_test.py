"""第三章第 1 節（安全、反應、呼吸判斷、求救）：倒地者互動、7 題、3 張知識卡、指派路人、章節關閉時不出現。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_lesson1_test.py http://localhost:8765/index.html`"""
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
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # --- 章節關閉：看不到倒地者與互動點
        page, errs = await boot(ctx, url, opened=False)
        r = await page.evaluate("() => ({open: window.__fa.CHAPTERS.ch3.open, cards: Object.keys(window.__fa.S.cards).filter(k => k.startsWith('ch3_'))})")
        check('章節關閉時：ch3 不開放、沒有第三章知識卡', r == {'open': False, 'cards': []}, str(r))
        await page.close()
        # --- 章節開放
        page, errs = await boot(ctx, url)
        await goto(page, 'ch3_market', 830, 800)
        check('市集有倒地的漁夫圖', await page.evaluate("() => !!document.querySelector('img[src*=\"ch3_fisher_down\"]')"))
        await page.evaluate("() => { window.__fa.S.pos = {x: 790, y: 650}; }"); await page.wait_for_timeout(300)
        lab = await page.inner_text('#act')
        check('走近倒地者：互動鈕「查看倒地的人」', lab == '查看倒地的人', lab)
        await act(page)
        await page.wait_for_selector('#dBtns button')
        first = await page.inner_text('#dText')
        check('開場：有人倒地，可選「先離開」', '倒在港口市集' in first and await page.locator('#dBtns button').count() == 2, first)
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(500)
        check('選先離開：沒有獲得任何知識卡', await st(page, "Object.keys(S.cards).filter(k => k.startsWith('ch3_')).length") == 0)
        await act(page); await page.wait_for_selector('#dBtns button')
        texts = await drive(page)
        joined = '\n'.join(texts)
        for key in ['ch3_q1_1', 'ch3_q1_2', 'ch3_q1_3', 'ch3_q1_4', 'ch3_q1_5', 'ch3_q1_6']:
            check(f'{key} 題目出現', QZ[key]['q'] in joined)
        check('排序題出現並答對', '[排序]' in joined and '順序完全正確' in joined)
        check('答對時顯示解析', QZ['ch3_q1_5']['explain'] in joined)
        cards = await st(page, "Object.keys(S.cards).filter(k => k.startsWith('ch3_')).sort()")
        check('三張知識卡都獲得', cards == ['ch3_k1_1', 'ch3_k1_2', 'ch3_k1_3'], str(cards))
        check('指派兩位不同路人', '你，請打 119' in joined and '你，請去拿 AED' in joined and joined.count('點點頭，立刻照做') == 2)
        check('結尾：第 1 節完成', '第 1 節完成' in joined)
        check('流程結束後對話關閉、可再次互動', await hidden(page))
        # --- 答錯：說「這個做法不對」並可再選一次；不會救援失敗、不扣金幣
        coins = await st(page, 'S.coins')
        await act(page); await page.wait_for_selector('#dBtns button')
        texts = await drive(page, wrong_first=True); joined = '\n'.join(texts)
        check('第一次都選錯：每題顯示「這個做法不對」、可再選', joined.count('這個做法不對') >= 6, str(joined.count('這個做法不對')))
        check('嚴重錯誤（E7／E1）本階段只標記、不觸發救援失敗：金幣不變、仍在市集', await st(page, 'S.coins') == coins and await st(page, 'S.scene') == 'ch3_market', await st(page, 'JSON.stringify([S.coins,S.scene])'))
        # --- 指派：第二人不能再選第一個人
        await act(page); await page.wait_for_selector('#dBtns button')
        for _ in range(40):
            txt = await page.inner_text('#dText'); btns = page.locator('#dBtns button:not([disabled])')
            z = next((v for q, v in ByQ.items() if q in txt), None)
            if '你，請打 119' in txt:
                labels = await btns.all_inner_texts(); check('指派 119：三位路人可選', labels == ['紅衣路人', '藍衣路人', '綠衣路人'], str(labels)); await btns.nth(1).click(); await page.wait_for_timeout(200); continue
            if '你，請去拿 AED' in txt:
                labels = await btns.all_inner_texts(); check('指派 AED：已被指派的不再出現', labels == ['紅衣路人', '綠衣路人'], str(labels)); break
            if await page.locator('#oq').count(): break
            await (btns.nth(z['ans']) if z and await btns.count() == len(z['opts']) else btns.nth(0)).click(); await page.wait_for_timeout(150)
        check('第 1 節測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章第 1 節測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
