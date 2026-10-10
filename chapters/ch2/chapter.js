/* 第二章「熔岩鍛造鎮」章節程式。
 * 由 V3.2 原型的第二章與渡海函式機械轉換而來（只加上 ch2_ 前綴與 FA 介面），對話與題目文字與 V3.2 逐字相同。
 * 章節開放時才載入；核心程式透過回傳的掛接點呼叫它。 */
import {makeVoyage} from '../voyage.js';
import {openStore} from '../store.js';
export default function(FA){
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;},has:(_,k)=>k in FA.S,ownKeys:()=>Reflect.ownKeys(FA.S),getOwnPropertyDescriptor:(_,k)=>({value:FA.S[k],enumerable:true,configurable:true})});
const {ITEMS,MATS,CARDS,A,RATIO,RM,STA_MAX,$,say,quiz,orderQuiz,checkpoint,play,T,lines,chatMenu,gift,shopMenu,merchantMenu,go,toast,refresh,buildScene,nextDay,sleep,kitCount,takeKit,addHeart,needCheck,sprite,quakeFx,base,expired,stashDepart}=FA;
const CHECKS=[{"id": "c_town", "scene": "ch2_town", "x": 900, "y": 430, "type": "ext", "ok": true, "where": "廣場消防隊門口（滅火器）"}, {"id": "c_smithy", "scene": "ch2_smithy", "x": 1200, "y": 470, "type": "ext", "ok": false, "where": "鐵匠鋪（滅火器）"}, {"id": "c_inn", "scene": "ch2_inn", "x": 420, "y": 450, "type": "alarm", "ok": true, "where": "旅館門口（警報器）"}, {"id": "c_inn2e", "scene": "ch2_inn2", "x": 347, "y": 627, "ix": 450, "iy": 720, "painted": true, "type": "ext", "ok": true, "where": "旅館二樓走廊（滅火器）"}, {"id": "c_inn2a", "scene": "ch2_inn2", "x": 331, "y": 407, "ix": 520, "iy": 580, "painted": true, "type": "alarm", "ok": false, "where": "旅館二樓走廊（警報器）"}];
const FIRES=[[1250, 430], [1360, 520], [1160, 400]];
function goal2(){const c=S.c;
  if(c.done)return '第二章完成！';
  if(c.fire){const left=['r_119','r_ext','r_clothes','r_smith','r_guest'].filter(k=>!c[k]).length;return `鍛造鎮大火！處理現場狀況（剩 ${left} 項）。旅館二樓可能還有人受困。`;}
  if(!c.smith)return '到鐵匠鋪找爺爺的老朋友：鐵匠老鐵。';
  if(!c.appr)return '看看學徒阿焰的燙傷。';
  if(!c.cap)return '到廣場的消防隊找消防隊長。';
  if(c.checking&&Object.keys(c.chk||{}).length<CHECKS.length)return `設備檢查（${Object.keys(c.chk||{}).length}/${CHECKS.length}），還剩：${CHECKS.filter(k=>!(c.chk||{})[k.id]).map(k=>k.where).join('、')}`;
  if(c.checking)return '檢查完成，回去向消防隊長回報。';
  if(!c.inn)return '往南走到溫泉旅館，看看老闆娘有什麼需要幫忙。';
  if(!c.elec)return '回鐵匠鋪看看阿焰，他在修電動砂輪機。';
  if(!c.clue)return '廣場的倉庫最近常有人進出，去看看。';
  return '向消防隊長報告倉庫的事。';}
function news2(id){const c=S.c;
  if(c.fire&&!c.done){if(id==='ch2_appr')return !c.r_clothes;if(id==='ch2_smith')return !c.r_smith;if(id==='ch2_cap')return !c.r_ext||!c.r_119;if(id==='ch2_guest')return !c.r_guest;return false;}
  if(id==='ch2_smith')return !c.smith;if(id==='ch2_appr')return (c.smith&&!c.appr)||(c.inn&&!c.elec);
  if(id==='ch2_cap')return (c.appr&&!c.cap)||(c.checking&&Object.keys(c.chk||{}).length>=CHECKS.length)||(c.clue&&!c.fire);
  if(id==='ch2_innk')return c.cap&&!c.checking&&!c.inn;return false;}
async function coolGame(p,label){
  for(;;){let res=null;
    await say({p,who:'用冷水沖',html:`<p>${label}</p><div class="meter" style="height:18px"><i id="coolBar" style="width:0%"></i></div><p id="coolTxt" class="small">已經沖了 0 分鐘</p><p class="small">燒燙傷要沖約 15 到 30 分鐘。沖夠了會自動停止。</p>`,buttons:[{label:'停止沖水'}],
      onRender:(root,fin)=>{let t=0;const iv=setInterval(()=>{t+=RM?100:2.2;const pct=Math.min(100,t);const bar=root.querySelector('#coolBar');if(!bar){clearInterval(iv);return;}
        bar.style.width=pct+'%';root.querySelector('#coolTxt').textContent=`已經沖了 ${Math.floor(pct*.15)} 分鐘`;res=Math.floor(pct*.15);if(pct>=100){clearInterval(iv);fin('ok');}},100);
        root.closest('.box').querySelectorAll('#dBtns button')[0].onclick=()=>{clearInterval(iv);fin('stop');};}});
    if(res>=15)return true;
    await say({p,html:`<p class="bad">才沖 ${res||0} 分鐘就停了，不夠久！</p><p>燙傷的熱會繼續往皮膚深處傷害，要用流動的冷水沖約 15 到 30 分鐘。</p>`,buttons:[{label:'再沖一次',primary:true}]});}}
async function extGame(p){
  await orderQuiz(p,'滅火器操作',['拉：拉開安全插銷','瞄：瞄準火焰底部','壓：壓下握把','掃：左右掃射'],'口訣「拉、瞄、壓、掃」。要瞄準火焰底部（燃燒的東西），不是火焰頂端或煙。');
  await quiz(p,'滅火時要瞄準哪裡？',['火焰的頂端','火焰底部（正在燃燒的東西）','上方的濃煙'],1,'要瞄準火焰底部，才能把燃燒中的東西覆蓋住。');}
function gaugeSvg(ok){const ang=ok?0:-62;return `<svg viewBox="0 0 200 130" width="220" style="display:block;margin:6px auto"><path d="M20 110 A80 80 0 0 1 180 110" fill="none" stroke="#ddd" stroke-width="22"/><path d="M20 110 A80 80 0 0 1 58 45" fill="none" stroke="#D9463B" stroke-width="22"/><path d="M58 45 A80 80 0 0 1 142 45" fill="none" stroke="#3E9B5C" stroke-width="22"/><path d="M142 45 A80 80 0 0 1 180 110" fill="none" stroke="#E3B95B" stroke-width="22"/><g transform="rotate(${ang} 100 110)"><line x1="100" y1="110" x2="100" y2="38" stroke="#111" stroke-width="5"/></g><circle cx="100" cy="110" r="8" fill="#111"/></svg>`;}
let AC=null;
function alarmSound(){try{AC=AC||new (window.AudioContext||window.webkitAudioContext)();if(AC.state==='suspended')AC.resume();
  const t0=AC.currentTime+.05;for(let rep=0;rep<2;rep++)for(let b=0;b<3;b++){const st=t0+rep*3+b*1.0;const o=AC.createOscillator(),g=AC.createGain();o.type='square';o.frequency.value=3100;
    g.gain.setValueAtTime(0,st);g.gain.linearRampToValueAtTime(.08,st+.01);g.gain.setValueAtTime(.08,st+.48);g.gain.linearRampToValueAtTime(0,st+.5);o.connect(g).connect(AC.destination);o.start(st);o.stop(st+.52);}}catch(e){}}
function clickSound(){try{AC=AC||new (window.AudioContext||window.webkitAudioContext)();if(AC.state==='suspended')AC.resume();const o=AC.createOscillator(),g=AC.createGain();o.frequency.value=180;g.gain.value=.05;o.connect(g).connect(AC.destination);const t=AC.currentTime;o.start(t);o.stop(t+.04);}catch(e){}}
async function check(c){
  if(c.type==='ext'){
    const i=await say({p:'hero',who:`檢查滅火器（${c.where}）`,html:`<p>看看壓力表的指針：</p>${gaugeSvg(c.ok)}<p class="small">綠色：壓力正常　紅色：壓力不足</p>`,buttons:[{label:'正常，可以使用'},{label:'壓力不足，需要更換'}]});
    const right=(i===0)===c.ok;
    await say({p:'hero',html:right?`<p class="good">判斷正確！</p><p>${c.ok?'指針在綠色區，壓力正常。':'指針在紅色區，壓力不足，火災時可能噴不出來，要送修或更換。'}</p>`:`<p class="bad">再仔細看看指針的位置。</p><p>指針在綠色區才是正常。</p>`});
    if(!right)return;}
  else{
    let beep=c.ok;
    const i=await say({p:'hero',who:`測試火災警報器（${c.where}）`,html:'<p>按下警報器上的測試鈕……</p><p class="small">請打開聲音。</p>',buttons:[{label:'按測試鈕',primary:true}]});
    if(beep)alarmSound();else clickSound();
    const j=await say({p:'hero',who:'測試結果',html:beep?'<p style="font-size:26px;font-weight:900;color:var(--warn)">嗶——嗶——嗶——！</p>':'<p style="font-size:22px;color:var(--muted)">……（沒有任何聲音）</p>',buttons:[{label:'正常'},{label:'需要更換電池或警報器'}]});
    const right=(j===0)===c.ok;
    await say({p:'hero',html:right?`<p class="good">判斷正確！</p><p>${c.ok?'有響，警報器正常。':'沒有聲音，要更換電池或整個警報器。'}</p>`:'<p class="bad">再想想：按測試鈕有沒有聲音？</p>'});
    if(!right)return;}
  S.c.chk=S.c.chk||{};S.c.chk[c.id]=true;toast(`完成檢查（${Object.keys(S.c.chk).length}/${CHECKS.length}）`);}
async function fountain(){await say({p:'hero',who:'水槽',html:'<p>水管不停流出清涼的水，這是鎮上的消防水槽，也可以用來沖洗燙傷。</p>'});}
async function warehouse(){
  if(!S.c.elec){await say({p:'hero',html:'<p>倉庫的門鎖著，裡面好像堆了很多東西。</p>'});return;}
  if(!S.c.clue){await say({p:'hero',html:'<p>門縫裡看得到一桶桶的油和成堆的乾草，就堆在火把旁邊……這樣太危險了！</p>'});
    await say({p:'merchant',html:'<p>喂喂，不准偷看！那些可是我要賣的「特製燃料」。放哪裡是我的自由。</p>'});S.c.clue=true;return;}
  await say({p:'hero',html:'<p>油桶和乾草還堆在火把旁邊。趕快告訴消防隊長。</p>'});}
async function forge(){
  const i=await say({p:'ch2_smith',who:'鍛造',html:`<p>要打什麼？</p><p class="small">素材袋：鐵礦石 ${S.mat.ch2_iron||0}、鐵錠 ${S.mat.ch2_ingot||0}　金幣 ${S.coins}</p>`,
    buttons:[{label:'冶煉鐵錠（鐵礦石 ×3）',disabled:(S.mat.ch2_iron||0)<3},{label:'強化十字鎬（鐵錠 ×2＋50 金幣，礦石 2 下就碎）',disabled:S.tools.pick2||(S.mat.ch2_ingot||0)<2||S.coins<50},{label:'離開',primary:true}]});
  if(i===0){S.mat.ch2_iron-=3;S.mat.ch2_ingot=(S.mat.ch2_ingot||0)+1;toast('冶煉出鐵錠 ×1');}
  else if(i===1){S.mat.ch2_ingot-=2;S.coins-=50;S.tools.pick2=true;toast('獲得強化十字鎬！');}}
async function grinder(){
  if(S.c.inn&&!S.c.elec)return elecEvent();
  await say({p:'hero',html:'<p>一台用電的砂輪機，電線看起來有點舊了。</p>'});}
async function elecEvent(){
  await say({p:'ch2_appr',html:'<p>這台砂輪機怪怪的，我來修修看——</p>'});
  await say({icon:'！',who:'',html:'<p class="bad">啪滋！阿焰的手碰到破損的電線，整個人僵住，動不了！</p>'});
  await quiz('hero','阿焰觸電了，第一步該怎麼做？',['立刻抓住他的手把他拉開','先切斷電源（關掉開關、拔掉插頭）','潑水讓他冷靜下來'],1,'直接碰觸電的人，自己也會觸電；水會導電更危險。要先切斷電源，確認安全後才能碰觸傷者。',undefined,{scenario:'electric',bad:[0,2]});
  await say({p:'ch2_smith',html:'<p>我來拔插頭！……好了，電斷了！</p>'});
  await say({p:'ch2_appr',wound:'elec',html:'<p>我、我沒事……只是手掌上多了一個小小的焦點。</p>'});
  await quiz('hero','阿焰清醒了，說自己沒事，只有手上一點點燒焦的痕跡。接下來呢？',['沒事就好，繼續工作','觸電可能造成體內看不見的傷害，要送醫檢查','塗一點牙膏在手上'],1,'觸電的傷害可能在體內，外表看起來很輕也要送醫檢查。');
  S.c.elec=true;S.cards.ch2_elec=true;addHeart('ch2_appr',1);
  await say({p:'ch2_appr',html:`<p>嚇死我了……謝謝你。我這就去給醫生看看。</p><p class="good">獲得知識卡：${CARDS.ch2_elec.title}</p>`});}
async function innRoom(){
  const i=await say({p:'ch2_innk',who:'溫泉旅館',html:`<p>要住一晚嗎？一晚 20 金幣，體力會完全恢復，進入下一天。</p><p class="small">金幣 ${S.coins}</p>`,buttons:[{label:'住一晚',primary:true,disabled:S.coins<20},{label:'不用了'}]});
  if(i!==0)return;S.coins-=20;$('fade').classList.add('on');await sleep(RM?0:500);const html=nextDay();S.sta=FA.staMax();refresh();$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>泡完溫泉睡了一覺，體力完全恢復了。</p>'+html});}
async function bigFire(){
  if(S.c.r_ext){await say({p:'ch2_cap',html:'<p>倉庫的火勢太大了，交給消防隊！你快去幫忙救人！</p>'});return;}
  if(kitCount('ch2_extinguisher')<1){await say({p:'hero',html:'<p class="bad">背包裡沒有滅火器！</p><p class="small">消防隊長給的滅火器要放在急救背包裡。</p>'});return;}
  await say({p:'hero',html:'<p>倉庫角落還是一團小火，趁它還小，用滅火器撲滅！</p>'});
  await extGame('ch2_cap');
  S.c.r_ext='ok';S.c.extOut=true;buildScene();
  await say({p:'ch2_cap',html:'<p>做得好，那團小火熄了！不過倉庫裡面的火勢已經太大，滅火器沒辦法處理。<b>火勢擴大時就不要硬拚</b>，交給消防隊，你去幫忙救人！</p>'});}
async function talk2(id){
  const c=S.c;
  if(c.fire&&!c.done){
    if(id==='ch2_cap'&&!c.r_119){const i=await say({p:'ch2_cap',html:'<p>倉庫起火了！你先打 119 報案，我去拿水帶！電話接通了，你要怎麼說？</p>'},
      );const j=await say({p:'hero',who:'撥打 119',html:'<p class="q">你要怎麼說？</p>',buttons:[{label:'「失火了！快來！」然後掛電話'},{label:'「鍛造鎮廣場旁的倉庫起火，裡面有油桶，可能有人受困。我的電話是……」並等對方掛電話'},{label:'先拍照傳給朋友，再打電話'}]});
      const ok=j===1;await say({p:'ch2_cap',html:`<p class="${ok?'good':'bad'}">${ok?'說得很清楚！':'這樣消防隊很難知道狀況。'}</p><p>${CARDS.ch2_call119.text}</p>`});
      c.r_119=ok?'ok':'wrong';S.cards.ch2_call119=true;return;}
    if(id==='ch2_cap')return say({p:'ch2_cap',html:`<p>${c.r_ext?'快去救人！阿焰、老鐵，還有旅館二樓的客人！':'倉庫角落那團小火還小，用滅火器試試！'}</p>`});
    if(id==='ch2_appr'&&!c.r_clothes){
      await say({p:'ch2_appr',html:'<p class="bad">哇啊啊！火星噴到我的衣服，著火了！好燙！</p>'});
      const i=await say({p:'hero',html:'<p class="q">阿焰的衣服著火了，你要大喊什麼？</p>',buttons:[{label:'「快跑！跑去水槽！」'},{label:'「停下來、躺下、摀住臉滾動！」'},{label:'「用手拍熄它！」'}]});
      const ok=i===1;await say({p:'ch2_appr',html:`<p class="${ok?'good':'bad'}">${ok?'阿焰照著做，在地上滾了幾圈，火熄了！':'奔跑會讓風助長火勢……你趕快改口叫他停、躺、滾，火才熄了。'}</p><p>${CARDS.ch2_clothes.text}</p>`});
      c.r_clothes=ok?'ok':'wrong';S.cards.ch2_clothes=true;return;}
    if(id==='ch2_smith'&&!c.r_smith){
      await say({p:'ch2_smith',wound:'burn2',html:'<p>我去搬油桶的時候，手臂被燒到了……可惡，給我醬油！</p>'});
      if(kitCount('gauze')<1){await say({p:'hero',html:'<p class="bad">背包裡沒有無菌紗布，沒辦法完成處理……</p>'});c.r_smith='missing';return;}
      await coolGame('ch2_smith','你讓老鐵把手臂放到水槽的水管下沖水……');
      await orderQuiz('ch2_smith','燒燙傷處理順序',['沖：流動冷水沖洗','脫：小心脫去衣物','泡：冷水浸泡','蓋：乾淨紗布覆蓋','送：送醫'],CARDS.burn.text);
      takeKit({gauze:1});c.r_smith='ok';await say({p:'ch2_smith',html:'<p>……臭小子，這次我聽你的。醬油留著炒菜就好。</p>'});return;}
    if(id==='ch2_guest'&&!c.r_guest){
      await say({p:'ch2_guest',html:'<p>救命！樓梯那邊都是黑煙，我、我下不去！</p>'});
      const i=await say({p:'hero',html:'<p class="q">往樓下的樓梯已經被濃煙擋住了，你要怎麼幫他？</p>',buttons:[{label:'屏住呼吸，拉著他衝過濃煙往下跑'},{label:'帶他往樓上屋頂跑'},{label:'退回房間關上門，用毛巾塞住門縫，到窗邊揮手呼救並打 119 告知位置'}]});
      const ok=i===2;await say({p:'ch2_guest',html:`<p class="${ok?'good':'bad'}">${ok?'你們躲進房間關好門，在窗邊揮手，消防隊很快架梯子把你們救了出來！':'濃煙非常危險，幾口就可能讓人昏倒。幸好消防隊及時趕到……'}</p><p>${CARDS.ch2_escape.text}</p>`});
      c.r_guest=ok?'ok':'wrong';S.cards.ch2_escape=true;buildScene();
      if(['r_119','r_ext','r_clothes','r_smith','r_guest'].every(k=>c[k]))await fireReport();return;}
    if(['r_119','r_ext','r_clothes','r_smith','r_guest'].every(k=>c[k]))return fireReport();
    return say({p:id,html:'<p>謝謝你！快去幫其他人！</p>'});}
  if(id==='merchant')return merchantMenu();
  if(id==='ch2_smith'){
    if(!c.smith){
      await lines('ch2_smith',['喔！你就是老團長的孫子？信我收到了，歡迎來到熔岩鍛造鎮！','看我打一把好刀給你瞧瞧——']);
      await say({icon:'！',who:'',wound:'burn1',html:'<p class="bad">燒紅的鐵塊一滑，老鐵的前臂被燙了一大塊！</p>'});
      const i=await say({p:'ch2_smith',html:'<p>嘶——小意思！阿焰，去拿醬油來，塗一塗就好了，我都是這樣處理的！</p>',buttons:[{label:'好，快拿醬油'},{label:'等等！先用冷水沖！'}]});
      if(i===0)await say({p:'hero',html:`<p>（想起爺爺說過的話……）</p><p>${ITEMS.soy.truth}</p>`});
      await coolGame('ch2_smith','你拉著老鐵到淬火水桶旁，用水瓢舀冷水，持續沖在燙傷的地方……');
      await orderQuiz('ch2_smith','燒燙傷處理順序',['沖：流動冷水沖洗','脫：小心脫去衣物','泡：冷水浸泡','蓋：乾淨紗布覆蓋','送：送醫'],CARDS.burn.text);
      if(kitCount('gauze')>0)takeKit({gauze:1});
      c.smith=true;S.cards.burn=true;addHeart('ch2_smith',1);
      await say({p:'ch2_smith',html:`<p>……我塗了幾十年醬油，難怪手上都是疤。好吧，我去給醫生看看。</p><p class="good">獲得知識卡：${CARDS.burn.title}</p>`});return;}
    return say({p:'ch2_smith',html:'<p>想打造工具就用鍛造爐跟我說。鐵礦石在北邊的熔岩礦坑。</p>'});}
  if(id==='ch2_appr'){
    if(c.smith&&!c.appr){
      await say({p:'ch2_appr',wound:'burn2',html:'<p>嘿嘿，我昨天也燙到了，起了一個好大的水泡！我正要拿針把它刺破，這樣比較快好對吧？</p>'});
      await quiz('ch2_appr','看看這張傷口圖，阿焰的燙傷屬於哪一種？',['一度燙傷','二度燙傷','三度燙傷'],1,CARDS.ch2_degree.text,'burn2');S.cards.ch2_degree=true;
      await quiz('ch2_appr','阿焰手上的燙傷水泡，應該怎麼處理？',['用針刺破，把水擠出來','不要刺破，用乾淨的紗布輕輕覆蓋保護；水泡很大就就醫','把水泡的皮撕掉，讓它透氣'],1,CARDS.ch2_blister.text);
      if(kitCount('gauze')>0)takeKit({gauze:1});
      c.appr=true;S.cards.ch2_blister=true;addHeart('ch2_appr',1);
      await say({p:'ch2_appr',html:`<p>原來不能刺破啊……好啦，我不亂來了。對了，消防隊長說想見見你！</p><p class="good">獲得知識卡：${CARDS.ch2_blister.title}</p>`});return;}
    if(c.inn&&!c.elec){const i=await say({p:'ch2_appr',html:'<p>我在修角落那台電動砂輪機，老是卡卡的。你要不要過來看看？</p>',buttons:[{label:'過去看看',primary:true},{label:'等一下再說'}]});if(i===0)return elecEvent();return;}
    return say({p:'ch2_appr',html:'<p>等我手好了，要打一把最帥的鎚子！</p>'});}
  if(id==='ch2_cap'){
    if(c.appr&&!c.cap){
      await lines('ch2_cap',['你就是幫老鐵處理燙傷的孩子？我是鍛造鎮義勇消防隊的隊長。','這個鎮每天跟火打交道，每個人都該會用滅火器。來，我教你。']);
      await extGame('ch2_cap');
      S.kit.push('ch2_extinguisher');S.cards.ch2_ext=true;c.cap=true;c.checking=true;
      await say({p:'ch2_cap',html:`<p>很好！這支滅火器送你，放在急救背包裡。</p><p>另外幫我個忙：鎮上有 ${CHECKS.length} 個地方的滅火器和火災警報器要檢查——消防隊門口、鐵匠鋪、旅館門口，還有旅館二樓。</p><p class="good">獲得：滅火器、知識卡「${CARDS.ch2_ext.title}」</p>`});return;}
    if(c.checking&&Object.keys(c.chk||{}).length>=CHECKS.length){
      c.checking=false;S.coins+=60;S.cards.ch2_alarm=true;addHeart('ch2_cap',2);
      await say({p:'ch2_cap',html:`<p>全部檢查完了？鐵匠鋪的滅火器壓力不足、旅館二樓的警報器沒電，我會安排更換。辛苦了！</p><p class="good">獲得 60 金幣、知識卡「${CARDS.ch2_alarm.title}」</p><p class="small">老闆娘說旅館最近常有客人受傷，去看看吧。</p>`});return;}
    if(c.clue&&!c.fire){
      await lines('ch2_cap',['什麼？倉庫裡的油桶和乾草堆在火把旁邊？那是迷霧商人的東西……','我今晚就去處理。你先準備好：急救背包裡要有滅火器、無菌紗布，以防萬一。']);
      const i=await say({p:'ch2_cap',html:'<p>……等等，你聞到了嗎？好像有燒焦的味道！</p>',buttons:[{label:'（背包準備好了）衝過去看看！',primary:true},{label:'先去準備一下'}]});
      if(i!==0)return;
      c.fire=true;quakeFx&&quakeFx();await go('ch2_townfire',[860,860]);
      await say({icon:'！',who:'',html:'<p class="bad">倉庫冒出熊熊大火，黑煙直衝天空！火星四處飛散！</p><p class="small">和消防隊長說話報案，並處理現場的每一個狀況。旅館二樓也可能有人受困。</p>'});return;}
    if(c.checking)return say({p:'ch2_cap',html:`<p>還有 ${CHECKS.length-Object.keys(c.chk||{}).length} 個地方沒檢查喔。</p>`});
    return chatMenu('ch2_cap','平時多一分準備，火場就多一分生機。');}
  if(id==='ch2_innk'){
    if(c.cap&&!c.checking&&!c.inn){
      await say({p:'ch2_innk',wound:'burn1',html:'<p>歡迎光臨……不好意思，剛剛有位客人不小心被溫泉的熱水燙到了，我正要去拿冰塊幫他冰敷。</p>'});
      await quiz('ch2_innk','客人手背發紅、很痛，但沒有水泡。這屬於哪一種燙傷？',['一度燙傷','二度燙傷','三度燙傷'],0,CARDS.ch2_degree.text,'burn1');S.cards.ch2_degree=true;
      await quiz('ch2_innk','客人被熱水燙到，應該怎麼處理？',['拿冰塊直接冰敷，越冰越好','用流動的冷水沖約 15 到 30 分鐘，不要用冰塊','泡進溫泉裡讓傷口適應'],1,CARDS.ch2_cool.text);
      await say({p:'ch2_innk',html:'<p>原來冰塊會凍傷啊……謝謝你！哎呀——！</p>'});
      await say({icon:'！',who:'',wound:'chem',html:'<p class="bad">老闆娘手上的清潔劑瓶子裂開，強效清潔劑潑到她的手背上！</p>'});
      await quiz('ch2_innk','皮膚沾到化學清潔劑，第一步該怎麼做？',['用醋把它中和掉','用大量清水持續沖洗至少 15 到 20 分鐘，並帶著清潔劑的瓶子就醫','用毛巾用力擦乾'],1,CARDS.ch2_chem.text);
      c.inn=true;S.cards.ch2_cool=true;S.cards.ch2_chem=true;S.coins+=40;addHeart('ch2_innk',2);
      await say({p:'ch2_innk',html:`<p>真是太感謝你了。這 40 金幣請收下，想休息的話，二樓的房間隨時歡迎。</p><p class="good">獲得 40 金幣、知識卡「${CARDS.ch2_cool.title}」「${CARDS.ch2_chem.title}」</p><p class="small">聽說阿焰在修一台舊的電動砂輪機……</p>`});return;}
    {const i=await say({p:'ch2_innk',html:'<p>泡個溫泉放鬆一下吧。旅館的小賣部也有急救用品，二樓的房間可以住宿喔。</p>',buttons:[{label:'購買用品',primary:true},{label:'送禮'},{label:'再見'}]});if(i===0)return shopMenu();if(i===1)return gift('ch2_innk');return;}}
  if(id==='ch2_guest')return say({p:'ch2_guest',html:'<p>這裡的溫泉真舒服！不過要小心熱水喔。</p>'});
  return say({p:id,html:'<p>……</p>'});}
async function fireReport(){
  const c=S.c;const items=[['r_119','撥打 119 報案'],['r_ext','用滅火器撲滅初期小火'],['r_clothes','阿焰衣服著火'],['r_smith','老鐵手臂燙傷'],['r_guest','旅館二樓受困的客人']];
  const stars=items.filter(([k])=>c[k]==='ok').length;c.done=true;c.stars=Math.max(c.stars||0,stars);
  await say({p:'ch2_cap',html:'<p>火終於撲滅了……多虧你，沒有人受重傷。迷霧商人已經逃走了，但他留下的油桶就是證據。</p>'});
  await say({p:'hero',who:'救援報告',html:`<div style="font-size:40px;color:var(--gold);letter-spacing:.1em">${'★'.repeat(stars)}${'☆'.repeat(5-stars)}</div>`+items.map(([k,t])=>`<div class="row"><div class="info"><b>${t}</b><span style="color:${c[k]==='ok'?'var(--ok)':c[k]==='wrong'?'var(--warn)':'var(--bad)'}">${c[k]==='ok'?'處置正確':c[k]==='wrong'?'處置有誤':'缺少用品'}</span></div></div>`).join('')+'<p class="good">第二章「熔岩鍛造鎮」完成！</p>',buttons:[{label:'完成',primary:true}]});
  await go('ch2_town',[860,860]);}
const stormy=()=>FA.stormy();  /* 颱風、豪雨（今天或明天）船長拒絕出航 */
const {captTalk,sleepAtSea:voyageSleep}=makeVoyage(FA,S,{capt:'ch2_capt',onShip:()=>S.scene==='ch2_deck',
  route:()=>S.scene==='ch2_port'?{to:'ch2_vport',name:'熔岩鍛造鎮'}:{to:'ch2_port',name:'綠葉谷'},
  deck:()=>['ch2_deck',[600,560]],arrive:{ch2_vport:[560,690],ch2_port:[1180,620]},
  beforeBoard:async()=>{if(!S.cards.ch2_lifejacket){
    await quiz('ch2_capt','上船前要穿救生衣，哪一種穿法正確？',['鬆鬆地披著就好，比較舒服','選合身的尺寸，所有扣帶扣好拉緊，往上拉也不會從頭部脫出','先放在旁邊，落水時再穿'],1,CARDS.ch2_lifejacket.text);S.cards.ch2_lifejacket=true;}},
  onArrive:async to=>{if(to==='ch2_vport'&&!S.c.intro){S.c.intro=true;await lines('ch2_smith',['喔！你就是老團長的孫子？我是鐵匠老鐵，特地來碼頭接你！','歡迎來到熔岩鍛造鎮！沿著碼頭往右上走就是鎮上，先來我的鐵匠鋪坐坐吧。']);}}});  /* 航行共用程式在 chapters/voyage.js */
const STORE_AT={x:330,y:640};
return {
  build(sceneId,H,{sprite,npcEls}){
    if(sceneId==='ch2_town'&&S.c.done){const m=sprite('shadow','',STORE_AT.x,STORE_AT.y-40,60,1);m.style.pointerEvents='none';m.innerHTML='<span class="badge lg" style="--c:#2F7D4F;--tc:#fff;--s:60px;opacity:.92">小店</span>';m.style.zIndex=Math.round(STORE_AT.y)+5;}
    CHECKS.filter(c=>c.scene===sceneId&&!c.painted).forEach(c=>{const k=c.type==='ext'?'ch2_extinguisher':'ch2_alarm';const e=sprite('',A[k],c.x,c.y,c.type==='ext'?Math.round(H*.42):Math.round(H*.22),RATIO[k]);e.querySelector('img').src=A[k];});
    if(sceneId==='ch2_townfire'){FIRES.forEach((f,i)=>{if(i===0&&S.c.extOut)return;const e=sprite('',A.fire,f[0],f[1],Math.round(H*(i===0?.8:1.4)),RATIO.fire);e.querySelector('img').src=A.fire;const sm=sprite('',A.ch2_smoke,f[0]+30,f[1]-H*.8,Math.round(H*1.6),RATIO.ch2_smoke);sm.querySelector('img').src=A.ch2_smoke;sm.style.opacity=.85;});}
    if(sceneId==='ch2_inn2'){const st=sprite('shadow','',430,790,90,1);st.innerHTML='<span class="badge lg" style="--c:#2F7D4F;--tc:#fff;--s:84px">包</span>';}
    if(sceneId==='ch2_inn2'&&S.c.fire&&!S.c.done){[[900,300],[1100,250],[700,500]].forEach(p=>{const sm=sprite('',A.ch2_smoke,p[0],p[1],Math.round(H*1.5),RATIO.ch2_smoke);sm.querySelector('img').src=A.ch2_smoke;sm.style.opacity=.7;sm.style.zIndex=2000;});
      if(!S.c.r_guest){const g=sprite('npc shadow',A.ch2_guest,1200,260,Math.round(H*.9),RATIO.ch2_guest);g.querySelector('img').src=A.ch2_guest;npcEls.ch2_guest=g;const tg=document.createElement('div');tg.className='tag';g.appendChild(tg);}}
  },
  things(sceneId){const L=[];
    CHECKS.filter(c=>c.scene===sceneId).forEach(c=>{if(S.c.checking&&!(S.c.chk||{})[c.id])L.push({kind:'ch2_check',x:c.ix||c.x,y:c.iy||c.y+40,label:c.type==='ext'?'檢查滅火器':'測試警報器',c});});
    if(sceneId==='ch2_inn2'&&S.c.fire&&!S.c.done&&!S.c.r_guest)L.push({kind:'npc',x:1200,y:260,label:'救援',id:'ch2_guest'});
    if(sceneId==='ch2_town'&&S.c.done)L.push({kind:'ch2_store',x:STORE_AT.x,y:STORE_AT.y,label:'鍛造鎮小店'});  /* 第二章完成後才有（老師 2026-10-10 同意加玩法，不影響還在進行第二章的人） */
    return L;},
  acts:{ch2_store:openStore(FA,S,{who:'鍛造鎮小店',intro:'這是鍛造鎮的小店，工匠和旅人出門在外用得上的東西都有。'}),ch2_check:it=>check(it.c),ch2_warehouse:warehouse,ch2_fountain:fountain,ch2_forge:forge,ch2_grinder:grinder,ch2_bigfire:bigFire,ch2_room:innRoom,ch2_board:captTalk,ch2_hatch:voyageSleep},
  talk(id){
    if(id==='ch2_capt')return captTalk();
    if(['ch2_town','ch2_townfire','ch2_smithy','ch2_lavamine','ch2_inn','ch2_inn2'].includes(S.scene))return talk2(id);},
  goal:()=>goal2(),
  news:id=>news2(id),
  /* 序章完成後（核心程式在爺爺對話、目標、頭上驚嘆號處呼叫） */
  goalBase(){
    if(S.f.final&&!S.c.letter)return '序章完成！回家和爺爺說說話，好像有一封信。';
    if(S.f.final&&S.c.letter&&!S.c.done)return S.c.intro?'第二章進行中：到東方草原東邊的漁港，搭船回熔岩鍛造鎮。':'到東方草原東邊的漁港，搭船前往熔岩鍛造鎮。';},
  newsBase:id=>id==='grandpa'&&S.f.final&&!S.c.letter,
  grandpaFinal(){
    if(!(S.f.final&&!S.c.letter))return;
    return (async()=>{
      await lines('grandpa',['孩子，鍛造鎮的老鐵寄信來了。他是爺爺年輕時的戰友。','信上說，鎮上最近常有人燙傷，迷霧商人也在那裡出沒……他需要幫手。']);
      S.c.letter=true;
      await say({icon:'★',who:'獲得：世界地圖',html:'<p>熔岩鍛造鎮在海的另一邊。從<b>東方草原往東</b>走到漁港，搭船就能到達，船程 2 天。</p><p class="small">記得帶乾糧和開水上船。畫面上方的「世界地圖」可以查看位置。綠葉谷的農田和自動化機器會繼續運作。</p>'});
    })();}
};
}
