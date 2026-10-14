"""第五章筆試（老師 2026-10-14 決定）：題庫（15＋10）、進入條件（登入、18 顆星、班級開關）、隨機順序、作答中不顯示對錯、計分、重考記最高分。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch5_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
E = json.load(open(ROOT / 'chapters/ch5/exam.json', encoding='utf-8'))
Z = json.load(open(ROOT / 'chapters/ch3/dialogues.json', encoding='utf-8'))['quizzes']
# 老師確認的標準答案（2026-10-14）：協會題題號 → 正確選項文字
KEY = {'a9': '5 公分以上', 'a10': '100–120 下', 'a11': '4–6 分鐘', 'a13': '5 公分', 'a14': '滿 28 天到一歲', 'a16': '兩乳連線中點下方', 'a17': '發燒', 'a19': 'CPR（心肺復甦術）',
       'a20': '評估環境安全', 'a23': '繼續 CPR', 'a29': '適用緊急避難免責規定', 'a26': '紗布、生理食鹽水、OK 繃、體溫計'}
async def main(url):
    # ---------- 題庫（不需瀏覽器）----------
    A = E['assoc']
    check('協會題 15 題、遊戲題 10 題', len(A) == 15 and len(E['game']) == 10)
    check('每題 4 個選項、答案編號在範圍內', all(len(a['opts']) == 4 and 0 <= a['ans'] < 4 for a in A))
    check('協會題答案與老師確認的標準答案一致', all(a['opts'][a['ans']] == KEY[a['id']] for a in A if a['id'] in KEY), [a['id'] for a in A if a['id'] in KEY and a['opts'][a['ans']] != KEY[a['id']]])
    byid = {a['id']: a for a in A}
    check('a12 貼片＝右鎖骨下方＋左乳頭外側下方、a21＝手肘伸直、a24＝叫叫 CABD',
          byid['a12']['opts'][byid['a12']['ans']].startswith('一片貼在右胸上方') and byid['a21']['opts'][byid['a21']['ans']].startswith('手肘伸直') and byid['a24']['opts'][byid['a24']['ans']] == '叫叫 CABD')
    check('遊戲題都在第三章已審核題目裡（有 reviewed）', all(k in Z and Z[k].get('reviewed') for k in E['game']), [k for k in E['game'] if k not in Z])
    check('沒有重複題', len({a['q'] for a in A} | {Z[k].get('q') or Z[k]['title'] for k in E['game']}) == 25)
    right = {a['q']: a['opts'][a['ans']] for a in A}
    for k in E['game']:
        z = Z[k]
        if not z.get('order'): right[z['q']] = z['opts'][z['ans']]
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.day = 5; document.getElementById('btnStart').click(); }")
        await page.wait_for_timeout(500)
        ev = lambda e, a=None: page.evaluate(e, a) if a is not None else page.evaluate(e)
        txt = lambda: page.inner_text('#dText')
        async def btn(label):
            await page.locator('#dBtns button', has_text=label).first.click(); await page.wait_for_timeout(150)
        async def closeAll():
            for _ in range(6):
                if await ev("() => document.getElementById('dialog').hidden"): return
                await page.locator('#dBtns button').last.click(); await page.wait_for_timeout(120)
        async def setStars(c, a, b_, d):
            await ev("([c,a,b,d]) => { const S = window.__fa.S; S.castleBest = c; S.c.stars = a; S.c.ch3_stars = b; S.c.ch4 = Object.assign(S.c.ch4 || {}, {stars: d}); window.__fa.refresh(); }", [c, a, b_, d])
        async def openExam():
            await ev("() => { window.__fa.examCenter(); }"); await page.wait_for_timeout(300)
        # ---------- 進入條件 ----------
        check('沒有班級（老師、訪客）：筆試開關預設開', await ev("() => window.__fa.examOn()"))
        await ev("() => { window.FACloud.email = () => null; }")
        await setStars(5, 5, 5, 5)
        await openExam(); t = await txt()
        check('沒登入：不能參加，提示要登入', '要先登入' in t, t); await closeAll()
        await ev("() => { window.FACloud.email = () => 'stu@example.com'; }")
        await setStars(4, 4, 4, 5)
        await openExam(); t = await txt()
        check('17 顆星：不能參加，提示還差 1 顆', '還差 1 顆' in t and '開始作答' not in t, t); await closeAll()
        await ev("() => { window.FACloud.refreshControl = async () => ({class_id: 7, flags: {ch5: false}}); return window.__fa.pullControl(); }")
        check('有班級且老師沒開 ch5：筆試關閉', not await ev("() => window.__fa.examOn()"))
        await ev("() => { window.FACloud.refreshControl = async () => ({class_id: 7, flags: {ch5: true}}); return window.__fa.pullControl(); }")
        check('有班級且老師開了 ch5：筆試開放', await ev("() => window.__fa.examOn()"))
        # ---------- 全對 ----------
        await setStars(5, 4, 5, 4)
        async def runExam(mode):
            """mode: 'right' 全答對、'wrong' 全答錯。回傳 (題目順序, 作答中看過的文字, 結果文字)"""
            await openExam(); intro = await txt(); await btn('開始作答')
            seen, order = [], []
            for _ in range(80):
                t = await txt()
                if '筆試結果' in await page.inner_text('#dWho'): return order, seen, t, intro
                q = await page.locator('#dText .q').first.inner_text(); order.append(q); seen.append(t)
                btns = page.locator('#dBtns button')
                if await page.locator('#eoq').count():
                    z = [Z[k] for k in E['game'] if Z[k].get('order') and Z[k]['title'] == q][0]
                    steps = z['steps'] if mode == 'right' else list(reversed(z['steps']))
                    for s in steps:
                        await page.locator('#eoq button:not([disabled])', has_text=s).first.click()
                    await page.locator('#dBtns button', has_text='確定').click()
                else:
                    n = await btns.count(); labels = await btns.all_inner_texts()
                    pick = [i for i, l in enumerate(labels) if (l == right[q]) == (mode == 'right')][0]
                    await btns.nth(pick).click()
                await page.wait_for_timeout(120)
            return order, seen, '', intro
        order1, seen1, res, intro = await runExam('right')
        check('簡介有規則：25 題、80 分及格、只供參考、不計時', '25 題' in intro and '80 分' in intro and '只供老師參考' in intro and '不計時' in intro, intro)
        check('作答 25 題', len(order1) == 25, len(order1))
        check('作答中不顯示對錯（題幹本身的「哪一個說法正確」不算）', not any(('處置正確' in s or '答對' in s or '答錯' in s or '這個做法不對' in s or '順序完全正確' in s or '順序不對' in s) for s in seen1))
        check('全對：100 分、及格、沒有答錯的題目', '100 / 100' in res and '達到 80 分' in res and '全部答對' in res, res)
        check('成績記在 S.c.ch5（最高 100、考 1 次）', await ev("() => [window.__fa.S.c.ch5.best, window.__fa.S.c.ch5.tries]") == [100, 1])
        await btn('再考一次')
        # ---------- 重考：全錯，最高分維持 ----------
        order2 = []; seen2 = []
        for _ in range(80):
            t = await txt()
            if '筆試結果' in await page.inner_text('#dWho'): res2 = t; break
            q = await page.locator('#dText .q').first.inner_text(); order2.append(q)
            if await page.locator('#eoq').count():
                z = [Z[k] for k in E['game'] if Z[k].get('order') and Z[k]['title'] == q][0]
                for s in reversed(z['steps']): await page.locator('#eoq button:not([disabled])', has_text=s).first.click()
                await page.locator('#dBtns button', has_text='確定').click()
            else:
                btns = page.locator('#dBtns button'); labels = await btns.all_inner_texts()
                await btns.nth([i for i, l in enumerate(labels) if l != right[q]][0]).click()
            await page.wait_for_timeout(120)
        check('全錯：0 分、不及格、列出 25 題答錯並附正確答案', '0 / 100' in res2 and '還差一點' in res2 and res2.count('正確答案：') == 25, res2[:200])
        check('遊戲題答錯會附原有解說', '先確保現場安全' not in res2 and '指定特定人最有效' in res2, res2[-300:])
        check('重考：最高分仍是 100、考 2 次', await ev("() => [window.__fa.S.c.ch5.best, window.__fa.S.c.ch5.tries, window.__fa.S.c.ch5.last]") == [100, 2, 0])
        check('題目順序每次隨機（兩次順序不同、且不是題庫順序）', order1 != order2 and order1 != [a['q'] for a in A] + [Z[k].get('q') or Z[k]['title'] for k in E['game']])
        await btn('關閉')
        # ---------- 獎狀與筆試入口 ----------
        await ev("() => { window.__fa.certCenter(); }"); await page.wait_for_timeout(300)
        labels = await page.locator('#dBtns button').all_inner_texts()
        check('獎狀中心有「第五章筆試」入口', '第五章筆試' in labels, labels); await closeAll()
        check('沒有 JS 錯誤', not errs, errs)
        await b.close()
    print('失敗', fails)
    sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
