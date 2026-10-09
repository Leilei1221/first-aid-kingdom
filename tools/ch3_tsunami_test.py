"""第三章海嘯警報選配支線（老師 2026-10-09 同意做，K4-3、Q4-4 文字照草稿）：第 4 節做完後，港口救生員選單多一項「海嘯警報」：聽警報（鳴 5、停 5、鳴 5，可跳過）→ Q4-4 → 知識卡 K4-3。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch3_tsunami_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, pathlib
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
ROOT = pathlib.Path(__file__).parent.parent
Q = json.load(open(ROOT / 'chapters/ch3/dialogues.json', encoding='utf-8'))['quizzes']['ch3_q4_4']
CARD = json.load(open(ROOT / 'chapters/ch3/cards.json', encoding='utf-8'))['CARDS']['ch3_k4_3']
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820}); await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
        await page.goto(url + '?open=ch2,ch3#debug'); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
        await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.c.ch3_met = true; S.started = true; S.coins = 300; S.sta = 100; S.day = 5; ['ch3_k1_3','ch3_k2_3','ch3_k3_1','ch3_k3_3'].forEach(k => S.cards[k] = true); document.getElementById('btnStart').click(); window.__ch3Tune = {alarm: {ms: 900}, clear: {ms: 700}}; window.__audioSrc = []; const A0 = window.Audio; window.Audio = function (src) { window.__audioSrc.push(String(src)); return new A0(src); }; }")
        await page.wait_for_timeout(500)
        st = lambda e: page.evaluate("() => { const S = window.__fa.S; return " + e + "; }")
        async def talk():
            await page.evaluate("() => { window.__fa.go('ch3_harbor', [1250, 800]); }"); await page.wait_for_timeout(800)
            await page.evaluate("() => { window.__fa.S.pos = {x: 1250, y: 800}; }"); await page.wait_for_timeout(300)
            await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(400)
        btns = lambda: page.locator('#dBtns button').all_inner_texts()
        async def click(label):
            await page.locator('#dBtns button', has_text=label).first.click(); await page.wait_for_timeout(300)
        # 第 4 節沒做完：沒有「海嘯警報」
        await talk(); m = await btns()
        check('第 4 節還沒做完：救生員選單沒有「海嘯警報」', '海嘯警報' not in m and '請教救生員' in m, str(m)); await click('先離開')
        await page.evaluate("() => { window.__fa.S.cards.ch3_k4_4 = true; }")
        await talk(); m = await btns()
        check('第 4 節做完後：選單有「海嘯警報」', m == ['請教救生員', '海嘯警報', '聊聊', '先離開'], str(m))
        await click('海嘯警報'); t = await page.inner_text('#dText')
        check('救生員邀請聽警報聲', '海嘯警報' in t and '聽聽看' in '|'.join(await btns()), t)
        await click('聽聽看'); t = await page.inner_text('#dText')
        srcs = await page.evaluate("() => window.__audioSrc")
        check('警報：播放中字樣，並且載入了老師提供的真實錄音（ch3_tsunami_alarm.m4a）', '警報聲播放中' in t and any('ch3_tsunami_alarm.m4a' in x for x in srcs), f'{t} {srcs}')
        await page.wait_for_function("() => document.getElementById('dText').innerText.includes('請所有民眾迅速往高處疏散')", timeout=6000)
        check('錄音播完才出語音字幕：「海嘯警報，請所有民眾迅速往高處疏散」（草稿原文）', True)
        await page.wait_for_function("(q) => document.getElementById('dText').innerText.includes(q)", arg=Q['q'], timeout=8000)
        check('警報播完自動進到 Q4-4', True)
        wrong = (Q['ans'] + 1) % len(Q['opts']); await page.locator('#dBtns button').nth(wrong).click(); await page.wait_for_timeout(300)
        t = await page.inner_text('#dText'); check('答錯：說「這個做法不對」並顯示解析', '不對' in t and Q['explain'] in t, t); await click('再選一次')
        await page.locator('#dBtns button').nth(Q['ans']).click(); await page.wait_for_timeout(300)
        t = await page.inner_text('#dText'); check('答對：顯示解析', '處置正確' in t and Q['explain'] in t, t); await click('繼續')
        t = await page.inner_text('#dText')
        check('知識卡 K4-3：標題、「鳴 5 秒、停 5 秒，反覆 9 遍，共 85 秒；解除一長聲 90 秒」與其他三行', CARD['title'] in t and '鳴 5 秒、停 5 秒，反覆 9 遍，共 85 秒' in t and '解除警報音：一長聲 90 秒' in t and '不開車逃' in t and '往海邊看看浪有多大再決定' in t, t)
        check('知識卡記進存檔', await st('!!S.cards.ch3_k4_3'))
        await click('關閉') if await page.locator('#dBtns button', has_text='關閉').count() else await page.locator('#dBtns button').first.click()
        await page.wait_for_timeout(400)
        t = await page.inner_text('#dText'); check('知識卡後：救生員問要不要聽解除警報音', '解除' in t and '聽聽解除警報音' in '|'.join(await btns()), t)
        await click('聽聽解除警報音'); t = await page.inner_text('#dText')
        check('解除警報音：一長聲（共 90 秒），可以跳過', '一長聲' in t and '90 秒' in t and '跳過' in '|'.join(await btns()), t)
        await page.wait_for_function("() => document.getElementById('dBtns').innerText.includes('先離開') || document.getElementById('dBtns').innerText.includes('海嘯警報')", timeout=6000)
        m = await btns(); check('說完回到選單', '海嘯警報' in m and '先離開' in m, str(m))
        # 跳過
        await click('海嘯警報'); await click('聽聽看'); await click('跳過')
        t = await page.inner_text('#dText'); check('警報可以跳過，直接到 Q4-4', Q['q'] in t, t)
        check('沒有 JS 錯誤', not errs, str(errs))
        await b.close()
    print('失敗', fails); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1]))
