"""天災與野外事件（D4-3）：颱風（避難／戶外選擇／雨衣／失溫）、山洪、濃霧、溺水、裝溪水、體力耗盡昏倒；嚴重錯誤走救援失敗。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/wild_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys, re
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
async def boot(ctx, url, extra='', rand=None):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    if rand is not None: await page.add_init_script(f"Math.random = () => {rand};")
    await page.goto(url + extra + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.started = true; S.coins = 500; S.sta = 100; S.day = 5; S.kitCap = 14; document.getElementById('btnStart').click(); }")
    await page.wait_for_timeout(500)
    return page, errs
async def st(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def idle(page, ms=700):
    for _ in range(40):
        await page.wait_for_timeout(ms // 4)
    return
async def wait_dialog(page, text=None, t=8000):
    await page.wait_for_function("(tx) => !document.getElementById('dialog').hidden && (!tx || document.getElementById('dText').innerText.includes(tx))", arg=text, timeout=t)
async def pick(page, i):
    await page.locator('#dBtns button:not([disabled])').nth(i).click(); await page.wait_for_timeout(180)
async def finish(page, n=40):
    out = []
    for _ in range(n):
        if await page.evaluate("() => document.getElementById('dialog').hidden"):
            await page.wait_for_timeout(1200)
            if await page.evaluate("() => document.getElementById('dialog').hidden"): return out
            continue
        out.append(await page.inner_text('#dText'))
        if await page.locator('#oq button').count():
            labels = await page.locator('#oq button').all_inner_texts()
            for key in ['叫：大聲呼救', '叫：打 119', '伸：', '拋：', '划：']:
                await page.locator('#oq button:not([disabled])', has_text=key).first.click(); await page.wait_for_timeout(80)
            await page.wait_for_timeout(700); continue
        await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(150)
    return out
async def start_go(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(600)
async def day_of(page, type_):
    await page.evaluate(f"() => {{ window.__fa.scheduleWx('{type_}'); window.__fa.nextDay(); }}")
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # ---- 颱風：馬上回室內
        page, errs = await boot(ctx, url, '?open=ch2')
        await day_of(page, 'typhoon'); await start_go(page, 'village', 1045, 330); await wait_dialog(page, '狂風暴雨')
        await pick(page, 0); await finish(page)
        check('颱風天走到戶外：選「馬上回到室內避難」→ 回爺爺家', await st(page, "S.scene") == 'home' and await st(page, "!!S.wxHit.village"), await st(page, 'S.scene'))
        # ---- 颱風：留在戶外選大樹（嚴重錯誤）
        await start_go(page, 'forest', 950, 300); await wait_dialog(page, '狂風暴雨'); await pick(page, 1)
        await wait_dialog(page, '要躲在哪裡'); c0 = await st(page, 'S.coins'); await pick(page, 0)
        t = await finish(page)
        check('颱風躲大樹：救援失敗、扣救援費、顯示颱風知識卡', any('失去了意識' in x for x in t) and any('颱風來時' in x for x in t) and await st(page, 'S.coins') == c0 - 200, str(t)[:200])
        # ---- 颱風：答對；沒雨衣 → 失溫題
        await start_go(page, 'farm', 865, 120); await wait_dialog(page, '狂風暴雨'); await pick(page, 1)
        await wait_dialog(page, '要躲在哪裡'); await pick(page, 2); await wait_dialog(page, '處置正確'); await pick(page, 0)
        await wait_dialog(page, '沒有雨衣，全身都濕透'); s0 = await st(page, 'S.sta')
        check('沒有雨衣：全身濕透、體力 -20', s0 <= 80, str(s0))
        await pick(page, 0); await wait_dialog(page, '一直發抖')
        await pick(page, 0)  # 繼續工作＝嚴重錯誤
        t = await finish(page)
        check('失溫繼續工作：救援失敗（失溫）', any('體溫越來越低' in x for x in t), str(t)[:200])
        # ---- 帶雨衣
        await page.evaluate("() => { window.__fa.S.kit = ['raincoat']; }")
        await start_go(page, 'mine_out', 400, 420); await wait_dialog(page, '狂風暴雨'); await pick(page, 1)
        await wait_dialog(page, '要躲在哪裡'); await pick(page, 2); t = await finish(page)
        check('有雨衣：保持乾燥、沒有失溫題', any('還好有穿雨衣' in x for x in t), str(t)[:200])
        check('颱風測試沒有頁面錯誤', not errs, str(errs)); await page.close()
        # ---- 山洪
        page, errs = await boot(ctx, url)
        await day_of(page, 'flood'); await start_go(page, 'river', 60, 440); await wait_dialog(page, '混濁'); await pick(page, 0)
        await wait_dialog(page, '該怎麼做'); c0 = await st(page, 'S.coins'); await pick(page, 0); t = await finish(page)
        check('山洪：走上橋看 → 救援失敗＋山洪知識卡', any('被捲走' in x for x in t) and any('山洪暴發的徵兆' in x for x in t) and await st(page, 'S.coins') == c0 - 200, str(t)[:200])
        await start_go(page, 'river', 60, 440); await page.wait_for_timeout(300)
        await page.evaluate("() => { window.__fa.S.wxHit = {}; }")
        await start_go(page, 'plain', 60, 400); await start_go(page, 'river', 60, 440); await wait_dialog(page, '混濁'); await pick(page, 0)
        await wait_dialog(page, '該怎麼做'); await pick(page, 2); await finish(page)
        check('山洪答對：撤離到村莊、得到知識卡', await st(page, "S.scene") == 'village' and await st(page, "!!S.cards.flood"), await st(page, 'S.scene'))
        check('山洪測試沒有頁面錯誤', not errs, str(errs)); await page.close()
        # ---- 濃霧（有哨子）
        page, errs = await boot(ctx, url)
        await page.evaluate("() => { window.__fa.S.kit = ['whistle']; }")
        await day_of(page, 'fog'); await start_go(page, 'forest', 950, 300); await wait_dialog(page, '濃霧'); await pick(page, 0)
        await wait_dialog(page, '第一步該怎麼做'); await pick(page, 1); await wait_dialog(page, '處置正確'); await pick(page, 0); await wait_dialog(page, '背包裡有哨子'); await pick(page, 0); await finish(page)
        check('濃霧：停下來＋吹哨子 → 回村莊、兩張知識卡', await st(page, "S.scene") == 'village' and await st(page, "!!S.cards.lost && !!S.cards.signal"))
        check('濃霧測試沒有頁面錯誤', not errs, str(errs)); await page.close()
        # ---- 溺水與裝溪水（野外項目要開 ?wild=1）
        page, errs = await boot(ctx, url, '?wild=1', rand=0)
        await start_go(page, 'river', 60, 440); await wait_dialog(page, '小芽在溪邊玩水'); await pick(page, 0); await wait_dialog(page, '不太會游泳'); await pick(page, 0)  # 跳下水
        await wait_dialog(page, '救溺', 100) if False else None
        t = await finish(page)
        check('溺水跳下水：救援失敗（溺水）、這件事可以重來', any('被水捲走' in x for x in t) and await st(page, '!S.f.drown'), str(t)[:200])
        await start_go(page, 'plain', 60, 400); await start_go(page, 'river', 60, 440); await wait_dialog(page, '小芽在溪邊玩水'); await pick(page, 0); await wait_dialog(page, '不太會游泳'); await pick(page, 1)
        t = await finish(page)
        check('溺水：叫叫伸拋划 → 得到過溪知識卡、好感度', await st(page, "!!S.cards.cross && S.f.drown === true"), str(t)[:200])
        await page.evaluate("() => { window.__fa.S.mat.rawwater = 0; }")
        await page.evaluate("() => { window.__fa.go('river', [560, 520]); }"); await page.wait_for_timeout(800)
        r = await page.evaluate("() => { document.getElementById('act').click(); return true; }"); await page.wait_for_timeout(500)
        await finish(page)
        check('河谷「裝溪水」：得到井水 1 份和野外找水知識卡', await st(page, "(S.mat.rawwater || 0) === 1 && !!S.cards.riverwater"), await st(page, 'JSON.stringify([S.mat.rawwater, S.cards.riverwater])'))
        check('溺水與溪水測試沒有頁面錯誤', not errs, str(errs)); await page.close()
        # ---- 野外項目預設關閉
        page, errs = await boot(ctx, url, '', rand=0)
        await start_go(page, 'river', 60, 440); await page.wait_for_timeout(800)
        check('預設（WILD 關閉）：河谷沒有溺水事件', await page.evaluate("() => document.getElementById('dialog').hidden") and await st(page, '!S.f.drown'))
        check('預設：阿鹿的高山症支線不出現', await page.evaluate("() => { const S = window.__fa.S; S.hearts.hunt = 3; return true; }") and await st(page, '!S.story.hunt'))
        # ---- 體力耗盡
        await page.evaluate("() => { window.__fa.go('home', [840, 770]); }"); await page.wait_for_timeout(700)
        await page.evaluate("() => { window.__fa.faint('exhaust'); }"); await wait_dialog(page, '眼前突然')
        t = await finish(page, 20)
        check('體力耗盡昏倒：顯示專屬說明（體力完全耗盡）', any('體力完全耗盡' in x for x in t), str(t)[:200])
        check('預設測試沒有頁面錯誤', not errs, str(errs)); await page.close(); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('野外事件測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
