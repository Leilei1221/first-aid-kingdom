/* 渡海航線的共用程式（第二章、第三章共用；2026-10-09 整理，行為與整理前完全相同）。
 * 規則：船票 30 金幣、兩晚、每晚 1 包乾糧＋1 瓶開水（自己帶，沒有就向船長買，沒錢扣體力）、帶在身上的防災包視為旅行行李、
 * 颱風或豪雨（今天或明天）停航、每晚睡醒建立存檔點、第一晚暈船題、第二晚有人落水題。
 * 各章只提供差異：cfg.capt（船長角色）、onShip()（是否在船上）、route()（從這裡出發去哪）、deck(left)（上船後去哪個場景）、
 * arrive（各港口抵達座標）、beforeBoard()（上船前要先做的事，例如第二章的救生衣題）、onArrive(to)（靠岸後的事，例如第一次抵達的迎接）。
 * 文字與題目與整理前逐字相同，不要在這裡改醫療內容。 */
export const FARE=30,SHIP_RATION=40,SHIP_WATER=30;
export function makeVoyage(FA,S,cfg){
  const {RM,$,say,quiz,go,refresh,nextDay,sleep,kitCount,base,expired,stashDepart,stormy,checkpoint,CARDS}=FA;
  const CAPT=cfg.capt;
  async function captTalk(){
    if(cfg.onShip()){const v=S.voyage;if(!v)return;return say({p:CAPT,html:`<p>${v.left>1?'還要再航行兩個晚上才會到。':'明天早上就會靠岸了！'}累了就到船艙休息吧。</p>`});}
    const rt=cfg.route();
    if(stormy()){await say({p:CAPT,html:'<p>颱風或豪雨就要來了，今天停航！海上的風浪可不是開玩笑的，等天氣好轉再出發。</p>'});return;}
    const r=kitCount('ration')?S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length:0,w=kitCount('water');
    const i=await say({p:CAPT,html:`<p>要去${rt.name}嗎？船票 ${FARE} 金幣，要在海上過兩夜。</p><p>船上每天吃一包乾糧、喝一瓶水，自己帶最划算；船上也有賣，乾糧 ${SHIP_RATION}、開水 ${SHIP_WATER} 金幣。</p><p class="small">你的背包：有效乾糧 ${r} 包、開水 ${w} 瓶　金幣 ${S.coins}</p>`,
      buttons:[{label:`買票上船（${FARE} 金幣）`,primary:true,disabled:S.coins<FARE},{label:'再準備一下'}]});
    if(i!==0)return;
    if(cfg.beforeBoard)await cfg.beforeBoard();
    await stashDepart();  /* 防災包是旅行行李：放在這個地區就問要不要帶上 */
    S.coins-=FARE;S.voyage={to:rt.to,left:2,sick:false,mob:false};
    const d=cfg.deck(2);await go(d[0],d[1]);
    await say({p:CAPT,html:'<p>起錨！出發囉——！</p><p class="small">可以在甲板上走動，累了就到船艙休息。</p>'});
  }
  function meal(){
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
  async function sleepAtSea(){
    const v=S.voyage;if(!v)return;
    if(!v.sick){await say({p:'hero',html:'<p>船搖來搖去，胃裡一陣翻騰，頭好暈……好像暈船了。</p>'});
      await quiz('hero','暈船了，怎麼做比較好？',['躲進船艙看書轉移注意力','到通風的甲板上，看著遠方的地平線','大吃一頓就不會暈了'],1,CARDS.ch2_seasick.text);S.cards.ch2_seasick=true;v.sick=true;return;}
    if(v.left===1&&!v.mob){await say({p:CAPT,html:'<p class="bad">有人落水了！一位船員被大浪捲下船！</p>'});
      const i=await say({p:'hero',html:'<p class="q">你要怎麼做？</p>',buttons:[{label:'立刻跳下海去救他'},{label:'大聲呼救，把救生圈拋給他'}]});
      await say({p:CAPT,html:`<p class="${i===1?'good':'bad'}">${i===1?'做得好！船員抓住了救生圈，被拉回船上了。':'別跳！在海上跳下去，只會多一個需要救的人！快拋救生圈！'}</p><p>他在水裡很冷靜，一直用<b>仰漂</b>的方式浮著等我們。</p>`});
      await say({p:CAPT,html:`<div class="card"><b>${CARDS.ch2_overboard.title}</b><p>${CARDS.ch2_overboard.text}</p></div>`});S.cards.ch2_overboard=true;v.mob=true;return;}
    const msg=meal();
    $('fade').classList.add('on');await sleep(RM?0:600);const html=nextDay();S.sta=Math.max(S.sta,FA.staMax()-20);v.left--;refresh();$('fade').classList.remove('on');checkpoint();
    if(v.left>0){await say({icon:'⚓',who:`第 ${S.day} 天・海上`,html:`<p>${msg.join('。')}。</p><p>在船艙睡了一晚，船還在海上航行。</p>`+html});return;}
    const to=v.to;S.voyage=null;
    await say({icon:'⚓',who:`第 ${S.day} 天・靠岸`,html:`<p>${msg.join('。')}。</p><p class="good">船靠岸了！</p>`+html});
    await go(to,cfg.arrive[to]);
    if(cfg.onArrive)await cfg.onArrive(to);
  }
  return {captTalk,sleepAtSea};
}
