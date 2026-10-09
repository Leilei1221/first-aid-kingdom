/* 第四章「雪嶺」章節程式（F1：章節骨架；F2：第 1 節出發前準備與裝備檢查、營地 1 與第 2 節失溫；F3：營地 2 與第 3 節高山症；F4：雪線與第 4 節雪盲、凍傷；F5：山屋與第 5 節迷路、求救訊號、分工）。
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
const CAMP1={scene:'ch4_camp1',at:[420,780]},CAMP2={scene:'ch4_camp2',at:[420,800]},SNOW={scene:'ch4_snowline',at:[320,700]},LODGE={scene:'ch4_lodge',at:[330,800]};
const WHISTLE={gap:1000,groups:2};  /* 求救哨聲小遊戲（遊戲參數）：三短聲為一組，兩組之間停一下（超過 gap 毫秒算一組結束），做對 groups 組就過關 */
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
if(DRAFT_OK)Object.assign(FA.WOUNDS,{frostbite:'手指凍傷',frostface:'臉部凍傷',snowblind:'雪盲'});
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
  const lodge=S.scene==='ch4_lodge_in';
  const i=await say({p:lodge?'ch4_keeper':'ch4_innk',who:lodge?'山屋':'山腳旅店',html:`<p>要住一晚嗎？一晚 ${INN_COST} 金幣，體力會完全恢復，進入下一天。</p><p class="small">金幣 ${S.coins}</p>`,buttons:[{label:'住一晚',primary:true,disabled:S.coins<INN_COST},{label:'不用了'}]});
  if(i!==0)return;
  S.coins-=INN_COST;$('fade').classList.add('on');await sleep(RM?0:500);
  const html=nextDay();S.sta=FA.staMax();refresh();$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>在暖暖的爐火旁睡了一覺，體力完全恢復了。</p>'+html});}
async function ask(key,p){  /* 同第三章：答錯顯示說明、可再選；選到標了嚴重錯誤的選項只記錄 */
  const z=(await quizzes())[key];
  for(;;){
    const pic=(z.img&&FA.A[z.img]?`<img src="${FA.A[z.img]}" alt="" style="display:block;margin:4px auto;max-height:150px;max-width:100%">`:'')+(z.imgs?`<div style="display:flex;gap:10px;justify-content:center;margin:4px 0">${z.imgs.filter(k=>FA.A[k]).map(k=>`<img src="${FA.A[k]}" alt="" style="height:64px">`).join('')}</div>`:'');
    const i=await say({p,hideCap:true,wound:z.wound,html:`${pic}<p class="q">${z.q}</p>`,buttons:z.opts.map(o=>({label:o}))});
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
/* 過夜（兩個營地共用）：白天營地 → 夜晚場景 → 睡前一題 → 睡覺 → 隔天回白天營地，該節完成 */
const CAMPS={
  ch4_camp1:{night:'ch4_camp1_night',day:CAMP1,need:'s2a',needMsg:'先去看看那個發抖的年輕人，再來休息。',ask:'ch4_q2_5',card:'ch4_k2_2',done:'s2',who:'營地 1',
    dark:'天黑了，營火還亮著，氣溫降了很多。',bed:()=>(st().warm||warmLevel())==='full'?'你把睡墊鋪好、換上乾襪子，一層層穿好，睡得很安穩。':'你照著做了，但帶的保暖衣物不太夠，半夜還是有點冷，帕桑把備用毯子借給你，才慢慢睡著。',
    finish:'營地 1 的課完成了。營地 1 右上的小徑現在可以上去營地 2。'},
  ch4_camp2:{night:'ch4_camp2_night',day:CAMP2,need:'s3a',needMsg:'先去看看老周，再來休息。',ask:'ch4_q3_4',card:null,done:'s3',who:'營地 2',
    dark:'天黑了，風從山谷吹上來，比營地 1 更冷、更安靜。',bed:()=>'你多喝了幾口水，早早躺下。老周也在旁邊的帳篷裡休息，頭痛慢慢退了。',
    finish:'營地 2 的課完成了。右上的小徑現在可以上雪線。'}};
async function tent(){
  const e=st(),id=S.scene.replace('_night',''),C=CAMPS[id];
  if(!e[C.need]){await say({p:'ch4_guide_up',html:`<p>${C.needMsg}</p>`});return;}
  if(S.scene===id){
    const i=await say({p:'ch4_guide_up',who:C.who,html:'<p>要在這裡過夜嗎？明天一早再上路。</p>',buttons:[{label:'過夜',primary:true},{label:'還不想睡'}]});
    if(i!==0)return;
    $('fade').classList.add('on');await sleep(RM?0:500);
    FA.setBusy(false);await go(C.night,[600,500]);FA.setBusy(true);$('fade').classList.remove('on');
    await say({icon:'🌙',who:'夜裡',html:`<p>${C.dark}</p>`});}
  await ask(C.ask,'ch4_guide_up');
  await say({p:'hero',html:`<p>${C.bed()}</p>`});
  if(C.card)await giveCard(C.card);
  e[C.done]=true;
  $('fade').classList.add('on');await sleep(RM?0:500);
  const html=nextDay();S.sta=FA.staMax();refresh();
  FA.setBusy(false);await go(C.day.scene,C.day.at);FA.setBusy(true);$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>早安！體力恢復了。</p>'+html});
  await say({icon:'🏔',who:`第 ${C.done.slice(1)} 節完成！`,html:`<p>${C.finish}</p>`});}
async function lesson3(){
  const e=st();
  await lines('ch4_elder',['哈哈，我爬過的山比你們走過的路還多……只是頭有點痛，沒事沒事。','（他扶著額頭，皺著眉。）']);
  await say({p:'ch4_guide_up',html:'<p>老周趕了一天路，沒有在營地 1 休息就直接上來。這種時候要特別小心。</p>'});
  await ask('ch4_q3_1','ch4_guide_up');
  await say({p:'ch4_elder',html:`<img src="${FA.A.ch4_elder_sick}" alt="" style="display:block;margin:4px auto;max-height:150px"><p>頭痛得像要裂開……還有點想吐，昨晚根本沒睡著。</p>`});
  await ask('ch4_q3_2','ch4_guide_up');
  await say({p:'hero',html:'<p>你請老周坐到長椅上休息，把水壺遞給他，也請他先不要再往上走。</p>'});
  await say({p:'ch4_guide_up',html:'<p>很好。我再考你一題，山上最怕的就是狀況慢慢變糟。</p>'});
  await ask('ch4_q3_3','ch4_guide_up');
  await giveCard('ch4_k3_1');S.cards.altitude=true;
  e.s3a=true;
  await lines('ch4_elder',['唉，是我太急了……謝謝你們，我今天就乖乖休息。']);
  await say({p:'ch4_guide_up',html:'<p>天快黑了，我們今晚就在營地 2 過夜，讓身體適應這個高度。去帳篷那邊吧。</p>'});}
async function up(){
  const e=st();
  if(!e.s2){await say({p:'hero',html:'<p>往上的小徑拉著繩子。帕桑說：「先把營地 1 的事做完，我們再上去。」</p>'});return;}
  const i=await say({p:'ch4_guide_up',who:'上山',html:'<p>要上營地 2 嗎？越往上，空氣越稀薄，要走慢一點。</p>',buttons:[{label:'出發',primary:true},{label:'再等一下'}]});
  if(i!==0)return;
  await stashDepart();
  const first=!e.c2;e.c2=true;
  await trip(CAMP2,{icon:'🥾',who:'上山',html:'<p>沿著小徑一路往上，空氣越來越稀薄，大家走得比之前慢，中途歇了好幾次，才到營地 2。</p>'});
  if(first)await say({p:'ch4_guide_up',html:'<p>營地 2 到了。這裡比營地 1 高很多，大家都慢慢來。……那邊那位老先生，臉色好像不太好。</p>'});}
async function lesson4(){
  const e=st();
  await say({p:'ch4_photog',html:`<img src="${FA.A.ch4_photog_snowblind}" alt="" style="display:block;margin:4px auto;max-height:150px"><p>好痛……眼睛像進了沙子，一直流眼淚，睜不開……我剛剛為了拍照把護目鏡拿下來，拍了好久。</p>`});
  await ask('ch4_q4_1','ch4_guide_up');
  await say({p:'hero',html:'<p>你扶阿岩到避風小屋裡比較暗的地方坐下，請阿岩閉上眼睛，用濕涼的布輕輕蓋在眼睛上。</p>'});
  await ask('ch4_q4_2','ch4_guide_up');
  await giveCard('ch4_k4_1');
  await say({p:'ch4_photog',html:'<p>眼睛好一點了……不過，我拿相機的時候，手套也脫了。手指怎麼……麻麻的，好像沒有感覺了。</p>'});
  await ask('ch4_q4_3','ch4_guide_up');
  await ask('ch4_q4_4','ch4_guide_up');
  await ask('ch4_q4_5','ch4_guide_up');
  await giveCard('ch4_k4_2');
  e.s4=true;
  await lines('ch4_photog',['謝謝你們……我以後一定戴好護目鏡和手套，再怎麼想拍照也一樣。']);
  await say({p:'ch4_guide_up',html:'<p>很好。再往上走，就是山屋了。路還沒準備好，我們先在這裡休息一下。</p>'});
  await say({icon:'🏔',who:'第 4 節完成！',html:'<p>雪線的課完成了。往山屋的小徑之後才會開放。</p>'});}
async function up2(){
  const e=st();
  if(!e.s3){await say({p:'hero',html:'<p>往上的小徑拉著繩子。帕桑說：「先把營地 2 的事做完，我們再上去。」</p>'});return;}
  const i=await say({p:'ch4_guide_up',who:'上山',html:'<p>要上雪線嗎？那裡沒有樹遮擋，陽光很強、風也大。護目鏡和手套要戴好。</p>',buttons:[{label:'出發',primary:true},{label:'再等一下'}]});
  if(i!==0)return;
  await stashDepart();
  const first=!e.c3;e.c3=true;
  await trip(SNOW,{icon:'🥾',who:'上山',html:'<p>沿著雪坡一路往上，樹越來越少，最後只剩下白茫茫的雪和岩石。陽光照在雪上，亮得讓人睜不開眼。</p>'});
  if(first)await say({p:'ch4_guide_up',html:'<p>雪線到了。這裡的雪會把陽光整個反射回來，特別刺眼，也特別冷。……那邊有人蹲在地上，過去看看。</p>'});}
async function up3(){
  const e=st();
  if(!e.s4){await say({p:'hero',html:'<p>往上的小徑拉著繩子。帕桑說：「先把雪線的事做完，我們再上去。」</p>'});return;}
  const i=await say({p:'ch4_guide_up',who:'上山',html:'<p>要上山屋嗎？再走一小段就到了。</p>',buttons:[{label:'出發',primary:true},{label:'再等一下'}]});
  if(i!==0)return;
  await stashDepart();
  const first=!e.c4;e.c4=true;
  await trip(LODGE,{icon:'🥾',who:'上山',html:'<p>沿著繩索標示的路線，再爬一段緩坡，煙囪冒著煙的山屋終於出現在眼前。</p>'});
  if(first)await lines('ch4_guide_up',['山屋到了！這裡是雪嶺最高的一個落腳處，也是我們整趟路的終點。','管理員達瓦在這裡守了很多年，什麼天氣、什麼狀況都見過。']);}
/* 求救哨聲小遊戲：按「吹」三下為一組，停一下再來一組；做對 WHISTLE.groups 組過關 */
async function whistleGame(){
  await say({p:'hero',who:'吹哨求救',html:`<img src="${FA.A.ch4_i_whistle}" alt="" style="display:block;margin:4px auto;height:70px"><p>三短聲為一組：按「吹」三下，停一下，再吹三下。</p><div class="meter" style="height:18px"><i id="whBar" style="width:0%"></i></div><p id="whTxt" class="small">已完成 0 組</p>`,
    buttons:[{label:'吹！',primary:true},{label:'放棄'}],
    onRender:(root,fin)=>{let n=0,good=0,timer=null;const bar=root.querySelector('#whBar'),txt=root.querySelector('#whTxt');
      const btn=root.closest('.box').querySelectorAll('#dBtns button');
      const close=()=>{if(n===3){good++;txt.textContent=`很好！三短聲。已完成 ${good} 組`;}else{good=0;txt.textContent=`這一組吹了 ${n} 下，三短聲要剛好三下。重新來。已完成 0 組`;}
        n=0;bar.style.width=(good/WHISTLE.groups*100)+'%';if(good>=WHISTLE.groups)setTimeout(()=>fin('ok'),400);};
      btn[0].onclick=()=>{clearTimeout(timer);n++;txt.textContent=`吹了 ${n} 下……`;timer=setTimeout(close,WHISTLE.gap);};
      btn[1].onclick=()=>{clearTimeout(timer);fin('quit');};}});}
async function lesson5(){
  const e=st();
  await lines('ch4_keeper',['歡迎來到山屋。帕桑都跟我說了，你一路上幫了不少人。','這裡是山上最後一道防線，所以我要再問你幾件事。']);
  await ask('ch4_q5_1','ch4_keeper');
  await ask('ch4_q5_2','ch4_keeper');
  await say({p:'ch4_keeper',html:'<p>知道是知道，真的吹出來是另一回事。來，吹一次給我聽聽。</p>'});
  await whistleGame();
  await say({p:'ch4_keeper',html:'<p>很好，記住那個節奏。</p>'});
  await ask('ch4_q5_3','ch4_keeper');
  await ask('ch4_q5_4','ch4_keeper');
  await giveCard('ch4_k5_1');S.cards.lost=true;S.cards.signal=true;
  e.s5=true;
  await say({p:'ch4_keeper',html:'<p>你已經學會山上最重要的幾件事了。山屋隨時歡迎你，累了就在樓上休息。</p>'});
  await say({icon:'🏔',who:'第 5 節完成！',html:'<p>山屋的課完成了。接下來是整趟旅程的章末演練，之後才會開放。</p>'});}
async function board(){await say({p:'hero',html:'<p>木製公告板上釘著幾張紙，畫著太陽、雲和雪花的小圖案。（每天的天氣與求助，之後才會貼上來。）</p>'});}
async function up4(){await say({p:'hero',html:'<p>往更高處的小徑拉著繩子，現在還不能上去。</p>'});}
async function shelter(){await say({p:'hero',html:'<p>石頭砌成的小屋擋住了風，坐在裡面，身體慢慢暖了起來。</p>'});}
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
  acts:{ch4_boat:boat,ch4_trail:trail,ch4_room:room,ch4_stall:stall,ch4_tent:tent,ch4_up:up,ch4_up2:up2,ch4_up3:up3,ch4_up4:up4,ch4_board:board,ch4_shelter:shelter},
  talk(id){if(id==='ch4_hiker'){const e=st();if(e.s2a)return lines('ch4_hiker',['多虧你們，我暖和多了。']);return lesson2();}
    if(id==='ch4_keeper'){if(st().s5)return lines('ch4_keeper',['外面風大，進來暖暖身子吧。']);return lesson5();}
    if(id==='ch4_photog'){if(st().s4)return lines('ch4_photog',['手指和眼睛都好多了。戴好護目鏡，我才敢再拍。']);return lesson4();}
    if(id==='ch4_elder'){if(st().s3a)return lines('ch4_elder',['頭痛好多了。山不會跑，慢慢來才是真本事。']);return lesson3();}
    if(id==='ch4_guide_up'){const e=st();if(S.scene.startsWith('ch4_lodge'))return lines('ch4_guide_up',[e.s5?'整趟路的課你都學完了。章末的演練，等我準備好再叫你。':'去跟管理員達瓦聊聊吧。']);
      if(S.scene.startsWith('ch4_snow'))return lines('ch4_guide_up',[e.s4?'雪線的事都處理好了。再往上是山屋，路還在整理。':'先去看看那個蹲在地上的人吧。']);
      if(S.scene.startsWith('ch4_camp2'))return lines('ch4_guide_up',[e.s3a?'今晚就在營地 2 過夜，讓身體適應高度。':'先去看看老周吧，他好像很不舒服。']);
      return lines('ch4_guide_up',[e.s2?'營地 1 右上的小徑可以去營地 2，記得慢慢走。':e.s2a?'今晚就在營地 1 過夜，明天再看看路況。':'先去看看那個年輕人吧，他好像很冷。']);}
    if(id==='ch4_guide')return guideTalk();if(id==='ch4_innk')return innkTalk();},
  goal(){const e=st();
    if(S.scene.startsWith('ch4_lodge')){if(!e.s5)return '和山屋管理員達瓦聊聊（第 5 節）。';return '第 5 節完成！章末演練之後才開放。';}
    if(S.scene.startsWith('ch4_snow')){if(!e.s4)return '雪線有人蹲在地上，去看看（第 4 節）。';return e.s5?'第 5 節完成！章末演練之後才開放。':'第 4 節完成！右上的小徑可以上山屋（第 5 節）。';}
    if(S.scene.startsWith('ch4_camp2')){if(!e.s3a)return '營地 2 的資深登山客老周頭很痛，去看看他（第 3 節）。';if(!e.s3)return '到帳篷過夜、適應高度（第 3 節）。';return e.s4?'第 4 節完成！往山屋的路之後才開放。':'第 3 節完成！右上的小徑可以上雪線（第 4 節）。';}
    if(S.scene.startsWith('ch4_camp1')){if(!e.s2a)return '營地 1 有個年輕登山客發抖，去看看他（第 2 節）。';if(!e.s2)return '到帳篷過夜（第 2 節）。';if(!e.s3)return '營地 1 右上的小徑可以上營地 2（第 3 節）。';return e.s4?'第 4 節完成！往山屋的路之後才開放。':'第 3 節完成！營地 2 右上的小徑可以上雪線（第 4 節）。';}
    if(!e.s1)return '和帕桑聊聊，做上山前的準備（第 1 節）。';
    if(!e.c1||!e.s2)return '從山腳村左上的石階上山，到營地 1（第 2 節）。';
    return e.s5?'第 5 節完成！章末演練之後才開放。':e.s4?'第 4 節完成！從雪線右上的小徑上山屋（第 5 節）。':e.s3?'從營地 2 右上的小徑上雪線（第 4 節）。':'從營地 1 右上的小徑上營地 2（第 3 節）。';},
  news(id){const e=st();return (id==='ch4_guide'&&!e.s1)||(id==='ch4_hiker'&&!e.s2a)||(id==='ch4_elder'&&!e.s3a)||(id==='ch4_photog'&&!e.s4)||(id==='ch4_keeper'&&!e.s5);},
  ready,depart};
}
