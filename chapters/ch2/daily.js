/* 第二章鍛造鎮的公告板與日常求助（老師 2026-10-10 同意第二章加玩法）：完成第二章（S.c.done）後，廣場多一塊公告板，每天輪一件事（5 件輪完再從頭），
 * 題目與知識卡都是第二章故事裡原本就有的（見 daily.json），做完得金幣與「鍛造鎮信譽」；信譽累積稱號。
 * 狀態記在既有的 S.c.ch2_hb（不新增頂層欄位）：{rep, done, n}。數字是遊戲參數，不是醫學數字。 */
export const HB2={reward:30,repPerEvent:1,
  titles:[[0,'見習學徒'],[3,'鍛造鎮志工'],[8,'資深志工'],[15,'鎮上守護者']],
  boardAt:{x:580,y:700},victimAt:{x:960,y:640}};
const ORDER=['hot','chem','blister','elec','ext'];
export const title2=rep=>HB2.titles.filter(t=>rep>=t[0]).pop()[1];
export const evOf=day=>ORDER[((day*3)%ORDER.length+ORDER.length)%ORDER.length];  /* 每天輪一件，5 天輪完，不用亂數 */
export default function(FA,{on}){
const {say,quiz,orderQuiz,refresh,CARDS,A,RATIO,takeKit,needCheck,ITEMS,dailyDone}=FA;
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
let DATA=null;
const data=async()=>DATA||(DATA=(await (await fetch(new URL('daily.json',import.meta.url))).json()).EVENTS);
const st=()=>{S.c=S.c||{};return S.c.ch2_hb||(S.c.ch2_hb={rep:0,done:0,n:0});};
const active=()=>on()&&st().done!==S.day;
const needTxt=n=>Object.entries(n).map(([k,v])=>`${ITEMS[k].name} ×${v}`).join('、');
const expl=e=>e&&typeof e==='object'&&e.card?CARDS[e.card].text:e;
async function board(){
  const h=st(),d=await data(),e=d[evOf(S.day)];
  await say({icon:'📋',who:'鍛造鎮公告板',html:`<p>你的稱號：<b>${title2(h.rep)}</b>　鍛造鎮信譽 ${h.rep}　已幫忙 ${h.n} 件</p>`+
    (h.done===S.day?'<p class="good">今天的求助都處理好了，明天再來看看。</p>':`<p><b>今天的求助：</b>${e.name}</p><p class="small">廣場上有人在等你，走近按「求助」。需要的用品：${Object.keys(e.needs).length?needTxt(e.needs):'沒有（要靠判斷）'}。</p>`)});
}
async function help(){
  if(!active())return;
  const d=await data(),e=d[evOf(S.day)];
  await say({p:e.who,wound:e.wound,html:`<p>${e.intro}</p>`});
  const miss=needCheck(e.needs);
  if(miss.length){await say({p:e.who,html:`<p>需要：${needTxt(e.needs)}</p><p class="warn">你的背包還缺：${miss.map(([k,n])=>ITEMS[k].name+' ×'+n).join('、')}</p><p class="small">今天之內帶用品回來還來得及。到鍛造鎮小店補齊吧。</p>`});return;}
  for(const q of e.qs){if(q.order)await orderQuiz(e.who,q.title,q.steps,expl(q.explain));else await quiz(e.who,q.q,q.opts,q.ans,expl(q.explain),q.wound);}
  takeKit(e.needs);
  const h=st(),first=!S.cards[e.card];S.cards[e.card]=true;
  h.done=S.day;h.n++;h.rep+=HB2.repPerEvent;S.coins+=HB2.reward;S.earned=(S.earned||0)+HB2.reward;
  await say({p:e.who,html:`<p>${e.thanks}</p><p class="good">獲得 ${HB2.reward} 金幣，鍛造鎮信譽 +${HB2.repPerEvent}${first?`、知識卡：${CARDS[e.card].title}`:''}</p>`});
  const t=title2(h.rep);if(HB2.titles.some(x=>x[1]===t&&x[0]===h.rep&&h.rep>0))await say({icon:'★',who:'稱號提升',html:`<p>你現在是<b>${t}</b>了！</p>`});
  await dailyDone('care');  /* 每日任務「處理一次事件或傷口」 */
  refresh();
}
const things=id=>{
  if(id!=='ch2_town'||!on())return [];
  const L=[{kind:'ch2_hbboard',x:HB2.boardAt.x,y:HB2.boardAt.y,label:'鍛造鎮公告板'}];
  if(active()){const e=DATA&&DATA[evOf(S.day)];L.push({kind:'ch2_hbhelp',x:HB2.victimAt.x,y:HB2.victimAt.y+45,label:'求助'+(e?`：${e.name}`:'')});}
  return L;};
const build=(id,H,{sprite})=>{
  if(id!=='ch2_town'||!on())return;
  const b=sprite('shadow','',HB2.boardAt.x,HB2.boardAt.y-30,64,1);b.style.pointerEvents='none';b.innerHTML='<span class="badge lg" style="--c:#8A4B1F;--tc:#fff;--s:64px;opacity:.95">公告</span>';b.style.zIndex=Math.round(HB2.boardAt.y)+5;
  if(active()){const e=DATA&&DATA[evOf(S.day)];const key=e?e.who:'ch2_guest';const s=sprite('shadow','',HB2.victimAt.x,HB2.victimAt.y,Math.round(H*.9),RATIO[key]);s.querySelector('img').src=A[key];}};
return {things,build,acts:{ch2_hbboard:board,ch2_hbhelp:help},load:data,active,rep:()=>st().rep,
  goal:()=>on()&&active()?'鍛造鎮廣場有人需要幫忙：看看公告板，再到廣場上找求助的人。':null};
}
