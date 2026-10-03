"""第三章第 3 節（人工呼吸 30:2 與 AED）：吹氣與 AED 步驟的判定、救生站面罩與 AED 互動、8 題、3 張知識卡、吹氣遊戲、AED 練習。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_lesson3_test.py http://localhost:8765/index.html`"""
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
            for s in QZ['ch3_q3_8']['steps']:
                await page.locator('#oq button:not([disabled])', has_text=s).first.click(); await page.wait_for_timeout(120)
            await page.wait_for_timeout(700); continue
        txt = await page.inner_text('#dText'); texts.append(txt)
        z = next((v for q, v in ByQ.items() if q in txt), None)
        btns = page.locator('#dBtns button:not([disabled])')
        if z and await btns.count() == len(z['opts']): await btns.nth(z['ans']).click()
        elif await btns.count(): await btns.nth(0).click()
        await page.wait_for_timeout(150)
    return texts
async def hold(page, ms):
    await page.evaluate("async (ms) => { const h = document.getElementById('bh'); h.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true})); await new Promise(r => setTimeout(r, ms)); h.dispatchEvent(new PointerEvent('pointerup', {bubbles: true})); }", ms)
    await page.wait_for_timeout(150)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url)
        # --- 純計算
        r = await page.evaluate("""async () => {
          const R = await import('/chapters/ch3/rhythm.js'), A = await import('/chapters/ch3/aed.js');
          return {lv: [R.breathLevel(0), R.breathLevel(1000), R.breathLevel(9999)], band: [R.breathBand(10), R.breathBand(50), R.breathBand(100), R.breathBand(40), R.breathBand(70)],
            n: A.STEPS.length, ids: A.STEPS.map(s => s.id), codes: A.STEPS.map(s => A.choose(+A.STEPS.indexOf(s), false).code), ok: A.choose(0, true), voice: A.STEPS[2].voice};
        }""")
        check('breathLevel：0、1 秒＝50、封頂 100', r['lv'] == [0, 50, 100], str(r['lv']))
        check('breathBand：太少、剛好、太多、邊界（40、70 算剛好）', r['band'] == ['low', 'ok', 'high', 'ok', 'ok'], str(r['band']))
        check('AED 5 步：開機→貼片→分析→電擊→電擊後', r['ids'] == ['on', 'pads', 'analyze', 'shock', 'after'], str(r['ids']))
        check('AED 錯誤示範的嚴重錯誤代碼：無、E2、E5、E5、E4', r['codes'] == [None, 'E2', 'E5', 'E5', 'E4'], str(r['codes']))
        check('AED 正確選擇：ok', r['ok']['ok'] is True and r['ok']['code'] is None)
        check('分析那一句語音取自草稿 Q3-6 題幹', r['voice'] == '正在分析心律，請勿碰觸傷者', r['voice'])
        await goto(page, 'ch3_rescue', 760, 840)
        check('救生站有 CPR 面罩圖', await page.evaluate("() => !!document.querySelector('img[src*=\"ch3_face_shield\"]')"))
        # --- 人工呼吸
        await page.evaluate("() => { window.__fa.S.pos = {x: 1010, y: 740}; }"); await page.wait_for_timeout(300)
        lab = await page.inner_text('#act'); check('走近面罩：互動鈕「練習人工呼吸」', lab == '練習人工呼吸', lab)
        await act(page); await page.wait_for_selector('#dBtns button')
        first = await page.inner_text('#dText'); check('開場：面罩，可選「先離開」', 'CPR 面罩' in first and await page.locator('#dBtns button').count() == 2, first)
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(500)
        check('選先離開：沒有第 3 節知識卡', await st(page, "Object.keys(S.cards).filter(k => k.startsWith('ch3_k3')).length") == 0)
        await act(page); await page.wait_for_selector('#dBtns button')
        t1 = '\n'.join(await answer_until(page, '#bh'))
        for key in ['ch3_q3_1', 'ch3_q3_2']: check(f'{key} 題目出現', QZ[key]['q'] in t1)
        check('K3-1 獲得', await st(page, "S.cards.ch3_k3_1 === true"))
        await page.wait_for_selector('#bh')
        check('吹氣遊戲畫面：壓額抬下巴、吹氣、回到壓胸、結束', all([await page.locator(s).count() for s in ['#ba', '#bh', '#bd', '#be', '#bf']]))
        check('還沒壓額抬下巴：不能吹氣、回到壓胸不能按', await page.locator('#bh').is_disabled() and await page.locator('#bd').is_disabled())
        await page.locator('#ba').click(); await page.wait_for_timeout(150)
        check('壓額抬下巴後：可以吹氣', not await page.locator('#bh').is_disabled())
        await hold(page, 250); m = await page.inner_text('#bm'); check('吹太短：顯示「吹得太少」並可再試', '吹得太少' in m and '再試一次' in m, m)
        await hold(page, 2400); m = await page.inner_text('#bm'); check('吹太久：顯示「吹太多了」', '吹太多了' in m, m)
        check('兩次失敗都不算：回到壓胸仍不能按', await page.locator('#bd').is_disabled())
        await hold(page, 1000); m = await page.inner_text('#bm'); check('吹 1 秒左右（落在綠色範圍）：胸部明顯起伏（1/2）', '明顯起伏' in m and '1/2' in m, m)
        await hold(page, 1000); m = await page.inner_text('#bm'); check('第 2 次吹好：提示吹完立刻回到壓胸', '2 次都吹好了' in m and '立刻回到壓胸' in m, m)
        check('2 次吹好後：回到壓胸可按、吹氣鈕鎖住', not await page.locator('#bd').is_disabled() and await page.locator('#bh').is_disabled())
        await page.locator('#bd').click(); await page.wait_for_timeout(500)
        t2 = await page.inner_text('#dText')
        att = await page.evaluate("() => window.__ch3Breath")
        check('記錄：4 次吹氣（低、高、好、好）', att and [a['band'] for a in att['attempts']] == ['low', 'high', 'ok', 'ok'] and att['good'] == 2, str(att))
        check('結尾：人工呼吸練習完成', '人工呼吸練習完成' in t2 and '一共吹了 4 次' in t2, t2)
        await page.locator('#dBtns button:not([disabled])').nth(0).click(); await page.wait_for_timeout(500)   # 關掉結尾對話
        # --- AED
        await page.evaluate("() => { const S = window.__fa.S; S.pos = {x: 1192, y: 512}; }"); await page.wait_for_timeout(300)
        lab = await page.inner_text('#act'); check('走近 AED：互動鈕「練習 AED」', lab == '練習 AED', lab)
        coins = await st(page, 'S.coins')
        await act(page); await page.wait_for_selector('#dBtns button')
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(500)
        check('AED 選先離開：沒有 K3-2、K3-3', await st(page, "!S.cards.ch3_k3_2 && !S.cards.ch3_k3_3"))
        await act(page); await page.wait_for_selector('#dBtns button')
        t3 = '\n'.join(await answer_until(page, '#av'))
        for key in ['ch3_q3_3', 'ch3_q3_4', 'ch3_q3_5']: check(f'{key} 題目出現', QZ[key]['q'] in t3)
        check('K3-2、K3-3 獲得', await st(page, "S.cards.ch3_k3_2 && S.cards.ch3_k3_3"))
        await page.wait_for_selector('#av')
        v0 = await page.inner_text('#av'); check('AED 畫面：第 1 步、有 AED 圖與語音', '（AED 還沒開機）' in v0 and await page.locator('img[alt=AED]').count() == 1 and '第 1 步，共 5 步' in await page.inner_text('#as'), v0)
        msgs = []
        for i in range(5):
            await page.locator('#ab button[data-right="0"]').click(); await page.wait_for_timeout(100)
            msgs.append(await page.inner_text('#am'))
            await page.locator('#ab button[data-right="1"]').click(); await page.wait_for_timeout(150 if i < 4 else 700)
        check('每一步先選錯：顯示「這個做法不對」與說明', all('這個做法不對' in m for m in msgs) and '會干擾判讀' in msgs[2] and '大家離開' in msgs[3] and '立刻續做 CPR' in msgs[4], str(msgs))
        errs_aed = await page.evaluate("() => window.__ch3Aed && window.__ch3Aed.errors")
        check('記錄：5 次錯誤示範，代碼 null、E2、E5、E5、E4', errs_aed and [e['code'] for e in errs_aed] == [None, 'E2', 'E5', 'E5', 'E4'], str(errs_aed))
        t4 = await page.inner_text('#dText'); check('AED 練習完成，說明選過 5 次錯誤做法', 'AED 練習完成' in t4 and '5 次錯誤' in t4, t4)
        t5 = '\n'.join(await answer_until(page, '#nothing'))
        for key in ['ch3_q3_6', 'ch3_q3_7']: check(f'{key} 題目出現', QZ[key]['q'] in t5)
        check('排序題 Q3-8 出現', '[排序]' in t5 or '順序完全正確' in t5)
        check('第 3 節完成、三張知識卡都獲得', '第 3 節完成' in t5 and await st(page, "['ch3_k3_1','ch3_k3_2','ch3_k3_3'].every(k => S.cards[k])"))
        check('E2／E4／E5 本階段只標記：金幣不變、仍在救生站', await st(page, 'S.coins') == coins and await st(page, 'S.scene') == 'ch3_rescue')
        # --- 全部選對一次：沒有錯誤
        await act(page); await page.wait_for_selector('#dBtns button'); await answer_until(page, '#av')
        for i in range(5):
            await page.locator('#ab button[data-right="1"]').click(); await page.wait_for_timeout(150 if i < 4 else 700)
        t6 = await page.inner_text('#dText'); check('全部選對：顯示「每一步都選對了」', '每一步都選對了' in t6, t6)
        check('第 3 節測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章第 3 節測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
