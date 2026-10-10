/* 第二章鍛造鎮的鍛造委託與島上探索點（老師 2026-10-10 同意第二章加玩法）：完成第二章（S.c.done）後才有。
 * 鍛造委託：鐵匠老鐵每天一張委託單（交鐵礦石或鐵錠，換金幣與鍛造信譽、稱號）；收購價很低、礦石買不到，不會有買低賣高。
 * 島上探索點：礦坑口、廣場營地、碼頭各一個，每天各一次，題目與知識卡都是現有已審核的（迷路、營火、颱風，逐字沿用），答完得一點金幣。
 * 港口商人：第三章「藍堡的日常」的三位商人（日本、澳洲、尼泊爾）輪流靠岸，現在也會到火山島碼頭，輪到的日子比藍堡晚一天（兩邊同一天通常不是同一位）；
 * 買賣、價格、收購上限都和藍堡共用（呼叫第三章的 merchantAt），所以規則一致；第三章沒開放（例如班級後台關閉）時不會出現。
 * 狀態記在既有的 S.c.ch2_or（委託）、S.c.ch2_ex（探索）；數字是遊戲參數，不是醫學數字。 */
export const MER={at:{x:690,y:640},offset:1,names:{jp:'日本商人',au:'澳洲商人',np:'尼泊爾商人'}};
export const OR={titles:[[0,'見習鐵匠'],[3,'鐵匠助手'],[8,'熟練鐵匠'],[15,'鍛造大師']],at:{x:840,y:640},
  list:[{name:'鐵礦石 ×6',need:{ch2_iron:6},pay:60},{name:'鐵錠 ×2',need:{ch2_ingot:2},pay:90},{name:'鐵礦石 ×10',need:{ch2_iron:10},pay:110},{name:'鐵錠 ×4',need:{ch2_ingot:4},pay:200}]};
export const orderOf=day=>OR.list[((day*3)%OR.list.length+OR.list.length)%OR.list.length];
export const titleOr=rep=>OR.titles.filter(t=>rep>=t[0]).pop()[1];
export const EX={reward:10,spots:{
  mine:{scene:'ch2_lavamine',x:900,y:780,label:'礦坑口的告示牌',card:'lost',intro:'礦坑裡岔路很多，告示牌上畫著一個人在黑漆漆的坑道裡迷了路。',
    q:'在濃霧中迷路了，第一步該怎麼做？',opts:['憑感覺一直往前走，總會走出去','停下來、保持冷靜，留在原地，發出求救訊號','往看起來比較亮的地方跑'],ans:1},
  camp:{scene:'ch2_town',x:860,y:780,label:'廣場的營火坑',card:'campfire',intro:'廣場角落有一個石頭圍起來的營火坑，旁邊放著木桶。',
    q:'營火要生在哪裡比較安全？',opts:['乾草堆旁邊，比較好點火','空曠的泥土或石頭地面，遠離草木，旁邊先準備好水','大樹底下，可以擋風'],ans:1,
    explain:'乾草和樹下的落葉很容易被火星點燃，引發野火。要選空曠、沒有可燃物的地面，旁邊準備好水。'},
  port:{scene:'ch2_vport',x:700,y:700,label:'碼頭的氣象公告',card:'typhoon',intro:'碼頭上貼著氣象公告，上面寫著颱風季節的提醒。',
    q:'被困在戶外，暫時回不了家，要躲在哪裡？',opts:['大樹下面，可以擋雨','廣告招牌旁邊','就近進入堅固的建築物；遠離大樹、招牌、電線和河邊'],ans:2}}};
export default function(FA,{on}){
const {say,quiz,refresh,CARDS,A,RATIO,dailyDone}=FA;
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
const ORN={ch2_iron:'鐵礦石',ch2_ingot:'鐵錠'};
const orst=()=>{S.c=S.c||{};return S.c.ch2_or||(S.c.ch2_or={rep:0,done:0,n:0});};
const exst=()=>{S.c=S.c||{};const e=S.c.ch2_ex;if(!e||e.day!==S.day)S.c.ch2_ex={day:S.day,got:{}};return S.c.ch2_ex;};
const have=k=>(S.mat[k]||0);
/* 今天輪到火山島碼頭的商人：回傳 jp/au/np、null（今天沒有商船）、undefined（第三章沒開放，不提供） */
const merchantToday=()=>FA.chCall('ch3','merchantKey',S.day+MER.offset);
async function orders(){
  const h=orst(),o=orderOf(S.day),done=h.done===S.day;
  const need=Object.entries(o.need).map(([k,n])=>`${ORN[k]} ×${n}`).join('、'),ok=Object.entries(o.need).every(([k,n])=>have(k)>=n);
  const i=await say({p:'ch2_smith',who:'鍛造委託',html:`<p>你的稱號：<b>${titleOr(h.rep)}</b>　鍛造信譽 ${h.rep}　已交出 ${h.n} 張</p>`+(done?'<p class="good">今天的委託已經交了，明天再來看看。</p>':`<p>今天的委託單：交 <b>${need}</b>，酬勞 <b>${o.pay}</b> 金幣。</p><p class="small">素材袋：鐵礦石 ${have('ch2_iron')}、鐵錠 ${have('ch2_ingot')}。礦石到熔岩礦坑挖，鐵錠請老鐵冶煉。</p>`),
    buttons:done?[{label:'離開',primary:true}]:[{label:`交出（${need}）`,primary:true,disabled:!ok},{label:'離開'}]});
  if(done||i!==0)return;
  Object.entries(o.need).forEach(([k,n])=>{S.mat[k]-=n;});
  h.done=S.day;h.n++;h.rep++;S.coins+=o.pay;S.earned=(S.earned||0)+o.pay;refresh();
  await say({p:'ch2_smith',html:`<p>做得不錯，這是你的酬勞。</p><p class="good">獲得 ${o.pay} 金幣，鍛造信譽 +1</p>`});
  const t=titleOr(h.rep);if(OR.titles.some(x=>x[1]===t&&x[0]===h.rep&&h.rep>0))await say({icon:'★',who:'稱號提升',html:`<p>你現在是<b>${t}</b>了！</p>`});
}
const explore=key=>async()=>{
  const sp=EX.spots[key],e=exst();
  if(e.got[key]){await say({p:'hero',html:'<p>這裡今天已經看過了，明天再來。</p>'});return;}
  await say({p:'hero',who:sp.label,html:`<p>${sp.intro}</p>`});
  await quiz('hero',sp.q,sp.opts,sp.ans,sp.explain||CARDS[sp.card].text);
  e.got[key]=true;const first=!S.cards[sp.card];S.cards[sp.card]=true;S.coins+=EX.reward;S.earned=(S.earned||0)+EX.reward;
  const n=Object.keys(e.got).length;
  await say({p:'hero',html:`<p class="good">獲得 ${EX.reward} 金幣${first?`、知識卡：${CARDS[sp.card].title}`:''}</p><p class="small">今天的探索：${n}/3</p>`});
  refresh();};
const things=id=>{
  if(!on())return [];
  const L=[];
  if(id==='ch2_smithy')L.push({kind:'ch2_orders',x:OR.at.x,y:OR.at.y,label:'鍛造委託'});
  Object.entries(EX.spots).forEach(([k,sp])=>{if(sp.scene===id)L.push({kind:'ch2_ex_'+k,x:sp.x,y:sp.y,label:sp.label});});
  if(id==='ch2_vport'){const m=merchantToday();if(m)L.push({kind:'ch2_merchant',x:MER.at.x,y:MER.at.y,label:MER.names[m]});}
  return L;};
const build=(id,H,{sprite})=>{
  if(!on())return;
  const mark=(x,y,t,c)=>{const m=sprite('shadow','',x,y-34,52,1);m.style.pointerEvents='none';m.innerHTML=`<span class="badge lg" style="--c:${c};--tc:#fff;--s:52px;opacity:.92">${t}</span>`;m.style.zIndex=Math.round(y)+5;};
  if(id==='ch2_smithy')mark(OR.at.x,OR.at.y,'委託','#8A4B1F');
  Object.values(EX.spots).forEach(sp=>{if(sp.scene===id)mark(sp.x,sp.y,'探索','#2B6CB0');});
  if(id==='ch2_vport'){const m=merchantToday(),key='ch3_m_'+m;if(m&&A[key]){const s=sprite('shadow','',MER.at.x,MER.at.y,Math.round(H*1.05),RATIO[key]);s.querySelector('img').src=A[key];}}};
const acts={ch2_orders:orders,ch2_merchant:()=>{const m=merchantToday();return m?FA.chCall('ch3','merchantAt',m):undefined;}};Object.keys(EX.spots).forEach(k=>{acts['ch2_ex_'+k]=explore(k);});
/* 公告板上說今天火山島碼頭有沒有商船 */
const boardLine=()=>{if(!on())return '';const m=merchantToday();if(m===undefined)return '';return m?`<p>今天火山島碼頭靠岸的商船：<b>${MER.names[m]}</b></p>`:'<p class="small">今天火山島碼頭沒有商船靠岸。</p>';};
return {things,build,acts,boardLine};
}
