/* 第三章「港口藍堡」章節程式（D1：航行）。
 * 航行規則沿用第二章：船票 30 金幣、兩晚、每晚 1 包乾糧＋1 瓶開水（自己帶，沒有就向船長買，沒錢扣體力）、
 * 帶在身上的防災包視為旅行行李、颱風或豪雨時停航、每晚睡醒建立存檔點。
 * D2-1：第 1 節（安全、反應、呼吸判斷、求救）。知識卡與題目的文字照老師提供的草稿，老師已於 2026-10-07 審核通過（照現有文字）。
 * CPR 按壓、吹氣、AED、章末事件尚未加入，等老師審核。 */
import * as R from './rhythm.js';
import * as AED from './aed.js';
import harborInit from './harbor.js';
import fishInit from './fish.js';
import e3Init,{merchantOn as e3MerchantOn} from './e3.js';
import {makeVoyage,SHIP_RATION,SHIP_WATER} from '../voyage.js';
export default function(FA){
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;},has:(_,k)=>k in FA.S,ownKeys:()=>Reflect.ownKeys(FA.S),getOwnPropertyDescriptor:(_,k)=>({value:FA.S[k],enumerable:true,configurable:true})});
const {RM,STA_MAX,$,say,lines,quiz,orderQuiz,go,toast,refresh,nextDay,sleep,kitCount,base,expired,stashDepart,stormy,checkpoint,CARDS,A,RATIO}=FA;
const QS=new URLSearchParams(location.search),PREV=!!QS.get('preview');
/* 「藍堡的日常」E1～E3（老師 2026-10-09 審核通過，全部照現有文字）：完成章末演練（S.c.ch3_done）後對所有人開放；老師預覽一直開著。傷口名稱在第一次開放時才註冊，傷口圖鑑不會提前多出格子。 */
let woundsReg=false;
const DAILY_ON=()=>{const ok=PREV||!!(S.c&&S.c.ch3_done);if(ok&&!woundsReg){woundsReg=true;Object.assign(FA.WOUNDS,{octopus:'藍環章魚咬傷',jelly:'水母螫傷',rockcut:'岩石割傷',vibrio:'海洋弧菌感染'});}return ok;};  /* 圖在 assets/w_*.webp；草稿期間只在 E1 開啟時加入，傷口圖鑑不會多出格子 */
const FISHPORT='ch3_fishport',HARBOR='ch3_harbor',CABIN='ch3_ship_cabin';
const deckOf=left=>left>=2?'ch3_ship_day':'ch3_ship_dusk';  /* 第一天白天、第二天黃昏 */
const ARRIVE={[HARBOR]:[820,640],[FISHPORT]:[760,110]};
const onShip=()=>['ch3_ship_day','ch3_ship_dusk',CABIN].includes(S.scene);
const {captTalk,sleepAtSea:bed}=makeVoyage(FA,S,{capt:'ch3_captain',onShip,
  route:()=>S.scene===FISHPORT?{to:HARBOR,name:'港口藍堡'}:{to:FISHPORT,name:'綠葉谷'},
  deck:left=>[deckOf(left),[800,660]],arrive:ARRIVE,
  onArrive:async to=>{if(to===HARBOR){S.c=S.c||{};if(!S.c.ch3_intro){S.c.ch3_intro=true;await lines(SAILOR,['你就是老團長的孫子吧？一路辛苦了！','你爺爺的老朋友在廣場的另一頭等你，是港口的救生員。往右下方走，救生站旁邊就是了。']);}}}});  /* 航行共用程式在 chapters/voyage.js */
async function hatch(){const v=S.voyage;if(!v)return;await go(CABIN,[870,600]);}
async function ladder(){const v=S.voyage;await go(deckOf(v?v.left:2),[1000,600]);}
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
 * 嚴重錯誤（E1～E7）：章末演練裡選到標了嚴重錯誤的選項（E1、E2、E4、E7）或中途按「停止急救」（E6）→ 演練失敗（老師 2026-10-09 授權我決定：只在章末演練觸發；
 * 顯示對應的現有知識卡、不扣金幣、不回存檔點、不影響已拿的星級獎勵與已完成狀態，回到演練前重來）。AED 練習的錯誤示範與「中斷超過 10 秒」只記錄、不觸發。
 * 記在 window.__ch3Finale（只有 #debug）。 */
const FAIL_CARD={E1:'ch3_k1_3',E2:'ch3_k3_2',E3:'ch3_k2_1',E4:'ch3_k2_3',E5:'ch3_k3_2',E6:'ch3_k2_3',E7:'ch3_k1_2'};  /* 失敗時顯示的現有知識卡（文字不改） */
const FIN_FAIL={finFail:true};
async function finaleFail(rec,code,what){
  rec.failed={code,what};if(DEBUG)window.__ch3Finale={rec,completed:false,failed:true};
  await say({p:'hero',who:'章末演練',html:`<p class="bad">演練失敗。</p><p>${what}</p><p class="small">先看看下面這張知識卡，再回來重新挑戰。這是演練，不扣金幣，已拿到的星級獎勵也不會收回。</p>`});
  await showCard(FAIL_CARD[code]);
  throw FIN_FAIL;}
async function askScored(key,rec){  /* 同核心的 quiz（答錯顯示說明、可再選），另外記錄答錯幾次與選到的嚴重錯誤 */
  const z=(await quizzes())[key];let wrong=0;
  for(;;){
    const i=await say({p:'hero',hideCap:true,html:`<p class="q">${z.q}</p>`,buttons:z.opts.map(o=>({label:o}))});
    const ok=i===z.ans;
    if(!ok){wrong++;if(z.severe&&(!z.severeOpts||z.severeOpts.includes(i))){rec.errs.push({key,code:z.severe,opt:i});
      if(rec.fatal&&FAIL_CARD[z.severe.slice(0,2)])await finaleFail(rec,z.severe.slice(0,2),`你選了「${z.opts[i]}」。`);}}
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
async function finale(){try{await finaleRun();}catch(e){if(e!==FIN_FAIL)throw e;}}  /* 演練失敗（FIN_FAIL）：已顯示知識卡，直接結束，回到演練前 */
async function finaleRun(){
  const T=Object.assign({},R.DEFAULTS,R.FINALE,DEBUG&&window.__ch3Tune||{});
  const ses={taps:[],segs:[],fatigueMs:0,swaps:0,sinceSwap:0,cut(){if(ses.taps.length)ses.segs.push(ses.taps);ses.taps=[];}};
  const rec={errs:[],judgeWrong:[],d1Wrong:null,breath:null,aedErrors:null,stopped:false,fatal:true};
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
  const completed=await run();rec.stopped=!completed;if(rec.stopped){rec.errs.push({key:'stop',code:'E6'});await finaleFail(rec,'E6','你中途停止了急救。');}
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
/* 海嘯警報選配支線（老師 2026-10-09 同意做；K4-3、Q4-4 文字照老師草稿）：第 4 節做完後，救生員選單多一項「海嘯警報」：
 * 先聽一次警報（老師提供的真實錄音，約 89 秒，可以跳過），再出情境題 Q4-4，最後給知識卡 K4-3。警報秒數來自草稿；救生員那句邀請與警報字幕是我加的非醫療用語。 */
/* 警報聲用老師提供的真實錄音（2026-10-09，「海嘯警報不具語音廣播」，約 89 秒，已轉成 m4a）；播完才出語音字幕，可以隨時按「跳過」。 */
const ALARM={ms:89400,src:new URL('assets/ch3_tsunami_alarm.m4a',import.meta.url).href};
async function alarmPlay(){
  const T=Object.assign({},ALARM,DEBUG&&window.__ch3Tune&&window.__ch3Tune.alarm||{});
  let au=null,timers=[];
  const stop=()=>{timers.forEach(clearTimeout);timers=[];try{au&&au.pause();}catch(e){}au=null;};
  try{await say({p:'hero',who:'海嘯警報',html:'<p id="al" style="font-size:1.4em;text-align:center;margin:14px 0">警報聲播放中……</p><p class="small" style="text-align:center">（要有聲音。太長可以按「跳過」）</p>',buttons:[{label:'跳過'}],
    onRender:(root,fin)=>{const al=root.querySelector('#al'),at=(ms,fn)=>timers.push(setTimeout(fn,ms));
      try{au=new Audio(T.src);au.play().catch(()=>{});}catch(e){}
      at(T.ms,()=>{al.innerHTML='語音：「海嘯警報，請所有民眾迅速往高處疏散」';});
      at(T.ms+2200,()=>fin('done'));}});}
  finally{stop();}}
/* 燈塔管理員（老師 2026-10-10 生圖；對白是我擬的閒聊，沒有醫療內容、沒有數字，老師可改字）：燈塔場景，依港口信譽與今晚求助有沒有處理三種話，說完抽一次聊天運氣 */
async function keeperTalk(){
  const KP='ch3_keeper';S.c=S.c||{};
  if(!S.c.ch3_keeper_met){S.c.ch3_keeper_met=true;await lines(KP,['爬上來累了吧？這裡風景不錯，慢慢看。']);}
  if(!HBR.lhOpen())await lines(KP,['這座燈塔從我爺爺那代就點著，海上的船看到它，就知道港口在哪裡。','夜裡風大，浪也大，所以我常常守在這裡。']);
  else if(HBR.lhActive())await lines(KP,['你就是常常幫港口忙的那個孩子吧？港口的人都說你可靠。','今晚要是有人需要幫忙，長椅那邊會有人等你。']);
  else await lines(KP,['辛苦了。燈亮著，大家就安心。','早點休息，明天港口還有事情等你。']);
  await FA.chatLuck(KP);}
/* 藍堡的休息處（老師 2026-10-09 同意加；藍堡原本沒有床，只有船艙）：救生站的休息區，免費睡一晚，沿用爺爺家床的規則（進入下一天、體力完全恢復、建立存檔點） */
const REST_AT={x:800,y:450};
async function restAct(){
  const i=await say({p:LIFEG,html:'<p>累了就在這裡休息一晚吧，救生站的休息區隨時可以用。</p><p class="small">睡一覺會進入下一天，體力完全恢復。</p>',buttons:[{label:'睡一晚',primary:true},{label:'先不用'}]});
  if(i!==0)return;
  $('fade').classList.add('on');await sleep(RM?0:500);const html=nextDay();S.sta=FA.staMax();refresh();$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>在救生站的休息區睡了一覺，體力完全恢復了。</p>'+html});}
/* 藍堡的急救用品補給點（老師 2026-10-09 同意加；藍堡沒有固定的雜貨店，只有商船來時的澳洲商人）：救生站的急救用品櫃，賣和綠葉谷雜貨店一樣的基本急救用品，
 * 價格相同（不打折、不賒帳）；全部用 content/items.json 的 SHOP_MED，沒有新寫醫療文字。 */
const SUPPLY_AT={x:990,y:490};
async function supplyAct(){
  let msg='';
  for(;;){
    let pick=null;const full=S.kit.length>=S.kitCap;
    const rows=FA.SHOP_MED.map(k=>{const it=FA.ITEMS[k];return `<div class="row">${FA.badge(k)}<div class="info"><b>${it.name}　<span style="color:var(--gold)">背包裡有 ${kitCount(k)} 個</span></b><span>${it.price} 金幣　重量 ${it.w}　${it.desc}</span></div><button type="button" data-a="${k}" ${S.coins>=it.price&&!full?'':'disabled'}>${full?'背包已滿':'買 1 個'}</button></div>`;}).join('');
    const r=await say({p:LIFEG,html:(msg?`<p class="good">${msg}</p>`:'')+`<p>這裡是救生站的急救用品櫃，需要什麼自己拿，照價錢付就好。</p><p class="small">金幣 ${S.coins}　急救背包 ${S.kit.length}/${S.kitCap}</p>`+rows,buttons:[{label:'離開',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{pick=b.dataset.a;fin('pick');})});
    if(r!=='pick')return;
    const it=FA.ITEMS[pick];if(S.coins>=it.price&&S.kit.length<S.kitCap){S.coins-=it.price;S.kit.push(pick);msg=`已買下：${it.name} ×1（急救背包 ${S.kit.length}/${S.kitCap}）`;refresh();}
  }}
/* 解除警報音（老師 2026-10-09 提供資訊：一長聲 90 秒）：沒有錄音檔，用程式合成一條穩定的單音長鳴；可以跳過 */
async function allClearPlay(){
  const T=Object.assign({ms:90000},DEBUG&&window.__ch3Tune&&window.__ch3Tune.clear||{}),AC=window.AudioContext||window.webkitAudioContext;
  let ctx=null,timers=[];
  const stop=()=>{timers.forEach(clearTimeout);timers=[];try{ctx&&ctx.close();}catch(e){}ctx=null;};
  try{await say({p:'hero',who:'解除警報音',html:'<p id="al" style="font-size:1.4em;text-align:center;margin:14px 0">一長聲……</p><p class="small" style="text-align:center">（解除警報音是一長聲，共 90 秒。太長可以按「跳過」）</p>',buttons:[{label:'跳過'}],
    onRender:(root,fin)=>{
      if(AC)try{ctx=new AC();const o=ctx.createOscillator(),g=ctx.createGain(),t=ctx.currentTime,d=T.ms/1000;o.type='sine';o.frequency.value=440;
        g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.1,t+.3);g.gain.setValueAtTime(.1,t+Math.max(.3,d-.3));g.gain.linearRampToValueAtTime(0,t+d);o.connect(g);g.connect(ctx.destination);o.start(t);o.stop(t+d);}catch(e){}
      timers.push(setTimeout(()=>fin('done'),T.ms));}});}
  finally{stop();}}
/* 藍堡的港口小店（老師 2026-10-09 同意加「小型固定商店」）：港口市集的水果攤，一開始就能用（不用完成章末）。
 * 賣乾糧與開水（價格和船上賣的一樣，才不會買低賣高）、能量點心與豐盛便當（體力，價格同雜貨店的體能補給）、哨子／手電筒／雨衣（價格同雜貨店）。
 * 全部沿用現有物品，沒有新寫任何醫療文字；沒有好感度折扣。急救用品在救生站的急救用品櫃。 */
const SHOP3_AT={x:650,y:420};
async function shop3Act(){
  let msg='';
  for(;;){
    let pick=null;const full=S.kit.length>=S.kitCap;
    const rows=[
      {id:'ration',name:'乾糧',price:SHIP_RATION,desc:`免烹煮、耐保存，保存 ${FA.RATION_LIFE} 天。放進急救背包或防災包。`,kit:true},
      {id:'water',name:'開水',price:SHIP_WATER,desc:'煮沸過的乾淨開水，防災包要放。',kit:true}]
      .concat(FA.STAMINA_SHOP.food.map(f=>({id:'sta:'+f.id,name:f.name,price:f.cost,desc:`${f.desc}（現在吃下，目前體力 ${S.sta}/${FA.staMax()}）`,eat:f})))
      .concat(FA.SHOP_EXTRA.map(k=>({id:k,name:FA.ITEMS[k].name,price:FA.ITEMS[k].price,desc:FA.ITEMS[k].desc,kit:true})));
    const html=(msg?`<p class="good">${msg}</p>`:'')+`<p>這裡是港口的小店，賣一些出門在外用得上的東西。</p><p class="small">金幣 ${S.coins}　急救背包 ${S.kit.length}/${S.kitCap}</p>`+rows.map(r=>{
      const dis=S.coins<r.price||(r.kit&&full)||(r.eat&&S.sta>=FA.staMax());
      return `<div class="row"><div class="info"><b>${r.name}</b><span>${r.price} 金幣　${r.desc}</span></div><button type="button" data-a="${r.id}" ${dis?'disabled':''}>${r.kit&&full?'背包已滿':r.eat&&S.sta>=FA.staMax()?'體力已滿':'買 1 個'}</button></div>`;}).join('');
    const r=await say({p:'hero',who:'港口小店',html,buttons:[{label:'離開',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{pick=b.dataset.a;fin('pick');})});
    if(r!=='pick')return;
    const it=rows.find(x=>x.id===pick);if(!it||S.coins<it.price)continue;
    if(it.kit){if(S.kit.length>=S.kitCap)continue;S.coins-=it.price;S.kit.push(it.id==='ration'?'ration@'+(S.day+FA.RATION_LIFE):it.id);msg=`已買下：${it.name} ×1（急救背包 ${S.kit.length}/${S.kitCap}）`;}
    else{if(S.sta>=FA.staMax())continue;S.coins-=it.price;const b4=S.sta;S.sta=Math.min(FA.staMax(),S.sta+it.eat.restore);msg=`吃了${it.name}，體力 +${S.sta-b4}`;}
    refresh();}}
async function tsunami(){
  const i=await say({p:LIFEG,html:'<p>要不要聽聽海嘯警報是什麼聲音？聽過一次，真的響起的時候才認得出來。</p>',buttons:[{label:'聽聽看',primary:true},{label:'先不用'}]});
  if(i!==0)return;
  await alarmPlay();
  await ask('ch3_q4_4');await showCard('ch3_k4_3');
  const j=await say({p:LIFEG,html:'<p>警報解除的時候，聲音又不一樣。要不要也聽聽看？</p>',buttons:[{label:'聽聽解除警報音',primary:true},{label:'不用了'}]});
  if(j===0)await allClearPlay();}
async function lifegHarbor(){
  S.c=S.c||{};
  if(!S.c.ch3_met){
    S.c.ch3_met=true;
    await lines(LIFEG,['你來了！我就是你爺爺的老朋友，他早就寫信說你會來。','藍堡的港口人來人往，這裡的人都得會急救才行。市集那邊人最多，你先過去看看。']);
  }
  for(;;){
    const ready=PREV||['ch3_k1_3','ch3_k2_3','ch3_k3_1','ch3_k3_3'].every(k=>S.cards[k]);  /* 第 1～3 節做完才開放專線與防災 */
    const labels=ready?['請教救生員'].concat(S.cards.ch3_k4_4?['海嘯警報']:[],['聊聊','先離開']):['接下來做什麼','聊聊','先離開'];
    const i=await say({p:LIFEG,html:ready?'<p>想聊聊，還是想請教急救和防災的事？</p>':'<p>港口人多，想聊聊嗎？市集和救生站都可以去看看。</p>',buttons:labels.map((l,k)=>({label:l,primary:k===0}))});
    const lab=labels[i];
    if(lab==='請教救生員')return lesson4();
    if(lab==='海嘯警報'){await tsunami();continue;}
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
/* 南岸漁港的漁婦、漁夫（老師 2026-10-09 同意擬稿；只有日常閒聊，沒有醫療內容、沒有數字）。章末前後各一組；說完抽一次聊天運氣 */
const FISH_LINES={
  ch3_fishwife:[['歡迎來到南岸漁港！這裡的船天天進出，要去藍堡的話，找老船長買票就對了。'],['聽說你在藍堡的市集幫了大忙，港口的人都在談呢。'],],
  ch3_fisher:[['今天的海面看起來很平靜，不過出海的人都知道，天氣說變就變。'],['你從藍堡回來啦？一個人闖過那麼多事，真不簡單。']]};
FISH_LINES.ch3_fishwife[0].push('路上海風大，記得帶好自己的東西。');FISH_LINES.ch3_fishwife[1].push('學來的本事，要在最要緊的時候用得上才有意義。');
FISH_LINES.ch3_fisher[0].push('我靠海吃飯一輩子，最怕的就是看輕了海。');FISH_LINES.ch3_fisher[1].push('海邊的人互相照應，有你這樣的人，我們放心多了。');
const fishTalk=async id=>{await lines(id,FISH_LINES[id][(S.c&&S.c.ch3_done)?1:0]);await FA.chatLuck(id);};
const passerTalk=async id=>{await lines(id,PASSER_LINES[id][(S.c&&S.c.ch3_done)?1:0]);await FA.chatLuck(id);};
let E3=null;
const HBR=harborInit(FA,{on:DAILY_ON,extra:()=>E3?E3.boardExtra():''});
const FSH=fishInit(FA,{on:DAILY_ON,debug:DEBUG,addRep:HBR.addRep,preview:PREV,lhOpen:HBR.lhOpen});
E3=e3Init(FA,{on:DAILY_ON,preview:PREV,previewM:QS.get('m'),rep:HBR.rep,fishSt:FSH.st});
HBR.load().catch(()=>{});E3.load().catch(()=>{});
return {
  /* 給第二章的鍛造鎮碼頭用（老師 2026-10-10 同意第二章加玩法）：商船輪流靠岸的商人也會到火山島碼頭，買賣規則、收購上限與藍堡共用 */
  merchantKey:day=>e3MerchantOn(day),merchantAt:k=>E3.merchant(k,{noAlp:true}),  /* 第二章的碼頭不提供「去雪嶺」 */
  acts:Object.assign({},HBR.acts,FSH.acts,E3.acts,{ch3_board:captTalk,ch3_hatch:hatch,ch3_bed:bed,ch3_ladder:ladder,ch3_down:downAct,ch3_mani:lesson2,ch3_breath:lesson3Breath,ch3_aed:lesson3Aed,ch3_rest:restAct,ch3_supply:supplyAct,ch3_shop:shop3Act}),
  build(sceneId,H,{sprite,npcEls}){
    HBR.build(sceneId,H,{sprite});FSH.build(sceneId,H,{sprite});E3.build(sceneId,H,{sprite});
    if(sceneId==='ch3_market'){const m=sprite('shadow','',SHOP3_AT.x,SHOP3_AT.y-40,60,1);m.style.pointerEvents='none';m.innerHTML='<span class="badge lg" style="--c:#2F7D4F;--tc:#fff;--s:60px;opacity:.92">小店</span>';m.style.zIndex=Math.round(SHOP3_AT.y)+5;}  /* 水果攤前的標記 */
    if(sceneId==='ch3_harbor'){  /* 去燈塔的路標：石階下方一個小的、棧橋起點（入口）一個大的（老師 2026-10-09 要求觸發方式更明確） */
      const mark=(x,y,big,t)=>{const m=sprite('shadow','',x,y,big?70:46,1);m.style.pointerEvents='none';m.innerHTML=`<span class="badge ${big?'lg':''}" style="--c:#2B6CB0;--tc:#fff;${big?'--s:64px':'--s:40px'};opacity:.92">${t}</span>`;m.style.zIndex=Math.round(y)+5;};
      mark(820,420,false,'↖');mark(695,236,true,'燈塔');}
    if(sceneId==='ch3_market'){const e=sprite('shadow','',DOWN.x,DOWN.y,Math.round(H*.85),RATIO.ch3_fisher_down);e.querySelector('img').src=A.ch3_fisher_down;}
    if(sceneId==='ch3_rescue'){const e=sprite('shadow','',MANI.x,MANI.y,Math.round(H*.55),RATIO.ch3_cpr_manikin);e.querySelector('img').src=A.ch3_cpr_manikin;
      const m=sprite('shadow','',MASK.x,MASK.y,Math.round(H*.2),RATIO.ch3_face_shield);m.querySelector('img').src=A.ch3_face_shield;}},
  things(sceneId){return HBR.things(sceneId).concat(FSH.things(sceneId),E3.things(sceneId),sceneId==='ch3_market'?[{kind:'ch3_down',x:DOWN.x,y:DOWN.y+50,label:'查看倒地的人'},{kind:'ch3_shop',x:SHOP3_AT.x,y:SHOP3_AT.y,label:'港口小店'}]:sceneId==='ch3_rescue'?[{kind:'ch3_mani',x:MANI.x,y:MANI.y+60,label:'練習按壓'},{kind:'ch3_breath',x:MASK.x,y:MASK.y+20,label:'練習人工呼吸'},{kind:'ch3_aed',x:AED_AT.x,y:AED_AT.y,label:'練習 AED'},{kind:'ch3_rest',x:REST_AT.x,y:REST_AT.y,label:'休息（睡一晚）'},{kind:'ch3_supply',x:SUPPLY_AT.x,y:SUPPLY_AT.y,label:'急救用品櫃'}]:[]);},
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
    return `第三章完成！心跳之匣已取得（最高 ${S.c.ch3_stars||0} 顆星）。想再挑戰，可以回市集的倒地者那裡。`+(HBR.goal()?'港口今天有人需要幫忙，看看公告板。':'');},
  wear:()=>E3.wardrobe(),
  gearShop:()=>E3.gearShop(),
  petNote(){return DAILY_ON()?'藍堡港口的公告板每天都有新的求助，有空去看看。':'';},
  talk(id){if(id==='ch3_captain')return captTalk();
    if(id===LIFEG)return S.scene===HARBOR?lifegHarbor():lifegStation();
    if(id===SAILOR)return S.scene===FISHPORT?sailorPort():sailorHarbor();
    if(PASSERS.includes(id))return passerTalk(id);
    if(id==='ch3_keeper')return keeperTalk();
    if(FISH_LINES[id])return fishTalk(id);
    if(id.startsWith('ch3_'))return say({p:id,html:'<p>……</p><p class="small">（這位角色的對話之後才會加入。）</p>'});}  /* 草稿沒有 NPC 對白：先給個提示，不要讓按鈕沒反應 */
};
}
