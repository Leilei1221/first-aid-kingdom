/* 第四章「雪嶺」G：抉擇與求生（老師 2026-10-13～14 決定、審過題目大綱）。
 * 上山前看氣象預報圖（等一天／勉強出發，不給獎勵）→ 路上遇到落石前兆與白茫茫迷路 → 到山屋遇暴風雪、窗戶破了，被困 1～3 天求生。
 * 撐不下去＝請救援：扣救援費、送回山腳村（同 rescueFail）；嚮導訓練的「求生練習」只記錄、不扣錢。
 * 天氣、天數都由日期算出來（沒有亂數），學生重來會遇到同樣的情況。
 * 題目在 dialogues.json 的 ch4_w*、ch4_r*、ch4_l*、ch4_s*；知識卡 ch4_k6_1～4。數字全是遊戲平衡參數，不是醫學數字。
 * 狀態只記在 S.c.ch4.fc（這趟旅程的預報與事件）與 S.c.ch4.compass，不新增頂層存檔欄位。 */
export default function(FA,{S,st,ask,PREV,have,warmLevel,fail,DL,innCost,cardOf}){
const {say,lines,refresh,sleep,go,RM,nextDay,checkpoint,$}=FA;
const pic=(k,h)=>k&&FA.A[k]?`<img src="${FA.A[k]}" alt="" style="display:block;margin:4px auto;max-height:${h}px;max-width:100%">`:'';
/* 遊戲參數：保暖值 0～100（歸零＝撐不下去）。每天先扣 BASE，再加上做對的事與裝備 */
const P={base:-40,start:{full:100,part:90,low:80},seal:10,sealLate:5,rain:5,wind:5,windLate:2,fire:20,fireWood:2,blanket:10,warmer:10,
  short:-10,shortKept:-5,coldRight:5,coldWrong:-10,watchRight:5,watchWrong:-5,lamp:3,wrongHit:-5,lodgeWood:3,compassCost:60,compassMiss:15};
const LEN=[1,2,3],n0=x=>x||0;
const cardOnce=async k=>{if(S.cards[k])return;const c=(await cardOf(k))||FA.CARDS[k];S.cards[k]=true;await say({p:'hero',html:`<div class="card"><b>${c.title}</b><p>${c.text}</p></div><p class="good">獲得知識卡</p>`});};
/* ---------- 氣象：由日期算出（不是亂數）。storm[i]＝出發日起第 i 天有沒有暴風雪 ---------- */
async function plan(d0){
  const storm=[];for(let i=0;i<3;i++)storm.push(await DL.stormDay(d0+i));
  return {d0,storm,len:LEN[((d0%3)+3)%3]};}
const WX_TXT=s=>s?'大雪，風很大':'晴或多雲，風不大';
async function forecastShow(p){
  const row=p.storm.map((s,i)=>`<div style="flex:1;text-align:center;padding:4px;border:1px solid #6b5a3a;border-radius:8px"><b>第 ${i+1} 天</b><br><span class="${s?'bad':'good'}">${WX_TXT(s)}</span></div>`).join('');
  const bad=p.storm.some(Boolean);
  return `${pic('ch4_forecast',210)}<div style="display:flex;gap:6px;margin:4px 0">${row}</div>`+(bad?`<p class="warn">這三天內有暴風雪${p.storm[2]?`，而且到山屋那天（第 3 天）剛好碰上，預計會持續約 ${p.len} 天`:''}。</p>`:'<p class="good">這三天天氣穩定。</p>');}
/* 上山前：看預報、自己決定。回傳 true＝出發 */
async function forecast(){
  const e=st();
  if(e.fc||e.c1)return true;  /* 已經出發過（或舊存檔）：不再看 */
  for(;;){
    const p=await plan(S.day),bad=p.storm.some(Boolean);
    if(!e.fcQ){e.fcQ=true;
      await say({icon:'🌤',who:'山腳村氣象公告',html:await forecastShow(p)+'<p class="small">先看一看預報圖，再回答幾個問題。</p>',buttons:[{label:'仔細看一看',primary:true}]});
      await ask('ch4_w1','ch4_guide');await ask('ch4_w2','ch4_guide');await ask('ch4_w3','ch4_guide');await cardOnce('ch4_k6_2');}
    const buttons=(bad?[{label:'勉強出發'}]:[{label:'出發',primary:true}]).concat([{label:`等一天（旅店 ${innCost} 金幣）`,disabled:S.coins<innCost},{label:'再準備一下'}]);
    const i=await say({icon:'🌤',who:'山腳村氣象公告',html:await forecastShow(p)+'<p class="small">天氣是由日期算出來的，不是運氣。要不要上山，你自己決定。</p>',buttons});
    const label=buttons[i].label;
    if(label==='再準備一下')return false;
    if(label.startsWith('等一天')){
      S.coins-=innCost;$('fade').classList.add('on');await sleep(RM?0:500);
      const html=nextDay();S.sta=FA.staMax();refresh();$('fade').classList.remove('on');checkpoint();
      await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>在旅店多住了一晚，體力完全恢復。</p>'+html});
      continue;}
    e.fc={d0:S.day,rock:!!(p.storm[0]||p.storm[1]),white:!!p.storm[2],len:p.len,force:bad};
    if(bad)await say({p:'ch4_guide',html:'<p>預報說會有暴風雪，你還是決定要上去……好，我會跟緊你。路上要特別小心。</p><p class="small">勉強出發沒有任何獎勵，只多了風險。</p>'});
    return true;}}
/* ---------- 路上：落石（營地 1→2，有前兆，先預測） ---------- */
async function rockfall(){
  const f=st().fc;if(!f||!f.rock||f.rockDone)return;f.rockDone=true;
  await say({p:'ch4_guide_up',html:`${pic('ch4_rockfall',170)}<p>走到一半，帕桑停了下來，指著上面的岩壁。「這一段，先看看。」</p>`});
  await ask('ch4_r1','ch4_guide_up');
  await ask('ch4_r2','ch4_guide_up');
  await say({icon:'🪨',who:'上面傳來悶響',html:'<p>一顆小石頭滾下來，接著是一整片碎石！</p>'});
  await ask('ch4_r3','ch4_guide_up');
  await say({p:'ch4_guide_up',html:'<p>石頭停了。我們快速離開這裡。</p>'});
  await cardOnce('ch4_k6_3');}
/* ---------- 路上：白茫茫迷路（雪線→山屋）。有指南針才有 L2、L3；沒有就多耗體力 ---------- */
async function whiteout(){
  const e=st(),f=e.fc;if(!f||!f.white||f.whiteDone)return;f.whiteDone=true;
  await say({p:'ch4_guide_up',html:`${pic('ch4_whiteout2',170)}<p>風雪突然變大，白茫茫的什麼都看不到，連帕桑的背影都模糊了。</p>`});
  await ask('ch4_l1','ch4_guide_up');
  if(e.compass){await ask('ch4_l2','ch4_guide_up');await ask('ch4_l3','ch4_guide_up');}
  else{S.sta=Math.max(5,S.sta-P.compassMiss);refresh();await say({p:'hero',html:`<p>沒有指南針，只能靠地圖和看得到的地標一小段一小段確認方向，走得又慢又累，多耗了 ${P.compassMiss} 體力（剩 ${S.sta}）。</p><p class="small">下次到山腳村的裝備攤買個指南針。</p>`});}
  await ask('ch4_l4','ch4_guide_up');}
/* ---------- 山屋：暴風雪求生 ---------- */
function inventory(practice){
  if(practice)return {ration:2,water:2,flint:1,wood:2,lv:'full',blanket:1,warmer:1,lamp:1,rain:1,signal:1,practice:true};
  const kit=k=>FA.kitCount(k);
  return {ration:kit('ration'),water:kit('water'),flint:n0(S.mat.flint),wood:n0(S.mat.wood),lv:warmLevel(),blanket:have('blanket'),warmer:have('warmer'),lamp:have('headlamp'),rain:kit('raincoat'),signal:kit('whistle')+kit('flashlight')+have('headlamp')};}
function spend(inv,k,real){  /* 用掉一件：練習只扣副本，真的才扣背包 */
  if(n0(inv[k])<=0)return false;inv[k]--;if(inv.practice||!real)return true;
  if(k==='ration'||k==='water')FA.takeKit({[k]:1});
  else if(k==='flint')S.mat.flint=Math.max(0,n0(S.mat.flint)-1);
  else if(k==='wood')S.mat.wood=Math.max(0,n0(S.mat.wood)-1);
  else if(k==='blanket'){const e=S.c.ch3_e3;if(e.cnt.blanket>0)e.cnt.blanket--;else if(e.own.blanket)e.own.blanket=0;}
  else if(k==='warmer'){const e=S.c.ch3_e3;if(e.cnt.warmer>0)e.cnt.warmer--;else if(e.own.warmer)e.own.warmer=0;}
  return true;}
const bar=w=>{const n=Math.max(0,Math.min(10,Math.round(w/10)));return '▮'.repeat(n)+'▯'.repeat(10-n);};
const stat=(w,inv)=>`<p class="small">保暖 ${bar(w)} ${Math.max(0,w)}／100　乾糧 ${inv.ration}　開水 ${inv.water}　木柴 ${inv.wood}　打火石 ${inv.flint}</p>`;
async function survive(opt){
  opt=opt||{};const practice=!!opt.practice,e=st();
  const len=opt.len||(e.fc&&e.fc.len)||2,inv=inventory(practice);
  inv.wood+=P.lodgeWood;  /* 山屋柴棚的存柴 */
  const eff=Math.max(1,len-(inv.signal>0&&len>1?1:0));
  let warm=P.start[inv.lv],fireOn=false,log=[];
  const q=async(k,pr)=>(await ask(k,'ch4_guide_up',{practice})).wrong;
  $('fade').classList.add('on');await sleep(RM?0:500);
  FA.setBusy(false);await go('ch4_lodge_in_storm',[820,650]);FA.setBusy(true);$('fade').classList.remove('on');
  await say({icon:'🌨',who:practice?'求生練習':'暴風雪夜',html:`<p>${practice?'這是嚮導訓練，不會扣錢，也不會送回山腳村。':'暴風雪來了！山屋的窗戶被風吹破，雪灌了進來。'}</p><p>山路被雪封住，救援預計要等 ${len} 天。我們得靠身上的東西撐下去。</p>${stat(warm,inv)}`});
  let kept=false;
  for(let d=1;d<=eff;d++){
    let net=P.base;const notes=[],last=d===eff;
    if(d===1){
      const w1=await q('ch4_s1');net+=w1===0?P.seal:P.sealLate;notes.push('用東西擋住了破窗');
      if(inv.rain>0){net+=P.rain;notes.push('用雨衣擋窗，更密實');}
      const w2=await q('ch4_s2');net+=w2===0?P.wind:P.windLate;notes.push('擋風的位置放對了');
      const w3=await q('ch4_s3');net+=w3*P.wrongHit;
      if(inv.flint>0&&inv.wood>0){spend(inv,'flint',true);fireOn=true;notes.push('用打火石生了火（有留通風口）');}
      else notes.push(inv.flint>0?'沒有木柴，生不了火':'沒有打火石，生不了火');
      if(spend(inv,'blanket',true)){net+=P.blanket;notes.push('蓋上保暖毯（用掉 1 條）');}
    }else if(!fireOn&&inv.flint>0&&inv.wood>0){spend(inv,'flint',true);fireOn=true;notes.push('重新生了火');}
    if(fireOn){
      if(inv.wood>0){net+=P.fire;for(let i=0;i<P.fireWood;i++)spend(inv,'wood',true);if(d>1)notes.push('火持續燒著，取暖');}
      else{fireOn=false;notes.push('木柴用完了，火滅了');}}
    if(spend(inv,'warmer',true)){net+=P.warmer;notes.push('用了暖暖包（用掉 1 個）');}
    if(d===2){
      const w4=await q('ch4_s4'),w5=await q('ch4_s5');kept=w5===0;net+=(w4+w5)*P.wrongHit;
      const w6=await q('ch4_s6');net+=w6===0?P.coldRight:P.coldWrong;notes.push(w6===0?'把毯子和乾衣服先給最冷的人':'沒有先照顧最冷的人，有人越來越冷');}
    /* 吃喝：每天 1 份乾糧、1 份開水；沒有的話扣保暖，雪要煮開才能喝（需要火） */
    if(spend(inv,'ration',true))notes.push('吃了 1 份乾糧');else{net+=kept?P.shortKept:P.short;notes.push('乾糧沒了，餓著肚子');}
    if(spend(inv,'water',true))notes.push('喝了 1 份開水');
    else if(fireOn)notes.push('把雪煮開當水喝');
    else{net+=kept?P.shortKept:P.short;notes.push('沒有水，也沒有火可以化雪');}
    if(d===1&&eff>1){const w8=await q('ch4_s8');net+=w8===0?P.watchRight:P.watchWrong;if(inv.lamp>0){net+=P.lamp;notes.push('有頭燈，夜裡輪流看顧比較方便');}}
    if(last)await q('ch4_s7');
    warm=Math.min(100,warm+net);log.push({d,net,warm});
    await say({icon:'📋',who:`第 ${d} 天結算`,html:`<ul>${notes.map(t=>`<li>${t}</li>`).join('')}</ul><p>這一天保暖 ${net>=0?'+':''}${net}。</p>${stat(warm,inv)}`});
    if(warm<=0){
      if(practice){await say({icon:'📋',who:'求生練習',html:'<p>這次撐不下去了。想想看：哪一步可以做得更好？再練習一次也可以。</p>'});return false;}
      await fail('C12','hypothermia','保暖歸零，撐不下去');}}
  /* 撐到救援 */
  const word=inv.signal>0&&len>1?'哨聲和燈光讓救援隊比預期更早找到你們。':'救援隊頂著風雪趕到了山屋。';
  if(!practice){S.sta=Math.round(FA.staMax()*.6);for(let i=0;i<eff;i++)nextDay();}
  $('fade').classList.add('on');await sleep(RM?0:500);
  FA.setBusy(false);await go('ch4_lodge',[330,800]);FA.setBusy(true);refresh();$('fade').classList.remove('on');
  await say({icon:'🚨',who:practice?'練習結束':`第 ${S.day} 天`,html:`<p>${word}</p><p class="good">你們撐過來了！${practice?'':`（${eff} 天）`}</p>`});
  if(!practice){if(e.fc)e.fc.svDone=true;e.sv={days:eff,warm};checkpoint();}
  await cardOnce('ch4_k6_1');await cardOnce('ch4_k6_4');
  return true;}
async function arrive(){const f=st().fc;if(f&&f.white&&!f.svDone&&!f.svSkip)await survive();}
/* ---------- 山腳村裝備攤：指南針 ---------- */
const compassRow=()=>({price:P.compassCost,has:!!st().compass});
return {forecast,rockfall,whiteout,survive,arrive,compassRow,P,plan};}
