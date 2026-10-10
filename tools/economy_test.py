"""經濟檢查（不需要瀏覽器）：不能有「買低賣高」的循環（老師 2026-10-10 發現救生站 OK 繃買 10、賣尼泊爾商人 25，可以無限刷金幣）。
規則：任何商人／商店收購同一種東西的價錢，不能高過任何地方賣它的最低價；藥品類收購價是買價的一半。
用法：python3 tools/economy_test.py"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
ITEMS = J('content/items.json')['ITEMS']; BAL = J('content/balance.json'); E3 = J('chapters/ch3/e3.json')
voy = open(os.path.join(ROOT, 'chapters/voyage.js'), encoding='utf-8').read()
SHIP_RATION = int(re.search(r'SHIP_RATION=(\d+)', voy).group(1))
fails = 0
def check(name, ok, info=''):
    global fails
    print(('✓' if ok else '✗'), name, '' if ok else info)
    if not ok: fails += 1
# 買價：雜貨店／急救用品櫃／澳洲商人都是 ITEMS 的 price；乾糧最低是船上與港口小店的 SHIP_RATION
buy = {k: v['price'] for k, v in ITEMS.items() if v.get('price')}; buy['ration'] = SHIP_RATION
# 收購價
def payOf(sp, it):
    return sp['pay'] if sp['kind'] == 'kit' and sp.get('pay') is not None else max(1, int(buy[it] * (sp.get('ratio') or .5)))
for k, sp in E3['SELL'].items():
    if sp['kind'] == 'fish': continue
    for it in ([sp['item']] if sp['kind'] == 'kit' else sp['items']):
        pay = payOf(sp, it)
        check(f'{k} 收 {it}：{pay} 金幣，不高於最低買價 {buy[it]}（沒有買低賣高）', pay <= buy[it], f'{pay} > {buy[it]}')
        if sp['kind'] == 'kitlist': check(f'{k} 收藥品 {it}：只付買價的一半以下', pay * 2 <= buy[it], f'{pay} vs {buy[it]}')
    check(f'{k} 每天有收購上限（cap）', sp.get('cap', 0) >= 1 and sp.get('cap', 99) <= 10, str(sp))
check('雜貨店收乾糧的價錢（RATION_SELL）低於買價', BAL['RATION_SELL'] < SHIP_RATION, str(BAL['RATION_SELL']))
print('失敗', fails); sys.exit(1 if fails else 0)
