"""友誼回饋（老師 2026-10-08 決定，完成第三章後開啟）：雜貨店老闆好感度折扣、聊天抽運氣、道具欄、疾風草鞋與幸運符。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/chat_luck_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
BAL = json.load(open(ROOT / 'content/balance.json', encoding='utf-8'))
CL, VIP = BAL['CHAT_LUCK'], BAL['VIP']
SEED = json.load(open(ROOT / 'content/items.json', encoding='utf-8'))['MATS']['seed']['buy']
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 1000; S.sta = 50; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        ev = lambda e, a=None: page.evaluate(e, a) if a is not None else page.evaluate(e)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def pump(n=25):
            """一路按第一個按鈕，直到對話結束；回傳看過的文字"""
            out = []
            for _ in range(n):
                if await ev("() => document.getElementById('dialog').hidden"):
                    await page.wait_for_timeout(350)
                    if await ev("() => document.getElementById('dialog').hidden"): return out
                    continue
                out.append(await page.inner_text('#dText'))
                btns = page.locator('#dBtns button:not([disabled])')
                if await btns.count(): await btns.nth(0).click()
                await page.wait_for_timeout(120)
            return out
        async def rand(seq): await ev("(q) => { window.__rq = q.slice(); Math.random = () => (window.__rq.length ? window.__rq.shift() : 0.5); }", seq)
        async def luck(npc, seq):
            await rand(seq); await ev("(id) => { window.__lr = null; window.__fa.chatLuck(id).then(r => { window.__lr = r; }); }", npc)
            texts = await pump(); return texts, await ev("() => window.__lr")
        # ---------- 開啟條件 ----------
        check('完成第三章前：聊天運氣不適用（回傳 off）、不扣機會', await ev("async () => (await window.__fa.chatLuck('kid')) === 'off'"))
        await ev("() => { window.__fa.chatMenu('kid', '嗨！'); }"); await page.wait_for_selector('#dBtns button')
        labels = await page.locator('#dBtns button').all_inner_texts()
        check('完成第三章前：小芽的選單與以前一樣（送禮、再見），沒有「聊聊」', labels == ['送禮', '再見'], str(labels)); await pump()
        await ev("() => { window.__fa.S.c.ch3_done = true; }")
        await ev("() => { window.__fa.chatMenu('kid', '嗨！'); }"); await page.wait_for_selector('#dBtns button')
        labels = await page.locator('#dBtns button').all_inner_texts()
        check('完成第三章後：小芽的選單多了「聊聊」（聊聊、送禮、再見）', labels == ['聊聊', '送禮', '再見'], str(labels))
        await page.locator('#dBtns button', has_text='再見').click(); await page.wait_for_timeout(300)
        # ---------- 機率權重 ----------
        w0 = await ev("() => window.__fa.luckWeights(0)"); w5 = await ev("() => window.__fa.luckWeights(5)")
        check('機率（0 顆心）：沒事 10、知識 60、小道具 25、金幣 5', w0 == {'none': 10, 'knowledge': 60, 'item': 25, 'coin': 5}, str(w0))
        check('機率（5 顆心）：小道具 35、金幣 10、知識 45，總和仍是 100', w5 == {'none': 10, 'knowledge': 45, 'item': 35, 'coin': 10} and sum(w5.values()) == 100, str(w5))
        # ---------- 各種結果 ----------
        c0 = await st('S.coins')
        t, r = await luck('kid', [0.05, 0.0]); check('結果「沒事」：只有一句閒聊、不扣不加', r == 'none' and await st('S.coins') == c0 and len(t) == 1, str((r, t)))
        t, r = await luck('wood', [0.3, 0.0, 0.0])
        check('結果「知識」：顯示現有知識卡並解鎖（阿木的話題：外出血等）', r == 'knowledge' and any('獲得知識卡' in x for x in t) and await st('Object.keys(S.cards).filter(k => ["bleed","cut","fracture","spine"].includes(k)).length') == 1, str((r, t[-1][:80] if t else '')))
        t, r = await luck('hunt', [0.8, 0.1, 0.0])
        check('結果「小道具」：得到提神小點心，進道具欄（1/10）', r == 'item' and await st('S.c.inv.snack') == 1 and any('提神小點心' in x and '1/10' in x for x in t), str((r, t)))
        t, r = await luck('guard', [0.97, 0.0, 0.0])
        check('結果「金幣」：最少 %d 金幣' % CL['coin']['min'], r == 'coin' and await st('S.coins') == c0 + CL['coin']['min'], str((r, await st('S.coins'), c0)))
        t, r = await luck('grandpa', [0.97, 0.9999, 0.0])
        check('金幣上限 %d' % CL['coin']['max'], r == 'coin' and await st('S.coins') == c0 + CL['coin']['min'] + CL['coin']['max'], str(await st('S.coins')))
        # ---------- 每天一次 ----------
        check('同一位角色當天再聊：回傳 done、不再抽', await ev("async () => (await window.__fa.chatLuck('kid')) === 'done'") and await ev("() => window.__fa.chatDone('kid')"))
        await ev("() => { window.__fa.S.c.chat.date = '2000-01-01'; }")
        check('隔天（現實日期變了）又可以聊', not await ev("() => window.__fa.chatDone('kid')"))
        await ev("() => { const m = window.__fa.S; m.c.chat = {date: new Date().toISOString().slice(0,10), done: {}}; }")
        # ---------- 道具欄滿了 ----------
        await ev("() => { window.__fa.S.c.chat = null; window.__fa.S.c.inv = {snack: 10}; }")
        t, r = await luck('kid', [0.8, 0.1, 0.0])
        check('道具欄滿了：角色說「下次再給你」、不給道具、不用掉當天機會', r == 'full' and await st('S.c.inv.snack') == 10 and any('道具欄已經滿了' in x for x in t) and not await ev("() => window.__fa.chatDone('kid')"), str((r, t)))
        await ev("() => { window.__fa.S.c.inv = {}; window.__fa.S.c.buff = {}; window.__fa.S.c.chat = null; }")
        # ---------- 使用道具 ----------
        sta = await st('S.sta'); await ev("() => { window.__fa.S.c.inv = {snack: 1, boots: 2, charm: 1, double: 1}; window.__fa.S.sta = 20; }")
        await ev("() => window.__fa.useItem('snack')")
        check('提神小點心：體力 +60（20 → 80）', await st('S.sta') == 80 and await st('S.c.inv.snack') == 0)
        check('沒有的道具用不了', await ev("() => window.__fa.useItem('snack')") is False)
        m0 = await ev("() => 0"); await ev("() => window.__fa.useItem('boots')")
        near = lambda a, b: abs(a - b) < 5   # 遊戲迴圈真的在倒數，測試期間會差零點幾秒
        check('疾風草鞋：10 分鐘（600 秒）', near(await st('S.c.buff.boots'), CL['effects']['boots']['seconds']), str(await st('S.c.buff')))
        await ev("() => window.__fa.useItem('boots')")
        check('再用一雙：時間累加（約 1200 秒）', near(await st('S.c.buff.boots'), 1200), str(await st('S.c.buff')))
        await ev("() => window.__fa.useItem('charm')"); check('幸運符：5 題', await st('S.c.buff.charm') == 5)
        await ev("() => window.__fa.useItem('double')")
        check('雙重驚喜：疾風草鞋 +600（到上限 1800）、幸運符 +5', near(await st('S.c.buff.boots'), 1800) and await st('S.c.buff.charm') == 10, str(await st('S.c.buff')))
        # ---------- 疾風草鞋：速度與倒數 ----------
        check('疾風草鞋生效中：走路速度 ×1.5（背包不重時）', abs(await ev("() => window.__fa.speedMul()") - 1.5) < 1e-9, str(await ev("() => window.__fa.speedMul()")))
        await ev("() => window.__fa.buffTick(30)")
        check('倒數：過 30 秒剩約 1770', abs(await st('S.c.buff.boots') - 1770) < 5, str(await st('S.c.buff.boots')))
        check('介面：有增益標示（疾風約 29:30、幸運 ×10）', await ev("() => { const e = document.getElementById('buffPill'); return !e.hidden && /疾風 29:[2-5]\d/.test(e.textContent) && e.textContent.includes('幸運 ×10'); }"))
        await ev("() => window.__fa.buffTick(5000)")
        check('時間用完：走路速度回到 ×1', abs(await ev("() => window.__fa.speedMul()") - 1) < 1e-9)
        check('時間用完：疾風草鞋失效，標示只剩幸運符', await st('S.c.buff.boots') == 0 and await ev("() => { const e = document.getElementById('buffPill'); return !e.hidden && !e.textContent.includes('疾風') && e.textContent.includes('幸運'); }"))
        # ---------- 幸運符：答對題目加成 ----------
        await ev("() => { window.__fa.S.c.buff = {charm: 2}; window.__fa.S.coins = 100; }")
        await ev("() => { window.__fa.quiz('hero', '測試題？', ['錯的', '對的'], 1, '解析'); }")
        await page.wait_for_selector('#dBtns button'); await page.locator('#dBtns button', has_text='錯的').click(); await page.wait_for_timeout(250)
        check('答錯：沒有加成、幸運符不消耗', await st('S.coins') == 100 and await st('S.c.buff.charm') == 2)
        await pump()   # 「再選一次」→ 再答
        await ev("() => { window.__fa.quiz('hero', '第二題？', ['對的', '錯的'], 0, '解析'); }")
        await page.wait_for_selector('#dBtns button'); await page.locator('#dBtns button', has_text='對的').click(); await page.wait_for_timeout(300); await pump()
        check('答對：額外 +%d 金幣、幸運符少 1 題（剩 1）' % CL['effects']['charm']['bonus'], await st('S.coins') == 100 + CL['effects']['charm']['bonus'] and await st('S.c.buff.charm') == 1, f"{await st('S.coins')} {await st('S.c.buff')}")
        await ev("() => window.__fa.luckyBonus()"); coins = await st('S.coins')
        check('次數用完後再答對：不再加成', await ev("() => window.__fa.luckyBonus()") == 0 and await st('S.coins') == coins)
        # ---------- 背包的「道具」區 ----------
        await ev("() => { window.__fa.S.c.inv = {snack: 2, charm: 1}; window.__fa.S.c.buff = {}; window.__fa.S.sta = 10; }")
        await page.click('#btnBag'); await page.wait_for_selector('#dText')
        t = await page.inner_text('#dText')
        check('背包有「道具 3/10」區：提神小點心 ×2、幸運符 ×1', '道具 3/10' in t and '提神小點心 ×2' in t and '幸運符 ×1' in t, t[:300])
        await page.locator('#dText button[data-u="snack"]').click(); await page.wait_for_timeout(400)
        check('在背包按「使用」：提神小點心立刻生效（體力 10 → 70）、剩 1 個', await st('S.sta') == 70 and await st('S.c.inv.snack') == 1)
        await page.locator('#dBtns button').last.click(); await page.wait_for_timeout(300)
        # ---------- 雜貨店 VIP 折扣 ----------
        async def shop_price():
            await ev("() => { window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a="seed"]'); t = await page.inner_text('#dText')
            return t
        await ev("() => { const S = window.__fa.S; S.c.ch3_done = false; S.hearts.shopkeeper = 5; S.coins = 1000; }")
        t = await shop_price(); check('完成第三章前：就算 5 顆心也沒有折扣（種子原價）', f'{SEED} 金幣一包' in t and 'VIP' not in t and '老主顧' not in t, t[:200]); await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await ev("() => { const S = window.__fa.S; S.c.ch3_done = true; S.hearts.shopkeeper = 0; }")
        t = await shop_price(); check('0 顆心：原價，並提示再多幾顆心有折扣', f'{SEED} 金幣一包' in t and '再多 3 顆好感度' in t, t[:300]); await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await ev("() => { window.__fa.S.hearts.shopkeeper = 3; }")
        p3 = max(1, int(SEED * 0.95)); t = await shop_price(); check(f'3 顆心：95 折（種子 {SEED} → {p3}，一定比原價少）、顯示老主顧', p3 < SEED and f'{p3} 金幣一包' in t and '9.5 折' in t, t[:300])
        c1 = await st('S.coins'); await page.locator('#dText button[data-a="seed"]').click(); await page.wait_for_timeout(350)
        check('買東西實際扣折後價格', await st('S.coins') == c1 - p3, f"{await st('S.coins')} {c1} {p3}"); await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await ev("() => { window.__fa.S.hearts.shopkeeper = 5; }")
        p5 = max(1, int(SEED * 0.85)); t = await shop_price(); check(f'5 顆心：85 折（種子 {SEED} → {p5}）', f'{p5} 金幣一包' in t and '8.5 折' in t, t[:300])
        check('體能補給、擴充背包也有折扣（能量點心 40 → 34、體能訓練 300 → 255）', f'{int(40*0.85)} 金幣' in t and f'{int(300*0.85)} 金幣' in t, t[-700:]); await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        await ev("() => { window.__fa.S.coins = 5000; window.__fa.S.c.staUp = 0; }")
        # 迷霧商人不打折
        await ev("() => { window.__fa.merchantMenu(); }"); await page.wait_for_selector('#dText button[data-a]'); tm = await page.inner_text('#dText')
        import re
        prices = re.findall(r'(\d+) 金幣', tm)
        merch = json.load(open(ROOT / 'content/items.json', encoding='utf-8'))
        base = {merch['ITEMS'][k]['price'] for k in merch['MERCHANT_GOODS']}
        check('迷霧商人：價格維持原價（不受 VIP 影響）', set(map(int, prices)) <= base and len(prices) > 0, f'{prices} vs {base}'); await page.locator('#dBtns button', has_text='離開').click(); await page.wait_for_timeout(300)
        # ---------- 第三章角色 ----------
        await ev("() => { const S = window.__fa.S; S.c.chat = null; S.c.inv = {}; window.__fa.go('ch3_market', [830, 800]); }"); await page.wait_for_timeout(900)
        await rand([0.05, 0.0, 0.0, 0.0]); await ev("() => { window.__fa.talk('ch3_by_red'); }"); t = await pump(30)
        check('第三章路人：說完對白後也有一次聊天運氣（今天記錄 done）', await ev("() => window.__fa.chatDone('ch3_by_red')") and await st('S.c.chat.done.ch3_by_red') is True, str(t[-2:]))
        await rand([0.05, 0.0, 0.0, 0.0]); await ev("() => { window.__fa.talk('ch3_by_red'); }"); t2 = await pump(30)
        check('第三章路人：同一天再說話只有對白，不再抽（亂數一個都沒用到、沒有任何獲得）', await ev("() => window.__rq.length") == 4 and all('獲得' not in x for x in t2), str(await ev("() => window.__rq.length")))
        # ---------- 存檔結構 ----------
        check('道具、增益、聊天紀錄都在既有的 S.c 裡，沒有新增頂層存檔欄位', await ev("() => ['inv', 'buff', 'chat'].every(k => !(k in window.__fa.S))") and await st("'inv' in S.c || 'chat' in S.c"))
        check('友誼回饋測試沒有頁面錯誤', not errs, str(errs))
        await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('友誼回饋測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
