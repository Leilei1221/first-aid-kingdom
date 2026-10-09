"""章節框架（D1）測試：用假章節驗證載入、前綴檢查、關閉章節擋入口、存檔所在章節消失時回村莊。
假章節資料由本檔產生在 tools/fixtures/chapters/（只在 #debug 且帶 ?chbase= 才會被遊戲讀取）。
用法：`python3 -m http.server 8765` 之後 `python3 tools/chapter_test.py http://localhost:8765/index.html`"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FX = os.path.join(ROOT, 'tools/fixtures/chapters')
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
def w(path, obj):
    path = os.path.join(FX, path); os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
def make_fixtures():
    walks = json.load(open(os.path.join(ROOT, 'data/walks.json')))['plain']
    w('index.json', [{'id': 'chtest', 'name': '測試章', 'open': True}, {'id': 'chclosed', 'name': '關閉章', 'open': False},
                     {'id': 'chbad', 'name': '壞章', 'open': True}])
    sc = lambda nx, ex: {'name': '測試場景', 'spawn': [400, 450], 'bg': 'plain', 'heroH': 130,
        'npcs': [{'id': 'chtest_npc', 'x': 800, 'y': 500}], 'things': [{'kind': 'stash', 'x': 600, 'y': 450, 'label': '防災包'}], 'exits': [ex]}
    w('chtest/chapter.json', {'id': 'chtest', 'files': {'scenes': 'scenes.json', 'characters': 'characters.json',
        'dialogues': 'dialogues.json', 'walks': 'walks.json'}, 'assets': [],
        'region': {'name': '測試地區', 'pin': [13, 68], 'unlock': '()=>S.c.go===true', 'center': {'scene': 'chtest_a', 'at': [400, 450]},
                   'home': {'scene': 'chtest_b', 'at': [400, 450]}, 'travelHint': '測試用：搭船過去。', 'goal': "()=>'測試目標：走到出口'",
                   'wake': {'other': 'chtest_wake', 'mushroom': 'chtest_wake'}}})
    w('chtest/scenes.json', {
        'chtest_a': sc(0, {'to': 'chtest_b', 'at': [400, 450], 'block': None, 'test': '(x,y)=>x<30', 'need': None}),
        'chtest_b': sc(0, {'to': 'chclosed_x', 'at': [400, 450], 'block': None, 'test': '(x,y)=>x<30', 'need': None})})
    w('chtest/characters.json', {'PEOPLE': {'chtest_npc': {'name': '測試村民', 'img': 'guard', 'face': 'guard_face', 'hk': 1}}})
    w('chtest/dialogues.json', {'say': {'chtest_wake': [{'p': 'hero', 'lines': ['你在測試地區的房間醒來。']}]}, 'quizzes': {}, 'text': {'chtest_hello': '你好，這是假章節。'}})
    w('chtest/walks.json', {'chtest_a': walks, 'chtest_b': walks})
    w('chbad/chapter.json', {'id': 'chbad', 'files': {'scenes': 'scenes.json'}})
    w('chbad/scenes.json', {'oops_no_prefix': {'name': 'x', 'spawn': [1, 1], 'bg': 'plain', 'heroH': 100, 'npcs': [], 'things': [], 'exits': []}})
async def boot(ctx, url, chbase=None):
    page = await ctx.new_page(); errs = []; page.on('pageerror', lambda e: errs.append(str(e)))
    logs = []; page.on('console', lambda m: logs.append(m.text) if m.type == 'error' else None)
    await page.goto(url + ('?chbase=' + chbase if chbase else '') + '#debug')
    await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    return page, errs, logs
async def start(page):
    await page.evaluate("() => { const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.started = true; document.getElementById('btnStart').click(); }")
    await page.wait_for_timeout(500)
async def walk_left(page):
    await page.wait_for_timeout(600)
    await page.evaluate("() => { window.__fa.S.pos = {x: 150, y: 400}; }")
    await page.keyboard.down('ArrowLeft'); await page.wait_for_timeout(1500); await page.keyboard.up('ArrowLeft')
    await page.wait_for_timeout(500)
async def dismiss(page, n=40):
    for _ in range(n):
        if await page.evaluate("() => document.getElementById('dialog').hidden"): return
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(120)
async def region_tests(ctx, url):
    # 預設：沒有地區、地圖鈕不顯示、新欄位有預設值
    page, errs, logs = await boot(ctx, url); await start(page)
    r = await page.evaluate("() => ({map: document.getElementById('btnMap').hidden, c: window.__fa.S.c, w: window.__fa.S.wounds, at: window.__fa.S.stashAt, a: window.__fa.mapAvail()})")
    check('預設：世界地圖鈕不顯示、S.c／S.wounds／S.stashAt 有預設值', r == {'map': True, 'c': {}, 'w': {}, 'at': 'base', 'a': False}, str(r))
    # 舊存檔（沒有新欄位）讀入後補預設值
    await page.evaluate("() => { const o = JSON.parse(JSON.stringify(window.__fa.S)); delete o.c; delete o.wounds; delete o.stashAt; localStorage.setItem('fa-kingdom-p1-v1', JSON.stringify(o)); }")
    await page.reload(); await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
    r = await page.evaluate("() => ({c: window.__fa.S.c, w: window.__fa.S.wounds, at: window.__fa.S.stashAt})")
    check('舊存檔讀入後補 c／wounds／stashAt', r == {'c': {}, 'w': {}, 'at': 'base'}, str(r))
    # 商店：地區沒開放時沒有哨子等
    await start(page)
    await page.evaluate("() => { window.__fa.S.step = 7; window.__fa.S.coins = 100; window.__fa.shopMenu(); }"); await page.wait_for_selector('#dText button[data-a]')
    txt = await page.inner_text('#dText')
    check('地區未開放：商店沒有哨子、手電筒、雨衣', not any(k in txt for k in ['哨子', '手電筒', '雨衣']))
    await dismiss(page)
    # 傷口圖：say 帶 wound 會顯示圖、記入圖鑑
    await page.evaluate("() => { window.__fa.say({p: 'hero', wound: 'bee', html: '<p>測試</p>'}); }"); await page.wait_for_selector('#dText figure img')
    r = await page.evaluate("() => ({src: document.querySelector('#dText figure img').getAttribute('src'), cap: !!document.querySelector('#dText figcaption'), seen: window.__fa.S.wounds})")
    check('傷口圖顯示並記入圖鑑', r == {'src': 'assets/w_bee.webp', 'cap': True, 'seen': {'bee': True}}, str(r))
    await dismiss(page)
    await page.evaluate("() => { window.__fa.cards(); }"); await page.wait_for_selector('#dText h4')
    check('知識卡頁顯示傷口圖鑑 1/15', '傷口圖鑑 1/15' in await page.inner_text('#dText'))
    await dismiss(page)
    check('預設地區測試沒有頁面錯誤', not errs, str(errs)); await page.close()
    # 假地區
    page, errs, logs = await boot(ctx, url, '/tools/fixtures/chapters'); await start(page)
    r = await page.evaluate("() => ({r: Object.keys(window.__fa.REGIONS), a: window.__fa.mapAvail(), hid: document.getElementById('btnMap').hidden})")
    check('地區條件未達成：地圖鈕不顯示', r == {'r': ['chtest'], 'a': False, 'hid': True}, str(r))
    await page.evaluate("() => { window.__fa.S.c.go = true; window.__fa.S.step = 7; window.__fa.S.coins = 100; window.__fa.shopMenu(); }")
    await page.wait_for_selector('#dText button[data-a]')
    txt = await page.inner_text('#dText')
    check('地區開放後：商店出現哨子、手電筒、雨衣', all(k in txt for k in ['哨子', '手電筒', '雨衣']))
    await dismiss(page)
    await page.evaluate("() => window.__fa.go('village', [1045, 300])"); await page.wait_for_timeout(800)
    check('條件達成後地圖鈕出現', await page.evaluate("() => !document.getElementById('btnMap').hidden"))
    # 世界地圖：點別的地區顯示怎麼過去
    await page.click('#btnMap'); await page.wait_for_selector('#dText button[data-r]')
    check('世界地圖有兩個地區按鈕（綠葉谷、測試地區）', await page.locator('#dText button[data-r]').count() == 2)
    await page.click('#dText button[data-r]:has-text("測試地區")'); await page.wait_for_timeout(300)
    check('點未到的地區顯示前往方式', '搭船過去' in await page.inner_text('#dText'))
    await dismiss(page)
    # 目前所在地區點下去：回中心地點
    await page.evaluate("() => window.__fa.go('chtest_b', [400, 450])"); await page.wait_for_timeout(800)
    check('章節場景的目標改用地區的目標文字', '測試目標' in await page.inner_text('#goal'))
    await page.click('#btnMap'); await page.wait_for_selector('#dText button[data-r]')
    await page.click('#dText button[data-r]:has-text("目前")'); await page.wait_for_timeout(1000)
    check('點目前地區：回到該地區的中心地點', await page.evaluate("() => window.__fa.S.scene") == 'chtest_a')
    # 防災包位置：在別的地區打不開，要先帶上再放下
    await page.evaluate("() => window.__fa.go('chtest_b', [400, 450])"); await page.wait_for_timeout(800)
    await page.evaluate("() => { window.__fa.stashMenu(); }"); await page.wait_for_selector('#dialog:not([hidden])')
    check('防災包不在這個地區：顯示放在綠葉谷', '放在綠葉谷' in await page.inner_text('#dText'))
    await dismiss(page)
    await page.evaluate("() => window.__fa.go('home', [420, 660])"); await page.wait_for_timeout(800)
    await page.evaluate("() => { window.__fa.stashDepart(); }"); await page.wait_for_selector('#dBtns button')
    await page.click('#dBtns button:first-child'); await page.wait_for_timeout(300)
    check('出發前選「帶上防災包」：stashAt = carry', await page.evaluate("() => window.__fa.S.stashAt") == 'carry')
    await page.evaluate("() => window.__fa.go('chtest_b', [400, 450])"); await page.wait_for_timeout(800)
    await page.evaluate("() => { window.__fa.stashMenu(); }"); await page.wait_for_selector('#dBtns button')
    check('帶著防災包到住處：詢問放在這裡', '放在這裡' in await page.inner_text('#dText'))
    await page.click('#dBtns button:first-child'); await page.wait_for_selector('#dText h4')
    check('放下後：stashAt = 地區 id、開啟防災包畫面', await page.evaluate("() => window.__fa.S.stashAt") == 'chtest' and '家中防災包' in await page.inner_text('#dText'))
    await dismiss(page)
    # 昏倒：在測試地區醒在該地區的住處，並用該地區的醒來對話
    await page.evaluate("() => { window.__fa.S.sta = 0; window.__fa.faint('work'); }")
    for _ in range(60):
        if 'chtest_b' == await page.evaluate("() => window.__fa.S.scene") and '測試地區的房間' in (await page.evaluate("() => document.getElementById('dText').innerText")): break
        await page.wait_for_timeout(150)
        if not await page.evaluate("() => document.getElementById('dialog').hidden"): await page.click('#dBtns button:first-child')
    r = await page.evaluate("() => window.__fa.S.scene")
    check('在測試地區昏倒：醒在該地區的住處', r == 'chtest_b', r)
    await dismiss(page)
    check('地區測試沒有頁面錯誤', not errs, str(errs)); await page.close()
async def main(url):
    make_fixtures()
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # 1) 預設（沒有 chbase）：只有序章，沒有章節
        page, errs, logs = await boot(ctx, url)
        r = await page.evaluate("() => ({ch: Object.keys(window.__fa.CHAPTERS), scenes: Object.keys(window.__fa.SCENES).length})")
        IDX_OPEN = json.load(open(os.path.join(ROOT, 'chapters/index.json')))[0]['open']
        check('預設載入序章與第二章資料（章節一律載入，開放與否在執行時判斷）', r == {'ch': ['ch2', 'ch3', 'ch4'], 'scenes': 38}, str(r))
        check('預設沒有頁面錯誤', not errs, str(errs))
        # 第二章關閉時，東方草原東邊的出口擋下並提示「還沒開放」
        await start(page)
        await page.evaluate("() => { window.__fa.go('plain', [1300, 680]); }"); await page.wait_for_timeout(800)
        await page.keyboard.down('ArrowRight'); await page.wait_for_timeout(2500); await page.keyboard.up('ArrowRight'); await page.wait_for_timeout(600)
        txt = await page.inner_text('#dText') if not await page.evaluate("() => document.getElementById('dialog').hidden") else ''
        check('東方草原東邊被擋下並留在草原（開放：等收到信；關閉：還沒開放）', ('等收到老鐵的信' if IDX_OPEN else '還沒開放') in txt and await page.evaluate("() => window.__fa.S.scene") == 'plain', txt)
        await page.close()
        # 2) 假章節
        page, errs, logs = await boot(ctx, url, '/tools/fixtures/chapters')
        r = await page.evaluate("() => ({ch: window.__fa.CHAPTERS, s: Object.keys(window.__fa.SCENES).filter(k => k.startsWith('ch') || k.startsWith('oops'))})")
        check('開放的章節載入、關閉的只留紀錄', r['ch']['chtest']['open'] and not r['ch']['chclosed']['open'], str(r))
        check('章節場景合併進 SCENES', sorted(r['s']) == ['chtest_a', 'chtest_b'], str(r))
        check('前綴不符的章節整章略過（沒有 oops_no_prefix）、不影響其他章', 'oops_no_prefix' not in r['s'] and not r['ch']['chbad']['open'], str(r))
        check('前綴不符會在 console 留下錯誤訊息', any('chbad' in l for l in logs), str(logs))
        check('章節文字可讀取', await page.evaluate("() => window.__fa.T('chtest_hello')") == '你好，這是假章節。')
        await start(page)
        await page.evaluate("() => window.__fa.go('chtest_a', [400, 450])"); await page.wait_for_timeout(800)
        check('可以切換到章節場景', await page.evaluate("() => window.__fa.S.scene") == 'chtest_a')
        check('章節 NPC 出現在場景', await page.locator('.npc').count() >= 1)
        # 走到出口：chtest_a → chtest_b
        await walk_left(page)
        check('走到出口換到章節的下一個場景', await page.evaluate("() => window.__fa.S.scene") == 'chtest_b')
        # chtest_b 的出口通往關閉的章節：擋住並提示
        await walk_left(page); await page.wait_for_selector('#dialog:not([hidden])', timeout=5000)
        txt = await page.inner_text('#dText')
        check('關閉章節的入口顯示「還沒開放」', '還沒開放' in txt, txt)
        await page.click('#dBtns button:first-child'); await page.wait_for_timeout(500)
        r = await page.evaluate("() => ({s: window.__fa.S.scene, x: window.__fa.S.pos.x})")
        check('被擋下後留在原場景、位置退回出口外', r['s'] == 'chtest_b' and r['x'] > 30, str(r))
        # 存檔：把存檔場景改成章節場景，再用「沒有章節」的設定重開
        await page.evaluate("() => { window.__fa.save(); }")
        raw = await page.evaluate("() => localStorage.getItem('fa-kingdom-p1-v1')")
        check('存檔記下章節場景', json.loads(raw)['scene'] == 'chtest_b')
        check('章節測試沒有頁面錯誤', not errs, str(errs)); await page.close()
        page, errs, logs = await boot(ctx, url)
        r = await page.evaluate("() => ({s: window.__fa.S.scene, ok: !!window.__fa.SCENES[window.__fa.S.scene]})")
        check('存檔在已不存在的章節：讀檔後回到村莊', r == {'s': 'village', 'ok': True}, str(r))
        check('回村莊後沒有頁面錯誤', not errs, str(errs)); await page.close()
        await region_tests(ctx, url)
        await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('章節框架測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
