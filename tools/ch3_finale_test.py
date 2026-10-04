"""第三章章末整合演練（4b）：合併數據與星數判定、入口選單、完整流程（判斷→分工→壓胸＋吹氣→AED→續壓換手→結算）、完成狀態與心跳之匣、重玩、中途停止。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_finale_test.py http://localhost:8765/index.html`"""
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
LESSONS = ['ch3_k1_3', 'ch3_k2_3', 'ch3_k3_1', 'ch3_k3_3', 'ch3_k4_4']
async def tune(page, **kw): await page.evaluate("(t) => { window.__ch3Tune = t; }", kw)
async def pick_quiz(page, wrong_first=False, seen=None):
    """目前對話若是題目就作答；回傳是否處理了"""
    txt = await page.inner_text('#dText')
    z = next((v for q, v in ByQ.items() if q in txt), None)
    btns = page.locator('#dBtns button:not([disabled])')
    if z and await btns.count() == len(z['opts']):
        pick = z['ans']
        if wrong_first and z['q'] not in seen:
            seen.add(z['q']); pick = (z['ans'] + 1) % len(z['opts'])
        await btns.nth(pick).click(); return True
    return False
async def until(page, selector, wrong_first=False, seen=None, max_steps=80):
    """按「繼續」、答題，直到出現 selector"""
    seen = seen if seen is not None else set()
    for _ in range(max_steps):
        if await page.locator(selector).count(): return True
        if await hidden(page): await page.wait_for_timeout(300); continue
        if not await pick_quiz(page, wrong_first, seen):
            btns = page.locator('#dBtns button:not([disabled])')
            if await btns.count(): await btns.nth(0).click()
        await page.wait_for_timeout(150)
    return False
async def taps(page, n, gap=545):
    await page.evaluate("async ([n, gap]) => { const rp = document.getElementById('rp'); for (let i = 0; i < n; i++) { rp.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true})); await new Promise(r => setTimeout(r, gap)); } }", [n, gap])
async def hold(page, ms):
    await page.evaluate("async (ms) => { const h = document.getElementById('bh'); h.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true})); await new Promise(r => setTimeout(r, ms)); h.dispatchEvent(new PointerEvent('pointerup', {bubbles: true})); }", ms)
    await page.wait_for_timeout(150)
async def run_finale(page, good=True, stop_at=None, slow_gap=0):
    """從市集倒地者開始，走完章末演練（good＝全部做對；good=False 時每題先答錯、吹氣不先開呼吸道、AED 每步先選錯）。回傳最後的文字"""
    seen = set()
    await page.evaluate("() => { window.__fa.S.pos = {x: 790, y: 650}; }"); await page.wait_for_timeout(300)
    await act(page); await page.wait_for_selector('#dBtns button')
    await page.locator('#dBtns button', has_text='章末演練').click(); await page.wait_for_timeout(300)
    await page.locator('#dBtns button', has_text='開始').click(); await page.wait_for_timeout(300)
    await until(page, '#dBtns button:has-text("紅衣路人")', not good, seen)
    for _ in range(4):                       # 指派 119 → 路人點頭 → 指派 AED（剩兩人）→ 路人點頭
        await page.wait_for_selector('#dBtns button'); await page.locator('#dBtns button').nth(0).click(); await page.wait_for_timeout(300)
    await page.wait_for_selector('#rp', timeout=8000)
    if stop_at == 'A':
        await taps(page, 2); await page.locator('#re').click(); await page.wait_for_timeout(500)
    else:
        if slow_gap: await taps(page, 1); await page.wait_for_timeout(slow_gap); await taps(page, 3)
        else: await taps(page, 4)
        await page.wait_for_selector('#bh', timeout=8000)
        if not good: await hold(page, 1000)                  # 沒先開呼吸道就吹：這次不算
        await page.locator('#ba').click(); await page.wait_for_timeout(150)
        await hold(page, 1000); await hold(page, 1000)
        await page.wait_for_function("() => !document.getElementById('bd').disabled", timeout=8000); await page.locator('#bd').click(); await page.wait_for_timeout(300)
        await page.wait_for_selector('#rp', timeout=8000); await taps(page, 4)
        await until(page, '#av', not good, seen)           # AED 送到、D-2
        for i in range(5):
            if not good: await page.locator('#ab button[data-right="0"]').click(); await page.wait_for_timeout(100)
            await page.locator('#ab button[data-right="1"]').click(); await page.wait_for_timeout(150 if i < 4 else 700)
        await page.wait_for_selector('#rp', timeout=8000)
        swapped = False
        for _ in range(40):
            if not await page.locator('#rp').count(): break
            if not swapped and not await page.locator('#rs').is_disabled(): await page.locator('#rs').click(); swapped = True
            await taps(page, 1)
    await page.wait_for_selector('text=章末演練結果', timeout=15000) if False else None
    for _ in range(40):
        t = await page.inner_text('#dText') if not await hidden(page) else ''
        if '演練完成' in t or '中途停止' in t: return t
        btns = page.locator('#dBtns button:not([disabled])')
        if await btns.count(): await btns.nth(0).click()
        await page.wait_for_timeout(200)
    return ''
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url)
        # --- 純計算
        r = await page.evaluate("""async () => {
          const R = await import('/chapters/ch3/rhythm.js');
          const even = (n, t0 = 0) => Array.from({length: n}, (_, i) => t0 + i * 545);
          const a = R.stats(even(11)), b = R.stats(even(11).concat(even(11, 10 * 545 + 4000)));
          const c = R.combine([a, a]), d = R.combine([a, b]);
          const good = {judgeWrong: [0, 0, 0], d1Wrong: 0, stats: c, breath: {attempts: [{band: 'ok', noAirway: false}, {band: 'ok', noAirway: false}]}, aedErrors: 0, stopped: false};
          const sc = x => R.scoreFinale(x, 3000);
          return {a: {n: a.n, compTaps: a.compTaps}, c: {n: c.n, ratio: c.ratio, avg: c.avgRate, pauses: c.pauses.length}, d: {pauses: d.pauses.length, longest: d.longestPauseMs, ratio: d.ratio},
            empty: R.combine([]).n, all: R.scoreFinale(good).total, noAir: sc({...good, breath: {attempts: [{band: 'ok', noAirway: true}, {band: 'ok', noAirway: false}]}}).stars.breathAed,
            pause: sc({...good, stats: d}).stars.quality, pauseOk: R.scoreFinale({...good, stats: d}, 60000).stars.quality, slow: R.scoreFinale({...good, stats: {...c, avgRate: 90}}).stars.quality,
            aed: R.scoreFinale({...good, aedErrors: 1}).stars.breathAed, stop: R.scoreFinale({...good, stopped: true}).stars.keep, j: R.scoreFinale({...good, judgeWrong: [0, 1, 0]}).stars.judge, d1: R.scoreFinale({...good, d1Wrong: 2}).stars.assign,
            none: R.scoreFinale({judgeWrong: [], d1Wrong: null, stats: R.combine([]), breath: null, aedErrors: 1, stopped: true}).total, FIN: R.FINALE};
        }""")
        check('stats 帶 compTaps；combine 兩段相加', r['a']['compTaps'] == 10 and r['c']['n'] == 22 and r['c']['pauses'] == 0 and r['c']['ratio'] == 1 and 108 <= r['c']['avg'] <= 112, str(r))
        check('combine 保留各段的中斷、取最長', r['d']['pauses'] == 1 and 4000 <= r['d']['longest'] < 4600 and r['d']['ratio'] < 1 and r['empty'] == 0, str(r['d']))
        check('章末星數：全部做對＝5 顆', r['all'] == 5, str(r['all']))
        check('星數：沒開呼吸道的吹氣不算、AED 選錯不算、中途停止沒有持續、判斷或分工答錯各自扣星', r['noAir'] is False and r['aed'] is False and r['stop'] is False and r['j'] is False and r['d1'] is False, str(r))
        check('星數：中斷超過門檻就沒有壓胸品質星（門檻放寬就有）、平均速率 90 沒有', r['pause'] is False and r['pauseOk'] is True and r['slow'] is False, str(r))
        check('星數：什麼都沒做＝0 顆', r['none'] == 0, str(r['none']))
        check('老師的課堂規則：單次中斷 10 秒、每輪 30 下', r['FIN']['pauseLimitMs'] == 10000 and r['FIN']['compress'] == 30, str(r['FIN']))
        # --- 入口：沒做完第 1～4 節時，倒地者仍是第 1 節
        await goto(page, 'ch3_market', 830, 800)
        await page.evaluate("() => { window.__fa.S.pos = {x: 790, y: 650}; }"); await page.wait_for_timeout(300)
        await act(page); await page.wait_for_selector('#dBtns button')
        first = await page.inner_text('#dText')
        check('還沒做完第 1～4 節：倒地者是第 1 節（沒有章末演練）', '倒在港口市集' in first and await page.locator('#dBtns button:has-text("章末演練")').count() == 0, first)
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(400)
        # --- 全部做完：入口多一個章末演練選項
        await page.evaluate("(k) => { k.forEach(c => window.__fa.S.cards[c] = true); }", LESSONS)
        await act(page); await page.wait_for_selector('#dBtns button')
        labels = await page.locator('#dBtns button').all_inner_texts()
        check('第 1～4 節都做完：選項「章末演練／複習第 1 節／先離開」', labels == ['章末演練', '複習第 1 節', '先離開'], str(labels))
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(400)
        await act(page); await page.wait_for_selector('#dBtns button')
        await page.locator('#dBtns button', has_text='複習第 1 節').click(); await page.wait_for_timeout(300)
        check('選「複習第 1 節」：回到第 1 節的流程', '上前查看' in await page.inner_text('#dBtns'), await page.inner_text('#dBtns'))
        await page.locator('#dBtns button', has_text='先離開').click(); await page.wait_for_timeout(400)
        # --- 完整流程（全部做對）
        await tune(page, fatigueSec=6, compress=4, afterSwap=3)
        coins = await st(page, 'S.coins')
        t = await run_finale(page, good=True)
        fin = await page.evaluate("() => window.__ch3Finale")
        check('全部做對：演練完成、5/5', '演練完成' in t and '（5/5）' in t, t)
        check('結算：五個面向都 ★、有平均速率、最長中斷、占比', t.count('★') >= 5 and '平均' in t and '最長一次中斷' in t and '按壓時間占比' in t and '做到救護人員接手' in t, t)
        check('記錄：完成、5 顆星、沒有嚴重錯誤記錄', fin and fin['completed'] and fin['score']['total'] == 5 and fin['rec']['errs'] == [], str(fin and (fin['score'], fin['rec']['errs'])))
        check('記錄：兩次吹氣都吹好、AED 沒錯、中斷都在 10 秒內', fin and [a['band'] for a in fin['rec']['breath']['attempts']] == ['ok', 'ok'] and fin['rec']['aedErrors'] == 0 and fin['stats']['longestPauseMs'] <= 10000, str(fin and (fin['rec']['breath'], fin['stats'])))
        await page.locator('#dBtns button:not([disabled])').nth(0).click()           # 結算 → 繼續
        await page.wait_for_function("() => document.getElementById('dText').innerText.includes('心跳之匣')", timeout=8000)
        box = await page.inner_text('#dText'); check('取得神器：心跳之匣（BLS 基礎急救包）、有圖', '獲得神器：心跳之匣' in box and await page.locator('img[alt="心跳之匣"]').count() == 1, box)
        await page.locator('#dBtns button:not([disabled])').nth(0).click(); await page.wait_for_timeout(500)
        c = await st(page, "({done: S.c.ch3_done, stars: S.c.ch3_stars, box: S.c.ch3_box})")
        check('存檔：S.c.ch3_done、ch3_stars＝5、ch3_box', c == {'done': True, 'stars': 5, 'box': True}, str(c))
        check('沒有新增頂層存檔欄位（只有 S.c 裡的 ch3_ 鍵）', await st(page, "Object.keys(S).filter(k => k.toLowerCase().startsWith('c3') || k.startsWith('ch3')).length") == 0)
        check('嚴重錯誤只記錄：金幣不變、仍在市集', await st(page, 'S.coins') == coins and await st(page, 'S.scene') == 'ch3_market')
        await page.wait_for_timeout(400); g = await page.inner_text('#goal')
        check('目標：第三章完成、顯示最高 5 顆星', '第三章完成' in g and '5' in g, g)
        # --- 重玩：每題先答錯、吹氣沒先開呼吸道、AED 先選錯、中途停了一下（超過 2.5 秒的單次中斷）
        await tune(page, fatigueSec=6, compress=4, afterSwap=3, pauseLimitMs=2500)
        t = await run_finale(page, good=False, slow_gap=3000)
        fin = await page.evaluate("() => window.__ch3Finale")
        sc = fin['score']['stars']
        check('重玩（亂做）：判斷、分工、壓胸品質、吹氣與 AED 都沒有星，只剩「持續」', sc == {'judge': False, 'assign': False, 'quality': False, 'breathAed': False, 'keep': True} and fin['score']['total'] == 1, str(fin['score']))
        codes = sorted({e['code'] for e in fin['rec']['errs']})
        check('嚴重錯誤只記錄：E4（中斷超過門檻）、E5、E2 都有記錄', set(codes) <= {'E1', 'E2', 'E4', 'E5', 'E6', 'E7', 'E3'} and 'E4' in codes and 'E5' in codes and 'E2' in codes, str(codes))
        check('重玩：結算顯示 1/5', '（1/5）' in t, t)
        await page.locator('#dBtns button:not([disabled])').nth(0).click(); await page.wait_for_timeout(500)
        c = await st(page, "({done: S.c.ch3_done, stars: S.c.ch3_stars, box: S.c.ch3_box})")
        check('重玩：最高星數仍是 5、不會再給一次心跳之匣', c == {'done': True, 'stars': 5, 'box': True} and await page.locator('img[alt="心跳之匣"]').count() == 0, str(c))
        check('重玩：金幣不變', await st(page, 'S.coins') == coins)
        check('章末測試沒有頁面錯誤', not errs, str(errs))
        await page.close()
        # --- 全新存檔：中途「停止急救」→ 不算完成、沒有心跳之匣
        page, errs = await boot(ctx, url)
        await tune(page, fatigueSec=6, compress=4, afterSwap=3)
        await goto(page, 'ch3_market', 830, 800)
        await page.evaluate("(k) => { k.forEach(c => window.__fa.S.cards[c] = true); }", LESSONS)
        t = await run_finale(page, good=True, stop_at='A')
        fin = await page.evaluate("() => window.__ch3Finale")
        check('停止急救：結算顯示中途停止、持續沒有星', '中途停止' in t and '中途停止了急救' in t and fin['score']['stars']['keep'] is False and fin['completed'] is False, t)
        check('停止急救：記 E6，不算完成、沒有心跳之匣、不扣錢', any(e['code'] == 'E6' for e in fin['rec']['errs']) and await st(page, "!S.c.ch3_done && !S.c.ch3_box && !S.c.ch3_stars") and await st(page, 'S.coins') == 300)
        await page.evaluate("() => window.__fa.refresh()"); await page.wait_for_timeout(300)
        check('停止急救後：目標仍是進行章末演練', '章末' in await page.inner_text('#goal'), await page.inner_text('#goal'))
        check('章末（停止）測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章章末演練測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
