/* 第三章「港口藍堡」章節程式（D1：航行）。
 * 航行規則沿用第二章：船票 30 金幣、兩晚、每晚 1 包乾糧＋1 瓶開水（自己帶，沒有就向船長買，沒錢扣體力）、
 * 帶在身上的防災包視為旅行行李、颱風或豪雨時停航、每晚睡醒建立存檔點。
 * 教學內容（知識卡、題目、CPR／AED 小遊戲）尚未加入，等老師審核。 */
export default function(FA){
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;},has:(_,k)=>k in FA.S,ownKeys:()=>Reflect.ownKeys(FA.S),getOwnPropertyDescriptor:(_,k)=>({value:FA.S[k],enumerable:true,configurable:true})});
const {RM,STA_MAX,$,say,go,toast,refresh,nextDay,sleep,kitCount,base,expired,stashDepart,stormy,checkpoint}=FA;
const FARE=30,SHIP_RATION=40,SHIP_WATER=30;
const FISHPORT='ch3_fishport',HARBOR='ch3_harbor',CABIN='ch3_ship_cabin';
const deckOf=left=>left>=2?'ch3_ship_day':'ch3_ship_dusk';  /* 第一天白天、第二天黃昏 */
const ARRIVE={[HARBOR]:[820,640],[FISHPORT]:[760,110]};
const onShip=()=>['ch3_ship_day','ch3_ship_dusk',CABIN].includes(S.scene);
async function captTalk(){
  if(onShip()){const v=S.voyage;if(!v)return;return say({p:'ch3_captain',html:`<p>${v.left>1?'還要再航行兩個晚上才會到。':'明天早上就會靠岸了！'}累了就到船艙休息吧。</p>`});}
  const toHarbor=S.scene===FISHPORT;
  if(stormy()){await say({p:'ch3_captain',html:'<p>颱風或豪雨就要來了，今天停航！海上的風浪可不是開玩笑的，等天氣好轉再出發。</p>'});return;}
  const r=S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length,w=kitCount('water');
  const i=await say({p:'ch3_captain',html:`<p>要去${toHarbor?'港口藍堡':'綠葉谷'}嗎？船票 ${FARE} 金幣，要在海上過兩夜。</p><p>船上每天吃一包乾糧、喝一瓶水，自己帶最划算；船上也有賣，乾糧 ${SHIP_RATION}、開水 ${SHIP_WATER} 金幣。</p><p class="small">你的背包：有效乾糧 ${r} 包、開水 ${w} 瓶　金幣 ${S.coins}</p>`,
    buttons:[{label:`買票上船（${FARE} 金幣）`,primary:true,disabled:S.coins<FARE},{label:'再準備一下'}]});
  if(i!==0)return;
  await stashDepart();  /* 防災包是旅行行李：放在這個地區就問要不要帶上 */
  S.coins-=FARE;S.voyage={to:toHarbor?HARBOR:FISHPORT,left:2};
  await go(deckOf(2),[800,660]);
  await say({p:'ch3_captain',html:'<p>起錨！出發囉——！</p><p class="small">可以在甲板上走動，累了就到船艙休息。</p>'});
}
function voyageMeal(){
  const carry=S.stashAt==='carry';  /* 帶在身上的防災包也算自己帶的行李 */
  const take=pred=>{let i=S.kit.findIndex(pred);if(i>=0){S.kit.splice(i,1);return true;}if(carry){i=S.stash.findIndex(pred);if(i>=0){S.stash.splice(i,1);return true;}}return false;};
  const msg=[];
  if(take(k=>base(k)==='ration'&&!expired(k)))msg.push('吃了一包自己帶的乾糧');
  else if(S.coins>=SHIP_RATION){S.coins-=SHIP_RATION;msg.push(`跟船長買了乾糧（${SHIP_RATION} 金幣）`);}
  else{S.sta=Math.max(0,S.sta-30);msg.push('<span class="bad">沒有食物也沒有錢，只能餓著肚子（體力 -30）</span>');}
  if(take(k=>base(k)==='water'))msg.push('喝了一瓶自己帶的開水');
  else if(S.coins>=SHIP_WATER){S.coins-=SHIP_WATER;msg.push(`跟船長買了開水（${SHIP_WATER} 金幣）`);}
  else{S.sta=Math.max(0,S.sta-30);msg.push('<span class="bad">沒有水也沒有錢，口乾舌燥（體力 -30）</span>');}
  return msg;}
async function hatch(){const v=S.voyage;if(!v)return;await go(CABIN,[870,600]);}
async function ladder(){const v=S.voyage;await go(deckOf(v?v.left:2),[1000,600]);}
async function bed(){
  const v=S.voyage;if(!v)return;
  const msg=voyageMeal();
  $('fade').classList.add('on');await sleep(RM?0:600);const html=nextDay();S.sta=Math.max(S.sta,STA_MAX-20);v.left--;refresh();$('fade').classList.remove('on');checkpoint();
  if(v.left>0){await say({icon:'⚓',who:`第 ${S.day} 天・海上`,html:`<p>${msg.join('。')}。</p><p>在船艙睡了一晚，船還在海上航行。</p>`+html});return;}
  const to=v.to;S.voyage=null;
  await say({icon:'⚓',who:`第 ${S.day} 天・靠岸`,html:`<p>${msg.join('。')}。</p><p class="good">船靠岸了！</p>`+html});
  await go(to,ARRIVE[to]);
}
return {
  acts:{ch3_board:captTalk,ch3_hatch:hatch,ch3_bed:bed,ch3_ladder:ladder},
  talk(id){if(id==='ch3_captain')return captTalk();}
};
}
