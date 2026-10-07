"""雲端存檔測試：用「模擬的雲端」（由本腳本扮演 Supabase）驗證登入後的同步、衝突、共用裝置、存檔點與救援失敗。
用法：python3 -m http.server 8765（專案根目錄）後，python3 tools/cloud_test.py http://localhost:8765/index.html
注意：這測的是遊戲端的邏輯；真正的 Supabase／Google 登入需要資料表建好、後台設定完成後另外實測。"""
import asyncio, json, sys
from playwright.async_api import async_playwright

MOCK_JS = r"""
(() => {
  window.__mockEmail = localStorage.getItem('mock-email');
  const call = async (op, args) => {
    const r = await fetch('/__mock', { method: 'POST', body: JSON.stringify({ op, ...args }) });
    if (!r.ok) throw new Error('offline');
    const j = await r.json(); if (j.error) { const e = new Error(j.error); e.code = j.code; throw e; } return j.v;
  };
  window.__faRemote = {
    async user() { return window.__mockEmail ? { email: window.__mockEmail } : null; },
    async signIn() {}, async signOut() { localStorage.removeItem('mock-email'); },
    load: e => call('load', { e }), insert: (e, state) => call('insert', { e, state }),
    update: (e, state, expected) => call('update', { e, state, expected }),
    checkpoint: (e, day, state) => call('checkpoint', { e, day, state }),
    loadCheckpoint: (e, day) => call('loadCheckpoint', { e, day }),
    clearCheckpoints: e => call('clearCheckpoints', { e }),
    failure: (e, scenario, choice) => call('failure', { e, scenario, choice }),
  };
  setInterval(() => { const d = document.getElementById('dialog'); if (d && !d.hidden && window.__autoclick) {
    const b = document.querySelector('#dBtns button:not([disabled])'); if (b) b.click(); } }, 30);
})();
"""

class Cloud:
    def __init__(self): self.saves = {}; self.cps = {}; self.failures = []; self.n = 0; self.offline = False
    def ts(self): self.n += 1; return f'2026-01-01T00:00:00.{self.n:06d}+00:00'
    def handle(self, d):
        op = d['op']; e = d.get('e')
        if op == 'load': return {'v': self.saves.get(e)}
        if op == 'insert':
            if e in self.saves: return {'error': 'dup', 'code': '23505'}
            self.saves[e] = {'state': d['state'], 'updated_at': self.ts()}; return {'v': self.saves[e]['updated_at']}
        if op == 'update':
            row = self.saves.get(e)
            if not row or row['updated_at'] != d['expected']: return {'v': None}
            self.saves[e] = {'state': d['state'], 'updated_at': self.ts()}; return {'v': self.saves[e]['updated_at']}
        if op == 'checkpoint': self.cps[(e, d['day'])] = d['state']; return {'v': None}
        if op == 'loadCheckpoint':
            days = sorted(k[1] for k in self.cps if k[0] == e and k[1] <= d['day'])
            return {'v': self.cps[(e, days[-1])] if days else None}
        if op == 'clearCheckpoints':
            for k in [k for k in self.cps if k[0] == e]: del self.cps[k]
            return {'v': None}
        if op == 'failure': self.failures.append((e, d['scenario'], d['choice'])); return {'v': None}
        return {'error': 'unknown'}

async def main(url):
    cloud = Cloud(); results = []
    def check(name, ok, extra=''):
        results.append(ok); print(('✓' if ok else '✗'), name, extra if not ok else '')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        async def device(email=None):
            ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
            async def route(r):
                if cloud.offline: await r.fulfill(status=500, body='offline'); return
                await r.fulfill(json=cloud.handle(json.loads(r.request.post_data)))
            await ctx.route('**/__mock', route)
            await ctx.add_init_script("localStorage.setItem('fa-debug','1');")
            await ctx.add_init_script(MOCK_JS)
            page = await ctx.new_page()
            if email:
                await page.goto(url); await page.evaluate(f"localStorage.setItem('mock-email','{email}')")
            return ctx, page
        async def open_(page, wait_btn=True):
            await page.goto(url + '#debug'); await page.reload()
            await page.wait_for_function("window.__fa && window.FACloud", timeout=60000)
            await page.wait_for_function("!document.getElementById('btnStart').disabled", timeout=30000)
            await page.wait_for_timeout(300)
        ALICE = 'alice@hlhs.hlc.edu.tw'; BOB = 'bob@hlhs.hlc.edu.tw'
        S = lambda page, expr: page.evaluate(f"() => window.__fa.S.{expr}")

        # T1：A 裝置登入、遊玩、上傳
        ctxA, A = await device(ALICE); await open_(A)
        check('T1 登入後顯示已登入', 'alice' in await A.inner_text('#authBox'))
        await A.click('#btnStart'); await A.wait_for_timeout(200)
        await A.evaluate("() => { window.__autoclick = true; }"); await A.wait_for_timeout(2500)
        await A.evaluate("() => { const S = window.__fa.S; S.coins = 77; S.step = 2; window.__fa.save(); return window.FACloud.flush(); }")
        await A.wait_for_timeout(500)
        check('T1 雲端收到進度', ALICE in cloud.saves and cloud.saves[ALICE]['state']['coins'] == 77, str(cloud.saves.keys()))

        # T2：B 裝置同帳號 → 採用雲端
        ctxB, B = await device(ALICE); await open_(B)
        check('T2 換裝置取得雲端進度', await S(B, 'coins') == 77 and await S(B, 'step') == 2)
        check('T2 按鈕顯示繼續冒險', (await B.inner_text('#btnStart')).strip() == '繼續冒險')

        # T3：B 更新 → A 重新整理，無本機變更 → 靜默採用雲端
        await B.evaluate("() => { const S = window.__fa.S; S.coins = 99; window.__fa.save(); return window.FACloud.flush(); }"); await B.wait_for_timeout(400)
        await open_(A)
        check('T3 較新的雲端進度自動套用', await S(A, 'coins') == 99)

        # T4：A 離線改動（dirty），B 上線推進 → A 重新上線時提示衝突
        cloud.offline = True
        await A.evaluate("() => { const S = window.__fa.S; S.coins = 5; window.__fa.save(); return window.FACloud.flush(); }"); await A.wait_for_timeout(300)
        cloud.offline = False
        await B.evaluate("() => { const S = window.__fa.S; S.coins = 123; window.__fa.save(); return window.FACloud.flush(); }"); await B.wait_for_timeout(400)
        await A.goto(url + '#debug'); await A.reload()
        await A.wait_for_function("window.__fa && window.FACloud", timeout=60000)
        await A.wait_for_selector('#dialog:not([hidden])', timeout=15000)
        txt = await A.inner_text('#dText')
        check('T4 兩邊都有變動時跳出選擇', '進度不一致' in await A.inner_text('#dWho') and '雲端' in txt and '這台裝置' in txt, txt)
        await A.click('#dBtns button:nth-child(2)')       # 用這台裝置
        await A.wait_for_function("!document.getElementById('btnStart').disabled", timeout=15000); await A.wait_for_timeout(500)
        check('T4 選這台裝置後雲端被更新', cloud.saves[ALICE]['state']['coins'] == 5, str(cloud.saves[ALICE]['state']['coins']))

        # T5：共用裝置，登出後換 Bob，不會看到 Alice 的進度
        await A.evaluate("() => { return window.FACloud.signOut(); }")
        await A.evaluate(f"() => {{ localStorage.removeItem('fa-kingdom-p1-v1'); localStorage.setItem('mock-email','{BOB}'); }}")
        await open_(A)
        check('T5 新帳號拿到全新進度', await S(A, 'coins') == 0 and ALICE not in (await A.inner_text('#authBox')))

        # T6：存檔點與救援失敗
        await A.click('#btnStart'); await A.evaluate("() => { window.__autoclick = true; }"); await A.wait_for_timeout(2500)
        await A.evaluate("() => { const S = window.__fa.S; S.day = 2; S.coins = 50; S.step = 3; window.__fa.checkpoint(); }"); await A.wait_for_timeout(300)
        check('T6 雲端有第 2 天存檔點', (BOB, 2) in cloud.cps)
        await A.evaluate("() => { const S = window.__fa.S; S.coins = 500; S.cards.bee = true; }")
        await A.evaluate("() => window.__fa.rescueFail({scenario:'flood', choice:'走上橋', intro:'你被洪水捲走，失去了意識……', cardKey:'water'})")
        check('T6 回到早上並扣 200 金幣', await S(A, 'coins') == 50 - 200 and await S(A, 'day') == 2, str(await S(A, 'coins')))
        check('T6 學到的知識卡保留', await A.evaluate("() => !!window.__fa.S.cards.water && !!window.__fa.S.cards.bee"))
        check('T6 失敗被記錄', (BOB, 'flood', '走上橋') in cloud.failures, str(cloud.failures))

        # T7：未登入也能玩，不呼叫雲端
        ctxC, C = await device(None); before = (len(cloud.saves), len(cloud.cps))
        await open_(C); await C.click('#btnStart'); await C.evaluate("() => { window.__autoclick = true; }"); await C.wait_for_timeout(2500)
        await C.evaluate("() => { window.__fa.S.coins = 9; window.__fa.save(); }"); await C.wait_for_timeout(300)
        check('T7 未登入可遊玩且不寫雲端', (len(cloud.saves), len(cloud.cps)) == before and await S(C, 'coins') == 9)
        check('T7 顯示登入按鈕', await C.locator('#btnLogin').count() == 1)

        # T8：登入時雲端連不上 → 仍可遊玩
        cloud.offline = True
        ctxD, D = await device(ALICE); await open_(D)
        check('T8 離線時仍可開始遊戲', not await D.evaluate("() => document.getElementById('btnStart').disabled"))
        await D.click('#btnStart'); await D.wait_for_timeout(800)
        check('T8 狀態顯示離線', await D.evaluate("() => window.FACloud.status()") == 'offline')
        # T9：標題畫面有登出鈕；登出後回到未登入、可換帳號
        ctxE, E = await device(ALICE); await open_(E)
        check('T9 標題畫面有登出鈕', await E.locator('#btnLogout').count() == 1)
        E.once('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await E.click('#btnLogout')
        await E.wait_for_function("window.FACloud && !window.FACloud.email() && document.getElementById('btnLogin')", timeout=15000)
        check('T9 登出後顯示登入按鈕、沒有登出鈕', await E.locator('#btnLogin').count() == 1 and await E.locator('#btnLogout').count() == 0)
        # T10：登出並保留進度：本機存檔還在、已登出、meta 清掉（之後換帳號登入視為這台的進度）
        ctxF, F = await device(ALICE); await open_(F)
        await F.evaluate("() => localStorage.setItem('fa-kingdom-p1-v1', JSON.stringify({v:2,day:3,step:5,started:true}))")
        await F.wait_for_selector('#btnLogoutKeep', timeout=15000)
        F.once('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await F.click('#btnLogoutKeep')
        await F.wait_for_function("window.FACloud && !window.FACloud.email() && document.getElementById('btnLogin')", timeout=15000)
        check('T10 保留進度登出：本機存檔還在', await F.evaluate("() => !!localStorage.getItem('fa-kingdom-p1-v1')"))
        check('T10 保留進度登出：已登出', await F.locator('#btnLogin').count() == 1)
        await b.close()
    n = results.count(False); print('全部通過' if not n else f'{n} 項失敗', f'（共 {len(results)} 項）'); return n

if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
