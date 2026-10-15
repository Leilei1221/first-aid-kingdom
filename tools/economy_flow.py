"""金幣收支估算（唯讀，不改任何遊戲數字；老師 2026-10-15 同意，供判斷獎勵與花費是否平衡）。
假設與限制都印在輸出裡。用法：python3 tools/economy_flow.py"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
B = J('content/balance.json'); M = J('content/items.json')['MATS']; REQ = J('content/quests_and_events.json')['REQUESTS']
C = B['COST']; STA = B['STA_MAX']
print('== 每天收入估算（體力 %d，睡一覺回滿；單位：金幣／體力）==' % STA)
tree = 3 * M['wood']['sell'] / (3 * C['chop'])               # 一棵樹 3 下、3 份木材
print('砍樹：每棵 %d 體力 → %d 金幣（每體力 %.2f），森林 5 棵，一天最多 %d 金幣' % (3 * C['chop'], 3 * M['wood']['sell'], tree, 5 * 3 * M['wood']['sell']))
rock = (.34 * M['gold']['sell'] + .66 * M['stone']['sell']) / (3 * C['mine'])   # 金礦機率 34%，其餘當作 1 份石頭
print('礦坑：每顆 %d 體力 → 期望約 %.1f 金幣（每體力 %.2f），6 顆；強化十字鎬後 2 下' % (3 * C['mine'], .34 * M['gold']['sell'] + .66 * M['stone']['sell'], rock))
avg = sum(r['pay'] for r in REQ) / len(REQ)
print('委託板：3 件同時掛著，平均每件 %.0f 金幣，睡一覺換新；一天至多約 %.0f 金幣（需要對應素材，木材委託每份約 %.1f 金幣，比直接賣 %d 高）' % (avg, avg * 3, 25 / 4, M['wood']['sell']))
print('合計：一天把體力用在砍樹、礦坑、委託，大約 80～150 金幣（未計種田、事件、每日任務）')
print()
print('== 主要花費（序章到第三章後）==')
kit = sum(x['cost'] for x in B['KIT_UP']); mat = sum(x['cost'] for x in B['MAT_UP'])
rows = [('急救背包擴充（全部 %d 次）' % len(B['KIT_UP']), kit), ('素材袋擴充（全部 %d 次）' % len(B['MAT_UP']), mat),
        ('乾糧製造機', B['MACHINE_COIN']), ('體能訓練（3 次）', sum(B['STAMINA_SHOP']['up']['costs'])),
        ('寵物（小貓）', [p for p in B['PETS']['list'] if p['id'] == 'cat'][0]['cost']), ('寵物（貓頭鷹）', [p for p in B['PETS']['list'] if p['id'] == 'owl'][0]['cost'] if any(p['id'] == 'owl' for p in B['PETS']['list']) else 800),
        ('水手裝＋登山裝', sum(o['cost'] for o in B['OUTFITS']['list'] if o.get('src') == 'shop'))]
for v in B['VEHICLES']['list']: rows.append(('交通工具：' + v['name'], v['cost']))
for n, v in rows: print('%-24s %6d 金幣　約 %.0f 天收入（以每天 100 金幣算）' % (n, v, v / 100))
print('救援失敗：扣救援費 %d；醫療費 %d' % (B['RESCUE_FEE'], B['MED_FEE']))
print()
print('== 其他收入（一次性）==')
for k, v in B['STAR_REWARD'].items():
    if isinstance(v, dict): print('星級獎勵', k, '：3／4／5 顆星 = %s（累積最多 %d）' % ('／'.join(str(x) for x in v.values()), sum(v.values())))
d = B['DAILY']; print('每日任務全完成 %d 金幣（現實每天一次）；累計簽到 3／7／14／30 天 = %s' % (d['reward']['coins'], '／'.join(str(m['coins']) for m in d['milestones'])))
print()
print('== 看法（估算，非結論）==')
print('· 整套花費約 %d 金幣（不含交通工具 20500），以每天約 100 金幣算要 70 天以上，要靠星級獎勵、每日任務、章節日常補。' % sum(v for n, v in rows if not n.startswith('交通')))
print('· 寵物 500／800 約 5～8 天的估算收入；收入估算只含序章的砍樹、礦坑、委託，章節日常（公告板、釣魚、商人）沒算，後期實際收入應更高。')
print('· 花費沒計入第四章裝備與防寒衣物。')
print('· 收入沒計入：種田（小麥賣價 %d，產量要看田數）、事件獎勵、章節日常、商人買賣，這些會讓真實收入更高。' % M['wheat']['sell'])
