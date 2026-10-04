"""第三章「目標」提示與各節結尾的指路：依做到哪一節，畫面上方的目標會告訴玩家下一步去哪。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_goal_test.py http://localhost:8765/index.html`"""
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
        page, errs = await boot(ctx, url)
        async def goal(scene, x, y, cards):
            await page.evaluate("(c) => { const S = window.__fa.S; Object.keys(S.cards).filter(k => k.startsWith('ch3_')).forEach(k => delete S.cards[k]); c.forEach(k => S.cards[k] = true); }", cards)
            await goto(page, scene, x, y); await page.wait_for_timeout(500)
            return await page.inner_text('#goal')
        g = await goal('ch3_harbor', 820, 640, [])
        check('一開始：目標是到港口市集查看倒地的人（第 1 節）', '市集' in g and '第 1 節' in g, g)
        g = await goal('ch3_market', 830, 800, ['ch3_k1_1', 'ch3_k1_2'])
        check('第 1 節還沒做完（只有前兩張卡）：目標仍是第 1 節', '第 1 節' in g, g)
        g = await goal('ch3_harbor', 820, 640, ['ch3_k1_3'])
        check('做完第 1 節：目標是到救生站練習按壓（第 2 節）', '救生站' in g and '按壓' in g and '第 2 節' in g, g)
        g = await goal('ch3_rescue', 760, 840, ['ch3_k1_3', 'ch3_k2_3'])
        check('做完第 2 節：目標是面罩練習人工呼吸（第 3 節）', '面罩' in g and '人工呼吸' in g, g)
        g = await goal('ch3_rescue', 760, 840, ['ch3_k1_3', 'ch3_k2_3', 'ch3_k3_1'])
        check('人工呼吸做過：目標是牆邊的 AED', 'AED' in g and '第 3 節' in g, g)
        g = await goal('ch3_harbor', 820, 640, ['ch3_k1_3', 'ch3_k2_3', 'ch3_k3_1', 'ch3_k3_3'])
        check('第 3 節都做完：目標是到港口找救生員（第 4 節）', '救生員' in g and '第 4 節' in g, g)
        g = await goal('ch3_harbor', 820, 640, ['ch3_k1_3', 'ch3_k2_3', 'ch3_k3_1', 'ch3_k3_3', 'ch3_k4_4'])
        check('第 4 節做完：目標是回市集進行章末演練', '章末' in g and '市集' in g, g)
        await page.evaluate("() => { const S = window.__fa.S; S.c.ch3_done = true; S.c.ch3_stars = 4; }")
        await page.evaluate("() => window.__fa.refresh()"); await page.wait_for_timeout(300); g = await page.inner_text('#goal')
        check('章末做完：目標是第三章完成、顯示最高星數', '第三章完成' in g and '4' in g and '心跳之匣' in g, g)
        await page.evaluate("() => { const S = window.__fa.S; delete S.c.ch3_done; delete S.c.ch3_stars; }")
        await page.evaluate("() => { window.__fa.S.voyage = {to: 'ch3_harbor', left: 2}; }")
        g = await goal('ch3_ship_day', 800, 660, [])
        check('在船上：目標是到艙口睡覺過夜', '艙口' in g and '睡覺' in g, g)
        await page.evaluate("() => { window.__fa.S.voyage = null; }")
        g = await goal('village', 1000, 700, [])
        check('回到序章地圖：不受第三章目標影響（不是第三章的字）', '第 1 節' not in g and '救生站' not in g, g)
        # 各節結尾有指路
        t = open(pathlib.Path(__file__).parent.parent / 'chapters/ch3/chapter.js', encoding='utf-8').read()
        check('第 1 節結尾：指路到救生站', '接下來到港口的救生站，練習壓胸（第 2 節）、人工呼吸與 AED（第 3 節）' in t)
        check('第 2 節結尾：指路到面罩與牆邊 AED', '下一步：在救生站，假人旁的面罩練習人工呼吸、牆邊練習 AED（第 3 節）' in t)
        check('各節結尾都不再寫「之後才會開放」', '之後才會開放' not in t)
        check('第 3 節結尾：指路到港口找救生員', '下一步：到港口找救生員（第 4 節）' in t)
        check('目標測試沒有頁面錯誤', not errs, str(errs))
        await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第三章目標提示測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
