"""實際走路測試：每個場景從入口出發，用鍵盤方向鍵走到每個出口，確認真的會換場景。
章節：`CHAPTER=ch2 python3 tools/walk_test.py ...` 改測 chapters/ch2/ 的場景（網址自動加 ?open=ch2）。
用法：先在專案根目錄 `python3 -m http.server 8765`，再 `python3 tools/walk_test.py http://localhost:8765/index.html`
路徑用 data/walks.json 的可行走網格做 BFS 找路，再以「按鍵」的方式沿路徑移動（不直接改座標）。"""
import asyncio, json, re, sys, os
from collections import deque
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.environ.get('CHAPTER')
if CH:
    WALKS = json.load(open(os.path.join(ROOT, f'chapters/{CH}/walks.json')))
    SCENES = json.load(open(os.path.join(ROOT, f'chapters/{CH}/scenes.json'), encoding='utf-8'))
else:
    WALKS = json.load(open(os.path.join(ROOT, 'data/walks.json')))
    SCENES = json.load(open(os.path.join(ROOT, 'content/scenes.json'), encoding='utf-8'))
CELL = 8

def conds(test):
    out = []
    for part in test.split('=>', 1)[1].split('&&'):
        m = re.match(r'([xy])([<>])(\d+)$', part.strip())
        out.append((m.group(1), m.group(2), int(m.group(3))))
    return out

def push_dir(test):
    ax, op, _ = conds(test)[0]
    d = -1 if op == '<' else 1
    return (d, 0) if ax == 'x' else (0, d)

def pred(test):
    cs = conds(test)
    return lambda x, y: all((((x if ax == 'x' else y) < v) if op == '<' else ((x if ax == 'x' else y) > v)) for ax, op, v in cs)

def bfs(rows, start, goal):
    H, W = len(rows), len(rows[0])
    sx, sy = int(start[0] // CELL), int(start[1] // CELL)
    q = deque([(sx, sy)]); prev = {(sx, sy): None}
    while q:
        cx, cy = q.popleft()
        if goal(cx * CELL + 4, cy * CELL + 4):
            path = []; c = (cx, cy)
            while c: path.append((c[0] * CELL + 4, c[1] * CELL + 4)); c = prev[c]
            return path[::-1]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < W and 0 <= ny < H and rows[ny][nx] == '1' and (nx, ny) not in prev:
                prev[(nx, ny)] = (cx, cy); q.append((nx, ny))
    return None

WALK_JS = """
async ([pts]) => {
  const F = window.__fa, S = F.S;
  const key = (t, k) => window.dispatchEvent(new KeyboardEvent(t, { key: k, bubbles: true }));
  const held = new Set();
  const set = (k, on) => { if (on && !held.has(k)) { key('keydown', k); held.add(k); } if (!on && held.has(k)) { key('keyup', k); held.delete(k); } };
  const start = S.scene; let i = 0, stuck = 0, last = null;
  for (let step = 0; step < 4000; step++) {
    if (S.scene !== start) break;
    if (!document.getElementById('dialog').hidden) { document.querySelector('#dBtns button')?.click(); await new Promise(r => setTimeout(r, 60)); continue; }
    const [tx, ty] = pts[Math.min(i, pts.length - 1)];
    const dx = tx - S.pos.x, dy = ty - S.pos.y;
    if (Math.hypot(dx, dy) < 14 && i < pts.length - 1) { i++; continue; }
    set('ArrowLeft', dx < -6); set('ArrowRight', dx > 6); set('ArrowUp', dy < -6); set('ArrowDown', dy > 6);
    await new Promise(r => setTimeout(r, 30));
    const p = S.pos.x + ',' + S.pos.y; stuck = (p === last) ? stuck + 1 : 0; last = p;
    if (stuck > 60) { ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].forEach(k => set(k, false)); return { ok: false, why: '卡住', scene: S.scene, pos: S.pos, i, n: pts.length }; }
  }
  ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].forEach(k => set(k, false));
  return { ok: S.scene !== start, scene: S.scene, pos: S.pos };
}
"""

async def main(url):
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        todo = list(SCENES.items())
        extra = []  # 章節模式：序章場景通往章節的出口（需要收到信）也要走一遍
        if CH:
            pro = json.load(open(os.path.join(ROOT, 'content/scenes.json'), encoding='utf-8'))
            for psid, psc in pro.items():
                psc2 = dict(psc, exits=[e for e in psc['exits'] if (e.get('to') or '').startswith(CH + '_')])
                if psc2['exits']: extra.append((psid, psc2))
            WALKS.update(json.load(open(os.path.join(ROOT, 'data/walks.json'))))
            todo += extra
        for sid, sc in todo:
            for ei, ex in enumerate(sc['exits']):
                if not CH and (ex.get('to') or '').startswith('ch'):
                    print('- ', sid, f'出口#{ei}', '→', ex['to'], '（章節出口，預設關閉，用 CHAPTER 模式測）'); continue
                path = bfs(WALKS[sid], sc['spawn'], pred(ex['test']))
                if not path:
                    print(f'✗ {sid} 出口#{ei}：從入口找不到可走的路'); bad += 1; continue
                dx, dy = push_dir(ex['test']); pts = path[::2] + [path[-1], (path[-1][0] + dx * 24, path[-1][1] + dy * 24)]
                ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
                await ctx.add_init_script("localStorage.setItem('fa-debug','1')")
                page = await ctx.new_page()
                await page.goto(url + (f'?open={CH}' if CH else '') + '#debug')
                await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
                await page.evaluate(f"""() => {{ const S = window.__fa.S; S.step = 10; S.f.p3 = true; S.c = Object.assign(S.c || {{}}, {{letter: true}}); S.scene = {json.dumps(sid)}; S.pos = {{x: {sc['spawn'][0]}, y: {sc['spawn'][1]}}}; S.started = true;
                  document.getElementById('btnStart').click(); }}""")
                await page.wait_for_timeout(600)
                r = await page.evaluate(WALK_JS, [pts])
                print(('✓' if r['ok'] else '✗'), sid, f'出口#{ei}', '→', r.get('scene'), '' if r['ok'] else r)
                bad += 0 if r['ok'] else 1
                await ctx.close()
        await b.close()
    print('全部出口都走得到' if not bad else f'有 {bad} 個出口有問題')
    return bad

if __name__ == '__main__':
    sys.exit(1 if asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/index.html')) else 0)
