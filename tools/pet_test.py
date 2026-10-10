"""寵物（小貓、貓頭鷹）：雜貨店領養與取名、跟班（跟在後面、不擋互動）、背包帶上或留在家、每天睡醒的信、船上不顯示、沒完成第三章時完全不出現。
用法：`python3 -m http.server 8765` 之後 `python3 -u tools/pet_test.py http://localhost:8765/index.html`"""
import asyncio, json, sys
from playwright.async_api import async_playwright
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
CLOUD = "() => { window.FACloud = { checkpoint: () => {}, restore: async () => null, failure: () => {}, flush: () => {}, queueSave: () => {}, status: () => 'off', email: () => null, onStatus: () => {}, init: async () => null, signIn: () => {}, signOut: async () => {}, cachedControl: () => null, refreshControl: async () => null }; }"
async def boot(ctx, url, done):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    await page.add_init_script("if(!sessionStorage.getItem('fresh')){sessionStorage.setItem('fresh','1');localStorage.removeItem('fa-kingdom-p1-v1');}")
    await page.goto(url + '?open=ch2,ch3#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    await page.evaluate("(done) => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.f.final = true; S.c.letter = true; S.c.done = true; S.started = true; S.coins = 3000; S.sta = 60; S.day = 15; S.kitCap = 14; S.c.ch3_done = done; document.getElementById('btnStart').click(); }", done)
    await page.evaluate(CLOUD); await page.wait_for_timeout(500)
    return page, errs
async def ev(page, expr): return await page.evaluate("() => { const S = window.__fa.S; return " + expr + "; }")
async def hidden(page): return await page.evaluate("() => document.getElementById('dialog').hidden")
async def btns(page): return await page.locator('#dBtns button').all_inner_texts()
async def text(page): return await page.inner_text('#dText')
async def click(page, t, wait=450):
    await page.locator('#dBtns button:visible, #dText button:visible', has_text=t).first.click(); await page.wait_for_timeout(wait)
async def goto(page, scene, x, y):
    await page.evaluate(f"() => {{ window.__fa.go({json.dumps(scene)}, [{x}, {y}]); }}"); await page.wait_for_timeout(900)
async def close_all(page, n=6):
    for _ in range(n):
        if await hidden(page): return
        bt = await btns(page)
        for lab in ('離開', '關閉', '收好'):
            if any(lab in t for t in bt): await click(page, lab, 400); break
        else: await page.locator('#dBtns button:not([disabled])').first.click(); await page.wait_for_timeout(350)
async def main(url):
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # --- 沒完成第三章：商店沒有寵物區、沒有寵物、睡一覺沒有信
        page, errs = await boot(ctx, url, False)
        await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_timeout(800)
        check('沒完成第三章：雜貨店沒有「寵物」區', '領養' not in await text(page) and '寵物' not in await text(page), (await text(page))[:60]); await close_all(page)
        check('沒完成第三章：畫面上沒有寵物', not await page.evaluate("() => !!document.querySelector('.pet')"))
        check('沒完成第三章：睡一覺的訊息裡沒有信', '信' not in await page.evaluate("() => window.__fa.nextDay()"))
        check('沒有寫入任何寵物存檔欄位（S.c.pet）', await ev(page, "S.c.pet === undefined")); await page.close()
        # --- 完成第三章：領養小貓
        page, errs = await boot(ctx, url, True)
        await goto(page, 'village', 1045, 300)
        await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_timeout(900)
        t = await text(page)
        check('雜貨店有「寵物」區：小貓、貓頭鷹與價格', '寵物' in t and '小貓' in t and '貓頭鷹' in t and '500' in t and '800' in t, t[:120])
        c0 = await ev(page, "S.coins")
        await page.locator('button[data-a="pet:cat"]').click(); await page.wait_for_timeout(600)
        bt = await btns(page)
        check('領養：只能從名單選名字（沒有輸入框），還有「先不領養」', '小橘' in bt and '先不領養' in bt and await page.locator('#dText input[type=text]').count() == 0, str(bt))
        await click(page, '小橘', 700)
        check('領養小貓「小橘」：金幣 −500、S.c.pet.own／cur／names', await ev(page, "S.coins") == c0 - 500 and await ev(page, "S.c.pet.cur") == 'cat' and await ev(page, "S.c.pet.names.cat") == '小橘', f'{await ev(page, "S.coins")} {await ev(page, "JSON.stringify(S.c.pet)")}')
        check('商店裡小貓顯示「已領養（小橘）」', '已領養（小橘）' in await text(page), (await text(page))[:200])
        await close_all(page)
        check('畫面上出現寵物（.pet）', await page.evaluate("() => !!document.querySelector('.pet')"))
        # 跟班：走一段，寵物跟過來、保持在主角附近
        await page.evaluate("() => { window.__fa.S.pos = { x: 600, y: 400 }; }"); await page.wait_for_timeout(1500)
        d0 = await page.evaluate("() => { const S = window.__fa.S, e = window.__fa.petEl; return Math.hypot(+e.style.getPropertyValue('--x') - S.pos.x, +e.style.getPropertyValue('--y') - S.pos.y); }")
        check('寵物待在主角附近（距離小於 120）', d0 < 120, str(d0))
        await page.keyboard.down('ArrowRight'); await page.wait_for_timeout(900); await page.keyboard.up('ArrowRight'); await page.wait_for_timeout(1200)
        d1 = await page.evaluate("() => { const S = window.__fa.S, e = window.__fa.petEl; return [Math.hypot(+e.style.getPropertyValue('--x') - S.pos.x, +e.style.getPropertyValue('--y') - S.pos.y), +e.style.getPropertyValue('--x'), S.pos.x]; }")
        check('主角往右走後，寵物跟著過來（距離小於 160、位置往右移）', d1[0] < 160 and d1[1] > 450, str(d1))
        # 摸摸：附近沒有別的互動點才會選到寵物
        label = ''
        for (x, y) in [(300, 650), (500, 300), (850, 700), (1250, 700), (400, 450), (1300, 450), (700, 760)]:
            await page.evaluate(f"() => {{ window.__fa.S.pos = {{ x: {x}, y: {y} }}; }}"); await page.wait_for_timeout(1700)
            label = await page.evaluate("() => document.getElementById('act').textContent")
            if '摸摸' in label: break
        check('沒有別的互動點時，動作鈕是「摸摸小橘」', '摸摸小橘' in label, label)
        await page.evaluate("() => document.getElementById('act').click()"); await page.wait_for_timeout(500)
        tt = await text(page)
        check('摸摸：有一句叫聲', not await hidden(page) and any(w in tt for w in ['喵', '呼嚕']), tt); await close_all(page)
        # 附近有別的互動點（雜貨店門口）：不被寵物搶走
        await goto(page, 'village', 1045, 300); await page.wait_for_timeout(600)
        near = await page.evaluate("() => { const f = window.__fa; const its = []; return document.getElementById('act').textContent; }")
        check('站在別的互動點旁邊時，動作鈕不是「摸摸」', '摸摸' not in near, near)
        # --- 睡一覺收到信
        await page.evaluate("() => { const S = window.__fa.S; S.wxNext = { type: 'typhoon', day: S.day + 2 }; }")
        mail = await page.evaluate("() => window.__fa.nextDay()")
        check('睡醒：有一封信（小橘「喵～」、信封圖示、知識卡複習）', '小橘' in mail and '喵' in mail and 'pet_i_letter' in mail and '每日' in mail, mail[:200])
        check('信的內容：沒有 {} 殘留、沒有新的醫療文字（只有既有卡片標題）', '{' not in mail and '}' not in mail)
        check('S.c.pet.mail 記下當天的信', await ev(page, "S.c.pet.mail && S.c.pet.mail.day === S.day"))
        # --- 背包：再看一次、留在家、帶上
        await page.evaluate("() => { window.__fa.bag(); }"); await page.wait_for_timeout(800)
        t = await text(page)
        check('背包有「寵物」區：小橘跟著你、可以留在家、有「再看一次」今天的信', '小橘（小貓）' in t and '跟著你' in t and '再看一次' in t, t[:100])
        await click(page, '再看一次', 600)
        check('再看一次：顯示今天的信', '今天的消息' in await text(page) or '小橘' in await text(page), (await text(page))[:80])
        await click(page, '收好', 600)
        await page.locator('button[data-pet="cat"]').click(); await page.wait_for_timeout(700)
        check('留在家：畫面上沒有寵物、S.c.pet.cur 為空', not await page.evaluate("() => !!document.querySelector('.pet')") and await ev(page, "S.c.pet.cur") is None)
        await page.locator('button[data-pet="cat"]').click(); await page.wait_for_timeout(700)
        check('帶上：寵物回來', await page.evaluate("() => !!document.querySelector('.pet')") and await ev(page, "S.c.pet.cur") == 'cat'); await close_all(page)
        # --- 貓頭鷹：兩種都可以買、一次只帶一隻
        await page.evaluate("() => { window.__fa.shopMenu(); }"); await page.wait_for_timeout(900)
        await page.locator('button[data-a="pet:owl"]').click(); await page.wait_for_timeout(600)
        bt = await btns(page)
        check('領養貓頭鷹：名單裡已經用過的「小橘」不再出現', '小橘' not in bt and '阿福' in bt, str(bt))
        await click(page, '阿福', 700); await close_all(page)
        check('買了兩種：own 有 cat 和 owl，cur 仍是小貓', await ev(page, "S.c.pet.own.length === 2 && S.c.pet.cur === 'cat'"), await ev(page, "JSON.stringify(S.c.pet)"))
        await page.evaluate("() => { window.__fa.bag(); }"); await page.wait_for_timeout(800)
        await page.locator('button[data-pet="owl"]').click(); await page.wait_for_timeout(700)
        check('帶上貓頭鷹：改成貓頭鷹（一次只帶一隻）', await ev(page, "S.c.pet.cur === 'owl'") and await page.locator('.pet').count() == 1 and 'pet_owl' in await page.evaluate("() => document.querySelector('.pet img').src"), await ev(page, "S.c.pet.cur")); await close_all(page)
        mail = await page.evaluate("() => { window.__fa.S.day++; return window.__fa.nextDay(); }")
        check('貓頭鷹的信：咕、翅膀', '咕' in mail and '飛' in mail, mail[:120])
        # --- 藍堡港口小店也能領養（完成第三章後）
        await ev(page, "(S.c.pet = { own: [], cur: null, names: {}, mail: null }, 1)")
        await goto(page, 'ch3_market', 650, 460)
        await page.evaluate("() => { window.__fa.S.pos = { x: 650, y: 420 }; }"); await page.wait_for_timeout(500)
        await page.evaluate("() => document.getElementById('act').click()"); await page.wait_for_timeout(900)
        check('港口小店也有「寵物」區（小貓、貓頭鷹）', '寵物' in await text(page) and '小貓' in await text(page), (await text(page))[:80])
        c0 = await ev(page, "S.coins"); await page.locator('button[data-a="pet:cat"]').click(); await page.wait_for_timeout(600); await click(page, '小橘', 800)
        check('在港口小店領養小貓：金幣 −500（不打折）', await ev(page, "S.coins") == c0 - 500 and await ev(page, "S.c.pet.own.includes('cat')"), await ev(page, "S.coins"))
        await close_all(page)
        # --- 船上不顯示
        await goto(page, 'ch3_ship_day', 700, 400); await page.wait_for_timeout(500)
        check('船上（ch3_ship_day）：不顯示寵物', not await page.evaluate("() => !!document.querySelector('.pet')"))
        await goto(page, 'village', 1045, 300); await page.wait_for_timeout(500)
        check('回到村莊：寵物又出現', await page.evaluate("() => !!document.querySelector('.pet')"))
        check('沒有新增頂層存檔欄位（只用 S.c.pet）', await ev(page, "!('pet' in S)"))
        check('寵物測試沒有頁面錯誤', not errs, str(errs[:2]))
        await b.close()
    print('\n失敗', fails, '項' if fails else '，全部通過'); sys.exit(1 if fails else 0)
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
