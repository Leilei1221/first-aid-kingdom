/* 第四章「雪嶺」章節程式（F1：章節骨架；F2：第 1 節出發前準備與裝備檢查、營地 1 與第 2 節失溫）。
 * 草稿：沒登入的人預設也「開放」章節，所以進入條件在這裡自己擋：只有老師預覽（preview.html）或 #debug 的 ?open=ch4 才進得去。
 * 對白全部是擬稿（沒有醫療內容），見 chapters/ch4/REVIEW.md。狀態記在 S.c.ch4，不新增頂層欄位。 */
export default function(FA){
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
const {$,say,lines,go,toast,refresh,nextDay,sleep,checkpoint,stashDepart,RM}=FA;
const QS=new URLSearchParams(location.search),PREV=!!QS.get('preview');
const DEBUG=location.hash==='#debug'&&localStorage.getItem('fa-debug')==='1';
const DRAFT_OK=PREV||(DEBUG&&(QS.get('open')||'').split(',').includes('ch4'));
const INN_COST=20;  /* 住一晚的價錢（遊戲參數，和鍛造鎮旅館一樣） */
const HARBOR={scene:'ch3_harbor',at:[820,640]},VILLAGE={scene:'ch4_village',at:[880,620]};
const CAMP1={scene:'ch4_camp1',at:[420,780]},CAMP1_DOWN={scene:'ch4_village',at:[420,430]};
let QZ=null;const quizzes=async()=>QZ||(QZ=(await (await fetch(new URL('dialogues.json',import.meta.url))).json()).quizzes);
/* 嚴重錯誤（C1～C6）只記錄、不觸發救援失敗（說明文字等老師提供）；只有 #debug 看得到 */
const LOG=()=>(window.__ch4Log=window.__ch4Log||[]);
/* 保暖檢查：外套、帽子、褲子、手套、登山靴各 1 分（遊戲參數，不是醫學數字）；護目鏡與小物另外列出 */
const WEAR=[['jacket','防寒外套'],['hat','保暖帽'],['pants','防寒褲'],['gloves','手套'],['boots','登山靴']];
const EXTRA=[['goggles','護目鏡'],['socks','保暖襪'],['warmer','暖暖包'],['blanket','保暖毯'],['headlamp','頭燈']];
const WARM={full:5,part:3};  /* 5 件＝齊全；3～4 件＝缺一些；其餘＝不足 */
const e3=()=>{const e=(S.c.ch3_e3=S.c.ch3_e3||{});e.own=e.own||{};e.cnt=e.cnt||{};e.seen=e.seen||{};e.frag=e.frag||{};e.wear=e.wear||{};
  if(PREV&&!e.own.jacket)['jacket','hat','pants','gloves','boots','goggles'].forEach(k=>e.own[k]=1);  /* 預覽：全部都有 */
  return e;};
const have=k=>{const e=e3();return e.own[k]?1:(e.cnt[k]||0);};
const warmLevel=()=>{const n=WEAR.filter(([k])=>e3().own[k]).length;return n>=WARM.full?'full':n>=WARM.part?'part':'low';};
const st=()=>{const c=S.c;c.ch4=c.ch4||{};return c.ch4;};
if(PREV&&String(QS.get('preview')).startsWith('ch4_'))st().arrived=true;  /* 預覽直接站在雪嶺：當作已經到過 */
/* 開放條件：完成第三章章末、見過帕桑、集滿 3 片海圖碎片（第三章 E3 的 S.c.ch3_e3）；預覽不需要 */
const ready=()=>{if(!DRAFT_OK)return false;if(PREV)return true;const e=(S.c&&S.c.ch3_e3)||{};return !!(S.c&&S.c.ch3_done&&e.seen&&e.seen.np&&Object.keys(e.frag||{}).length>=3);};
async function trip(to,msg){
  $('fade').classList.add('on');await sleep(RM?0:500);
  FA.setBusy(false);await go(to.scene,to.at);FA.setBusy(true);
  $('fade').classList.remove('on');
  if(msg)await say(msg);}
/* 在藍堡港口跟帕桑出發（由第三章 e3.js 的帕桑選單呼叫）；回傳有沒有出發 */
async function depart(){
  if(!ready())return false;
  const first=!st().arrived;
  if(first){
    await lines('ch3_m_np',['三片海圖碎片拼在一起了，你看，這就是我的家鄉——雪嶺。','山上很冷，也很美。我是嚮導，我帶你上去；不過你也要學會照顧自己和同伴。']);}
  const i=await say({p:'ch3_m_np',html:`<p>${first?'要不要跟我回去看看？':'要回雪嶺嗎？'}</p>`,buttons:[{label:'出發去雪嶺',primary:true},{label:'再準備一下'}]});
  if(i!==0)return false;
  await stashDepart();
  st().arrived=true;
  await trip(VILLAGE,{icon:'🛶',who:'前往雪嶺',html:'<p>帕桑的朋友把船開進河口，你們換上小船，沿著河一路往上游划。傍晚，山腳村的炊煙出現在眼前。</p>'});
  if(first)await lines('ch4_guide',['歡迎來到雪嶺山腳村！這裡是上山前的最後一個村子。','上山的路我還在檢查，等路況確認好，我們就出發。你先逛逛村子，跟旅店老闆娘打個招呼吧。']);
  return true;}
async function boat(){
  const i=await say({p:'hero',who:'小船',html:'<p>要搭小船回藍堡嗎？</p>',buttons:[{label:'回藍堡',primary:true},{label:'不用了'}]});
  if(i!==0)return;
  await stashDepart();
  await trip(HARBOR);}
async function trail(){
  if(!st().s1){await say({p:'ch4_guide',html:'<p>先跟我做上山前的準備（第 1 節）：到我這裡來。</p>'});return;}
  const i=await say({p:'ch4_guide',who:'上山',html:'<p>要上山去營地 1 嗎？</p>',buttons:[{label:'出發',primary:true},{label:'再等一下'}]});
  if(i!==0)return;
  await stashDepart();
  const first=!st().c1;st().c1=true;
  await trip(CAMP1,{icon:'🥾',who:'上山',html:'<p>沿著石階一路往上，走了大半天，山腰的營地 1 出現在眼前。</p>'});
  if(first)await say({p:'ch4_guide_up',html:'<p>營地 1 到了！先喘口氣……咦，那邊好像有個年輕人不太對勁。</p>'});}
async function room(){
  const i=await say({p:'ch4_innk',who:'山腳旅店',html:`<p>要住一晚嗎？一晚 ${INN_COST} 金幣，體力會完全恢復，進入下一天。</p><p class="small">金幣 ${S.coins}</p>`,buttons:[{label:'住一晚',primary:true,disabled:S.coins<INN_COST},{label:'不用了'}]});
  if(i!==0)return;
  S.coins-=INN_COST;$('fade').classList.add('on');await sleep(RM?0:500);
  const html=nextDay();S.sta=FA.staMax();refresh();$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>在暖暖的爐火旁睡了一覺，體力完全恢復了。</p>'+html});}
async function ask(key,p){  /* 同第三章：答錯顯示說明、可再選；選到標了嚴重錯誤的選項只記錄 */
  const z=(await quizzes())[key];
  for(;;){
    const i=await say({p,hideCap:true,html:`<p class="q">${z.q}</p>`,buttons:z.opts.map(o=>({label:o}))});
    const ok=i===z.ans;
    if(!ok&&z.sev&&z.sev[i])LOG().push({key,code:z.sev[i],opt:i});
    await say({p,html:`<p class="${ok?'good':'bad'}">${ok?'回答正確！':'這個做法不對。'}</p><p>${z.explain}</p>`,buttons:[{label:ok?'繼續':'再選一次',primary:true}]});
    if(ok){FA.luckyBonus();return z;}}}
const giveCard=async k=>{const c=await cardOf(k);S.cards[k]=true;await say({p:'hero',html:`<div class="card"><b>${c.title}</b><p>${c.text}</p></div><p class="good">獲得知識卡</p>`});};
let CD=null;const cardOf=async k=>{CD=CD||(await (await fetch(new URL('cards.json',import.meta.url))).json()).CARDS;return CD[k];};
/* 裝備檢查：列出有／沒有，帕桑依保暖等級說一句話；不擋人，缺的可以去攤位補買 */
async function gearCheck(){
  const row=([k,n])=>`<div class="row"><div class="info"><b>${n}</b></div><span class="${have(k)?'good':'bad'}">${have(k)?'有':'沒有'}${k==='socks'||k==='warmer'||k==='blanket'||k==='headlamp'?(have(k)?` ×${have(k)}`:''):''}</span></div>`;
  const lv=warmLevel();
  await say({p:'ch4_guide',who:'裝備檢查',html:`<p>${WEAR.map(row).join('')}</p><p class="small">其他：</p>${EXTRA.map(row).join('')}`,buttons:[{label:'檢查完了',primary:true}]});
  await lines('ch4_guide',[lv==='full'?'一層一層都穿戴齊了，很好！山上就看你的了。':lv==='part'?'還缺幾樣。攤位那邊有賣，缺的最好先補上，不然上山會很辛苦。':'這樣上山會很冷。攤位在那邊，先去看看吧，缺的東西補上再出發比較安全。']);
  st().warm=lv;}
async function lesson1(){
  await lines('ch4_guide',['上山前，我們先檢查裝備，再聊聊怎麼穿、怎麼喝水。']);
  await gearCheck();
  await ask('ch4_q1_1','ch4_guide');await ask('ch4_q1_2','ch4_guide');
  await giveCard('ch4_k1_1');
  await ask('ch4_q1_3','ch4_guide');
  await giveCard('ch4_k1_2');
  st().s1=true;
  await say({icon:'🏔',who:'第 1 節完成！',html:'<p>出發前的準備做好了。從山腳村左上的石階上山，就是營地 1。</p>'});}
async function lesson2(){
  const e=st();
  await lines('ch4_hiker',['啊，你們也上山啊……我、我過溪的時候不小心弄濕了袖子和褲子，好冷……']);
  await say({p:'ch4_guide_up',html:'<p>他穿得太少了，又弄濕了衣服，這種時候最容易失溫。你來幫他，我在旁邊看。</p>'});
  await ask('ch4_q2_1','ch4_guide_up');
  const k=e3();let msg;
  if((k.cnt.warmer||0)>0){k.cnt.warmer--;msg='你拿出一個暖暖包和乾衣服給小宇，他換好衣服、裹上毯子，慢慢不抖了。';}
  else msg='你手邊沒有暖暖包，帕桑從自己的背包拿出乾衣服和毯子借給小宇。';
  await say({p:'hero',html:`<p>${msg}</p>`});
  await ask('ch4_q2_2','ch4_guide_up');
  await say({p:'ch4_guide_up',html:'<p>做得不錯。我再考你兩題，山上最怕的就是狀況慢慢變糟。</p>'});
  await ask('ch4_q2_3','ch4_guide_up');
  await ask('ch4_q2_4','ch4_guide_up');
  await giveCard('ch4_k2_1');S.cards.hypothermia=true;
  e.s2a=true;
  await lines('ch4_hiker',['謝謝你們……我以後上山一定穿暖一點。']);
  await say({p:'ch4_guide_up',html:'<p>天快黑了，我們今晚就在營地 1 過夜。去帳篷那邊吧。</p>'});}
async function tent(){
  const e=st();
  if(!e.s2a){await say({p:'ch4_guide_up',html:'<p>先去看看那個發抖的年輕人，再來休息。</p>'});return;}
  if(S.scene==='ch4_camp1'){
    const i=await say({p:'ch4_guide_up',who:'營地 1',html:'<p>要在這裡過夜嗎？明天一早再上路。</p>',buttons:[{label:'過夜',primary:true},{label:'還不想睡'}]});
    if(i!==0)return;
    $('fade').classList.add('on');await sleep(RM?0:500);
    FA.setBusy(false);await go('ch4_camp1_night',[600,500]);FA.setBusy(true);$('fade').classList.remove('on');
    await say({icon:'🌙',who:'夜裡',html:'<p>天黑了，營火還亮著，氣溫降了很多。</p>'});}
  await ask('ch4_q2_5','ch4_guide_up');
  const lv=e.warm||warmLevel();
  await say({p:'hero',html:`<p>${lv==='full'?'你把睡墊鋪好、換上乾襪子，一層層穿好，睡得很安穩。':'你照著做了，但帶的保暖衣物不太夠，半夜還是有點冷，帕桑把備用毯子借給你，才慢慢睡著。'}</p>`});
  await giveCard('ch4_k2_2');
  e.s2=true;
  $('fade').classList.add('on');await sleep(RM?0:500);
  const html=nextDay();S.sta=FA.staMax();refresh();
  FA.setBusy(false);await go(CAMP1.scene,CAMP1.at);FA.setBusy(true);$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>早安！體力恢復了。</p>'+html});
  await say({icon:'🏔',who:'第 2 節完成！',html:'<p>營地 1 的課完成了。往營地 2 的小徑之後才會開放。</p>'});}
async function up(){await say({p:'hero',html:'<p>往上的小徑拉著繩子，營地 2 還沒有開放。</p>'});}
async function stall(){
  const r=await FA.chCall('ch3','gearShop');
  if(r===undefined)await say({p:'hero',html:'<p>攤位上沒有人。</p>'});}
async function guideTalk(){
  const e=st();
  for(;;){
    const i=await say({p:'ch4_guide',html:`<p>${e.met?'有什麼事嗎？':'你好，我們又見面了。'}</p>`,buttons:[{label:'聊聊雪嶺'},{label:e.s1?'什麼時候上山？':'準備上山（第 1 節）'},{label:'先離開',primary:true}]});
    e.met=true;
    if(i===1&&!e.s1){await lesson1();continue;}
    if(i===0)await lines('ch4_guide',['雪嶺的村子在山谷裡，冬天雪封了路，大家就待在屋子裡織毛線、煮熱茶。','Warm clothes 是保暖衣物。上山前，衣服要一層一層穿，濕了就要換。']);
    else if(i===1)await lines('ch4_guide',[e.s2?'營地 1 我們去過了，再往上的路還在整理，再給我一點時間。':'準備好了就從左上的石階上山，我們在營地 1 見。']);
    else return;}}
async function innkTalk(){
  const e=st();
  if(!e.innk){e.innk=true;await lines('ch4_innk',['歡迎！你是帕桑帶來的客人吧？','旅店有熱茶，也有乾淨的床。累了就在床上好好睡一覺。']);return;}
  await lines('ch4_innk',['山上的天氣說變就變，趕路的人最需要一個暖暖的地方休息。','想睡覺就走到床邊，住一晚 '+INN_COST+' 金幣。']);}
return {
  acts:{ch4_boat:boat,ch4_trail:trail,ch4_room:room,ch4_stall:stall,ch4_tent:tent,ch4_up:up},
  talk(id){if(id==='ch4_hiker'){const e=st();if(e.s2a)return lines('ch4_hiker',['多虧你們，我暖和多了。']);return lesson2();}
    if(id==='ch4_guide_up')return lines('ch4_guide_up',[st().s2a?'今晚就在營地 1 過夜，明天再看看路況。':'先去看看那個年輕人吧，他好像很冷。']);
    if(id==='ch4_guide')return guideTalk();if(id==='ch4_innk')return innkTalk();},
  goal(){const e=st();
    if(S.scene==='ch4_camp1'||S.scene==='ch4_camp1_night'){if(!e.s2a)return '營地 1 有個年輕登山客發抖，去看看他（第 2 節）。';if(!e.s2)return '到帳篷過夜（第 2 節）。';return '第 2 節完成！往營地 2 的路之後才開放。';}
    if(!e.s1)return '和帕桑聊聊，做上山前的準備（第 1 節）。';
    if(!e.c1||!e.s2)return '從山腳村左上的石階上山，到營地 1（第 2 節）。';
    return '第 2 節完成！往營地 2 的路之後才開放。';},
  news(id){const e=st();return (id==='ch4_guide'&&!e.s1)||(id==='ch4_hiker'&&!e.s2a);},
  ready,depart};
}
