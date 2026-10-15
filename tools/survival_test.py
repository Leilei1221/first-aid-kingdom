"""雪嶺「抉擇與求生」：上山前氣象判斷（等一天／勉強出發）、落石前兆、白茫茫與指南針、山屋暴風雪求生（保暖值、資源、撐過與撐不下去＝救援扣費送回山腳村）、嚮導訓練的求生練習、指南針與打火石。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/survival_test.py http://localhost:8765/index.html`"""
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
async def boot(ctx, url, setup=''):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '?open=ch2,ch3,ch4#debug')
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
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # --- 預報：day 23 第 3 天有暴風雪（山屋那天），預計 3 天；「勉強出發」、沒有獎勵
        page, errs = await boot(ctx, url)
        await goto(page, 'ch4_village', 880, 620)
        plan = await page.evaluate("async () => JSON.stringify(await window.__ch4Sv.plan(23))")
        check('day 23：預報第 3 天有暴風雪、預計 3 天', json.loads(plan)['storm'] == [False, False, True] and json.loads(plan)['len'] == 3, plan)
        plan14 = json.loads(await page.evaluate("async () => JSON.stringify(await window.__ch4Sv.plan(14))"))
        check('day 14：三天都沒有暴風雪', plan14['storm'] == [False, False, False], str(plan14))
        await page.evaluate("() => { document.getElementById('act'); }")
        await page.evaluate("() => { window.__fa.S.pos = { x: 400, y: 400 }; }"); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(600)
        await click(page, '出發', 500)
        t = await text(page)
        check('出發前先看氣象公告：有「第 3 天」與「暴風雪」', '第 3 天' in t and '暴風雪' in t, t[:100])
        log = []
        # 先看一看 → 三題 → 知識卡 → 選擇
        for _ in range(14):
            bt = await btns(page)
            if any('勉強出發' in x for x in bt): break
            await drive(page, 'right', limit=1, log=log)
        check('第一次看預報會問 3 題（W1～W3）並給知識卡', log[:3] == ['ch4_w1', 'ch4_w2', 'ch4_w3'] and await ev(page, "!!S.cards.ch4_k6_2"), str(log))
        check('有三個選項：勉強出發、等一天、再準備一下（沒有「出發」）', any('勉強出發' in x for x in await btns(page)) and any('等一天' in x for x in await btns(page)) and any('再準備' in x for x in await btns(page)), str(await btns(page)))
        c0 = await ev(page, "S.coins"); d0 = await ev(page, "S.day")
        await click(page, '等一天', 1200)
        await drive(page, 'right', limit=1)  # 「第 N 天」的早安對話
        check('等一天：旅店費 −20、天數 +1、體力回滿', await ev(page, "S.coins") == c0 - 20 and await ev(page, "S.day") == d0 + 1 and await ev(page, "S.sta") >= 100, f'{await ev(page, "S.coins")} {await ev(page, "S.day")}')
        # day 24：第 2 天（=26）... 重新看預報後選「勉強出發」
        await page.wait_for_timeout(500); bt = await btns(page)
        check('隔天再看預報（day 24：第 2 天 25 有暴風雪）還有選項', any('出發' in x for x in bt), str(bt))
        c1 = await ev(page, "S.coins")
        await click(page, '勉強出發' if any('勉強出發' in x for x in bt) else '出發', 700)
        await drive(page, 'right', limit=5)
        fc = await ev(page, "S.c.ch4.fc")
        check('勉強出發：記下 fc（force），沒有給任何金幣獎勵', fc and fc.get('force') in (True, False) and await ev(page, "S.coins") <= c1, f'{fc} {await ev(page, "S.coins")}')
        await page.close()
        # --- 已經上過山的存檔（c1 已做、有舊的 fc）：再從山腳村出發，仍然會看氣象公告；山腳村帕桑有「求生練習」
        page, errs = await boot(ctx, url, "S.c.ch4.c1 = true; S.c.ch4.fcQ = true; S.c.ch4.fc = { d0: 1, rock: false, white: false, len: 1 };")
        await goto(page, 'ch4_village', 880, 620)
        await page.evaluate("() => { window.__fa.S.pos = { x: 400, y: 400 }; }"); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(600)
        await click(page, '出發', 600)
        check('上過山的存檔再出發：重新看氣象公告（預報是這趟的，不是舊的）', '氣象公告' in await page.inner_text('#dWho') and '第 3 天' in await text(page), await text(page))
        await page.close()
        page, errs = await boot(ctx, url)
        await goto(page, 'ch4_village', 880, 620)
        await page.evaluate("() => { window.__fa.talk('ch4_guide'); }"); await page.wait_for_timeout(700)
        check('山腳村帕桑的選單有「求生練習（不扣錢）」', any('求生練習' in x for x in await btns(page)), str(await btns(page))); await page.close()
        # --- 指南針：買一個（60），不能重複買；背包不佔格
        page, errs = await boot(ctx, url)
        await goto(page, 'ch4_village', 880, 620)
        await page.evaluate("() => { window.__fa.S.pos = { x: 1330, y: 548 }; }"); await page.wait_for_timeout(400)
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(600)
        check('裝備攤有指南針 60 金幣', '指南針' in await text(page) and '60' in await text(page))
        c0 = await ev(page, "S.coins"); await click(page, '買指南針', 500)
        check('買指南針：金幣 −60、S.c.ch4.compass', await ev(page, "S.coins") == c0 - 60 and await ev(page, "S.c.ch4.compass") is True, await ev(page, "S.coins"))
        check('買過之後按鈕變成「指南針（已有）」且不能再買', any('已有' in x for x in await btns(page)) and await page.locator('#dBtns button', has_text='已有').is_disabled())
        await page.close()
        # --- 落石：day 16（第 2 天有暴風雪）→ 前兆題 R1～R3；選錯（抬頭看）＝救援失敗
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 16, rock: true, white: false, len: 1 };")
        await goto(page, 'ch4_camp1', 420, 780)
        log = []
        await page.evaluate("() => { window.__ch4Sv.rockfall(); }"); await page.wait_for_timeout(500)
        await drive(page, 'right', limit=40, log=log)
        check('落石：先預測 R1、再 R2、落石時 R3（全答對）', log[:3] == ['ch4_r1', 'ch4_r2', 'ch4_r3'], str(log))
        check('落石結束：給知識卡、rockDone 記下，不會重複觸發', await ev(page, "!!S.cards.ch4_k6_3 && S.c.ch4.fc.rockDone === true"))
        await page.close()
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 16, rock: true, white: false, len: 1 };")
        await goto(page, 'ch4_camp1', 420, 780); c0 = await ev(page, "S.coins")
        await page.evaluate("() => { window.__ch4Sv.rockfall().catch(() => {}); }"); await page.wait_for_timeout(500)
        await drive(page, {'ch4_r3': 1}, limit=40)
        check('落石時選「抬頭看」＝救援失敗：扣 200、送回山腳村', await ev(page, "S.coins") == c0 - 200 and await ev(page, "S.scene") == 'ch4_village', f'{await ev(page, "S.coins")} {await ev(page, "S.scene")}')
        await page.close()
        # --- 白茫茫：有指南針 L1～L4；沒有指南針 L1、L4、體力 −15
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 23, rock: false, white: true, len: 2 }; S.c.ch4.compass = true;")
        await goto(page, 'ch4_snowline', 320, 700); log = []
        await page.evaluate("() => { window.__ch4Sv.whiteout(); }"); await page.wait_for_timeout(500)
        await drive(page, 'right', limit=40, log=log)
        check('有指南針：L1、L2、L3、L4 四題', log[:4] == ['ch4_l1', 'ch4_l2', 'ch4_l3', 'ch4_l4'], str(log)); await page.close()
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 23, rock: false, white: true, len: 2 };")
        await goto(page, 'ch4_snowline', 320, 700); log = []; s0 = await ev(page, "S.sta")
        await page.evaluate("() => { window.__ch4Sv.whiteout(); }"); await page.wait_for_timeout(500)
        await drive(page, 'right', limit=40, log=log)
        check('沒有指南針：只有 L1、L4，體力 −15', log[:2] == ['ch4_l1', 'ch4_l4'] and await ev(page, "S.sta") == s0 - 15, f'{log} {await ev(page, "S.sta")}'); await page.close()
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 23, rock: false, white: true, len: 2 };")
        await goto(page, 'ch4_snowline', 320, 700); c0 = await ev(page, "S.coins")
        await page.evaluate("() => { window.__ch4Sv.whiteout().catch(() => {}); }"); await page.wait_for_timeout(500)
        await drive(page, {'ch4_l1': 0}, limit=30)
        check('白茫茫亂走＝救援失敗：扣 200、送回山腳村', await ev(page, "S.coins") == c0 - 200 and await ev(page, "S.scene") == 'ch4_village', f'{await ev(page, "S.coins")} {await ev(page, "S.scene")}'); await page.close()
        # --- 山屋求生：準備齊全、全答對 → 撐過（3 天），消耗物品，回到山屋室外
        GEAR = "['jacket','hat','pants','gloves','boots'].forEach(k => S.c.ch3_e3.own[k] = 1); S.c.ch3_e3.cnt.blanket = 1; S.c.ch3_e3.cnt.warmer = 1; S.c.ch3_e3.own.headlamp = 1; S.mat.flint = 2; S.mat.wood = 6; S.kit.push('ration@40','ration@40','ration@40','water','water','water','whistle');"
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 23, rock: false, white: true, len: 3 }; S.c.ch4.s5 = true; " + GEAR)
        await goto(page, 'ch4_lodge', 330, 800); day0 = await ev(page, "S.day")
        await page.evaluate("() => { window.__ch4Sv.survive(); }"); await page.wait_for_timeout(900)
        check('暴風雪求生：進到破窗的山屋室內', await ev(page, "S.scene") == 'ch4_lodge_in_storm', await ev(page, "S.scene"))
        log = []; await drive(page, 'right', limit=140, log=log)
        used = [k for k in log]
        check('全答對、裝備齊全：撐過去，回到山屋室外', await ev(page, "S.scene") == 'ch4_lodge', await ev(page, "S.scene"))
        check('求生題 S1～S8 都出現過', all(k in log for k in ['ch4_s1', 'ch4_s2', 'ch4_s3', 'ch4_s4', 'ch4_s5', 'ch4_s6', 'ch4_s7', 'ch4_s8']), str(log))
        check('撐過：記下 svDone、天數 +（因為有哨子／頭燈，救援提早 1 天）', await ev(page, "S.c.ch4.fc.svDone === true") and await ev(page, "S.day") == day0 + 2, f'{day0} {await ev(page, "S.day")}')
        check('物品被用掉：乾糧、開水、打火石、毯子、暖暖包', await ev(page, "S.kit.filter(k => k.startsWith('ration')).length") < 3 and await ev(page, "S.mat.flint") < 2 and await ev(page, "(S.c.ch3_e3.cnt.blanket || 0) === 0 && (S.c.ch3_e3.cnt.warmer || 0) === 0"))
        check('給知識卡 k6_1、k6_4', await ev(page, "!!S.cards.ch4_k6_1 && !!S.cards.ch4_k6_4"))
        check('沒有被扣救援費、沒有回山腳村', await ev(page, "S.coins") == 5000 and await ev(page, "S.scene") == 'ch4_lodge'); await page.close()
        # --- 什麼都沒帶（3 天）：撐不下去＝救援失敗，扣 200、送回山腳村
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 23, rock: false, white: true, len: 3 }; S.c.ch4.s5 = true; S.kit = [];")
        await goto(page, 'ch4_lodge', 330, 800); c0 = await ev(page, "S.coins")
        await page.evaluate("() => { window.__ch4Sv.survive().catch(() => {}); }"); await page.wait_for_timeout(900)
        await drive(page, 'right', limit=160)
        check('什麼都沒帶、預計 3 天：撐不下去，救援失敗扣 200、送回山腳村', await ev(page, "S.coins") == c0 - 200 and await ev(page, "S.scene") == 'ch4_village', f'{await ev(page, "S.coins")} {await ev(page, "S.scene")}')
        check('失敗也給救援知識卡（失溫）', await ev(page, "!!S.cards.hypothermia")); await page.close()
        # --- 嚴重錯誤：S3 全部塞緊 → 救援失敗；練習版只記錄
        page, errs = await boot(ctx, url, "S.c.ch4.fc = { d0: 23, rock: false, white: true, len: 2 }; S.c.ch4.s5 = true; " + GEAR)
        await goto(page, 'ch4_lodge', 330, 800); c0 = await ev(page, "S.coins")
        await page.evaluate("() => { window.__ch4Sv.survive().catch(() => {}); }"); await page.wait_for_timeout(900)
        await drive(page, {'ch4_s3': 1}, limit=60)
        check('S3 選「全部塞緊」＝救援失敗：扣 200、送回山腳村', await ev(page, "S.coins") == c0 - 200 and await ev(page, "S.scene") == 'ch4_village', f'{await ev(page, "S.coins")} {await ev(page, "S.scene")}'); await page.close()
        page, errs = await boot(ctx, url, "S.c.ch4.s5 = true; S.c.ch4.done = true; " + GEAR)
        await goto(page, 'ch4_lodge', 330, 800); c0 = await ev(page, "S.coins"); k0 = await ev(page, "S.kit.length"); f0 = await ev(page, "S.mat.flint")
        await page.evaluate("() => { window.__ch4Sv.survive({ practice: true, len: 2 }); }"); await page.wait_for_timeout(900)
        await drive(page, {'ch4_s3': 1, 'ch4_s7': 0}, limit=160)
        check('求生練習：就算選了嚴重錯誤也不扣錢、不送回、不用掉背包物品', await ev(page, "S.coins") == c0 and await ev(page, "S.scene") == 'ch4_lodge' and await ev(page, "S.kit.length") == k0 and await ev(page, "S.mat.flint") == f0, f'{await ev(page, "S.coins")} {await ev(page, "S.scene")}')
        check('求生練習不記 svDone', await ev(page, "!(S.c.ch4.fc && S.c.ch4.fc.svDone)"))
        check('求生測試沒有頁面錯誤', not errs, str(errs[:2]))
        await b.close()
    print('\n失敗', fails, '項' if fails else '，全部通過'); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
