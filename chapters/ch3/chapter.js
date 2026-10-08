/* 第三章「港口藍堡」章節程式（D1：航行）。
 * 航行規則沿用第二章：船票 30 金幣、兩晚、每晚 1 包乾糧＋1 瓶開水（自己帶，沒有就向船長買，沒錢扣體力）、
 * 帶在身上的防災包視為旅行行李、颱風或豪雨時停航、每晚睡醒建立存檔點。
 * D2-1：第 1 節（安全、反應、呼吸判斷、求救）。知識卡與題目的文字照老師提供的草稿，老師已於 2026-10-07 審核通過（照現有文字）。
 * CPR 按壓、吹氣、AED、章末事件尚未加入，等老師審核。 */
import * as R from './rhythm.js';
import * as AED from './aed.js';
import harborInit from './harbor.js';
import fishInit from './fish.js';
import e3Init from './e3.js';
export default function(FA){
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;},has:(_,k)=>k in FA.S,ownKeys:()=>Reflect.ownKeys(FA.S),getOwnPropertyDescriptor:(_,k)=>({value:FA.S[k],enumerable:true,configurable:true})});
const {RM,STA_MAX,$,say,lines,quiz,orderQuiz,go,toast,refresh,nextDay,sleep,kitCount,base,expired,stashDepart,stormy,checkpoint,CARDS,A,RATIO}=FA;
const QS=new URLSearchParams(location.search),PREV=!!QS.get('preview');
const E1_ON=PREV||(location.hash==='#debug'&&QS.get('e1')==='1');  /* 「藍堡的日常」E1 是草稿：只有老師預覽或本機 #debug ?e1=1 看得到 */
if(E1_ON)Object.assign(FA.WOUNDS,{octopus:'藍環章魚咬傷',jelly:'水母螫傷',rockcut:'岩石割傷',vibrio:'海洋弧菌感染'});  /* 圖在 assets/w_*.webp；草稿期間只在 E1 開啟時加入，傷口圖鑑不會多出格子 */
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
    buttons:[{label:`買票上船（${FARE} 金幣）`,primary:true,disabled:S.coins<FARE},{label:'再準備一下'},...(toHarbor&&E3&&E3.sailorOffer()?[{label:'買水手服（200 金幣）'}]:[])]});
  if(i===2)return E3.buySailor();
  if(i!==0)return;
  await stashDepart();  /* 防災包是旅行行李：放在這個地區就問要不要帶上 */
  S.coins-=FARE;S.voyage={to:toHarbor?HARBOR:FISHPORT,left:2,sick:false,mob:false};
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
  if(!v.sick){await say({p:'hero',html:'<p>船搖來搖去，胃裡一陣翻騰，頭好暈……好像暈船了。</p>'});
    await quiz('hero','暈船了，怎麼做比較好？',['躲進船艙看書轉移注意力','到通風的甲板上，看著遠方的地平線','大吃一頓就不會暈了'],1,CARDS.ch2_seasick.text);S.cards.ch2_seasick=true;v.sick=true;return;}
  if(v.left===1&&!v.mob){await say({p:'ch3_captain',html:'<p class="bad">有人落水了！一位船員被大浪捲下船！</p>'});
    const i=await say({p:'hero',html:'<p class="q">你要怎麼做？</p>',buttons:[{label:'立刻跳下海去救他'},{label:'大聲呼救，把救生圈拋給他'}]});
    await say({p:'ch3_captain',html:`<p class="${i===1?'good':'bad'}">${i===1?'做得好！船員抓住了救生圈，被拉回船上了。':'別跳！在海上跳下去，只會多一個需要救的人！快拋救生圈！'}</p><p>他在水裡很冷靜，一直用<b>仰漂</b>的方式浮著等我們。</p>`});
    await say({p:'ch3_captain',html:`<div class="card"><b>${CARDS.ch2_overboard.title}</b><p>${CARDS.ch2_overboard.text}</p></div>`});S.cards.ch2_overboard=true;v.mob=true;return;}
  const msg=voyageMeal();
  $('fade').classList.add('on');await sleep(RM?0:600);const html=nextDay();S.sta=Math.max(S.sta,FA.staMax()-20);v.left--;refresh();$('fade').classList.remove('on');checkpoint();
  if(v.left>0){await say({icon:'⚓',who:`第 ${S.day} 天・海上`,html:`<p>${msg.join('。')}。</p><p>在船艙睡了一晚，船還在海上航行。</p>`+html});return;}
  const to=v.to;S.voyage=null;
  await say({icon:'⚓',who:`第 ${S.day} 天・靠岸`,html:`<p>${msg.join('。')}。</p><p class="good">船靠岸了！</p>`+html});
  await go(to,ARRIVE[to]);
  if(to===HARBOR){S.c=S.c||{};if(!S.c.ch3_intro){S.c.ch3_intro=true;await lines(SAILOR,['你就是老團長的孫子吧？一路辛苦了！','你爺爺的老朋友在廣場的另一頭等你，是港口的救生員。往右下方走，救生站旁邊就是了。']);}}
}
/* ---------- 第 1 節：市集倒地者（知識卡 K1-1～K1-3、題目 Q1-1～Q1-7；資料在 dialogues.json、cards.json） ---------- */
{const q=new URLSearchParams(location.search);if(q.get('preview')&&q.get('lessons')==='1')['ch3_k1_3','ch3_k2_3','ch3_k3_1','ch3_k3_3','ch3_k4_4'].forEach(k=>{S.cards[k]=true;});}  /* 老師預覽用：不影響一般進入 */
const DOWN={x:790,y:575},PASSERS=['ch3_by_red','ch3_by_blue','ch3_by_green'],PNAME={ch3_by_red:'紅衣路人',ch3_by_blue:'藍衣路人',ch3_by_green:'綠衣路人'};
let QZ=null;
const quizzes=async()=>QZ||(QZ=(await (await fetch(new URL('dialogues.json',import.meta.url))).json()).quizzes);
const showCard=async k=>{const first=!S.cards[k];S.cards[k]=true;await say({p:'hero',html:`<div class="card"><b>${CARDS[k].title}</b><p>${CARDS[k].text}</p></div>${first?'<p class="good">獲得知識卡</p>':''}`});};
const ask=async key=>{const z=(await quizzes())[key];await quiz('hero',z.q,z.opts,z.ans,z.explain);};
const askOrder=async key=>{const z=(await quizzes())[key];await orderQuiz('hero',z.title,z.steps,z.explain);};
async function assign(job,left){  /* 指派路人：點選要請誰；對錯標準就是 Q1-5（指定特定的人），這裡不另設判定 */
  const i=await say({p:'hero',html:`<p>用手指向一個人：「你，${job}！」</p>`,buttons:left.map(id=>({label:PNAME[id]}))});
  const id=left[i];await say({p:id,html:`<p>（點點頭，立刻照做。）</p>`});return id;}
async function lesson1(){
  const go1=await say({p:'hero',html:'<p>有人倒在港口市集的空地上，旁邊圍了幾個人，沒有人動手。</p>',buttons:[{label:'上前查看',primary:true},{label:'先離開'}]});
  if(go1!==0)return;
  await ask('ch3_q1_1');await showCard('ch3_k1_1');
  await ask('ch3_q1_2');await ask('ch3_q1_3');await showCard('ch3_k1_2');
  await ask('ch3_q1_4');
  await say({p:'hero',html:'<p>傷者沒有反應，也沒有正常呼吸。圍觀的人只是看著。</p>'});
  await ask('ch3_q1_5');
  const a=await assign('請打 119',PASSERS);
  await assign('請去拿 AED',PASSERS.filter(x=>x!==a));
  await ask('ch3_q1_6');await askOrder('ch3_q1_7');await showCard('ch3_k1_3');
  await say({p:'hero',html:'<p class="good">第 1 節完成！</p><p class="small">接下來到港口的救生站，練習壓胸、人工呼吸與 AED。</p>'});
}

/* ---------- 第 2 節：救生站假人（知識卡 K2-1～K2-3、題目 Q2-1～Q2-8、按壓節拍＋換手；數字計算在 rhythm.js） ---------- */
const MANI={x:1110,y:640};
const DEBUG=location.hash==='#debug'&&localStorage.getItem('fa-debug')==='1';
let LAST=null;  /* 最近一次練習的記錄（不存檔；本階段只記錄、不判定 E4） */
async function rhythmGame(){
  const T=Object.assign({},R.DEFAULTS,DEBUG&&window.__ch3Tune||{});
  const taps=[];let fatigueMs=0,swapped=false,after=0;
  const r=await say({p:'hero',who:'按壓練習',html:`<p class="small">跟著節拍燈點「壓」（或按空白鍵）；目標每分鐘 100 至 120 下。手臂累了就換手。</p>
    <div style="display:flex;gap:14px;align-items:center;justify-content:center;margin:8px 0">
      <div id="rb" style="width:34px;height:34px;border-radius:50%;background:#5BD18B;opacity:.25;transition:opacity .12s"></div>
      <button id="rp" type="button" class="btn primary" style="min-width:150px;min-height:64px;font-size:1.5em;touch-action:manipulation">壓</button>
      <div id="rr" style="min-width:96px;font-weight:bold">—</div></div>
    <div style="height:12px;background:#E4DCCB;border-radius:6px;overflow:hidden"><div id="rf" style="height:100%;width:0;background:#C0392B;transition:width .1s"></div></div>
    <p class="small" id="rm">手臂狀態：還有力氣</p>
    <div style="display:flex;gap:8px"><button id="rs" type="button" class="btn" disabled style="flex:1">換手</button><button id="re" type="button" class="btn" style="flex:1">結束練習</button></div>`,buttons:[],
    onRender:(root,fin)=>{
      const $q=id=>root.querySelector('#'+id),done=v=>{clearInterval(tick);clearInterval(beat);document.removeEventListener('keydown',key);fin(v);};
      const tap=()=>{const t=performance.now();if(taps.length){const g=t-taps[taps.length-1];if(g<=T.pauseGapMs)fatigueMs+=g;}
        taps.push(t);if(swapped&&++after>=T.afterSwap)return done('done');
        const b=R.rateBand(R.recentRate(taps)),rate=R.recentRate(taps);
        $q('rr').textContent=rate==null?'—':`${rate} 下／分`;$q('rr').style.color=b==='ok'?'#2F7D4F':'#C0392B';
        if(b)$q('rr').textContent+=b==='slow'?'・太慢':b==='fast'?'・太快':'・剛好';};
      const key=e=>{if(e.code==='Space'){e.preventDefault();if(!e.repeat)tap();}};
      $q('rp').addEventListener('pointerdown',e=>{e.preventDefault();tap();});
      document.addEventListener('keydown',key);
      $q('re').onclick=()=>done('stop');
      $q('rs').onclick=()=>{swapped=true;fatigueMs=0;after=0;$q('rs').disabled=true;$q('rm').innerHTML='<span class="good">換手！新的施救者接手，趕快接著壓。</span>';};
      const beat=setInterval(()=>{const b=$q('rb');b.style.opacity=1;setTimeout(()=>b.style.opacity=.25,120);},60000/R.GUIDE_BPM);
      const tick=setInterval(()=>{const f=Math.min(1,fatigueMs/(T.fatigueSec*1000));$q('rf').style.width=Math.round(f*100)+'%';
        if(!swapped){$q('rs').disabled=f<1;$q('rm').textContent=f>=1?'手臂痠了，該換手了！':'手臂狀態：還有力氣';}
        if(taps.length&&performance.now()-taps[taps.length-1]>T.pauseGapMs&&!swapped)$q('rm').textContent='中斷了，快繼續壓！';},100);}});
  return {taps,stats:R.stats(taps,T),why:r};}
async function lesson2(){
  const go1=await say({p:'hero',html:'<p>救生站裡擺著一具 CPR 練習假人。</p>',buttons:[{label:'開始練習',primary:true},{label:'先離開'}]});
  if(go1!==0)return;
  await ask('ch3_q2_1');await ask('ch3_q2_3');await ask('ch3_q2_4');await showCard('ch3_k2_1');
  await ask('ch3_q2_2');await ask('ch3_q2_5');await showCard('ch3_k2_2');
  await say({p:'hero',html:'<p>換你練習了。跟著節拍燈按壓，累了就換手。</p>',buttons:[{label:'開始',primary:true}]});
  const g=await rhythmGame();LAST=g.stats;if(DEBUG)window.__ch3Last=g;
  const st=g.stats,sec=ms=>(ms/1000).toFixed(1);
  await say({p:'hero',html:st.n<2?'<p>這次沒有按壓紀錄。</p>':`<p><b>練習紀錄</b>（遊戲內的實際時間）</p><p>按壓 ${st.n} 下，平均 ${st.avgRate==null?'—':st.avgRate} 下／分（目標 100 至 120）<br>最長一次中斷：${sec(st.longestPauseMs)} 秒<br>按壓時間占比：${st.ratio==null?'—':Math.round(st.ratio*100)}%</p><p class="small">這些數字目前只是紀錄，之後會用在章末評分。</p>`});
  await ask('ch3_q2_6');await ask('ch3_q2_7');await ask('ch3_q2_8');await showCard('ch3_k2_3');
  await say({p:'hero',html:'<p class="good">第 2 節完成！</p><p class="small">下一步：在救生站，假人旁的面罩練習人工呼吸、牆邊練習 AED。</p>'});
}

/* ---------- 第 3 節：人工呼吸 30:2（假人旁的 CPR 面罩）與 AED（牆上的壁掛箱）。兩個練習各自獨立 ---------- */
const MASK={x:1010,y:700},AED_AT={x:1192,y:512};
async function breathGame(opt={}){  /* opt.finale：章末版——沒有步驟提示、不能中途結束，沒先壓額抬下巴就吹的那一次不算 */
  const fin0=!!opt.finale;const att=[];let open=false,good=0,t0=null,tick=null;
  await say({p:'hero',who:'人工呼吸練習',html:`<p class="small">${fin0?'按住「吹氣」，讓胸部起伏到綠色範圍內放開（也可以按住空白鍵）。':'先壓額抬下巴打開呼吸道；再按住「吹氣」，讓胸部起伏到綠色範圍內放開（也可以按住空白鍵）。要吹 2 次。'}</p>
    <div style="height:22px;background:#E4DCCB;border-radius:11px;position:relative;overflow:hidden;margin:8px 0"><div style="position:absolute;left:${R.BREATH.low}%;width:${R.BREATH.high-R.BREATH.low}%;top:0;bottom:0;background:rgba(91,209,139,.55)"></div><div id="bf" style="height:100%;width:0;background:#4A9BD9;opacity:.9"></div></div>
    <p class="small" id="bm">${fin0?'':'先壓額抬下巴。'}</p>
    <div style="display:flex;gap:8px"><button id="ba" type="button" class="btn" style="flex:1">壓額抬下巴</button><button id="bh" type="button" class="btn primary" ${fin0?'':'disabled'} style="flex:1;touch-action:manipulation">按住吹氣</button></div>
    <div style="display:flex;gap:8px;margin-top:8px"><button id="bd" type="button" class="btn" disabled style="flex:1">回到壓胸</button><button id="be" type="button" class="btn" style="flex:1;${fin0?'display:none':''}">結束練習</button></div>`,buttons:[],
    onRender:(root,fin)=>{
      const $q=id=>root.querySelector('#'+id),msg=h=>{$q('bm').innerHTML=h;};
      const done=v=>{clearInterval(tick);document.removeEventListener('keydown',kd);document.removeEventListener('keyup',ku);fin(v);};
      const start=()=>{if((!open&&!fin0)||t0!=null||good>=2)return;t0=performance.now();msg('吹氣中……到綠色範圍就放開。');tick=setInterval(()=>{$q('bf').style.width=R.breathLevel(performance.now()-t0)+'%';},40);};
      const stop=()=>{if(t0==null)return;const lv=R.breathLevel(performance.now()-t0),band=R.breathBand(lv);t0=null;clearInterval(tick);$q('bf').style.width=lv+'%';att.push({level:Math.round(lv),band,noAirway:!open});
        if(fin0&&!open)msg('<span class="bad">沒有先打開呼吸道，這次不算。</span>');
        else if(band==='ok'){good++;msg(`<span class="good">胸部明顯起伏，很好！</span>（${good}/2）`);}
        else msg(`<span class="bad">${band==='low'?'吹得太少，胸部沒有明顯起伏。':'吹太多了。吹到胸部明顯起伏就好，不是越用力越好。'}</span>再試一次。`);
        if(good>=2){$q('bh').disabled=true;$q('bd').disabled=false;msg(fin0?'<span class="good">2 次都吹好了。</span>':'<span class="good">2 次都吹好了！</span>吹氣完立刻回到壓胸，不要拖延。');}};
      const kd=e=>{if(e.code==='Space'){e.preventDefault();if(!e.repeat)start();}},ku=e=>{if(e.code==='Space'){e.preventDefault();stop();}};
      document.addEventListener('keydown',kd);document.addEventListener('keyup',ku);
      $q('ba').onclick=()=>{open=true;$q('ba').disabled=true;$q('bh').disabled=false;msg('呼吸道打開了。按住「吹氣」。');};
      const h=$q('bh');h.addEventListener('pointerdown',e=>{e.preventDefault();start();});['pointerup','pointercancel','pointerleave'].forEach(ev=>h.addEventListener(ev,stop));
      $q('bd').onclick=()=>done('done');$q('be').onclick=()=>done('stop');}});
  return {attempts:att,good};}
async function aedGame(){
  const errors=[];let i=0;
  await say({p:'hero',who:'AED 練習',html:`<div style="display:flex;gap:12px;align-items:center"><img src="${A.ch3_aed_device}" alt="AED" style="height:74px"><div id="av" style="flex:1;font-weight:700;color:#7FD6A5"></div></div>
    <p class="small" id="as"></p><div id="ab" style="display:flex;flex-direction:column;gap:8px;margin-top:6px"></div><p id="am" style="margin-top:8px"></p>`,buttons:[],
    onRender:(root,fin)=>{
      const $q=id=>root.querySelector('#'+id);
      const draw=()=>{const s=AED.STEPS[i];$q('av').textContent='AED：「'+s.voice+'」';$q('as').textContent=`第 ${i+1} 步，共 ${AED.STEPS.length} 步`;
        const opts=[{t:s.right,r:true},{t:s.wrong.label,r:false}].sort(()=>Math.random()-.5);$q('ab').innerHTML='';
        opts.forEach(o=>{const b=document.createElement('button');b.type='button';b.className='btn';b.textContent=o.t;b.dataset.right=o.r?'1':'0';
          b.onclick=()=>{const r=AED.choose(i,o.r);if(!r.ok){errors.push({step:AED.STEPS[i].id,code:r.code});$q('am').innerHTML=`<span class="bad">這個做法不對。</span>${r.msg}`;return;}
            $q('am').innerHTML='<span class="good">正確！</span>';i++;if(i>=AED.STEPS.length)setTimeout(()=>fin('done'),500);else draw();};$q('ab').appendChild(b);});};
      draw();}});
  return {errors};}
async function lesson3Breath(){
  const go1=await say({p:'hero',html:'<p>假人旁邊放著一個 CPR 面罩。</p>',buttons:[{label:'開始練習',primary:true},{label:'先離開'}]});
  if(go1!==0)return;
  await ask('ch3_q3_1');await ask('ch3_q3_2');await showCard('ch3_k3_1');
  await say({p:'hero',html:'<p>換你練習了：打開呼吸道，吹 2 次氣。</p>',buttons:[{label:'開始',primary:true}]});
  const g=await breathGame();if(DEBUG)window.__ch3Breath=g;
  await say({p:'hero',html:g.good>=2?`<p class="good">人工呼吸練習完成！</p><p class="small">${S.cards.ch3_k3_3?'':'接著可以到牆邊練習 AED。'}一共吹了 ${g.attempts.length} 次，其中 ${g.good} 次吹到胸部明顯起伏。</p>`:'<p>這次沒有練完。想再練的話，隨時可以再來。</p>'});
}
async function lesson3Aed(){
  const go1=await say({p:'hero',html:'<p>牆上掛著一個 AED。</p>',buttons:[{label:'開始練習',primary:true},{label:'先離開'}]});
  if(go1!==0)return;
  await ask('ch3_q3_3');await showCard('ch3_k3_2');await ask('ch3_q3_4');await ask('ch3_q3_5');await showCard('ch3_k3_3');
  await say({p:'hero',html:'<p>換你練習了：跟著 AED 的語音，一步一步操作。</p>',buttons:[{label:'開始',primary:true}]});
  const g=await aedGame();if(DEBUG)window.__ch3Aed=g;
  await say({p:'hero',html:`<p class="good">AED 練習完成！</p><p class="small">${g.errors.length?`練習中選過 ${g.errors.length} 次錯誤的做法，說明都看過了。`:'每一步都選對了。'}</p>`});
  await ask('ch3_q3_6');await ask('ch3_q3_7');await askOrder('ch3_q3_8');
  await say({p:'hero',html:'<p class="good">第 3 節完成！</p><p class="small">下一步：到港口找救生員。</p>'});
}

/* ---------- 第 4 節：港口救生員（專線、防災、技能要回實體練習，加上分工決策題 D-1～D-3） ---------- */
async function lesson4(){  /* 入口在救生員的選單（lifegHarbor），選「請教救生員（第 4 節）」才進來 */
  await ask('ch3_q4_1');await showCard('ch3_k4_1');
  await ask('ch3_q4_2');await ask('ch3_q4_3');await showCard('ch3_k4_2');
  await say({p:'hero',html:'<p>接下來是分工練習：現場有人倒下，你要怎麼分配？</p>',buttons:[{label:'開始',primary:true}]});
  await ask('ch3_d1');await ask('ch3_d2');await ask('ch3_d3');
  await askOrder('ch3_q4_5');await ask('ch3_q4_6');await showCard('ch3_k4_4');
  await say({p:'hero',html:'<p class="good">第 4 節完成！</p><p class="small">接下來回港口市集，查看倒在地上的人，進行章末整合演練。</p>'});
}

/* ---------- 章末整合演練（第 4 節 4b）：判斷 → 分工 → 壓胸＋吹氣 → AED 送到 → 續壓與換手 → 救護人員接手 → 結算 ----------
 * 沒有逐步提示：沒有「太慢／太快」文字、沒有「該換手了」文字、吹氣沒有步驟說明。
 * 完成、星數、心跳之匣記在現有的 S.c（各章進度）：S.c.ch3_done、S.c.ch3_stars、S.c.ch3_box，不新增存檔欄位。
 * 嚴重錯誤（E1～E7）只記錄，不觸發救援失敗；記在 window.__ch3Finale（只有 #debug）。 */
async function askScored(key,rec){  /* 同核心的 quiz（答錯顯示說明、可再選），另外記錄答錯幾次與選到的嚴重錯誤 */
  const z=(await quizzes())[key];let wrong=0;
  for(;;){
    const i=await say({p:'hero',hideCap:true,html:`<p class="q">${z.q}</p>`,buttons:z.opts.map(o=>({label:o}))});
    const ok=i===z.ans;
    if(!ok){wrong++;if(z.severe&&(!z.severeOpts||z.severeOpts.includes(i)))rec.errs.push({key,code:z.severe,opt:i});}
    await say({p:'hero',html:`<p class="${ok?'good':'bad'}">${ok?'處置正確！':'這個做法不對。'}</p><p>${z.explain}</p>`,buttons:[{label:ok?'繼續':'再選一次',primary:true}]});
    if(ok){FA.luckyBonus();return wrong;}}}
async function finaleCompress(ses,T,{count,untilSwap}){  /* 一段按壓：count 下就結束；或換手後再壓 afterSwap 下就結束。回傳 'done' 或 'stop'（停止急救） */
  let n=0;
  return say({p:'hero',who:'章末演練',html:`<div style="display:flex;gap:14px;align-items:center;justify-content:center;margin:8px 0">
      <div id="rb" style="width:34px;height:34px;border-radius:50%;background:#5BD18B;opacity:.25;transition:opacity .12s"></div>
      <button id="rp" type="button" class="btn primary" style="min-width:150px;min-height:64px;font-size:1.5em;touch-action:manipulation">壓</button></div>
    <div style="height:12px;background:#E4DCCB;border-radius:6px;overflow:hidden"><div id="rf" style="height:100%;width:0;background:#C0392B;transition:width .1s"></div></div>
    <div style="display:flex;gap:8px;margin-top:8px"><button id="rs" type="button" class="btn" disabled style="flex:1">換手</button><button id="re" type="button" class="btn" style="flex:1">停止急救</button></div>`,buttons:[],
    onRender:(root,fin)=>{
      const $q=id=>root.querySelector('#'+id),done=v=>{clearInterval(tick);clearInterval(beat);document.removeEventListener('keydown',key);fin(v);};
      const tap=()=>{const t=performance.now(),L=ses.taps;if(L.length){const g=t-L[L.length-1];if(g<=T.pauseGapMs)ses.fatigueMs+=g;}
        L.push(t);ses.sinceSwap++;n++;
        if(untilSwap?(ses.swaps>=1&&ses.sinceSwap>=T.afterSwap):n>=count)done('done');};
      const key=e=>{if(e.code==='Space'){e.preventDefault();if(!e.repeat)tap();}};
      $q('rp').addEventListener('pointerdown',e=>{e.preventDefault();tap();});document.addEventListener('keydown',key);
      $q('re').onclick=()=>done('stop');
      $q('rs').onclick=()=>{ses.swaps++;ses.fatigueMs=0;ses.sinceSwap=0;$q('rs').disabled=true;};
      const beat=setInterval(()=>{const b=$q('rb');b.style.opacity=1;setTimeout(()=>b.style.opacity=.25,120);},60000/R.GUIDE_BPM);
      const tick=setInterval(()=>{const f=Math.min(1,ses.fatigueMs/(T.fatigueSec*1000));$q('rf').style.width=Math.round(f*100)+'%';$q('rs').disabled=f<1;},100);}});}
async function finale(){
  const T=Object.assign({},R.DEFAULTS,R.FINALE,DEBUG&&window.__ch3Tune||{});
  const ses={taps:[],segs:[],fatigueMs:0,swaps:0,sinceSwap:0,cut(){if(ses.taps.length)ses.segs.push(ses.taps);ses.taps=[];}};
  const rec={errs:[],judgeWrong:[],d1Wrong:null,breath:null,aedErrors:null,stopped:false};
  const go1=await say({p:'hero',who:'章末演練',html:'<p>市集的人群圍了過來，有人倒在地上。這是章末演練，不會有逐步提示。</p>',buttons:[{label:'開始',primary:true},{label:'先離開'}]});
  if(go1!==0)return;
  for(const k of ['ch3_q1_1','ch3_q1_2','ch3_q1_3'])rec.judgeWrong.push(await askScored(k,rec));
  rec.d1Wrong=await askScored('ch3_d1',rec);
  const a=await assign('請打 119',PASSERS);const b=await assign('請去拿 AED',PASSERS.filter(x=>x!==a));
  const run=async()=>{
    if(await finaleCompress(ses,T,{count:T.compress})==='stop')return false;
    rec.breath=await breathGame({finale:true});
    if(await finaleCompress(ses,T,{count:T.compress})==='stop')return false;
    ses.cut();  /* 接下來路人接手壓胸，你操作 AED：不算你的中斷時間 */
    await say({p:b,html:'<p>（把 AED 放在傷者旁邊。）</p>'});
    await askScored('ch3_d2',rec);rec.aedErrors=(await aedGame()).errors;for(const e of ['E2','E4','E5'])rec.aedErrors.filter(x=>x.code===e).forEach(x=>rec.errs.push({key:'aed:'+x.step,code:x.code}));rec.aedErrors=rec.aedErrors.length;
    if(await finaleCompress(ses,T,{untilSwap:true})==='stop')return false;
    return true;};
  const completed=await run();rec.stopped=!completed;if(rec.stopped)rec.errs.push({key:'stop',code:'E6'});
  ses.cut();
  if(completed)await say({p:'hero',html:'<p>救護人員到了，接手急救。</p>'});
  const st=R.combine(ses.segs.map(x=>R.stats(x,T)));
  if(st.longestPauseMs>T.pauseLimitMs)rec.errs.push({key:'pause',code:'E4'});
  const sc=R.scoreFinale({judgeWrong:rec.judgeWrong,d1Wrong:rec.d1Wrong,stats:st,breath:rec.breath,aedErrors:rec.aedErrors==null?1:rec.aedErrors,stopped:rec.stopped},T.pauseLimitMs);
  S.c=S.c||{};let box=false;
  const rw=completed?FA.starReward('ch3',sc.total):null;  /* 星級獎勵：每個新達成的星級只領一次（見 content/balance.json 的 STAR_REWARD） */
  if(completed){S.c.ch3_done=true;S.c.ch3_stars=Math.max(S.c.ch3_stars||0,sc.total);if(!S.c.ch3_box){S.c.ch3_box=true;box=true;}}
  if(DEBUG)window.__ch3Finale={rec,stats:st,score:sc,completed};
  const mark=ok=>ok?'★':'☆',sec=ms=>(ms/1000).toFixed(1),br=rec.breath?rec.breath.attempts.slice(0,2).filter(x=>x.band==='ok'&&!x.noAirway).length:0;
  await say({p:'hero',who:'章末演練結果',html:`<p><b>${completed?'演練完成':'演練中途停止'}</b>　${'★'.repeat(sc.total)+'☆'.repeat(5-sc.total)}（${sc.total}/5）</p>
    <p>${mark(sc.stars.judge)} 判斷：三題第一次答對 ${rec.judgeWrong.filter(w=>w===0).length}/3<br>
    ${mark(sc.stars.assign)} 求救與分工：分工題${rec.d1Wrong===0?'第一次就答對':`答錯 ${rec.d1Wrong} 次`}<br>
    ${mark(sc.stars.quality)} 壓胸品質：平均 ${st.avgRate==null?'—':st.avgRate} 下／分（目標 100 至 120），最長一次中斷 ${sec(st.longestPauseMs)} 秒，按壓時間占比 ${st.ratio==null?'—':Math.round(st.ratio*100)}%<br>
    ${mark(sc.stars.breathAed)} 人工呼吸與 AED：兩次吹氣第一次吹好 ${br}/2，AED 選過 ${rec.aedErrors==null?'—':rec.aedErrors} 次錯誤做法<br>
    ${mark(sc.stars.keep)} 持續：${completed?'做到救護人員接手':'中途停止了急救'}</p>${rw?(rw.gain?`<p class="good">星級獎勵：+${rw.gain} 金幣</p>`:'')+(rw.next?`<p class="small">下次達成 ${rw.next.tier} 顆星，可以再領 ${rw.next.coins} 金幣。</p>`:''):''}`});
  if(box)await say({p:'hero',who:'神器',html:`<div style="text-align:center"><img src="${A.ch3_bls_box}" alt="心跳之匣" style="height:96px"></div><p class="good">獲得神器：心跳之匣（BLS 基礎急救包）</p>`});
  if(completed)await FA.dailyDone('care');  /* 每日任務：處理一次事件或傷口（章末演練算） */
}
async function downAct(){  /* 市集倒地的人：第 1～4 節都做完就多一個「章末演練」 */
  const done=['ch3_k1_3','ch3_k2_3','ch3_k3_1','ch3_k3_3','ch3_k4_4'].every(k=>S.cards[k]);
  if(!done)return lesson1();
  const i=await say({p:'hero',html:'<p>有人倒在港口市集的空地上。</p>',buttons:[{label:'章末演練',primary:true},{label:'複習第 1 節'},{label:'先離開'}]});
  if(i===0)return finale();if(i===1)return lesson1();
}

/* ---------- NPC 對話（2026-10-07 老師同意的擬稿；沒有醫療數字，只用遊戲現有規則與已審核內容） ---------- */
const LIFEG='ch3_lifeg',SAILOR='ch3_sailor';
async function lifegHarbor(){
  S.c=S.c||{};
  if(!S.c.ch3_met){
    S.c.ch3_met=true;
    await lines(LIFEG,['你來了！我就是你爺爺的老朋友，他早就寫信說你會來。','藍堡的港口人來人往，這裡的人都得會急救才行。市集那邊人最多，你先過去看看。']);
  }
  for(;;){
    const ready=PREV||['ch3_k1_3','ch3_k2_3','ch3_k3_1','ch3_k3_3'].every(k=>S.cards[k]);  /* 第 1～3 節做完才開放專線與防災 */
    const labels=(ready?['請教救生員','聊聊']:['接下來做什麼','聊聊']).concat(E3&&E3.lifegOffer()?['領取救生員裝']:[],['先離開']);
    const i=await say({p:LIFEG,html:ready?'<p>想聊聊，還是想請教急救和防災的事？</p>':'<p>港口人多，想聊聊嗎？市集和救生站都可以去看看。</p>',buttons:labels.map((l,k)=>({label:l,primary:k===0}))});
    const lab=labels[i];
    if(lab==='領取救生員裝'){await E3.giveLifeg();continue;}
    if(lab==='請教救生員')return lesson4();
    if(lab==='接下來做什麼'){await lines(LIFEG,[!S.cards.ch3_k1_3?'市集的空地上有人倒下了，快過去看看！':!S.cards.ch3_k2_3?'去救生站吧，假人旁邊可以練習按壓。':!S.cards.ch3_k3_1?'假人旁邊的面罩，可以練習人工呼吸。':'救生站牆上的 AED，也要練習怎麼用。']);continue;}
    if(lab!=='聊聊')return;
    const c=S.c||{};
    if(c.ch3_done){
      await lines(LIFEG,[(c.ch3_stars||0)>=4?'聽說市集那邊的事你處理得很好。心跳之匣交給你，我放心多了。':'第一次就走完全程很不容易。哪裡不順，就再練幾次，會越來越熟的。']);
    }else{
      await lines(LIFEG,['港口人來人往，市集尤其擠。真的有人倒下的時候，旁邊的人常常只是看著。你要是遇到了，別當那個只看著的人。','救生站裡有練習用的假人和 AED，想練習隨時過來。']);
    }
    await FA.chatLuck(LIFEG);  /* 完成第三章後，聊天有機會抽到知識、小道具或金幣（每天一次，見 js/game.js 的 chatLuck） */
  }}
const lifegStation=()=>lines(LIFEG,['這具假人是給大家練習用的。按壓、吹氣、AED，都可以在這裡一步一步練。','別怕弄壞它，壞了我再修。']);
const sailorHarbor=async()=>{await lines(SAILOR,['海上的天氣說變就變。颱風或豪雨要來的時候，船長會停航，到時候只能在港口等天氣好轉。','要回綠葉谷的話，到告示牌那邊搭船就行。']);await FA.chatLuck(SAILOR);};
const SAILOR_TOPICS=[
  ['去藍堡怎麼走',['要去藍堡的話，找老船長買票。船上要過兩個晚上，乾糧和水自己帶比較划算。']],
  ['看浪況',['出海前先看海：浪越來越大、海面一直冒白色浪花、浪一波接一波的時候，就不是出船的好時機。','看不懂的時候別硬撐，問問老船長或港口的人，寧可多等一天。']],
  ['天氣與颱風季',['出船前要先看天氣預報。颱風季節，或是颱風、豪雨快來的時候，我們就不出船，船長說停航就是停航。','就算海面看起來很平靜，也不能因為「看起來沒事」就出海。風雨突然變小，也可能只是暫時的。']],
  ['救生衣與落水',['上船、在碼頭邊做事，都要穿好救生衣。不要一個人跑到岸邊或礁石上玩水、釣魚。','萬一有人掉進海裡，大聲呼救，把救生圈或浮具拋給他，自己不要跳下去。碼頭或海上出事，要打 118 找海巡。']]];
async function sailorPort(){
  for(;;){
    const i=await say({p:SAILOR,html:'<p>要出海的話，有什麼想先問的嗎？</p>',buttons:SAILOR_TOPICS.map((t,k)=>({label:t[0],primary:k===0})).concat([{label:'先離開'}])});
    if(i>=SAILOR_TOPICS.length)return;
    await lines(SAILOR,SAILOR_TOPICS[i][1]);
  }}

const PASSER_LINES={
  ch3_by_red:[['我剛剛看到他突然就倒下去了，嚇得不知道該怎麼辦。'],['剛才真的謝謝你！我以後也想學學急救。']],
  ch3_by_blue:[['不知道有沒有人會急救……我只敢站在這裡看。'],['你好厲害，那麼多人在，你還是第一個動手的。']],
  ch3_by_green:[['聽說港口的救生員很懂急救，他說不定有辦法。'],['有人在現場帶頭，大家就知道該做什麼了。']]};
const passerTalk=async id=>{await lines(id,PASSER_LINES[id][(S.c&&S.c.ch3_done)?1:0]);await FA.chatLuck(id);};
let E3=null;
const HBR=harborInit(FA,{on:()=>E1_ON&&(PREV||!!(S.c&&S.c.ch3_done)),extra:()=>E3?E3.boardExtra():''});
const FSH=fishInit(FA,{on:()=>E1_ON&&(PREV||!!(S.c&&S.c.ch3_done)),debug:DEBUG,addRep:HBR.addRep,preview:PREV});
E3=e3Init(FA,{on:()=>E1_ON&&(PREV||!!(S.c&&S.c.ch3_done)),preview:PREV,previewM:QS.get('m'),rep:HBR.rep,fishSt:FSH.st});
HBR.load().catch(()=>{});E3.load().catch(()=>{});
return {
  acts:Object.assign({},HBR.acts,FSH.acts,E3.acts,{ch3_board:captTalk,ch3_hatch:hatch,ch3_bed:bed,ch3_ladder:ladder,ch3_down:downAct,ch3_mani:lesson2,ch3_breath:lesson3Breath,ch3_aed:lesson3Aed}),
  build(sceneId,H,{sprite,npcEls}){
    HBR.build(sceneId,H,{sprite});FSH.build(sceneId,H,{sprite});E3.build(sceneId,H,{sprite});
    if(sceneId==='ch3_market'){const e=sprite('shadow','',DOWN.x,DOWN.y,Math.round(H*.85),RATIO.ch3_fisher_down);e.querySelector('img').src=A.ch3_fisher_down;}
    if(sceneId==='ch3_rescue'){const e=sprite('shadow','',MANI.x,MANI.y,Math.round(H*.55),RATIO.ch3_cpr_manikin);e.querySelector('img').src=A.ch3_cpr_manikin;
      const m=sprite('shadow','',MASK.x,MASK.y,Math.round(H*.2),RATIO.ch3_face_shield);m.querySelector('img').src=A.ch3_face_shield;}},
  things(sceneId){return HBR.things(sceneId).concat(FSH.things(sceneId),E3.things(sceneId),sceneId==='ch3_market'?[{kind:'ch3_down',x:DOWN.x,y:DOWN.y+50,label:'查看倒地的人'}]:sceneId==='ch3_rescue'?[{kind:'ch3_mani',x:MANI.x,y:MANI.y+60,label:'練習按壓'},{kind:'ch3_breath',x:MASK.x,y:MASK.y+20,label:'練習人工呼吸'},{kind:'ch3_aed',x:AED_AT.x,y:AED_AT.y,label:'練習 AED'}]:[]);},
  goalBase:()=>onShip()?'在船上度過兩個晚上：到艙口進船艙，在床上睡覺。':undefined,  /* 船上的場景算綠葉谷地區，目標要走這個接點 */
  goal(){  /* 畫面上方「目標」：依知識卡判斷做到哪一節，告訴玩家下一步去哪裡 */
    if(onShip())return '在船上度過兩個晚上：到艙口進船艙，在床上睡覺。';
    if(!(S.c&&(S.c.ch3_met||S.c.ch3_done))&&!Object.keys(S.cards).some(k=>k.startsWith('ch3_k')))return '到港口廣場的另一頭，救生站旁，找爺爺的老朋友——港口救生員。';
    if(!S.cards.ch3_k1_3)return '到港口市集，查看倒在地上的人。';
    if(!S.cards.ch3_k2_3)return '到港口的救生站，在假人旁練習按壓。';
    if(!S.cards.ch3_k3_1)return '在救生站，假人旁的面罩可以練習人工呼吸。';
    if(!S.cards.ch3_k3_3)return '在救生站，牆邊的 AED 可以練習。';
    if(!S.cards.ch3_k4_4)return '到港口，找救生員請教專線與防災。';
    if(!(S.c&&S.c.ch3_done))return '到港口市集，查看倒在地上的人，進行章末整合演練。';
    {const g=HBR.goal();if(g)return g;}
    return `第三章完成！心跳之匣已取得（最高 ${S.c.ch3_stars||0} 顆星）。想再挑戰，可以回市集的倒地者那裡。`;},
  wear:()=>E3.wardrobe(),
  talk(id){if(id==='ch3_captain')return captTalk();
    if(id===LIFEG)return S.scene===HARBOR?lifegHarbor():lifegStation();
    if(id===SAILOR)return S.scene===FISHPORT?sailorPort():sailorHarbor();
    if(PASSERS.includes(id))return passerTalk(id);
    if(id.startsWith('ch3_'))return say({p:id,html:'<p>……</p><p class="small">（這位角色的對話之後才會加入。）</p>'});}  /* 草稿沒有 NPC 對白：先給個提示，不要讓按鈕沒反應 */
};
}
