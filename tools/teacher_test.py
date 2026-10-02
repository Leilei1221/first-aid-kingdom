"""老師端進度頁測試：用模擬的資料驗證畫面、統計、權限提示與 CSV 匯出。
用法：python3 -m http.server 8765（專案根目錄）後，python3 tools/teacher_test.py http://localhost:8765/teacher.html"""
import asyncio, json, sys
from playwright.async_api import async_playwright

def api_js(user, teacher, classes, students, saves):
    return f"""
    window.__faTeacherApi = {{
      async user() {{ return {json.dumps(user)}; }}, signIn() {{}}, async signOut() {{}},
      async isTeacher() {{ return {json.dumps(teacher)}; }},
      async classes(uid) {{ return {json.dumps(classes)}; }},
      async students(cid) {{ return {json.dumps(students)}[cid] || []; }},
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
   'state': {'day': 9, 'step': 10, 'coins': -100, 'cards': {}, 'hearts': {}, 'f': {'p3': True, 'tablet': True, 'hunter': True, 'guard': True, 'final': True}, 'castleDone': True, 'castleBest': 5}},
  {'email': 's110003@hlhs.hlc.edu.tw', 'updated_at': '2026-10-01T02:00:00+00:00', 'state': {'day': 1, 'step': 1, 'coins': 0, 'cards': {'legend': True}, 'hearts': {}, 'f': {}}},
  {'email': 's120001@hlhs.hlc.edu.tw', 'updated_at': '2026-10-01T02:00:00+00:00', 'state': {'day': 3, 'step': 5, 'coins': 5, 'cards': {}, 'hearts': {}, 'f': {}}},
]

async def main(url):
    res = []
    def check(name, ok, extra=''):
        res.append(ok); print(('✓' if ok else '✗'), name, '' if ok else extra)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        async def page_for(user, teacher, classes=CLASSES):
            ctx = await b.new_context(viewport={'width': 390, 'height': 800}, accept_downloads=True)
            await ctx.add_init_script(api_js(user, teacher, classes, STUDENTS, SAVES))
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
        check('CSV 的姓名逸出正確（含 < > 的名字）', '李<b>大華</b>' in data)
        check('頁面沒有 JS 錯誤', not errs, str(errs))
        r = await pg.evaluate("() => ['{}', '{\"c\":{\"letter\":true}}', '{\"c\":{\"letter\":true,\"intro\":true}}', '{\"c\":{\"done\":true,\"stars\":4}}'].map(j => window.FATeacher.summarize(JSON.parse(j), 20).ch2)")
        check('第二章狀態：未開始／已收到信／進行中／已完成（4★）', [x['label'] for x in r] == ['', '已收到信', '進行中', '已完成'] and r[3]['stars'] == 4, str(r))
        check('CSV 標題含第二章欄位', lines[0].endswith('第二章,第二章星數'), lines[0])

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
