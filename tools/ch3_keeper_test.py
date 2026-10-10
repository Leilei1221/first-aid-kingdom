"""燈塔管理員（老師 2026-10-10 生圖）：燈塔場景的 NPC；依港口信譽與今晚求助有沒有處理說三種話，說完抽聊天運氣。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_keeper_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
npc = next(n for n in json.load(open(ROOT / 'chapters/ch3/scenes.json', encoding='utf-8'))['ch3_lighthouse']['npcs'] if n['id'] == 'ch3_keeper')
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.c.ch3_done = true; S.started = true; S.coins = 100; S.sta = 100; S.day = 6; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(600)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def talk():
            await page.evaluate("() => { window.__fa.go('ch3_lighthouse', [1100, 600]); }"); await page.wait_for_timeout(1000)
            await page.evaluate("([x, y]) => { window.__fa.S.pos = {x, y}; }", [npc['x'], npc['y'] + 50]); await page.wait_for_timeout(450)
            act = await page.inner_text('#act'); await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(450)
            out = []
            for _ in range(8):
                if await page.evaluate("() => document.getElementById('dialog').hidden"): break
                out.append(await page.inner_text('#dText')); await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(250)
            return act, '\n'.join(out)
        # 今天的聊天運氣先標成抽過（運氣由 chat_luck_test 驗證）
        await page.evaluate("() => { const d = new Date(), t = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); window.__fa.S.c.chat = {date: t, done: {ch3_keeper: true}}; }")
        await page.evaluate("() => { window.__fa.S.c.ch3_hb = {rep: 0, done: 0, n: 0}; }")
        act, t = await talk()
        check('燈塔有管理員：走近出現「對話」', '對話' in act, act)
        check('第一次見面：爬上來累了吧；信譽不夠：這座燈塔從我爺爺那代就點著', '爬上來累了吧' in t and '爺爺那代就點著' in t and '夜裡風大' in t, t)
        await page.evaluate("() => { window.__fa.S.c.ch3_hb = {rep: 3, done: 0, n: 3}; }")
        act, t = await talk()
        check('信譽 3、今晚還有求助：港口的人都說你可靠、長椅那邊有人等你（不再說第一次的話）', '爬上來累了吧' not in t and '都說你可靠' in t and '長椅那邊會有人等你' in t, t)
        await page.evaluate("() => { window.__fa.S.c.ch3_hb = {rep: 3, done: 0, n: 3, lh: {done: window.__fa.S.day, n: 1}}; }")
        act, t = await talk()
        check('今晚求助處理完：辛苦了，燈亮著，大家就安心', '辛苦了' in t and '燈亮著' in t, t)
        # 聊天運氣：沒抽過時會抽一次（用現有知識卡）
        await page.evaluate("() => { window.__fa.S.c.chat = {date: '2000-01-01', done: {}}; }")
        topics = json.load(open(ROOT / 'content/balance.json', encoding='utf-8'))['CHAT_TOPICS']['ch3_keeper']
        check('聊天話題用現有知識卡：颱風來時、山洪暴發的徵兆、預防失溫', topics == ['typhoon', 'flood', 'hypothermia'], str(topics))
        act, t = await talk()
        check('說完對白後抽一次聊天運氣（記成今天抽過）', await st("S.c.chat && S.c.chat.done && S.c.chat.done.ch3_keeper === true"), str(await st('JSON.stringify(S.c.chat)')))
        check('燈塔日誌（挪到 1120,560）不會擋到管理員', abs(1120 - npc['x']) > 150)
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
