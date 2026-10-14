"""雪嶺「抉擇與求生」擋門（老師 2026-10-14 決定）：最終題目文字審完之前，只有老師預覽（preview.html）和 #debug 看得到；其他人走原本的第四章流程。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/survival_gate_test.py http://localhost:8765/index.html`"""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
Q = json.load(open(ROOT / 'chapters/ch4/dialogues.json'))['quizzes']
CLOUD = "() => { window.FACloud = { checkpoint: () => {}, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }"
FRAG = "S.c.ch3_e3 = { seen: { np: true }, frag: { jp: 1, au: 1, np: 1 }, own: {}, cnt: {}, wear: {} };"
GEAR = "['jacket','hat','pants','gloves','boots'].forEach(k => S.c.ch3_e3.own[k] = 1); S.mat.flint = 2;"
QSTR = '?open=ch2,ch3,ch4&sv=0#debug'
async def boot(ctx, url, setup=''):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + QSTR)
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 5000; S.sta = 100; S.day = 23; S.kitCap = 14; S.c.ch3_done = true; " + FRAG + " S.c.ch4 = { arrived: true, s1: true }; " + setup + " document.getElementById('btnStart').click(); }")
    await page.evaluate(CLOUD); await page.wait_for_timeout(600)
    return page, errs
async def ev(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def goto(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(900)
async def hidden(page): return await page.evaluate("() => document.getElementById('dialog').hidden")
async def btns(page): return await page.locator('#dBtns button').all_inner_texts()
async def text(page): return await page.inner_text('#dText')
async def click(page, t, wait=450):
    await page.locator('#dBtns button:visible, #dText button:visible', has_text=t).first.click(); await page.wait_for_timeout(wait)
def qkey(txt):
    for k, z in Q.items():
        if z['q'][:18] in txt: return k
async def drive(page, mode='right', until=None, limit=120, log=None):
    """依畫面往下走：遇到題目就答（mode right＝全答對；也可傳 dict {題目key: 要選的選項編號}）；其他對話按第一個可按的鈕；until(text) 為真就停。"""
    used = set()
    for _ in range(limit):
        await page.wait_for_timeout(260)
        if await hidden(page):
            await page.wait_for_timeout(900)
            if await hidden(page): return 'hidden'
            continue
        t = await text(page)
        if until and until(t): return t
        bt = await btns(page); k = qkey(t)
        if k and k in Q and any(Q[k]['opts'][0][:6] in b for b in bt):
            if log is not None: log.append(k)
            pick = Q[k]['ans']
            if mode != 'right' and k in mode and k not in used: pick = mode[k]; used.add(k)  # 指定的錯誤選項只選一次，之後答對
            await page.locator('#dBtns button').nth(pick).click(); continue
        en = page.locator('#dBtns button:not([disabled])')
        if await en.count() == 0: continue
        await en.first.click()
    return 'limit'
async def main(url):
    global QSTR
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # ---------- 求生關閉（模擬一般玩家：非預覽、非 #debug 的開關狀態）----------
        QSTR = '?open=ch2,ch3,ch4&sv=0#debug'
        page, errs = await boot(ctx, url)
        await goto(page, 'ch4_village', 880, 620)
        await page.evaluate("() => { window.__fa.S.pos = { x: 400, y: 400 }; }"); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(600)
        await click(page, '出發', 900)
        who = await page.inner_text('#dWho') if not await hidden(page) else ''
        check('關閉時：按「出發」之後沒有「山腳村氣象公告」', '氣象公告' not in who, who)
        await drive(page, 'right', limit=6)
        check('關閉時：不會進到 fc（預報）狀態', await ev(page, "!S.c.ch4.fc"), await ev(page, "JSON.stringify(S.c.ch4.fc)"))
        got = [await ev(page, f"!!S.cards.ch4_k6_{i}") for i in (1, 2, 3, 4)]
        check('關閉時：沒有拿到求生的新知識卡（ch4_k6_1～4）', not any(got), str(got))
        await page.close()
        page, errs = await boot(ctx, url)
        await goto(page, 'ch4_village', 880, 620)
        await page.evaluate("() => { window.__fa.S.pos = { x: 1330, y: 548 }; }"); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(600)
        t = await text(page); bt = await btns(page)
        check('關閉時：裝備攤沒有指南針（文字與按鈕）', '指南針' not in t and not any('指南針' in x for x in bt), str(bt))
        check('關閉時：裝備攤仍有打火石與登山裝備', any('打火石' in x for x in bt) and any('看登山裝備' in x for x in bt), str(bt))
        await page.close()
        page, errs = await boot(ctx, url, "S.c.ch4.s5 = true; " + GEAR)
        await goto(page, 'ch4_lodge', 330, 800)
        await page.evaluate("() => { const g = Object.values(window.__fa.SCENES.ch4_lodge.npcs || {}); }")
        await page.evaluate("() => { window.__fa.talk('ch4_guide_up'); }"); await page.wait_for_timeout(700)
        bt = await btns(page)
        check('關閉時：山屋嚮導選單沒有「求生練習」，章末演練還在', not any('求生練習' in x for x in bt) and any('章末演練' in x for x in bt), str(bt))
        await page.close()
        # ---------- 求生開啟（#debug 預設）----------
        QSTR = '?open=ch2,ch3,ch4#debug'
        page, errs = await boot(ctx, url)
        await goto(page, 'ch4_village', 880, 620)
        await page.evaluate("() => { window.__fa.S.pos = { x: 1330, y: 548 }; }"); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(600)
        check('#debug：裝備攤有指南針（求生開啟）', '指南針' in await text(page))
        await page.close()
        page, errs = await boot(ctx, url)
        await goto(page, 'ch4_village', 880, 620)
        await page.evaluate("() => { window.__fa.S.pos = { x: 400, y: 400 }; }"); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(600)
        await click(page, '出發', 500)
        check('#debug：出發前會看到氣象公告', '氣象公告' in await page.inner_text('#dWho') or '暴風雪' in await text(page) or '第 1 天' in await text(page), await text(page))
        await page.close()
        # ---------- 老師預覽（?preview=）：求生開啟 ----------
        page = await ctx.new_page(); errs2 = []; page.on('pageerror', lambda e: errs2.append(str(e)))
        await page.goto(url + '?preview=ch4_village#debug')
        await page.wait_for_function("window.__fa", timeout=60000); await page.wait_for_timeout(800)
        check('老師預覽：求生程式載入（__ch4Sv 有 plan）', await page.evaluate("() => !!(window.__ch4Sv && window.__ch4Sv.plan)"))
        await page.close()
        check('沒有 JS 錯誤', not errs and not errs2, str(errs) + str(errs2))
        await b.close()
    print('失敗', fails)
    sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
