"""第二章（熔岩鍛造鎮）＋渡海：整條流程用介面操作跑一遍（網址自動加 ?open=ch2）。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/ch2_test.py http://localhost:8765/index.html`"""
import asyncio, json, os, sys, re
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1

# 題目 → 正確選項（依 V3.2 原型的 ans）；沒列的對話一律按第一個按鈕
ANS = [('阿焰的燙傷屬於哪一種', 1), ('燙傷水泡，應該怎麼處理', 1), ('手背發紅、很痛，但沒有水泡', 0), ('被熱水燙到，應該怎麼處理', 1),
       ('沾到化學清潔劑，第一步', 1), ('阿焰觸電了，第一步', 1), ('阿焰清醒了', 1), ('滅火時要瞄準哪裡', 1), ('你要怎麼說？', 1),
       ('你要大喊什麼', 1), ('要怎麼幫他？', 2), ('哪一種穿法正確', 1), ('暈船了，怎麼做比較好', 1), ('你要怎麼做？', 1),
       ('營火要生在哪裡', 1)]
ORDERS = {'沖': ['沖', '脫', '泡', '蓋', '送'], '拉': ['拉', '瞄', '壓', '掃']}
async def drive(page, limit=120, stop=None, extra=()):
    """一直處理對話框直到關閉；回傳看過的所有文字"""
    seen = []
    for _ in range(limit):
        if await page.evaluate("() => document.getElementById('dialog').hidden"):
            await page.wait_for_timeout(450)  # 場景切換時對話框會暫時關閉，再確認一次
            if await page.evaluate("() => document.getElementById('dialog').hidden"): return seen
            continue
        txt = await page.inner_text('#dText'); seen.append(txt)
        if await page.locator('#oq button').count():
            labels = await page.locator('#oq button').all_inner_texts(); first = labels[0][0]
            order = next(o for k, o in ORDERS.items() if any(l[0] == k for l in labels))
            for ch in order:
                await page.locator('#oq button:not([disabled])', has_text=re.compile('^' + ch + '：')).first.click(); await page.wait_for_timeout(60)
            await page.wait_for_timeout(700); continue
        if await page.locator('#coolBar').count():
            await page.wait_for_function("() => document.getElementById('dialog').hidden || !document.getElementById('coolBar') || document.getElementById('coolBar').style.width === '100%'", timeout=20000)
            await page.wait_for_timeout(400); continue
        btns = page.locator('#dBtns button:not([disabled])'); n = await btns.count()
        pick = 0
        if n > 1:
            for key, i in list(extra) + ANS:
                if key in txt: pick = i; break
        if stop and stop in txt: return seen
        if n == 0: await page.wait_for_timeout(200); continue
        await btns.nth(min(pick, n - 1)).click(); await page.wait_for_timeout(120)
    return seen
async def boot(ctx, url):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")  # 每個測試都從新存檔開始
    await page.goto(url + '?open=ch2#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.started = true; S.coins = 500; document.getElementById('btnStart').click(); }")
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def act(page, kind=None):
    await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(150)
async def goto(page, scene, x, y):
    await page.evaluate(f"() => window.__fa.go({json.dumps(scene)}, [{x}, {y}])"); await page.wait_for_timeout(700)
async def talk(page, id):
    await page.evaluate(f"() => {{ window.__fa.talk({json.dumps(id)}); }}"); await page.wait_for_timeout(250)
    return await drive(page)
async def near_act(page, scene, x, y, wait=250):
    await goto(page, scene, x, y); await page.wait_for_timeout(wait)
    await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(250)
async def east_exit(page, letter):
    await page.evaluate(f"() => {{ const S = window.__fa.S; S.c.letter = {str(letter).lower()}; window.__fa.go('plain', [1300, 680]); }}"); await page.wait_for_timeout(800)
    await page.keyboard.down('ArrowRight'); await page.wait_for_timeout(2500); await page.keyboard.up('ArrowRight'); await page.wait_for_timeout(600)
async def plain_exit_tests(ctx, url):
    page, errs = await boot(ctx, url)
    await east_exit(page, False)
    txt = await page.inner_text('#dText') if not await page.evaluate("() => document.getElementById('dialog').hidden") else ''
    check('章節開放、還沒收到信：東方草原東邊被擋下並提示', '等收到老鐵的信' in txt and await st(page, 'S.scene') == 'plain', txt)
    await drive(page, limit=3)
    await east_exit(page, True)
    check('收到信後：從東方草原走到東邊進入漁港', await st(page, 'S.scene') == 'ch2_port', await st(page, 'S.scene'))
    check('出口測試沒有頁面錯誤', not errs, str(errs)); await page.close()
async def story_tests(ctx, url):
    page, errs = await boot(ctx, url)
    await page.evaluate("() => { const S = window.__fa.S; S.c.letter = true; S.c.intro = true; S.kit = ['gauze']; S.kitCap = 14; S.coins = 300; }")
    # 老鐵燙傷 → 阿焰水泡 → 消防隊長（拿滅火器）
    await goto(page, 'ch2_smithy', 835, 860); await talk(page, 'ch2_smith')
    check('老鐵：燙傷處理完成、獲得知識卡、好感度', await st(page, "S.c.smith === true && !!S.cards.burn && S.hearts.ch2_smith === 1"))
    await talk(page, 'ch2_appr')
    check('阿焰：水泡處理完成', await st(page, "S.c.appr === true && !!S.cards.ch2_blister && !!S.cards.ch2_degree"))
    await goto(page, 'ch2_town', 860, 700); await talk(page, 'ch2_cap')
    check('消防隊長：教滅火器、送滅火器、開始設備檢查', await st(page, "S.c.cap === true && S.c.checking === true && S.kit.includes('ch2_extinguisher')"))
    # 設備檢查：滅火器（壓力正常）與壞掉的警報器各走一次介面
    await near_act(page, 'ch2_town', 900, 470)
    await drive(page, extra=[('看看壓力表的指針', 0)])
    await near_act(page, 'ch2_inn2', 520, 600)
    await drive(page, extra=[('沒有任何聲音', 1)])
    n = await st(page, 'Object.keys(S.c.chk || {}).length')
    check('設備檢查：介面操作 2 處完成', n == 2 and await st(page, "!!S.c.chk.c_town && !!S.c.chk.c_inn2a"), str(n))
    await page.evaluate("() => { const S = window.__fa.S; ['c_smithy', 'c_inn', 'c_inn2e'].forEach(k => S.c.chk[k] = true); }")
    await goto(page, 'ch2_town', 860, 700); await talk(page, 'ch2_cap')
    check('設備檢查回報：+60 金幣、警報器知識卡、checking 結束', await st(page, "S.c.checking === false && S.coins === 360 && !!S.cards.ch2_alarm"))
    # 旅館：燙傷與化學灼傷
    await goto(page, 'ch2_inn', 560, 600); await talk(page, 'ch2_innk')
    check('旅館老闆娘：兩題＋化學灼傷處理完成', await st(page, "S.c.inn === true && !!S.cards.ch2_cool && !!S.cards.ch2_chem && S.coins === 400"))
    # 砂輪機 → 觸電
    await goto(page, 'ch2_smithy', 835, 860); await talk(page, 'ch2_appr')
    check('阿焰觸電事件完成', await st(page, "S.c.elec === true && !!S.cards.ch2_elec"))
    # 倉庫線索
    await page.evaluate("() => { window.__fa.go('ch2_town', [1100, 560]); }"); await page.wait_for_timeout(700)
    await near_act(page, 'ch2_town', 1180, 560); await drive(page)
    check('倉庫線索：S.c.clue', await st(page, 'S.c.clue === true'))
    # 鍛造與採礦（熔岩礦坑的鐵礦）
    await page.evaluate("() => { const S = window.__fa.S; S.tools.pick = true; S.sta = 100; }")
    await goto(page, 'ch2_lavamine', 830, 880)
    for _ in range(3): await page.evaluate("() => { window.__fa.mine(0); }"); await page.wait_for_timeout(500); await drive(page, limit=3)
    check('熔岩礦坑：敲 3 下得到鐵礦石（S.mat.ch2_iron）', await st(page, '(S.mat.ch2_iron || 0) === 1'), await st(page, 'JSON.stringify(S.mat)'))
    await page.evaluate("() => { window.__fa.S.mat.ch2_iron = 3; }")
    await near_act(page, 'ch2_smithy', 560, 540); await page.wait_for_selector('#dBtns button'); await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300); await drive(page, limit=3)
    check('鍛造：3 鐵礦石 → 1 鐵錠', await st(page, '(S.mat.ch2_ingot || 0) === 1 && S.mat.ch2_iron === 0'))
    # 旅館住宿
    d0 = await st(page, 'S.day'); c0 = await st(page, 'S.coins')
    await near_act(page, 'ch2_inn2', 780, 500); await page.wait_for_selector('#dBtns button'); await page.click('#dBtns button:first-child'); await page.wait_for_timeout(1500); await drive(page, limit=5)
    check('旅館住一晚：-20 金幣、進入下一天', await st(page, 'S.day') == d0 + 1 and await st(page, 'S.coins') == c0 - 20)
    # 章末大火
    await page.evaluate("() => { const S = window.__fa.S; S.kit = ['gauze', 'ch2_extinguisher']; S.coins = 100; }")
    await goto(page, 'ch2_town', 860, 700); await talk(page, 'ch2_cap')
    check('章末：消防隊長帶去大火現場', await st(page, "S.c.fire === true && S.scene === 'ch2_townfire'"), await st(page, 'S.scene'))
    await talk(page, 'ch2_cap')
    await talk(page, 'ch2_appr')
    await talk(page, 'ch2_smith')
    await page.evaluate("() => window.__fa.go('ch2_inn2', [650, 700])"); await page.wait_for_timeout(700)
    await talk(page, 'ch2_guest')
    await page.evaluate("() => window.__fa.go('ch2_townfire', [860, 860])"); await page.wait_for_timeout(700)
    await near_act(page, 'ch2_townfire', 1180, 560); await drive(page, limit=60)
    r = await st(page, "({r_119: S.c.r_119, r_ext: S.c.r_ext, r_clothes: S.c.r_clothes, r_smith: S.c.r_smith, r_guest: S.c.r_guest})")
    check('大火五項任務都完成且處置正確', all(v == 'ok' for v in r.values()), str(r))
    await talk(page, 'ch2_appr')  # 五項都完成後，跟消防隊長以外的人說話就會出現救援報告
    check('救援報告：第二章完成、5 顆星', await st(page, 'S.c.done === true && S.c.stars === 5'), await st(page, 'JSON.stringify(S.c)'))
    check('第二章劇情沒有頁面錯誤', not errs, str(errs)); await page.close()
async def stash_trip(ctx, url):
    page, errs = await boot(ctx, url)
    await page.evaluate("() => { const S = window.__fa.S; S.c.letter = true; S.kit = []; S.stash = ['ration@50', 'ration@50', 'ration@50', 'water', 'water', 'water']; S.coins = 200; S.day = 3; }")
    await goto(page, 'ch2_port', 1000, 600)
    await page.evaluate("() => { window.__fa.talk('ch2_capt'); }"); await page.wait_for_selector('#dBtns button'); await page.click('#dBtns button:first-child')
    await drive(page, limit=10, stop='要帶上防災包嗎')
    await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
    check('買票後詢問帶不帶防災包：帶上 → stashAt = carry', await st(page, "S.stashAt") == 'carry')
    await drive(page, limit=6)
    for _ in range(8):
        if await st(page, 'S.scene') != 'ch2_deck': break
        await page.evaluate("() => { window.__fa.S.pos = {x: 1000, y: 590}; }")
        await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(300)
        await drive(page, limit=40)
    r = await st(page, "({scene: S.scene, stash: S.stash.length, kit: S.kit.length, coins: S.coins})")
    check('兩晚後到碼頭：自帶的 2 包乾糧＋2 瓶水取自防災包、沒花錢買補給', r['scene'] == 'ch2_vport' and r['stash'] == 2 and r['coins'] == 170, str(r))
    await goto(page, 'ch2_inn2', 650, 700)
    await page.evaluate("() => { window.__fa.stashMenu(); }"); await page.wait_for_selector('#dBtns button')
    await page.click('#dBtns button:first-child'); await page.wait_for_selector('#dText h4')
    check('到旅館把防災包放下：stashAt = ch2', await st(page, 'S.stashAt') == 'ch2')
    check('防災包測試沒有頁面錯誤', not errs, str(errs)); await page.close()
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        page, errs = await boot(ctx, url)
        r = await page.evaluate("() => ({ch: window.__fa.CHAPTERS.ch2, reg: Object.keys(window.__fa.REGIONS), n: Object.keys(window.__fa.SCENES).length, hs: Object.keys(window.__fa.S.hearts).filter(k => k.startsWith('ch2_'))})")
        check('?open=ch2：第二章載入、有 20 個場景、5 位角色有好感度欄位', r['ch']['open'] and r['reg'] == ['ch2'] and r['n'] == 20 and len(r['hs']) == 5, str(r))
        # --- 序章接點：爺爺的信
        await page.evaluate("() => window.__fa.go('home', [840, 770])"); await page.wait_for_timeout(600)
        g = await page.inner_text('#goal')
        check('序章完成、還沒收到信：目標提示回家找爺爺', '好像有一封信' in g, g)
        txts = await talk(page, 'grandpa')
        check('爺爺給信：提到鍛造鎮與搭船、S.c.letter = true', any('老鐵寄信' in t for t in txts) and any('搭船' in t for t in txts) and await st(page, 'S.c.letter') is True, str(txts[-2:]))
        await page.evaluate("() => window.__fa.refresh()"); g = await page.inner_text('#goal')
        check('收到信後目標：去漁港搭船', '漁港，搭船前往熔岩鍛造鎮' in g, g)
        check('收到信後世界地圖鈕出現', await page.evaluate("() => !document.getElementById('btnMap').hidden"))
        # --- 渡海：不帶補給
        await page.evaluate("() => { const S = window.__fa.S; S.kit = []; S.coins = 100; }")
        await goto(page, 'ch2_port', 1000, 600)
        await page.evaluate("() => { window.__fa.talk('ch2_capt'); }"); await page.wait_for_selector('#dBtns button')
        txt = await page.inner_text('#dText')
        check('船長：船票 30、乾糧 40、開水 30', '30 金幣' in txt and '乾糧 40' in txt and '開水 30' in txt, txt)
        await drive(page, stop='再準備一下') if False else None
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
        await drive(page, limit=6)  # 救生衣題（答對後）與起錨
        await page.wait_for_timeout(500)
        sc = await st(page, 'S.scene'); v = await st(page, 'S.voyage')
        check('買票上船：到甲板、S.voyage 兩晚、金幣 -30', sc == 'ch2_deck' and v and v['left'] == 2 and await st(page, 'S.coins') == 70, f'{sc} {v}')
        check('看過救生衣知識卡', await st(page, "!!S.cards.ch2_lifejacket"))
        # 船艙休息：暈船題 → 落水 → 兩晚
        for _ in range(8):
            if await st(page, 'S.scene') != 'ch2_deck': break
            await page.evaluate("() => { window.__fa.go; }")
            await page.evaluate("() => { window.__fa.S.pos = {x: 1000, y: 590}; }")
            await page.evaluate("() => { document.getElementById('act').click(); }"); await page.wait_for_timeout(300)
            await drive(page, limit=40)
        sc = await st(page, 'S.scene')
        check('兩晚後抵達火山島碼頭', sc == 'ch2_vport', sc)
        coins = await st(page, 'S.coins'); sta = await st(page, 'S.sta')
        check('沒帶補給：向船長買了乾糧和開水（2 晚共 140 金幣），金幣 70 不夠 → 扣體力', coins >= 0 and sta < 100, f'coins={coins} sta={sta}')
        check('暈船、落水知識卡', await st(page, "!!S.cards.ch2_seasick && !!S.cards.ch2_overboard"))
        check('第一次抵達碼頭：老鐵迎接 S.c.intro', await st(page, 'S.c.intro') is True)
        check('第二章場景目標與地區', 'ch2' == await page.evaluate("() => window.__fa.curRegion().id") and '鐵匠鋪' in await page.inner_text('#goal'))
        check('渡海沒有頁面錯誤', not errs, str(errs))
        await page.close()
        await plain_exit_tests(ctx, url)
        await story_tests(ctx, url)
        await stash_trip(ctx, url)
        await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('第二章測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
