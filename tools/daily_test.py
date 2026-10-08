"""每日任務與累計簽到（老師 2026-10-08 決定，完成第三章後開啟）：三項每日任務（聊天、事件或傷口、複習知識卡）、完成給獎勵、隔天重置、累計簽到（中斷不歸零）、里程碑獎勵與稱號、介面。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/daily_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
D = json.load(open(ROOT / 'content/balance.json', encoding='utf-8'))['DAILY']
MS = {m['days']: m for m in D['milestones']}
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 0; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        ev = lambda e, a=None: page.evaluate(e, a) if a is not None else page.evaluate(e)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def pump(n=30, quizzes=None):
            out = []
            for _ in range(n):
                if await ev("() => document.getElementById('dialog').hidden"):
                    await page.wait_for_timeout(350)
                    if await ev("() => document.getElementById('dialog').hidden"): return out
                    continue
                txt = await page.inner_text('#dText'); out.append(txt)
                btns = page.locator('#dBtns button:not([disabled])')
                pick = 0
                for q in (quizzes or []):
                    if q['q'] in txt and await btns.count() == len(q['opts']): pick = q['ans']
                if await btns.count(): await btns.nth(pick).click()
                await page.wait_for_timeout(120)
            return out
        async def rand(seq): await ev("(q) => { window.__rq = q.slice(); Math.random = () => (window.__rq.length ? window.__rq.shift() : 0.5); }", seq)
        # ---------- 完成第三章前：全部不適用 ----------
        check('完成第三章前：每日任務按鈕不出現', await ev("() => document.getElementById('btnDaily').hidden"))
        check('完成第三章前：記任務、簽到都不適用（不記錄）', await ev("async () => { const a = await window.__fa.dailyDone('chat'), b = await window.__fa.dailyCheck(); return a === false && b === false; }") and await st("!S.c.daily"))
        await ev("() => { window.__fa.S.c.ch3_done = true; window.__fa.refresh(); }")
        check('完成第三章後：出現「每日 0/3」按鈕', await ev("() => { const e = document.getElementById('btnDaily'); return !e.hidden && e.textContent.replace(/\\s/g, '') === '每日0/3'; }"), await ev("() => document.getElementById('btnDaily').textContent"))
        # ---------- 每日任務 ----------
        await ev("() => { window.__fa.dailyDone('chat'); }"); await page.wait_for_timeout(300)
        check('完成「聊聊天」：1/3，不會重複計算', await st('S.c.daily.done.chat') is True and await ev("() => document.getElementById('dailyInfo').textContent") == '1/3')
        check('同一項再完成：沒有任何變化', await ev("async () => (await window.__fa.dailyDone('chat')) === false"))
        check('不存在的任務編號：沒反應', await ev("async () => (await window.__fa.dailyDone('nope')) === false"))
        c0 = await st('S.coins'); await rand([0.9, 0.0])   # 0.9 > itemChance(0.3)：不給道具
        await ev("() => { window.__fa.dailyDone('care'); window.__fa.dailyDone('review'); }"); t = await pump()
        check('三項都完成：領 %d 金幣（沒抽到道具）、顯示「每日任務全部完成」' % D['reward']['coins'], await st('S.coins') == c0 + D['reward']['coins'] and any('全部完成' in x for x in t) and await st('S.c.daily.claimed') is True and not await st('S.c.inv && Object.keys(S.c.inv).length'), f"{await st('S.coins')} {t}")
        c1 = await st('S.coins'); await ev("() => { window.__fa.dailyDone('chat'); }"); await page.wait_for_timeout(300)
        check('同一天已經領過：不會再領', await st('S.coins') == c1)
        # 幸運：抽到小道具（itemChance 以內）
        await ev("() => { const d = window.__fa.S.c.daily; d.done = {}; d.claimed = false; }")
        await rand([0.1, 0.1, 0.0]); c2 = await st('S.coins')
        await ev("() => { window.__fa.dailyDone('chat'); window.__fa.dailyDone('care'); window.__fa.dailyDone('review'); }"); t = await pump()
        check('有機率額外得到一個小道具（這次抽到：提神小點心）', await st('S.coins') == c2 + D['reward']['coins'] and await st('S.c.inv.snack') == 1 and any('還額外得到' in x for x in t), str(t))
        # 隔天重置
        await ev("() => { window.__fa.S.c.daily.date = '2000-01-01'; }"); await ev("() => { window.__fa.dailyState(); window.__fa.refresh(); }")
        check('隔天（現實日期變了）：任務重新開始（0/3）、可以再領', await st('!S.c.daily.done.chat') and await st('S.c.daily.claimed') is False and await ev("() => document.getElementById('dailyInfo').textContent") == '0/3')
        # ---------- 掛接：真的聊天、複習、事件會算 ----------
        await ev("() => { window.__fa.S.c.daily.done = {}; window.__fa.S.c.daily.claimed = false; window.__fa.S.c.chat = null; }")
        await rand([0.05, 0.0]); await ev("() => { window.__fa.chatLuck('kid'); }"); await pump()
        check('真的跟 NPC 聊天（抽運氣）：算完成「聊聊天」', await st('S.c.daily.done.chat') is True)
        await ev("() => { window.__fa.chatLuck('kid'); }"); await pump()   # 今天聊過了：回傳 done，不應再計
        await ev("() => { window.__fa.S.c.daily.done = {}; }")
        await ev("() => { window.__fa.chatLuck('kid'); }"); await pump()
        check('同一位角色當天聊過了：不再算任務（done 狀態沒有被重新標記）', await st('!S.c.daily.done.chat'))
        await ev("() => { window.__fa.S.c.daily.done = {}; }")
        await page.click('#btnCards'); await page.wait_for_selector('#dBtns button'); await page.locator('#dBtns button').last.click(); await page.wait_for_timeout(400); await pump()
        check('打開知識卡並關閉：算完成「複習知識卡」', await st('S.c.daily.done.review') is True)
        e = await ev("() => { const E = window.__fa.EVENTS[0]; return {id: E.id, who: E.who, needs: E.needs, qs: E.qs.map(q => ({q: q.q, opts: q.opts, ans: q.ans}))}; }")
        kit = [k for k, n in e['needs'].items() for _ in range(n)]
        await ev("([e, kit]) => { const S = window.__fa.S; S.kit = kit; S.event = {id: e.id, day: S.day}; window.__fa.doEvent(window.__fa.EVENTS.find(x => x.id === e.id)); }", [e, kit]); await pump(60, e['qs'])
        check('處理一次小意外事件：算完成「處理一次事件或傷口」', await st('S.c.daily.done.care') is True and await st('S.event.done') is True, str(await st('S.c.daily')))
        # ---------- 累計簽到 ----------
        await ev("() => { const d = window.__fa.S.c.daily; d.days = 0; d.last = null; d.got = {}; d.title = null; d.titles = []; d.done = {}; window.__fa.S.coins = 0; window.__fa.S.c.inv = {}; }")
        await ev("() => { window.__fa.dailyCheck(); }"); await pump()
        check('第一次簽到：累計第 1 天（只有提示，不跳視窗）、記下今天', await st('S.c.daily.days') == 1 and await st('S.c.daily.last') is not None)
        check('同一天再簽：不重複算', await ev("async () => (await window.__fa.dailyCheck()) === false") and await st('S.c.daily.days') == 1)
        await ev("() => { const d = window.__fa.S.c.daily; d.days = 2; d.last = '2000-01-01'; }")
        await ev("() => { window.__fa.dailyCheck(); }"); t = await pump()
        m = MS[3]
        check('累計第 3 天：領 %d 金幣與幸運符、顯示簽到視窗' % m['coins'], await st('S.c.daily.days') == 3 and await st('S.coins') == m['coins'] and await st('S.c.inv.charm') == 1 and any('累計登入第 3 天' in x for x in t), str((await st('S.coins'), t)))
        await ev("() => { const d = window.__fa.S.c.daily; d.days = 6; d.last = '2000-01-01'; }")
        await ev("() => { window.__fa.dailyCheck(); }"); t = await pump(); m = MS[7]
        check('累計第 7 天：領金幣、雙重驚喜與稱號「常客」', await st('S.c.daily.title') == '常客' and await st('S.c.inv.double') == m['items']['double'] and any('稱號：「常客」' in x for x in t), str(await st('S.c.daily')))
        await ev("() => { const d = window.__fa.S.c.daily; d.days = 9; d.last = '2000-01-01'; }")   # 中斷幾天：第 10 天，不歸零，也不補發中間的
        await ev("() => { window.__fa.dailyCheck(); }"); await pump()
        check('中間隔了很多天再回來：天數照樣累加（第 10 天）、沒有領錯獎勵', await st('S.c.daily.days') == 10 and await st('S.c.daily.title') == '常客')
        await ev("() => { const d = window.__fa.S.c.daily; d.days = 13; d.last = '2000-01-01'; }"); await ev("() => { window.__fa.dailyCheck(); }"); await pump()
        check('累計第 14 天：稱號改成「老朋友」，已領過的不會再領', await st('S.c.daily.title') == '老朋友' and await st('S.c.daily.titles.length') == 2)
        # 重領防護：把天數調回去
        coins = await st('S.coins'); await ev("() => { const d = window.__fa.S.c.daily; d.days = 2; d.last = '2000-01-01'; }"); await ev("() => { window.__fa.dailyCheck(); }"); await pump()
        check('同一個里程碑（第 3 天）領過一次就不再領', await st('S.coins') == coins)
        await ev("() => { const d = window.__fa.S.c.inv; d.snack = 10; d.boots = 10; d.charm = 10; d.double = 10; const x = window.__fa.S.c.daily; x.days = 29; x.last = '2000-01-01'; }")
        await ev("() => { window.__fa.dailyCheck(); }"); await pump()
        check('里程碑的小道具不受道具欄上限限制（道具欄已滿也領得到）', await st('S.c.inv.double') == 10 + MS[30]['items']['double'] and await st('S.c.daily.title') == '港口之友')
        # ---------- 介面 ----------
        await page.click('#btnDaily'); await page.wait_for_selector('#dText'); t = await page.inner_text('#dText')
        check('每日任務視窗：三項任務、累計登入天數、稱號、「中斷也沒關係」', all(k in t for k in ['跟一位 NPC 聊聊天', '處理一次事件或傷口', '複習知識卡', '累計登入', '30', '港口之友', '累計登入的獎勵都領完了']), t[:400])
        await page.locator('#dBtns button').last.click(); await page.wait_for_timeout(300)
        await page.click('#btnBag'); await page.wait_for_selector('#dText'); tb = await page.inner_text('#dText')
        check('背包顯示稱號「港口之友」', '稱號：「港口之友」' in tb, tb[:200]); await page.locator('#dBtns button').last.click(); await page.wait_for_timeout(300)
        # ---------- 存檔結構 ----------
        check('全部記在既有的 S.c.daily，沒有新增頂層存檔欄位', await ev("() => !('daily' in window.__fa.S)") and await st("typeof S.c.daily === 'object'"))
        check('每日任務測試沒有頁面錯誤', not errs, str(errs)); await page.close()
        # ---------- 真實路徑：進遊戲時簽到、遊戲開著跨日自動簽到 ----------
        async def boot(c3, daily):
            pg = await ctx.new_page(); e2 = []; pg.on('pageerror', lambda e: e2.append(str(e)))
            await pg.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
            await pg.goto(url + '#debug'); await pg.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
            await pg.evaluate("([c3, d]) => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 0; S.day = 5; if (c3) S.c.ch3_done = true; if (d) S.c.daily = d; document.getElementById('btnStart').click(); }", [c3, daily])
            return pg, e2
        pg, e2 = await boot(True, {'days': 2, 'last': '2000-01-01', 'date': '2000-01-01', 'done': {}, 'claimed': False, 'got': {}, 'title': None, 'titles': []})
        await pg.wait_for_selector('#dText', timeout=8000); txt = await pg.inner_text('#dText')
        check('按「開始／繼續冒險」進遊戲：自動累計簽到，第 3 天跳出簽到視窗', '累計登入第 3 天' in txt, txt)
        await pg.locator('#dBtns button').nth(0).click(); await pg.wait_for_timeout(400)
        check('進遊戲簽到後：天數記下、獎勵入帳', await pg.evaluate("() => window.__fa.S.c.daily.days") == 3 and await pg.evaluate("() => window.__fa.S.coins") == MS[3]['coins'])
        await pg.close()
        pg, e3 = await boot(False, None); await pg.wait_for_timeout(800)
        check('還沒完成第三章：進遊戲不簽到', await pg.evaluate("() => !window.__fa.S.c.daily") and not await pg.evaluate("() => !!document.getElementById('dialog') && !document.getElementById('dialog').hidden"))
        await pg.close()
        pg, e4 = await boot(True, {'days': 3, 'last': __import__('datetime').date.today().isoformat(), 'date': __import__('datetime').date.today().isoformat(), 'done': {}, 'claimed': False, 'got': {'3': True}, 'title': None, 'titles': []})
        await pg.wait_for_timeout(800)
        check('今天已經簽到過：再進遊戲不會多算一天', await pg.evaluate("() => window.__fa.S.c.daily.days") == 3)
        await pg.evaluate("() => { const d = window.__fa.S.c.daily; d.last = '2000-01-01'; }")   # 遊戲開著時過了午夜
        await pg.wait_for_function("() => window.__fa.S.c.daily.days === 4", timeout=15000)
        check('遊戲開著跨日：自動算新的一天（第 4 天，不是里程碑所以不跳視窗）', await pg.evaluate("() => window.__fa.S.c.daily.days") == 4 and await pg.evaluate("() => document.getElementById('dialog').hidden"))
        check('跨日路徑沒有頁面錯誤', not (e2 or e3 or e4), str((e2, e3, e4)))
        await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('每日任務測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
