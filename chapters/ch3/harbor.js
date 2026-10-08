/* 第三章「藍堡的日常」E1：港口公告板、每天一件海洋傷害求助、港口信譽。
 * 全部是草稿（老師尚未審題目）：只有老師預覽或本機 #debug 加 ?e1=1 才會出現，審核後再改成完成第三章就開放。
 * 狀態記在既有的 S.c.ch3_hb（不新增頂層欄位）：{rep:信譽, done:最近處理完的日子, n:處理過幾件}。
 * 數字都是遊戲參數，不是醫學數字。 */
export const HB={reward:30,repPerEvent:1,
  titles:[[0,'見習志工'],[3,'港口志工'],[8,'資深志工'],[15,'港口隊長']],  /* [需要的信譽, 稱號] */
  boardAt:{x:1050,y:640},victimAt:{x:880,y:740}};
const ORDER=['ch3_h_octopus','ch3_h_jelly','ch3_h_cut','ch3_h_vibrio'];
export const title=rep=>HB.titles.filter(t=>rep>=t[0]).pop()[1];
export const evIdOf=day=>ORDER[((day*3)%ORDER.length+ORDER.length)%ORDER.length];  /* 每天輪一件，4 天輪完，不用亂數 */
export default function(FA,{on,extra}){
const {say,quiz,toast,refresh,CARDS,A,RATIO,takeKit,needCheck,ITEMS,sprite}=FA;
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
let DATA=null;
const data=async()=>DATA||(DATA=(await (await fetch(new URL('harbor.json',import.meta.url))).json()).EVENTS);
const st=()=>{S.c=S.c||{};return S.c.ch3_hb||(S.c.ch3_hb={rep:0,done:0,n:0});};
const needTxt=n=>Object.entries(n).map(([k,v])=>`${ITEMS[k].name} ×${v}`).join('、');
const active=()=>on()&&st().done!==S.day;
const QQ=new URLSearchParams(location.search),PREV=!!QQ.get('preview'),EVQ=Number(QQ.get('ev'));
const todayId=()=>PREV&&EVQ>=1&&EVQ<=ORDER.length?ORDER[EVQ-1]:evIdOf(S.day);  /* 老師預覽可用 ?ev=1～4 直接看第幾件；平常每天輪一件 */
async function board(){
  const h=st(),d=await data(),e=d[todayId()];
  await say({icon:'📋',who:'港口公告板',html:`<p>你的稱號：<b>${title(h.rep)}</b>　港口信譽 ${h.rep}　已幫忙 ${h.n} 件</p>`+
    (extra?extra():'')+(h.done===S.day?'<p class="good">今天的求助都處理好了，明天再來看看。</p>':`<p><b>今天的求助：</b>${e.name}</p><p class="small">港口廣場上有人在等你，走近按「求助」。需要的用品：${Object.keys(e.needs).length?needTxt(e.needs):'不用準備，帶著判斷力就好'}。</p>`)});
}
async function help(){
  if(!active())return;
  const d=await data(),e=d[todayId()];
  await say({p:e.who,wound:e.wound,html:`<p>${e.intro}</p>`});
  const miss=PREV?[]:needCheck(e.needs);  /* 預覽不檢查用品，方便直接看題目 */
  if(miss.length){await say({p:e.who,html:`<p>需要：${needTxt(e.needs)}</p><p class="warn">你的背包還缺：${miss.map(([k,n])=>ITEMS[k].name+' ×'+n).join('、')}</p><p class="small">今天之內帶用品回來還來得及。到港口市集或商店補齊吧。</p>`});return;}
  for(const q of e.qs)await quiz(e.who,q.q,q.opts,q.ans,q.explain);
  if(!PREV)takeKit(e.needs);
  const h=st(),first=!S.cards[e.card];S.cards[e.card]=true;
  h.done=S.day;h.n++;h.rep+=HB.repPerEvent;S.coins+=HB.reward;S.earned=(S.earned||0)+HB.reward;
  await say({p:e.who,html:`<p>${e.thanks}</p><p class="good">獲得 ${HB.reward} 金幣，港口信譽 +${HB.repPerEvent}${first?`、知識卡：${CARDS[e.card].title}`:''}</p>`});
  if(e.emph)await say({icon:'！',who:'請記住',html:'<p style="font-size:1.2em"><b>傷口碰過海水或生海鮮，紅腫、發熱、起水泡、發燒，一定要先就醫。</b></p>'});
  const t=title(h.rep);if(HB.titles.some(x=>x[1]===t&&x[0]===h.rep&&h.rep>0))await say({icon:'★',who:'稱號提升',html:`<p>你現在是<b>${t}</b>了！</p>`});
  refresh();
}
const things=id=>{
  if(id!=='ch3_harbor'||!on())return [];
  const L=[{kind:'ch3_hbboard',x:HB.boardAt.x,y:HB.boardAt.y,label:'港口公告板'}];
  if(active()){const e=DATA&&DATA[todayId()];L.push({kind:'ch3_hbhelp',x:HB.victimAt.x,y:HB.victimAt.y+45,label:'求助'+(e?`：${e.name}`:'')});}
  return L;};
const build=(id,H,{sprite})=>{
  if(id!=='ch3_harbor'||!on())return;
  const b=sprite('shadow','',HB.boardAt.x,HB.boardAt.y,Math.round(H*1.7),RATIO.ch3_hb_board);b.querySelector('img').src=A.ch3_hb_board;
  if(active()){const e=DATA&&DATA[todayId()];const key=e?e.who:'ch3_by_red';const s=sprite('shadow','',HB.victimAt.x,HB.victimAt.y,Math.round(H*.9),RATIO[key]);s.querySelector('img').src=A[key];}};
const addRep=n=>{st().rep+=n;};
return {things,build,acts:{ch3_hbboard:board,ch3_hbhelp:help},load:data,active,addRep,rep:()=>st().rep,
  goal:()=>on()&&active()?'港口有人需要幫忙：看看港口公告板，再到廣場上找求助的人。':null};
}
