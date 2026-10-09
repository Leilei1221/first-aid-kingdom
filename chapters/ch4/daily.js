/* 第四章「雪嶺」F7：山屋的日常（章末演練完成後開啟）。
 * 公告板每天一件登山求助（五種輪流）、天氣窗口（風雪天不接戶外求助）、山屋小店、嚮導訓練、嚮導信譽與稱號。
 * 題目全部沿用第 2～5 節的 ch4_q*（不新增醫療內容）；數字與開場白在 daily.json（遊戲參數與擬稿）。狀態記在 S.c.ch4.d 與 S.c.ch4.rep，不新增頂層欄位。 */
export default function(FA,{S,st,ask,PREV}){
const {say,lines,toast,refresh}=FA;
let D=null;const data=async()=>D||(D=await (await fetch(new URL('daily.json',import.meta.url))).json());
const on=()=>!!(st().done||(PREV&&st().s5));
const day=()=>{const e=st();if(!e.d||e.d.day!==S.day)e.d={day:S.day,ev:0,train:0};return e.d;};
const stormDay=(W,d)=>(d+W.offset)%W.stormEvery===0;
const titleOf=(R,rep)=>R.titles[rep>=R.captain?2:rep>=R.guide?1:0];
const rep=()=>st().rep||0;
async function addRep(n,why){
  const R=(await data()).REP,before=titleOf(R,rep());
  st().rep=rep()+n;const after=titleOf(R,rep());
  toast(`嚮導信譽 +${n}（${rep()} 點）`);
  if(after!==before)await say({icon:'🏅',who:'稱號',html:`<p class="good">你的稱號升級了：${after}！</p><p class="small">${why||''}</p>`});}
function pickSome(pool,n,seed){const a=pool.slice();for(let i=a.length-1;i>0;i--){const j=(seed*7+i*13)%(i+1);[a[i],a[j]]=[a[j],a[i]];}return a.slice(0,Math.min(n,a.length));}
async function event(ev){
  const d=day(),Dd=await data();
  await lines(ev.who,ev.intro);
  let wrong=0;
  for(const k of pickSome(ev.pool,ev.pick,S.day))wrong+=(await ask(k,'ch4_guide_up')).wrong;
  d.ev=1;
  await addRep(1+(wrong===0?Dd.REWARD.careBonus:0),`處理了一件${ev.title}求助。`);
  S.coins+=Dd.REWARD.coins;S.earned=(S.earned||0)+Dd.REWARD.coins;refresh();
  await say({p:'hero',html:`<p class="good">求助處理好了。${wrong===0?'每題都第一次答對，信譽多加 1 點。':''}</p><p class="small">獲得 ${Dd.REWARD.coins} 金幣。</p>`});
  if(FA.dailyDone)await FA.dailyDone('care');}
/* 公告板：今日天氣、今日求助、嚮導信譽 */
async function board(){
  if(!on()){await say({p:'hero',html:'<p>木製公告板上釘著幾張紙，畫著太陽、雲和雪花的小圖案。（每天的天氣與求助，完成章末演練之後才會貼上來。）</p>'});return;}
  const Dd=await data();
  for(;;){
    const d=day(),storm=stormDay(Dd.WX,S.day),ev=Dd.EVENTS[S.day%Dd.EVENTS.length];
    const R=Dd.REP,t=titleOf(R,rep()),next=rep()>=R.captain?null:rep()>=R.guide?R.captain:R.guide;
    const i=await say({p:'hero',who:'山屋公告板',html:`<p><b>今日天氣：</b>${storm?'🌨 風雪大，不宜出門':'☀ 適合上山'}</p><p><b>今日求助：</b>${storm?'風雪太大，今天沒有戶外求助。':d.ev?`「${ev.title}」已經處理好了。`:`「${ev.title}」，有人需要幫忙。`}</p><p><b>嚮導信譽：</b>${rep()} 點　<b>稱號：</b>${t}${next?`（再 ${next-rep()} 點升級）`:'（最高）'}</p>`,
      buttons:[{label:'幫忙處理今天的求助',primary:true,disabled:storm||!!d.ev},{label:'離開'}]});
    if(i!==0)return;
    await event(ev);}}
/* 嚮導訓練：選一個主題，抽 3 題；每天第一次完成加信譽 */
async function train(){
  const Dd=await data();
  const i=await say({p:'ch4_guide_up',who:'嚮導訓練',html:'<p>要練哪一種？每天第一次完成，可以累積嚮導信譽。</p>',buttons:Dd.TRAIN.map(t=>({label:t.name})).concat([{label:'先不要',primary:true}])});
  if(i>=Dd.TRAIN.length)return;
  const T=Dd.TRAIN[i],d=day();let wrong=0;
  for(const k of pickSome(T.pool,3,S.day+i))wrong+=(await ask(k,'ch4_guide_up')).wrong;
  if(!d.train){d.train=1;await addRep(1,`完成了「${T.name}」的嚮導訓練。`);}
  else await say({p:'ch4_guide_up',html:'<p>今天的訓練信譽已經領過了，不過多練幾次沒有壞處。</p>'});
  await say({p:'ch4_guide_up',html:`<p>${wrong===0?'每題都答對，很穩。':'有幾題答錯了，不要緊，多練幾次就熟了。'}</p>`});}
/* 山屋小店（管理員達瓦） */
async function shop(){
  const Dd=await data();
  for(;;){
    const e3=(S.c.ch3_e3=S.c.ch3_e3||{});e3.cnt=e3.cnt||{};
    const i=await say({p:'ch4_keeper',who:'山屋小店',html:`<p class="small">金幣 ${S.coins}　體力 ${S.sta}／${FA.staMax()}</p>${Dd.SHOP.map(g=>`<p><b>${g.name}</b>　${g.price} 金幣<br><span class="small">${g.desc}${g.cnt?`（現有 ${e3.cnt[g.cnt]||0}）`:''}</span></p>`).join('')}`,
      buttons:Dd.SHOP.map(g=>({label:`買${g.name}（${g.price}）`,disabled:S.coins<g.price||(g.sta&&S.sta>=FA.staMax())})).concat([{label:'離開',primary:true}])});
    if(i>=Dd.SHOP.length)return;
    const g=Dd.SHOP[i];S.coins-=g.price;
    if(g.sta)S.sta=Math.min(FA.staMax(),S.sta+g.sta);
    if(g.cnt)e3.cnt[g.cnt]=(e3.cnt[g.cnt]||0)+1;
    refresh();toast(`買了${g.name}`);}}
let G=null;data().then(x=>{G=x;}).catch(()=>{});
const goal=()=>{if(!G||!on())return '';const d=day(),storm=stormDay(G.WX,S.day);
  if(storm)return '今天風雪大，沒有戶外求助。可以找帕桑做嚮導訓練，或到山屋小店補給。';
  if(!d.ev)return '山屋的公告板上有今天的求助，去看看。';
  if(!d.train)return '今天的求助處理好了。找帕桑做一次嚮導訓練，可以再加信譽。';
  return '今天的事都做完了。明天再來看看公告板。';};
return {on,board,train,shop,goal,rep,titleOf:async()=>titleOf((await data()).REP,rep()),load:data,stormDay:async d=>stormDay((await data()).WX,d)};
}
