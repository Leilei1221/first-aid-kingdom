"""第三章第 2 節（胸部按壓與換手）：節拍與統計計算（rhythm.js）、救生站假人互動、8 題、3 張知識卡、按壓遊戲（換手、紀錄）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_lesson2_test.py http://localhost:8765/index.html`"""
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
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url)
        # --- rhythm.js 的計算
        r = await page.evaluate("""async () => {
          const R = await import('/chapters/ch3/rhythm.js');
          const even = n => Array.from({length: n}, (_, i) => i * 545);                 // 110 下／分
          const a = R.stats(even(21));
          const gap = even(10).concat(even(10).map(t => t + 9 * 545 + 4000));             // 中間停 4 秒（算一次中斷）
          const b = R.stats(gap);
          return {rate: R.recentRate(even(8)), band: [R.rateBand(90), R.rateBand(110), R.rateBand(130), R.rateBand(null)], a, b, few: R.stats([0])};
        }""")
        check('recentRate：每 545 毫秒一下 ≈ 110 下／分', abs(r['rate'] - 110) <= 1, str(r['rate']))
        check('rateBand：90 太慢、110 剛好、130 太快、資料不足為空', r['band'] == ['slow', 'ok', 'fast', None], str(r['band']))
        check('stats 規律按壓：沒有中斷、占比 100%', r['a']['pauses'] == [] and r['a']['ratio'] == 1 and r['a']['longestPauseMs'] == 0, str(r['a']))
        check('stats 中間停 4 秒：一次中斷、最長 4 秒多、占比低於 100%', len(r['b']['pauses']) == 1 and 4000 <= r['b']['longestPauseMs'] < 4600 and 0 < r['b']['ratio'] < 1, str(r['b']))
        check('stats 不到 2 下：占比為空', r['few']['ratio'] is None and r['few']['n'] == 1, str(r['few']))
        # --- 救生站
        await goto(page, 'ch3_rescue', 760, 840)
        check('救生站有假人圖', await page.evaluate("() => !!document.querySelector('img[src*=\"ch3_cpr_manikin\"]')"))
        await page.evaluate("() => { window.__fa.S.pos = {x: 1110, y: 690}; }"); await page.wait_for_timeout(300)
        lab = await page.inner_text('#act'); check('走近假人：互動鈕「練習按壓」', lab == '練習按壓', lab)
        await page.evaluate("() => { window.__ch3Tune = {fatigueSec: 2, afterSwap: 4, pauseGapMs: 1500}; }")
        await act(page); await page.wait_for_selector('#dBtns button')
        first = await page.inner_text('#dText'); check('開場：有假人，可選「先離開」', '練習假人' in first and await page.locator('#dBtns button').count() == 2, first)
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(500)
        check('選先離開：沒有第 2 節知識卡', await st(page, "Object.keys(S.cards).filter(k => k.startsWith('ch3_k2')).length") == 0)
        await act(page); await page.wait_for_selector('#dBtns button')
        t1 = '\n'.join(await answer_until(page, '#rp'))
        for key in ['ch3_q2_1', 'ch3_q2_3', 'ch3_q2_4', 'ch3_q2_2', 'ch3_q2_5']: check(f'{key} 題目出現', QZ[key]['q'] in t1)
        check('K2-1、K2-2 獲得', await st(page, "['ch3_k2_1','ch3_k2_2'].every(k => S.cards[k])") and not await st(page, "S.cards.ch3_k2_3"))
        # 提示畫面「開始」→ 遊戲畫面
        await page.wait_for_selector('#rp', timeout=8000) if await page.locator('#rp').count() == 0 else None
        check('按壓遊戲畫面：壓鈕、節拍燈、疲勞條、換手鈕', all([await page.locator(s).count() for s in ['#rp', '#rb', '#rf', '#rs', '#re']]))
        check('一開始換手鈕不能按', await page.locator('#rs').is_disabled())
        # 以約 545 毫秒一下按壓；疲勞滿了就換手；換手後再壓 4 下自動結束
        out = await page.evaluate("""async () => {
          const rp = document.getElementById('rp'), rs = document.getElementById('rs'), seen = {slowFast: new Set()};
          const tap = () => rp.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true}));
          const sleep = ms => new Promise(r => setTimeout(r, ms));
          let swapAt = null;
          for (let i = 0; i < 40 && document.getElementById('rp'); i++) {
            tap(); seen.slowFast.add(document.getElementById('rr') && document.getElementById('rr').textContent);
            if (swapAt === null && !rs.disabled) { rs.click(); swapAt = i; await sleep(2200); }   // 換手時停了約 2 秒
            await sleep(545);
          }
          return {swapAt, rates: [...seen.slowFast]};
        }""")
        check('疲勞滿後換手鈕可按、已換手', out['swapAt'] is not None, str(out))
        check('節拍約 110 下／分時顯示「剛好」', any('剛好' in (x or '') for x in out['rates']), str(out['rates']))
        await page.wait_for_timeout(600)
        t2 = await page.inner_text('#dText')
        check('遊戲結束後顯示練習紀錄（下數、平均速率、最長中斷、占比）', all(k in t2 for k in ['練習紀錄', '平均', '最長一次中斷', '按壓時間占比']), t2)
        last = await page.evaluate("() => window.__ch3Last && window.__ch3Last.stats")
        check('記錄：有一次 2 秒以上的換手中斷、占比小於 100%', last and len(last['pauses']) >= 1 and last['longestPauseMs'] >= 1500 and last['ratio'] < 1, str(last))
        check('記錄：平均速率落在 100～120', last and 100 <= last['avgRate'] <= 120, str(last))
        coins = await st(page, 'S.coins')
        t3 = '\n'.join(await answer_until(page, '#nothing'))
        for key in ['ch3_q2_6', 'ch3_q2_7', 'ch3_q2_8']: check(f'{key} 題目出現', QZ[key]['q'] in t3)
        check('第 2 節完成、三張知識卡都獲得', '第 2 節完成' in t3 and await st(page, "['ch3_k2_1','ch3_k2_2','ch3_k2_3'].every(k => S.cards[k])"))
        check('E4／E6 本階段只標記：金幣不變、仍在救生站', await st(page, 'S.coins') == coins and await st(page, 'S.scene') == 'ch3_rescue')
        # --- 提早結束
        await act(page); await page.wait_for_selector('#dBtns button')
        await answer_until(page, '#rp')
        await page.locator('#re').click(); await page.wait_for_timeout(500)
        txt = await page.inner_text('#dText'); check('沒按壓就結束：顯示「沒有按壓紀錄」', '沒有按壓紀錄' in txt, txt)
        check('第 2 節測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章第 2 節測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
