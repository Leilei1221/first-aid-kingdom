"""行為比對：在「基準版」與「新版」執行同一組劇情腳本，逐字比對所有對話框、提示與存檔狀態。

用法：
  python3 tools/compare_run.py baseline <基準版 HTML 路徑> <輸出 json>
  python3 tools/compare_run.py new <網址，例如 http://localhost:8765/index.html> <輸出 json>
  python3 tools/compare_run.py diff <a.json> <b.json>

基準版請用 `python3 tools/build_inline.py`（含 #debug 掛鉤）在舊版 src 上組出來。
新版需要 localStorage 旗標 fa-debug=1 才會開放 #debug（本腳本會自動設定）。
"""
import json, sys, asyncio
from playwright.async_api import async_playwright

INIT = r"""
(() => {
  // 固定亂數，讓兩個版本的隨機事件一致
  let seed = 12345;
  const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  Math.random = rnd;
  window.__seed = n => { seed = n; };
  window.__log = [];
  window.__policy = 'first';
  window.__clicks = 0;
  let snapN = 0, clickedN = 0;
  const snap = () => {
    const d = document.getElementById('dialog'); if (!d || d.hidden) return;
    const btns = [...document.querySelectorAll('#dBtns button')].map(b => (b.disabled ? '[x]' : '') + b.textContent);
    window.__log.push({ t: 'dlg', who: document.getElementById('dWho').innerHTML, face: document.getElementById('dFace').style.backgroundImage.replace(/url\(.*?([^\/"]+)\.webp.*\)/, '$1') || document.getElementById('dFace').textContent,
      text: document.getElementById('dText').innerHTML.replace(/src="[^"]*\/([^\/"]+)\.webp"/g, 'src="$1"').replace(/src="data:[^"]*"/g, 'src="(data)"'), btns });
    snapN++;
  };
  window.addEventListener('DOMContentLoaded', () => {
    new MutationObserver(snap).observe(document.getElementById('dText'), { childList: true });
    const toast = document.getElementById('toast');
    new MutationObserver(() => { if (toast.textContent) window.__log.push({ t: 'toast', text: toast.textContent }); })
      .observe(toast, { childList: true, characterData: true, subtree: true });
    setInterval(() => {
      const d = document.getElementById('dialog'); if (d.hidden || snapN === clickedN) return;
      const bs = [...document.querySelectorAll('#dBtns button:not([disabled])')]; if (!bs.length) return;
      clickedN = snapN; window.__clicks++;
      const p = window.__policy;
      const i = p === 'first' ? 0 : p === 'last' ? bs.length - 1 : window.__clicks % bs.length;
      window.__log.push({ t: 'click', i, of: bs.length });
      bs[i].click();
    }, 15);
  });
})();
"""

# 每個情境：setup（在按下「開始」之前修改存檔狀態）與 run（在頁面內執行的腳本）
SCEN = {
 'intro':        dict(setup="", run=""),
 'wood_axe':     dict(setup="S.step=1;", run="await F.talk('wood');"),
 'accident':     dict(setup="S.step=3;S.earned=100;S.scene='village';S.pos={x:1045,y:305};", run="await F.go('forest',[950,300]);"),
 'step5_missing':dict(setup="S.step=5;S.scene='forest';", run="await F.talk('wood');await F.talk('kid');"),
 'step5_ok':     dict(setup="S.step=5;S.scene='forest';S.kit=['glove','gauze','elastic','saline','bandaid'];", run="await F.talk('wood');await F.talk('kid');F.refresh();L('goal',document.getElementById('goal').innerHTML);"),
 'grandpa_steps':dict(setup="S.step=6;S.scene='home';S.hearts.grandpa=3;S.kit=['ration@50'];",
   run="""for(const st of [6,7,8,9,10]){S.step=st;await F.talk('grandpa');}
          S.bench=true;await F.talk('grandpa');S.step=7;await F.talk('grandpa');S.step=5;await F.talk('grandpa');S.step=3;await F.talk('grandpa');
          S.step=10;S.f.p3=true;S.castleDone=true;S.castleBest=4;await F.talk('grandpa');await F.talk('grandpa');
          S.kit=['cotton','ration@1'];S.day=5;await F.talk('grandpa');await F.talk('grandpa');"""),
 'hypo_faint':   dict(setup="S.step=8;S.kit=['sugar'];", run="""await F.hypoWarn();S.kit=[];await F.hypoWarn();
          await F.faint('mushroom');await F.faint('work');S.mat.mushroom=2;await F.eatMushroom();await F.eatMushroom();"""),
 'well_boil':    dict(setup="S.step=8;S.scene='village';S.kitCap=6;", run="""await F.well();await F.well();await F.well();await F.boil();S.mat.rawwater=2;await F.boil();"""),
 'hunter':       dict(setup="S.step=10;S.f.p3=true;S.scene='plain';", run="""await F.hunter();S.kit=['ice','elastic'];await F.hunter();await F.hunter();"""),
 'castle_full':  dict(setup="S.step=10;S.f.p3=true;S.f.hunter=true;S.scene='gate';S.kitCap=14;S.hearts.guard=1;S.kit=['glove','glove','gauze','gauze','sling','ice','elastic','ration@99','ration@99','ration@99','water','water','water','cotton'];",
   run="""await F.gateDoor();await F.guardTalk();await F.gateDoor();
          await F.victim('guard');await F.victim('cook');await F.victim('soldier');
          await F.victim('guard');await F.talk('guard');F.refresh();L('goal',document.getElementById('goal').innerHTML);
          S.scene='gate';S.f.guard=true;await F.gateDoor();"""),
 'castle_empty': dict(setup="S.step=10;S.f.p3=true;S.scene='gate';S.f.guard=true;S.kit=['ration@1'];S.day=9;",
   run="await F.gateDoor();await F.victim('guard');await F.victim('cook');await F.victim('soldier');"),
 'tablet':       dict(setup="S.step=10;S.f.p3=true;S.scene='river';", run="await F.tablet();await F.tablet();"),
 'events':       dict(setup="S.step=7;S.kit=['glove','gauze','bandaid','ice'];S.kitCap=14;S.cards.bee=true;",
   run="""for(const ev of F.EVENTS){S.event={id:ev.id,day:S.day};await F.talk(ev.who);}
          S.kit=[];for(const ev of F.EVENTS){S.event={id:ev.id,day:S.day};await F.talk(ev.who);}"""),
 'shops':        dict(setup="S.step=2;S.scene='shop';S.mat.wood=5;S.coins=300;", run="""await F.talk('shopkeeper');S.step=7;S.mat.mushroom=1;S.mat.flower=1;await F.talk('shopkeeper');await F.talk('shopkeeper');
          S.step=3;await F.talk('merchant');S.step=5;await F.talk('merchant');S.step=7;await F.talk('merchant');
          await F.talk('kid');await F.talk('wood');S.hearts.kid=3;await F.talk('kid');S.hearts.wood=3;S.hearts.shopkeeper=3;S.hearts.grandpa=3;await F.talk('wood');await F.talk('shopkeeper');await F.talk('grandpa');"""),
 'bed':          dict(setup="S.step=8;S.scene='home';", run="await F.bed();await F.bed();F.refresh();L('goal',document.getElementById('goal').innerHTML);"),
 'goals':        dict(setup="", run="""const out=[];
          const set=(o)=>{Object.assign(S,o);F.refresh();out.push(JSON.stringify(o)+' => '+document.getElementById('goal').innerHTML);};
          for(let i=0;i<=10;i++)set({step:i,flagWoodDone:false,flagKidDone:false});
          set({step:5,flagWoodDone:true,flagKidDone:false});set({step:5,flagWoodDone:true,flagKidDone:true});
          set({step:10,coins:-30});S.coins=10;
          set({step:10,bench:false,spr:[],harvester:false});set({step:10,bench:true});set({step:10,spr:[0],harvester:true});
          S.f.p3=false;set({step:10});S.f.p3=true;set({step:10});S.f.tablet=true;set({step:10});S.f.hunter=true;set({step:10});S.f.guard=true;set({step:10});
          S.castleDone=true;set({step:10});S.f.final=true;set({step:10});
          out.forEach(o=>L('goal',o));"""),
 'signs':        dict(setup="S.step=3;", run="""const out=[];
          for(const [p3,step] of [[false,3],[true,7]]){S.f.p3=p3;S.step=step;
            for(const sc of ['village','forest','farm','mine_out','river','plain','gate','ruin','home','shop','mine_in']){
              S.scene=sc;F.buildScene();out.push(`${p3}/${step}/${sc}: `+[...document.querySelectorAll('.signpost')].map(e=>e.textContent).join('|'));}}
          out.forEach(o=>L('sign',o));"""),
}

RUNNER = """
async (args) => {
  const [name, setup, run, policy] = args;
  const F = window.__fa; const S = F.S;
  window.__policy = policy; window.__log = []; window.__clicks = 0; window.__seed(777);
  window.L = (k, v) => window.__log.push({ t: k, v });
  new Function('S', setup)(S);
  document.getElementById('btnStart').click();
  await new Promise(r => setTimeout(r, 900));      // 讓開場（step 0 的爺爺對話）先跑完
  const wait = async () => { for (let i = 0; i < 400; i++) { if (document.getElementById('dialog').hidden) { await new Promise(r => setTimeout(r, 120)); if (document.getElementById('dialog').hidden) return; } else await new Promise(r => setTimeout(r, 50)); } };
  await wait();
  const fn = new (Object.getPrototypeOf(async function(){}).constructor)('F', 'S', 'L', run);
  const S2 = () => F.S;
  await Promise.race([fn(F, F.S, window.L), new Promise((_, rej) => setTimeout(() => rej(new Error('逾時')), 60000))]);
  await wait();
  F.refresh();
  window.__log.push({ t: 'state', v: JSON.stringify(F.S) });
  return window.__log;
}
"""

async def run(mode, target, out, only=None):
    results = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for policy in ('first', 'last', 'cycle'):
            for name, sc in SCEN.items():
                if only and only not in name: continue
                ctx = await b.new_context(viewport={'width': 1180, 'height': 820})
                await ctx.add_init_script("localStorage.setItem('fa-debug','1');" if mode == 'new' else "")
                await ctx.add_init_script(INIT)
                page = await ctx.new_page()
                errs = []
                page.on('pageerror', lambda e, errs=errs: errs.append(str(e)))
                url = (('file://' + target) if mode == 'baseline' else target) + '#debug'
                await page.goto(url)
                await page.wait_for_function("window.__fa && !document.getElementById('btnStart').disabled", timeout=60000)
                try:
                    log = await page.evaluate(RUNNER, [name, sc['setup'], sc['run'], policy])
                except Exception as e:
                    log = [{'t': 'error', 'v': str(e)}]
                if errs: log.append({'t': 'pageerror', 'v': errs})
                results[f'{policy}/{name}'] = log
                print(f'{policy}/{name}: {len(log)} 筆', '(有錯誤)' if errs or log[-1].get('t') == 'error' else '')
                await ctx.close()
        await b.close()
    json.dump(results, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def _norm(log):
    """基準版的頭像/圖示是 base64、新版是檔案路徑：兩邊都轉成「圖片內容前 80 字元」再比。"""
    import base64, os, re
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
    def key_of_name(n):
        return base64.b64encode(open(os.path.join(root, n + '.webp'), 'rb').read()).decode()[:80]
    out = []
    for e in log:
        e = dict(e)
        if e.get('t') == 'error': e['v'] = e['v'].split('\n')[0]  # 堆疊路徑兩版本不同，只比第一行
        if e.get('t') == 'dlg':
            f = e['face']
            if f.startswith('url("data:'): e['face'] = 'img:' + f.split('base64,', 1)[1][:80]
            elif os.path.exists(os.path.join(root, f + '.webp')): e['face'] = 'img:' + key_of_name(f)
            e['text'] = re.sub(r'src="[^"]*"', 'src="(img)"', e['text'])
        out.append(e)
    return out

def diff(a, b):
    A = {k: _norm(v) for k, v in json.load(open(a, encoding='utf-8')).items()}
    B = {k: _norm(v) for k, v in json.load(open(b, encoding='utf-8')).items()}
    bad = 0; total = 0
    for k in sorted(set(A) | set(B)):
        la, lb = A.get(k), B.get(k); total += 1
        if la == lb: continue
        bad += 1
        print('不一致：', k, len(la or []), len(lb or []))
        for i, (x, y) in enumerate(zip(la or [], lb or [])):
            if x != y:
                print('  第', i, '筆\n   基準:', json.dumps(x, ensure_ascii=False)[:500], '\n   新版:', json.dumps(y, ensure_ascii=False)[:500]); break
    print(f'共 {total} 個情境，不一致 {bad} 個')
    return bad

if __name__ == '__main__':
    m = sys.argv[1]
    if m == 'diff': sys.exit(1 if diff(sys.argv[2], sys.argv[3]) else 0)
    asyncio.run(run(m, sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None))
