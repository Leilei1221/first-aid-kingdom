"""老師端進度頁測試：用模擬的資料驗證畫面、統計、權限提示與 CSV 匯出。
用法：python3 -m http.server 8765（專案根目錄）後，python3 tools/teacher_test.py http://localhost:8765/teacher.html"""
import asyncio, json, sys
from playwright.async_api import async_playwright

def api_js(user, teacher, classes, students, saves, failures=(), ctl_error=False):
    return f"""
    window.__ctl = {{}}; window.__ctlLog = [];
    window.__faTeacherApi = {{
      async user() {{ return {json.dumps(user)}; }}, signIn() {{}}, async signOut() {{}},
      async isTeacher() {{ return {json.dumps(teacher)}; }},
      async classes(uid) {{ return {json.dumps(classes)}; }},
      async students(cid) {{ return {json.dumps(students)}[cid] || []; }},
      async failures(emails) {{ const all = {json.dumps(list(failures))}; return all.filter(r => emails.includes(r.email)); }},
      async flags(cid) {{ if ({json.dumps(ctl_error)}) throw new Error('no table'); const s = (window.__ctl[cid] || {{}}).flags || {{}}; return Object.entries(s).map(([flag, enabled]) => ({{flag, enabled}})); }},
      async setFlag(cid, flag, enabled) {{ const s = window.__ctl[cid] = window.__ctl[cid] || {{flags: {{}}, weather: []}}; s.flags[flag] = enabled; window.__ctlLog.push(['flag', cid, flag, enabled]); }},
      async weather(cid) {{ return ((window.__ctl[cid] || {{}}).weather || []).slice().reverse(); }},
      async publishWeather(cid, type) {{ const s = window.__ctl[cid] = window.__ctl[cid] || {{flags: {{}}, weather: []}}; s.weather.push({{id: s.weather.length + 1, type, cancelled: false, published_at: '2026-10-02T06:30:00+00:00'}}); window.__ctlLog.push(['wx', cid, type]); }},
      async cancelWeather(id) {{ for (const s of Object.values(window.__ctl)) s.weather.forEach(w => {{ if (w.id == id) w.cancelled = true; }}); window.__ctlLog.push(['cancel', id]); }},
      async saves(emails) {{ const all = {json.dumps(saves)}; return all.filter(r => emails.includes(r.email)); }}
    }};"""

CLASSES = [{'id': 'c1', 'name': '多元選修A', 'grade': 2}, {'id': 'c2', 'name': '多元選修B', 'grade': 2}]
STUDENTS = {
  'c1': [
    {'id': 's1', 'student_no': '110001', 'seat_no': 1, 'name': '王小明', 'email': 's110001@hlhs.hlc.edu.tw', 'login_email': None},
    {'id': 's2', 'student_no': '110002', 'seat_no': 2, 'name': '李<b>大華</b>', 'email': 's110002@hlhs.hlc.edu.tw', 'login_email': None},
    {'id': 's3', 'student_no': '110003', 'seat_no': 3, 'name': '陳小美', 'email': 'x@y.z', 'login_email': 's110003@hlhs.hlc.edu.tw'},
    {'id': 's4', 'student_no': '110004', 'seat_no': 4, 'name': '林尚未', 'email': 's110004@hlhs.hlc.edu.tw', 'login_email': None},
  ],
  'c2': [{'id': 's9', 'student_no': '120001', 'seat_no': 1, 'name': '黃別班', 'email': 's120001@hlhs.hlc.edu.tw', 'login_email': None}],
}
SAVES = [
  {'email': 's110001@hlhs.hlc.edu.tw', 'updated_at': '2026-10-01T01:00:00+00:00',
   'state': {'day': 5, 'step': 10, 'coins': 120, 'cards': {'a': 1, 'b': 1, 'c': 1}, 'hearts': {'grandpa': 3, 'kid': 1}, 'f': {'p3': True, 'tablet': True}, 'castleBest': 0}},
  {'email': 's110002@hlhs.hlc.edu.tw', 'updated_at': '2026-09-30T01:00:00+00:00',
   'state': {'day': 9, 'step': 10, 'coins': -100, 'cards': {}, 'hearts': {}, 'f': {'p3': True, 'tablet': True, 'hunter': True, 'guard': True, 'final': True}, 'castleDone': True, 'castleBest': 5, 'c': {'ch3_done': True, 'ch3_stars': 5}}},
  {'email': 's110003@hlhs.hlc.edu.tw', 'updated_at': '2026-10-01T02:00:00+00:00', 'state': {'day': 1, 'step': 1, 'coins': 0, 'cards': {'legend': True}, 'hearts': {}, 'f': {}}},
  {'email': 's120001@hlhs.hlc.edu.tw', 'updated_at': '2026-10-01T02:00:00+00:00', 'state': {'day': 3, 'step': 5, 'coins': 5, 'cards': {}, 'hearts': {}, 'f': {}}},
]

FAILS = [
  {'email': 's110001@hlhs.hlc.edu.tw', 'scenario': 'flood', 'choice': '走到橋上看清楚一點', 'created_at': '2026-10-01T03:00:00+00:00'},
  {'email': 's110001@hlhs.hlc.edu.tw', 'scenario': 'flood', 'choice': '走到橋上看清楚一點', 'created_at': '2026-10-01T04:00:00+00:00'},
  {'email': 's110002@hlhs.hlc.edu.tw', 'scenario': 'flood', 'choice': '沿著溪谷往下游跑', 'created_at': '2026-10-01T05:00:00+00:00'},
  {'email': 's110002@hlhs.hlc.edu.tw', 'scenario': 'typhoon', 'choice': '大樹下面，可以擋雨', 'created_at': '2026-10-01T05:30:00+00:00'},
  {'email': 's120001@hlhs.hlc.edu.tw', 'scenario': 'typhoon', 'choice': '別班的不算', 'created_at': '2026-10-01T06:00:00+00:00'},
]
async def main(url):
    res = []
    def check(name, ok, extra=''):
        res.append(ok); print(('✓' if ok else '✗'), name, '' if ok else extra)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        async def page_for(user, teacher, classes=CLASSES, ctl_error=False):
            ctx = await b.new_context(viewport={'width': 390, 'height': 800}, accept_downloads=True)
            await ctx.add_init_script(api_js(user, teacher, classes, STUDENTS, SAVES, FAILS, ctl_error))
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(url); return pg, errs
        T = {'id': 'u1', 'email': 'teacher@hlhs.hlc.edu.tw'}

        pg, errs = await page_for(T, True)
        await pg.wait_for_selector('#app:not([hidden])', timeout=20000); await pg.wait_for_selector('details.st')
        txt = await pg.inner_text('#app')
        check('班級下拉只有自己的班', await pg.locator('#cls option').count() == 2)
        check('統計：3 / 4 人已開始', '3 / 4' in txt, txt[:200])
        check('未開始的學生顯示「尚未開始」', '林尚未' in txt and '尚未開始' in txt)
        row3 = await pg.locator('details.st').nth(2).inner_text()
        check('login_email 優先於 email 對應存檔', '陳小美' in row3 and '第 1 天' in row3 and '尚未開始' not in row3, row3)
        row2 = await pg.locator('details.st').nth(1).inner_text()
        check('欠款以「欠款」標示', '欠款' in row2 and '-100' in row2, row2)
        check('通關與星數顯示', '5' in row2 and '序章完成' in row2, row2)
        check('姓名內的 HTML 被跳脫，不會變成標籤', await pg.locator('#list b', has_text='大華').count() == 0 and '<b>大華</b>' in await pg.inner_text('#list'))
        row1 = await pg.locator('details.st').nth(0).inner_text()
        check('第 1 位：第 5 天、知識卡 3、進度%', '第 5 天' in row1 and '知識卡 3' in row1 and '%' in row1, row1)
        no_scroll = await pg.evaluate("() => document.documentElement.scrollWidth <= document.documentElement.clientWidth")
        check('手機寬度沒有橫向捲動', no_scroll)
        # 切換班級
        await pg.select_option('#cls', 'c2'); await pg.wait_for_function("document.getElementById('list').innerText.includes('黃別班')")
        check('切換班級後只顯示該班學生', '王小明' not in await pg.inner_text('#list'))
        await pg.select_option('#cls', 'c1'); await pg.wait_for_function("document.getElementById('list').innerText.includes('王小明')")
        # CSV
        async with pg.expect_download() as dl:
            await pg.click('#btnCsv')
        d = await dl.value; path = await d.path(); data = open(path, 'rb').read().decode('utf-8-sig')
        lines = data.strip().split('\r\n')
        check('CSV 有標題列與 4 位學生', len(lines) == 5 and lines[0].startswith('班級,座號,學號,姓名'), data[:200])
        check('CSV 含尚未開始與欠款數字', '尚未開始' in data and ',-100' in data, data)
        lt = await pg.inner_text('#list'); st_ = await pg.inner_text('#sum')
        check('第三章：完成者顯示「第三章 已完成 5★」，沒進第三章的不顯示', '第三章 已完成 5★' in lt and lt.count('第三章') == 1, lt)
        check('統計有「完成第三章」與「章末拿到 5 顆星」各 1 人', '完成第三章' in st_ and '第三章章末拿到 5 顆星' in st_, st_)
        check('CSV 第三章欄位：完成者「已完成,5」', data.count(',已完成,5') == 1, data)
        check('CSV 的姓名逸出正確（含 < > 的名字）', '李<b>大華</b>' in data)
        ftxt = await pg.inner_text('#fails')
        check('全班最常犯的錯：山洪 2 人 3 次排第一、颱風 1 人 1 次（別班不算）', '山洪徵兆時走上橋或沿溪谷跑' in ftxt and '2 人、3 次' in ftxt and '1 人、1 次' in ftxt and ftxt.index('山洪') < ftxt.index('颱風'), ftxt)
        check('最常選的答案：走到橋上看清楚一點', '最常選：走到橋上看清楚一點' in ftxt, ftxt)
        check('頁面沒有 JS 錯誤', not errs, str(errs))
        r = await pg.evaluate("() => ['{}', '{\"c\":{\"letter\":true}}', '{\"c\":{\"letter\":true,\"intro\":true}}', '{\"c\":{\"done\":true,\"stars\":4}}'].map(j => window.FATeacher.summarize(JSON.parse(j), 20).ch2)")
        check('第二章狀態：未開始／已收到信／進行中／已完成（4★）', [x['label'] for x in r] == ['', '已收到信', '進行中', '已完成'] and r[3]['stars'] == 4, str(r))
        check('CSV 標題含第二、三、四章欄位', lines[0].endswith('第二章,第二章星數,第三章,第三章星數,第四章,第四章星數'), lines[0])
        r4 = await pg.evaluate("() => ['{}', '{\"c\":{\"ch4\":{\"arrived\":true}}}', '{\"cards\":{\"ch4_k1_1\":true}}', '{\"c\":{\"ch4\":{\"done\":true,\"stars\":4}}}', '{\"c\":{\"ch3_done\":true,\"ch3_stars\":5}}'].map(j => window.FATeacher.summarize(JSON.parse(j), 20).ch4)")
        check('第四章狀態：未開始／到過雪嶺／有第四章知識卡／已完成（4★）；第三章的星數不會算進第四章', [x['label'] for x in r4] == ['', '進行中', '進行中', '已完成', ''] and r4[3]['stars'] == 4 and r4[4]['stars'] == 0, str(r4))
        r3 = await pg.evaluate("() => ['{}', '{\"c\":{\"ch3_intro\":true}}', '{\"cards\":{\"ch3_k1_1\":true}}', '{\"c\":{\"ch3_done\":true,\"ch3_stars\":5}}', '{\"c\":{\"done\":true,\"stars\":4}}'].map(j => window.FATeacher.summarize(JSON.parse(j), 20).ch3)")
        check('第三章狀態：未開始／到過藍堡／有第三章知識卡／已完成（5★）；第二章的星數不會算進第三章', [x['label'] for x in r3] == ['', '進行中', '進行中', '已完成', ''] and r3[3]['stars'] == 5 and r3[4]['stars'] == 0, str(r3))

        # --- 班級控制
        ct = await pg.inner_text('#ctrl')
        check('班級控制：第二章預設開啟、第三章／第四章／野外項目／村長救災預設關閉', '第二章（熔岩鍛造鎮）' in ct and '開啟（預設）' in ct and ct.count('關閉（預設）') == 4 and '第四章（雪嶺）' in ct, ct)
        await pg.click('button[data-flag="wild"]'); await pg.wait_for_function("document.getElementById('ctrl').innerText.includes('野外項目')")
        await pg.wait_for_timeout(300)
        ct = await pg.inner_text('#ctrl'); log = await pg.evaluate("() => window.__ctlLog")
        check('開啟野外項目：寫入設定、畫面改成「開啟」（不再是預設）', log[-1] == ['flag', 'c1', 'wild', True] and '野外項目\n開啟\n' in ct.replace('\n\n', '\n'), str(log) + ct)
        await pg.click('button[data-flag="ch2"]'); await pg.wait_for_timeout(300)
        check('關閉第二章：寫入設定', (await pg.evaluate("() => window.__ctlLog"))[-1] == ['flag', 'c1', 'ch2', False] and '第二章（熔岩鍛造鎮）\n關閉' in (await pg.inner_text('#ctrl')).replace('\n\n', '\n'))
        pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await pg.click('button[data-wx="typhoon"]'); await pg.wait_for_function("document.getElementById('ctrl').innerText.includes('目前公告：颱風')", timeout=5000)
        check('發布颱風（確認後）：顯示目前公告、有「取消」鈕', await pg.locator('button[data-cancel]').count() == 1)
        await pg.click('button[data-cancel]'); await pg.wait_for_function("document.getElementById('ctrl').innerText.includes('沒有進行中的公告')", timeout=5000)
        check('取消公告：回到沒有公告', await pg.locator('button[data-cancel]').count() == 0)
        await pg.select_option('#cls', 'c2'); await pg.wait_for_function("document.getElementById('list').innerText.includes('黃別班')")
        ct = await pg.inner_text('#ctrl')
        check('切換班級：另一班的設定不受影響（仍是預設）', ct.count('（預設）') == 5, ct)
        await pg.select_option('#cls', 'c1'); await pg.wait_for_function("document.getElementById('list').innerText.includes('王小明')")
        pgE, _ = await page_for(T, True, ctl_error=True)
        await pgE.wait_for_selector('#app:not([hidden])', timeout=20000); await pgE.wait_for_selector('details.st')
        check('資料表還沒建：班級控制顯示說明，進度頁照常', '002_fa_class_control.sql' in await pgE.inner_text('#ctrl') and await pgE.locator('details.st').count() >= 3)
        pg2, _ = await page_for(T, False)
        await pg2.wait_for_selector('#status:not([hidden])'); await pg2.wait_for_timeout(300)
        check('非老師帳號顯示沒有權限，且不載入名單', '沒有老師端權限' in await pg2.inner_text('#status') and await pg2.locator('#app:not([hidden])').count() == 0)
        pg3, _ = await page_for(None, False)
        await pg3.wait_for_selector('#btnIn', timeout=10000)
        check('未登入顯示登入按鈕', True)
        pg4, _ = await page_for(T, True, classes=[])
        await pg4.wait_for_selector('#status:not([hidden])'); await pg4.wait_for_timeout(300)
        check('沒有班級時顯示說明', '沒有屬於您的班級' in await pg4.inner_text('#status'))
        await b.close()
    n = res.count(False); print('全部通過' if not n else f'{n} 項失敗', f'（共 {len(res)} 項）'); return n

if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/teacher.html')) else 0)
