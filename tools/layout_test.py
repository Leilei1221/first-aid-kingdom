"""章節場景版面檢查（不需要瀏覽器）：出生點、NPC、互動點、出口落點是否在可行走範圍內（互動點允許在 120px 內有可走處）。
用法：python3 tools/layout_test.py ch3    （檢查 chapters/ch3/ 的 scenes.json 與 walks.json）"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ch = sys.argv[1] if len(sys.argv) > 1 else 'ch3'
S = json.load(open(os.path.join(ROOT, f'chapters/{ch}/scenes.json'), encoding='utf-8'))
W = json.load(open(os.path.join(ROOT, f'chapters/{ch}/walks.json'))); W.update(json.load(open(os.path.join(ROOT, 'data/walks.json'))))
def ok(sc, x, y):
    j, i = int(y // 8), int(x // 8); rows = W[sc]
    return 0 <= j < len(rows) and 0 <= i < len(rows[0]) and rows[j][i] == '1'
def near(sc, x, y, r=120):
    return any(ok(sc, x + dx, y + dy) for dx in range(-r, r + 1, 8) for dy in range(-r, r + 1, 8) if math.hypot(dx, dy) <= r)
bad = 0
for sid, s in S.items():
    probs = []
    if not ok(sid, *s['spawn']): probs.append(f"出生點 {s['spawn']} 不可走")
    for n in s['npcs']:
        if not ok(sid, n['x'], n['y']): probs.append(f"NPC {n['id']} ({n['x']},{n['y']}) 不在可走處")
    for t in s['things']:
        if not near(sid, t['x'], t['y']): probs.append(f"互動點「{t['label']}」({t['x']},{t['y']}) 120px 內沒有可走處")
        if t['kind'] == 'door' and not ok(t['to'], *t['at']): probs.append(f"門「{t['label']}」落點 {t['at']} 不可走")
    for e in s['exits']:
        if not e.get('to'): continue  # toFn（執行時才決定去哪）的出口不檢查
        if not ok(e['to'], *e['at']): probs.append(f"出口→{e['to']} 落點 {e['at']} 不可走")
        if e['to'] not in W: probs.append(f"出口→{e['to']} 沒有遮罩")
    print(('✓' if not probs else '✗'), sid, '；'.join(probs)); bad += len(probs)
print('版面檢查全過' if not bad else f'{bad} 項有問題'); sys.exit(1 if bad else 0)
