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
        'npcs': [{'id': 'chtest_npc', 'x': 800, 'y': 500}], 'things': [], 'exits': [ex]}
    w('chtest/chapter.json', {'id': 'chtest', 'files': {'scenes': 'scenes.json', 'characters': 'characters.json',
        'dialogues': 'dialogues.json', 'walks': 'walks.json'}, 'assets': []})
    w('chtest/scenes.json', {
        'chtest_a': sc(0, {'to': 'chtest_b', 'at': [400, 450], 'block': None, 'test': '(x,y)=>x<30', 'need': None}),
        'chtest_b': sc(0, {'to': 'chclosed_x', 'at': [400, 450], 'block': None, 'test': '(x,y)=>x<30', 'need': None})})
    w('chtest/characters.json', {'PEOPLE': {'chtest_npc': {'name': '測試村民', 'img': 'guard', 'face': 'guard_face', 'hk': 1}}})
    w('chtest/dialogues.json', {'say': {}, 'quizzes': {}, 'text': {'chtest_hello': '你好，這是假章節。'}})
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
async def main(url):
    make_fixtures()
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
        await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
        # 1) 預設（沒有 chbase）：只有序章，沒有章節
        page, errs, logs = await boot(ctx, url)
        r = await page.evaluate("() => ({ch: Object.keys(window.__fa.CHAPTERS), scenes: Object.keys(window.__fa.SCENES).length})")
        check('預設只載入序章（11 個場景、沒有章節）', r == {'ch': [], 'scenes': 11}, str(r))
        check('預設沒有頁面錯誤', not errs, str(errs)); await page.close()
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
        check('回村莊後沒有頁面錯誤', not errs, str(errs)); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html'))
print('章節框架測試全過' if not fails else f'{fails} 項失敗'); sys.exit(1 if fails else 0)
