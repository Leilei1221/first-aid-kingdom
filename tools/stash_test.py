"""防災包專項測試（HANDOFF v3.2 第 6 節 #2–#8）。
用法：先在專案根目錄 `python3 -m http.server 8765`，再 `python3 tools/stash_test.py http://localhost:8765/index.html`
實際用鍵盤走到防災包，再用按鈕操作選單；不直接改座標。"""
import asyncio, json, sys, os
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(__file__))
from walk_test import WALKS, bfs, WALK_JS  # noqa: E402

KEY = 'fa-kingdom-p1-v1'
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1

async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page()
        await page.goto(url + '#debug')
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        ev = lambda js: page.evaluate(js)
        page.on('pageerror', lambda e: print('頁面錯誤：', e))

        # T2 舊存檔（沒有 stash 欄位、背包有乾糧與開水）
        await ev("""() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.day = 5; S.kitCap = 14; S.kit = ['ration@12','ration@12','water','water'];
          delete S.stash; localStorage.setItem('%s', JSON.stringify(S)); }""" % KEY)
        await page.reload(); await page.goto(url + '#debug')
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        r = await ev("() => ({stash: window.__fa.S.stash, kit: window.__fa.S.kit})")
        check('T2 舊存檔載入：stash 補 []、背包乾糧開水仍在', r['stash'] == [] and r['kit'] == ['ration@12', 'ration@12', 'water', 'water'], str(r))

        # T3 實際走到防災包
        await ev("""() => { const S = window.__fa.S; S.scene = 'home'; S.pos = {x: 1010, y: 690}; S.started = true; document.getElementById('btnStart').click(); }""")
        await page.wait_for_timeout(600)
        path = bfs(WALKS['home'], (1010, 690), lambda x, y: abs(x - 1290) < 60 and abs(y - 700) < 40)
        check('T3 防災包位置有路可走', path is not None)
        pts = path[::2] + [path[-1]]
        await ev("() => { window.__stop = true; }")
        # 走到定點後不換場景，改用自訂短腳本
        await page.evaluate("""async (pts) => { const F = window.__fa, S = F.S; const key=(t,k)=>window.dispatchEvent(new KeyboardEvent(t,{key:k,bubbles:true})); const held=new Set();
          const set=(k,on)=>{ if(on&&!held.has(k)){key('keydown',k);held.add(k);} if(!on&&held.has(k)){key('keyup',k);held.delete(k);} };
          let i=0; for(let s=0;s<3000;s++){ const [tx,ty]=pts[Math.min(i,pts.length-1)]; const dx=tx-S.pos.x, dy=ty-S.pos.y;
            if(Math.hypot(dx,dy)<14){ if(i<pts.length-1){i++;continue;} break; }
            set('ArrowLeft',dx<-6);set('ArrowRight',dx>6);set('ArrowUp',dy<-6);set('ArrowDown',dy>6); await new Promise(r=>setTimeout(r,30)); }
          ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].forEach(k=>set(k,false)); }""", pts)
        await page.wait_for_timeout(300)
        label = (await page.inner_text('#act')).strip()
        check('T3 靠近時動作鍵顯示「防災包」', label == '防災包', label)

        # T4 放入：背包乾糧與開水放進防災包
        await page.click('#act'); await page.wait_for_selector('#dialog:not([hidden])')
        txt = await page.inner_text('#dText')
        check('T4 查看畫面顯示一週目標與容量', '0/20' in txt and '乾糧 0/7' in txt and '開水 0/7' in txt, txt)
        for _ in range(4):
            await page.click('#dText button[data-p]'); await page.wait_for_timeout(80)
        r = await ev("() => ({stash: window.__fa.S.stash, kit: window.__fa.S.kit})")
        check('T4 放入後背包清空、防災包 4 件', r['kit'] == [] and len(r['stash']) == 4, str(r))
        txt = await page.inner_text('#dText')
        check('T4 查看顯示乾糧 2 包、開水 2 瓶、最快到期', '乾糧 2/7' in txt and '開水 2/7' in txt and '第 12 天' in txt, txt)

        # T5 取出 + 負重
        await page.click('#dText button[data-o]'); await page.wait_for_timeout(80)
        r = await ev("() => ({n: window.__fa.S.stash.length, kit: window.__fa.S.kit})")
        check('T5 取出一件到背包', r['n'] == 3 and len(r['kit']) == 1, str(r))
        await ev("() => { const S = window.__fa.S; S.kitCap = 4; S.kit = ['water','water','water','water']; window.__fa.refresh(); }")
        await page.click('#dText button[data-o]'); await page.wait_for_timeout(80)
        check('T5 背包滿時不能取出', await ev("() => window.__fa.S.stash.length") == 3)
        # 容量：塞滿 20
        await ev("() => { const S = window.__fa.S; S.stash = Array(20).fill('water'); S.kitCap = 14; S.kit = ['water']; }")
        await page.click('#dBtns button'); await page.wait_for_timeout(200)
        await page.click('#act'); await page.wait_for_selector('#dialog:not([hidden])')
        await page.click('#dText button[data-p]'); await page.wait_for_timeout(80)
        r = await ev("() => ({n: window.__fa.S.stash.length, k: window.__fa.S.kit.length})")
        check('T4 容量上限生效（20）', r['n'] == 20 and r['k'] == 1, str(r))
        # 防災包不計負重：防災包 20 瓶水，背包空 → 背包畫面負重 0；取出一瓶後負重 2
        await ev("() => { const S = window.__fa.S; S.kit = []; S.stash = Array(20).fill('water'); }")
        await page.click('#dBtns button'); await page.wait_for_timeout(200)
        await ev("() => { window.__fa.bag(); }"); await page.wait_for_selector('#dialog:not([hidden])')
        txt = await page.inner_text('#dText')
        check('T5 防災包內的東西不計負重', '負重 0' in txt, txt[:200])
        await page.click('#dBtns button'); await page.wait_for_timeout(200)
        await ev("() => { const S = window.__fa.S; S.kit.push(S.stash.pop()); }")
        await ev("() => { window.__fa.bag(); }"); await page.wait_for_selector('#dialog:not([hidden])')
        txt = await page.inner_text('#dText')
        check('T5 取出到背包後才計負重', '負重 2' in txt, txt[:200])
        await page.click('#dBtns button'); await page.wait_for_timeout(200)

        # T6 過期通知與爺爺提醒
        await ev("() => { const S = window.__fa.S; S.kit = ['ration@5']; S.stash = ['ration@5','ration@20']; S.day = 5; window.__fa.refresh(); }")
        html = await ev("() => { const S = window.__fa.S; window.__fa.S.day = 5; return 0 }")
        await ev("() => { window.__fa.bed(); }")
        await page.wait_for_selector('#dialog:not([hidden])'); await page.click('#dBtns button:first-child')
        await page.wait_for_selector('#dText:has-text(\"過期\")', timeout=8000)
        txt = await page.inner_text('#dText')
        check('T6 隔天通知：背包與防災包分開寫', '背包裡有 1 包乾糧過期' in txt and '家裡的防災包有 1 包乾糧過期' in txt, txt)
        await page.click('#dBtns button'); await page.wait_for_timeout(200)
        await ev("() => { const S = window.__fa.S; S.kit = []; S.event = null; S.scene = 'home'; window.__fa.talk('grandpa'); }")
        await page.wait_for_selector('#dialog:not([hidden])')
        txt = await page.inner_text('#dText')
        check('T6 爺爺提醒防災包過期乾糧', '家裡的防災包有 1 包乾糧已經過期' in txt, txt)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
        r = await ev("() => window.__fa.S.stash")
        check('T6 丟掉過期乾糧後只剩有效的', r == ['ration@20'], str(r))

        # T7 進城確認畫面
        await ev("() => { const S = window.__fa.S; S.f.guard = true; S.kit = ['ration@20','water']; S.stash = ['ration@20','ration@20','water']; S.castleDone = false; window.__fa.gateDoor(); }")
        await page.wait_for_selector('#dialog:not([hidden])')
        txt = await page.inner_text('#dText')
        check('T7 進城確認同時顯示背包與家中數量與提示', '有效乾糧：1 包' in txt and '家中防災包：有效乾糧 2 包　開水 1 瓶' in txt and '不能在這裡拿' in txt, txt)
        await page.click('#dBtns button:nth-child(2)'); await page.wait_for_timeout(200)

        # T8 地震章末：物資留在家裡 → 判定不變（不足）並提示；背包足夠 → 三星食水照舊
        await ev("() => { const S = window.__fa.S; S.kit = []; S.stash = ['ration@20','ration@20','ration@20','water','water','water']; S.rescue = {}; S.rescueMiss = {}; S.fakesAtStart = []; S.expiredAtStart = 0; S.castleDone = false; window.__fa.rationPhase(); }")
        seen = []
        for _ in range(40):
            await page.wait_for_selector('#dialog:not([hidden])', timeout=5000)
            seen.append(await page.inner_text('#dText'))
            if '救援報告' in await page.inner_text('#dWho'): break
            await page.click('#dBtns button:first-child'); await page.wait_for_timeout(120)
        blob = '\n'.join(seen)
        r = await ev("() => window.__fa.S.rescue")
        check('T8 留在家裡：不足且有提示', r.get('rations') == 'missing' and r.get('water') == 'missing' and '你把防災包留在家裡了' in blob, str(r))
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(200)
        await ev("() => { const S = window.__fa.S; S.kit = ['ration@20','ration@20','ration@20','water','water','water']; S.stash = []; S.rescue = {guard:'ok',cook:'ok',soldier:'ok'}; S.rescueMiss = {}; S.fakesAtStart = []; window.__fa.rationPhase(); }")
        seen = []
        for _ in range(40):
            await page.wait_for_selector('#dialog:not([hidden])', timeout=5000)
            seen.append(await page.inner_text('#dText'))
            if '救援報告' in await page.inner_text('#dWho'): break
            await page.click('#dBtns button:first-child'); await page.wait_for_timeout(120)
        r = await ev("() => ({r: window.__fa.S.rescue, kit: window.__fa.S.kit})")
        check('T8 背包足夠：食水都 ok、扣除 3+3', r['r'].get('rations') == 'ok' and r['r'].get('water') == 'ok' and r['kit'] == [], str(r))

        # T9 從防災包前走到爺爺家出口（不被防災包擋住）
        await ev("() => { const S = window.__fa.S; S.scene = 'home'; S.pos = {x: 1290, y: 700}; S.kit = []; S.started = true; localStorage.setItem('%s', JSON.stringify(S)); }" % KEY)
        await page.goto(url + '#debug'); await page.reload()
        await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await ev("() => document.getElementById('btnStart').click()"); await page.wait_for_timeout(600)
        # 沿房間中線：先走到門前（x=840，y=704），再直線向下；舊版 BFS 貼牆路徑在門口轉角會卡（舊版也一樣，是測試工具限制）
        pts = [(1290 - 30 * i, 704) for i in range(0, 10)] + [(1000, 704), (950, 740), (900, 780), (880, 830), (870, 880), (870, 920)]
        r = await page.evaluate(WALK_JS, [pts])
        check('T9 實際走路從防災包走到出口並換場景', r['ok'], str(r))
        await b.close()
    print('防災包測試全過' if not fails else f'有 {fails} 項失敗')
    return fails

if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
