(async function(){
/* ================= 載入內容與圖片 ================= */
const startBtn=document.getElementById('btnStart'),startLabel=startBtn.textContent;
startBtn.disabled=true;startBtn.textContent='載入中…';
const getJSON=async u=>{const r=await fetch(u);if(!r.ok)throw new Error(u+' '+r.status);return r.json();};
let C,A={};
const CHAPTERS={};
const CH_MODS={};  /* 章節 id → 章節程式的工廠函式，核心程式定義好之後才呼叫（見檔案最後的 FA） */
const REGIONS={};  /* 章節宣告的地區（chapter.json 的 region）；綠葉谷（base）固定存在，見下方 BASE */  /* 章節 id → {id,name,open}；沒開放的章節只留這筆紀錄，用來擋住入口 */
const DEBUG=location.hash==='#debug'&&localStorage.getItem('fa-debug')==='1';
const WILD_FORCE=DEBUG&&new URLSearchParams(location.search).get('wild')==='1';  /* 只有 #debug 的 ?wild=1 能在本機強制開啟野外項目 */
const FORCE_OPEN=DEBUG?(new URLSearchParams(location.search).get('open')||'').split(','):[];
const CH_BASE=(DEBUG&&new URLSearchParams(location.search).get('chbase'))||'chapters';  /* 只有 #debug 才能換章節資料夾（測試用） */
const chOf=id=>Object.keys(CHAPTERS).find(c=>(id||'').startsWith(c+'_'))||null;
const chClosed=id=>{const c=chOf(id);return !!c&&!(CHAPTERS[c]&&CHAPTERS[c].open);};
async function loadChapters(){
  let idx;try{idx=await getJSON(`${CH_BASE}/index.json`);}catch(e){return [];}
  const loaded=[];
  for(const e of idx){
    CHAPTERS[e.id]={id:e.id,name:e.name,open:false};
    if(!e.open&&!FORCE_OPEN.includes(e.id))continue;  /* FORCE_OPEN：只有 #debug 的 ?open=ch2 才會強制開放（本機測試用） */
    try{
      const meta=await getJSON(`${CH_BASE}/${e.id}/chapter.json`),f=meta.files||{};
      /* 章節程式（選用）：只在章節開放時載入；default export 是 (FA)=>掛接點 */
      if(meta.script)CH_MODS[e.id]=(await import(new URL(`${CH_BASE}/${e.id}/${meta.script}`,location.href).href)).default;
      const get=async n=>f[n]?getJSON(`${CH_BASE}/${e.id}/${f[n]}`):null;
      const d={scenes:await get('scenes'),signs:await get('signs'),characters:await get('characters'),cards:await get('cards'),
        events:await get('events'),items:await get('items'),ratios:await get('ratios'),dialogues:await get('dialogues'),walks:await get('walks')};
      const bad=[];const pre=k=>{if(!k.startsWith(e.id+'_'))bad.push(k);};
      Object.keys(d.scenes||{}).forEach(pre);Object.keys(d.signs||{}).forEach(pre);Object.keys((d.characters||{}).PEOPLE||{}).forEach(pre);
      Object.keys((d.cards||{}).CARDS||{}).forEach(pre);Object.keys(d.walks||{}).forEach(pre);
      ['say','quizzes','text'].forEach(g=>Object.keys((d.dialogues||{})[g]||{}).forEach(pre));
      ((d.events||{}).EVENTS||[]).forEach(v=>pre(v.id));Object.keys((d.events||{}).VICTIMS||{}).forEach(pre);
      Object.keys((d.items||{}).ITEMS||{}).forEach(pre);Object.keys((d.items||{}).MATS||{}).forEach(pre);Object.keys((d.ratios||{}).RATIO||{}).forEach(pre);
      if(bad.length)throw new Error(`章節 ${e.id} 有 id 沒有 ${e.id}_ 前綴：${bad.join(', ')}`);
      Object.assign(C.scenes,d.scenes||{});Object.assign(C.signs,d.signs||{});Object.assign(C.walks,d.walks||{});
      Object.assign(C.characters.PEOPLE,(d.characters||{}).PEOPLE||{});Object.assign(C.cards.CARDS,(d.cards||{}).CARDS||{});
      if(d.events){C.quests.EVENTS.push(...(d.events.EVENTS||[]));Object.assign(C.quests.VICTIMS,d.events.VICTIMS||{});}
      if(d.items){Object.assign(C.items.ITEMS,d.items.ITEMS||{});Object.assign(C.items.MATS,d.items.MATS||{});}
      if(d.ratios)Object.assign(C.ratios.RATIO,d.ratios.RATIO||{});
      ['say','quizzes','text'].forEach(g=>Object.assign(C.dialogues[g],((d.dialogues||{})[g])||{}));
      if(meta.region)REGIONS[e.id]=Object.assign({chapter:e.id,id:e.id},meta.region);
      CHAPTERS[e.id].open=true;loaded.push({id:e.id,assets:meta.assets||[]});
    }catch(err){delete CH_MODS[e.id];console.error('章節載入失敗，已略過：',e.id,err);}
  }
  return loaded;}
try{
  const [items,balance,characters,crafting,cards,quests,ratios,scenes,signs,dialogues,wounds,weather,rescue,walks,manifest]=await Promise.all(
    ['items','balance','characters','crafting_and_farm','knowledge_cards','quests_and_events','sprite_ratios','scenes','signs','dialogues','wounds','weather','rescue'].map(n=>getJSON(`content/${n}.json`))
    .concat([getJSON('data/walks.json'),getJSON('assets/manifest.json')]));
  C={items,balance,characters,crafting,cards,quests,ratios,scenes,signs,dialogues,wounds,weather,rescue,walks};
  manifest.forEach(n=>A[n]=`assets/${n}.webp`);
  const imgs=manifest.map(n=>A[n]);
  /* 章節：chapters/index.json 列出各章與開關；開放的章節才載入（格式見 docs/chapter-pack-format.md）。章節載入失敗不影響序章 */
  for(const ch of await loadChapters())(ch.assets||[]).forEach(n=>{A[n]=`${CH_BASE}/${ch.id}/assets/${n}.webp`;imgs.push(A[n]);});
  let done=0;
  await Promise.all(imgs.map(u=>new Promise(r=>{const im=new Image();
    im.onload=im.onerror=()=>{startBtn.textContent=`載入中… ${++done}/${imgs.length}`;r();};im.src=u;})));
}catch(err){
  console.error(err);startBtn.textContent='載入失敗，請重新整理（不能直接雙擊檔案開啟）';return;
}
startBtn.disabled=false;startBtn.textContent=startLabel;
const WALKS=C.walks;
const KEY='fa-kingdom-p1-v1',MW=1672,MH=941,CELL=8;
const RM=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
document.documentElement.style.setProperty('--world',`url(${A.world})`);
document.getElementById('titleHero').src=A.hero;

/* ================= 內容編譯（JSON 字串條件 → 函式） ================= */
/* 場景出口、路標的條件在 JSON 裡是函式原始碼字串，這裡轉成函式；S 每次呼叫時取當下的存檔狀態 */
const mk=src=>{const f=new Function('S','return ('+src+')');return (...a)=>f(S)(...a);};
function compileScenes(raw){const out={};
  for(const [id,s] of Object.entries(raw))out[id]=Object.assign({},s,{exits:(s.exits||[]).map(e=>({
    test:mk(e.test),to:e.toFn?mk(e.toFn):e.to,at:e.at,
    need:chClosed(e.to)?()=>false:(e.need?mk(e.need):undefined),block:chClosed(e.to)?'這一章還沒開放，等老師開放之後再來探險吧。':(e.block||undefined)}))});
  return out;}
function compileSigns(raw){const out={};
  for(const [id,list] of Object.entries(raw))out[id]=list.map(g=>({x:g.x,y:g.y,
    t:typeof g.t==='string'?()=>g.t:(c=>()=>c()?g.t.yes:g.t.no)(mk(g.t.cond))}));
  return out;}
/* ================= 對話文字（content/dialogues.json） ================= */
function lookup(path,v){const ks=path.split('.');let o=(ks[0] in v)?v:GLOBALS;
  for(const k of ks){if(o==null||!(k in Object(o)))throw new Error('對話缺少變數：'+path);o=o[k];}return o;}
const fill=(s,v)=>s.replace(/\{([\w.]+)\}/g,(m,p)=>lookup(p,v));
function T(key,v){const s=DLG.text[key];if(s==null)throw new Error('找不到文字：'+key);return fill(s,v||{});}
function steps(key,v){const d=DLG.say[key];if(!d)throw new Error('找不到對話：'+key);v=v||{};const out=[];
  for(const st of d){
    const sp=(v.__p&&st.p==='shopkeeper')?v.__p:st.p;  /* __p：商店在別的地區時，店員換成該地區的人 */
    if(st.lines){for(const l of st.lines)out.push({p:sp,html:`<p>${fill(l,v)}</p>`});}
    else{const o=Object.assign({},st);o.p=sp;o.html=fill(st.html,v);out.push(o);}}
  return out;}
async function play(key,v){let r;for(const o of steps(key,v))r=await say(o);return r;}
const quizOf=k=>{const z=DLG.quizzes[k];return quiz(k,z.q,z.opts,z.ans,z.explain);};
const missTxt=miss=>miss.map(([k,n])=>ITEMS[k].name+' \u00d7'+(n-kitCount(k))).join('、');

/* ================= 內容資料（從 content/*.json 載入；審核時改 JSON） ================= */
const {ITEMS,MATS,GIFTABLE,LIKES,RECIPES,BENCH_WOOD,MED_FEE,HYPO_AT,EVENTS,STORIES,VICTIMS,RATION_NEED,RATION_SELL,WATER_NEED,RESCUE_FEE,DEBT_LIMIT,RATION_EAT,STASH_CAP,SPRINKLER_AREA,SPRINKLER_SLOTS,FORAGE_SPOTS,FORAGE_N,SHOP_MED,SHOP_EXTRA,WOUNDS,OUTDOOR,WX,WILD_ON,DROWN_CHANCE,SCENARIOS,MERCHANT_GOODS,MAT_UP,KIT_UP,LOAD_OK,LOAD_HEAVY,STA_MAX,COST,GROW_DAYS,RATION_WHEAT,RATION_LIFE,MACHINE_WOOD,MACHINE_COIN,CARDS,REQUESTS,PEOPLE,RATIO,PLOTS,ROCKS}=Object.assign({},C.items,C.balance,C.characters,C.crafting,C.cards,C.quests,C.ratios,C.wounds,C.weather,C.rescue);
const SCENES=compileScenes(C.scenes),SIGNS=compileSigns(C.signs);
/* ================= 地區（綠葉谷＋各章宣告的地區） ================= */
const BASE={id:'base',name:'綠葉谷',pin:[41,44],center:{scene:'village',at:[1045,300]},home:{scene:'home',at:[420,660]}};
const regionOf=sceneId=>{const s=C.scenes[sceneId],c=chOf(sceneId);return (s&&s.region==='base')?BASE:(c&&REGIONS[c])||BASE;};
const curRegion=()=>regionOf(S.scene);
const shopP=()=>curRegion().shopkeeper||'shopkeeper';
const regionList=()=>[BASE].concat(Object.values(REGIONS));
const regionName=id=>(regionList().find(r=>r.id===id)||BASE).name;
const regionOpen=r=>r===BASE||(CHAPTERS[r.chapter]&&CHAPTERS[r.chapter].open&&(!r.unlock||mk(r.unlock)()));
const mapAvail=()=>Object.values(REGIONS).some(regionOpen);
/* ================= 章節掛接點（章節程式提供，沒開放的章節沒有） ================= */
const CHH={};
const hookOf=sceneId=>CHH[chOf(sceneId)]||null;
const chBase=(name,...a)=>{for(const h of Object.values(CHH)){const r=h[name]&&h[name](...a);if(r!==undefined&&r!==null&&r!==false)return r;}};
/* ================= 天氣：由老師發布（D5）或除錯入口排定，沒有隨機；沒有排定時整套不作用 ================= */
const wxToday=()=>S.wx&&S.wx.day===S.day?S.wx.type:null;
const wxTomorrow=()=>S.wxNext&&S.wxNext.day===S.day+1?S.wxNext.type:null;
const wild=()=>WILD_ON||WILD_FORCE;  /* 野外項目（溺水、裝溪水、營火、阿鹿的支線）：內容審過後在 content/weather.json 的 WILD_ON 開啟 */
const storyOf=id=>{const s=STORIES[id];return s&&(!s.draft||wild())?s:null;};  /* draft 的支線在 WILD 開啟前不出現 */
const isOutdoor=id=>{const s=C.scenes[id];return s&&s.outdoor!=null?!!s.outdoor:OUTDOOR.includes(id);};
const stormy=()=>['typhoon','flood'].includes(wxToday())||['typhoon','flood'].includes(wxTomorrow());  /* 船長停航 */
/* 排定「明天」的天災；之後老師端（D5）發布的天災也走這裡 */
function scheduleWx(type){if(!WX[type])throw new Error('沒有這種天災：'+type);S.wxNext={type,day:S.day+1};}
function applyWx(){const t=wxToday(),out=isOutdoor(S.scene),v=$('view');
  v.classList.toggle('rain',(t==='typhoon'||t==='flood')&&out);v.classList.toggle('storm',t==='typhoon'&&out);v.classList.toggle('fog',t==='fog'&&S.scene==='forest');}
const DLG=C.dialogues,GLOBALS=Object.assign({CARDS,ITEMS},C.balance);
function autoWater(){let n=0;(S.spr||[]).map(i=>SPRINKLER_SLOTS[i]).forEach(sl=>sl.plots.forEach(i=>{const p=S.plots[i];if(p&&(p.st==='tilled'||(p.st==='planted'&&p.g<GROW_DAYS))&&!p.wet){p.wet=true;n++;}}));return n;}

/* ================= 狀態 ================= */
let S=null,busy=true;
function newState(){return migrate({v:1,scene:'home',pos:{x:1010,y:690},coins:0,earned:0,matCap:10,matLv:0,kit:[],kitCap:4,kitLv:0,
  step:0,trees:{},chests:{},cards:{},hearts:{grandpa:0,kid:0,wood:0,shopkeeper:0},req:[0,2,1],reqNext:3,started:false,ctrl:'joy',warned:{}});}
function migrate(o){
  if(!o.mat)o.mat={wood:o.wood||0,stone:0,gold:0,wheat:0,seed:0};delete o.wood;
  if(o.day==null)o.day=1;if(o.sta==null)o.sta=STA_MAX;
  o.tools=o.tools||{};o.plots=o.plots||{};o.rocks=o.rocks||{};
  ['flower','scrap','mushroom','pipe','gear'].forEach(k=>{if(o.mat[k]==null)o.mat[k]=0;});
  o.gifted=o.gifted||{};if(!o.spr){o.spr=[];for(let i=0;i<(o.sprinklers||0);i++)o.spr.push(i);}o.f=o.f||{};o.story=o.story||{};o.rescue=o.rescue||{};['hunt','guard','cook','soldier'].forEach(k=>{if(o.hearts[k]==null)o.hearts[k]=0;});o.sprinklers=o.sprinklers||0;o.bin=o.bin||0;if(!o.forage){o.forage={};o.forageDay=0;}
  Object.values(o.trees||{}).forEach(t=>{if(t.regrow&&t.regrow>1e6)t.regrow=o.day+1;});
  if(!Array.isArray(o.stash))o.stash=[];
  Object.entries(PEOPLE).forEach(([k,p])=>{if(p.heart&&o.hearts&&o.hearts[k]==null)o.hearts[k]=0;});  /* 章節角色的好感度（heart:true） */
  o.c=o.c||{};o.wounds=o.wounds||{};if(!o.stashAt)o.stashAt='base';  /* c：各章進度；wounds：看過的傷口圖；stashAt：防災包在哪（base＝爺爺家、地區 id＝該地區住處、carry＝帶在身上） */
  if(!SCENES[o.scene]){o.scene='village';o.pos={x:SCENES.village.spawn[0],y:SCENES.village.spawn[1]};}  /* 存檔所在的章節已關閉或不存在：回村莊 */
  o.v=2;return o;}
function save(){if(window.__loggingOut)return;try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}if(window.FACloud)FACloud.queueSave(S);}
function load(){try{const r=localStorage.getItem(KEY);if(r){const o=JSON.parse(r);if(o&&(o.v===1||o.v===2))return migrate(o);}}catch(e){}return null;}
const $=id=>document.getElementById(id);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const base=k=>k.split('@')[0];
const expiry=k=>+(k.split('@')[1]||0);
const expired=k=>base(k)==='ration'&&S.day>expiry(k);
const kitCount=k=>S.kit.filter(x=>base(x)===k&&!expired(x)).length;
const stashCount=k=>S.stash.filter(x=>base(x)===k&&!expired(x)).length;
const load_=()=>S.kit.reduce((s,k)=>s+ITEMS[base(k)].w,0);
const matUsed=()=>Object.values(S.mat).reduce((a,b)=>a+b,0);
const matFree=()=>S.matCap-matUsed();
function speedMul(){const l=load_();return l>LOAD_HEAVY?.5:l>LOAD_OK?.72:1;}
function badge(k,lg){const it=ITEMS[base(k)];return `<span class="badge ${lg?'lg':''}" style="--c:${it.color};--tc:${it.text||'#1b1b1b'}" aria-hidden="true">${it.ch}</span>`;}
function hearts(id){const n=Math.min(5,S.hearts[id]||0);return '♥'.repeat(n)+'♡'.repeat(5-n);}
function addHeart(id,n){if(id in S.hearts)S.hearts[id]=Math.min(5,S.hearts[id]+n);}
function toast(m){const t=$('toast');t.textContent=m;t.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>t.classList.remove('on'),1800);}
async function useSta(n){
  if(S.sta<=0){S.pendingFaint='work';return false;}
  const before=S.sta;S.sta=Math.max(0,S.sta-n);refresh();
  if(S.sta<=0){S.pendingFaint='work';return true;}
  if(before>=HYPO_AT&&S.sta<HYPO_AT&&S.hypoDay!==S.day){S.hypoDay=S.day;await hypoWarn();}
  return true;}
async function hypoWarn(){
  const has=kitCount('sugar')>0;
  const i=await play(has?'hypo.warnHas':'hypo.warnNone');
  if(has&&i===0){S.kit.splice(S.kit.findIndex(k=>base(k)==='sugar'),1);S.sta=Math.min(STA_MAX,S.sta+30);refresh();
    const isNew=!S.cards.hypo;S.cards.hypo=true;
    await play('hypo.ate',{newTag:isNew?'<p class="good">獲得知識卡</p>':''});}
  else if(!has)await play('hypo.tip');
}
/* 背包裡的方糖：體力低於 HYPO_AT 時隨時可以吃（原本只能在跨過門檻當下的提示裡吃，錯過就只能丟掉） */
async function eatSugar(i){
  if(S.sta>=HYPO_AT){toast('現在體力還夠，方糖先留著');return;}
  S.kit.splice(i,1);S.sta=Math.min(STA_MAX,S.sta+30);refresh();
  const isNew=!S.cards.hypo;S.cards.hypo=true;
  await play('hypo.ate',{newTag:isNew?'<p class="good">獲得知識卡</p>':''});
}
/* 乾糧：沒過期的可以吃，體力 +RATION_EAT（防災包食物本來就要「吃舊換新」）；體力滿時不浪費 */
function eatRation(i){
  if(S.step===9&&kitCount('ration')<=1){toast('這包乾糧要先拿給爺爺看');return;}   // 劇情第 9 步要用第一包乾糧向爺爺報告
  if(S.sta>=STA_MAX){toast('現在還不餓，乾糧先留著');return;}
  S.kit.splice(i,1);S.sta=Math.min(STA_MAX,S.sta+RATION_EAT);toast(`吃了乾糧，體力 +${RATION_EAT}`);
}
async function faint(reason){
  stopInput();
  await play(reason==='mushroom'?'faint.mushroom':'faint.other');
  $('fade').classList.add('on');await sleep(RM?0:800);
  const summary=nextDay();
  const wk=curRegion(),wh=wk.home||BASE.home;
  S.scene=wh.scene;S.pos={x:wh.at[0],y:wh.at[1]};buildScene();S.sta=Math.round(STA_MAX*.6);
  S.coins-=MED_FEE;refresh();$('fade').classList.remove('on');checkpoint();
  if(reason==='exhaust'){
    await say({p:wk===BASE?'grandpa':(wk.shopkeeper||'grandpa'),html:'<p>你終於醒了！你的體力完全耗盡，倒在路邊，是大家把你抬回來的。醫生說你太累了，要好好休息。</p><p class="small">體力不足的時候不要勉強行動，身上可以帶些方糖和開水。</p>'});}
  else if(reason==='mushroom'){
    await play((wk.wake&&wk.wake.mushroom)||'faint.mushroomWake');
    S.cards.mushroom=true;S.cards.faint=true;
    await play('faint.mushroomCards');}
  else{
    await play((wk.wake&&wk.wake.other)||'faint.otherWake');
    S.cards.hypo=true;
    await play('faint.otherCard');}
  await say({icon:'￥',who:'醫療費',html:`<p>醫生的診療費 ${MED_FEE} 金幣。</p>${S.coins<0?`<p class="bad">金幣不夠，先欠著 ${-S.coins} 金幣。還清之前不能在商店買東西。</p>`:`<p>剩下 ${S.coins} 金幣。</p>`}<p class="small">今天是第 ${S.day} 天，體力恢復到 ${S.sta}。</p>`});
  if(summary)await say({icon:'☀',who:`第 ${S.day} 天`,html:summary});
  save();refresh();
}
function matIcon(k,s){const ic=MATS[k].icon;return ic?`<img alt="" src="${A[ic]}" style="width:${s||34}px;height:${s||34}px;object-fit:contain;vertical-align:middle">`:'';}
function matList(){return Object.entries(S.mat).filter(([k,n])=>n>0).map(([k,n])=>`${MATS[k].name} ×${n}`).join('、')||'空的';}

function genForage(){S.forage={};Object.entries(FORAGE_SPOTS).forEach(([sc,spots])=>{
  const pick=spots.slice().sort(()=>Math.random()-.5).slice(0,FORAGE_N[sc]);
  S.forage[sc]=pick.map(([x,y])=>{const r=Math.random();let t=r<.3?'twig':r<.55?'pebble':r<.75?'flower':'scrap';
    if(sc==='forest'&&Math.random()<.35)t='mushroom';return {x,y,t};});});S.forageDay=S.day;}
const PICK={twig:{mat:'wood',txt:'撿到樹枝（木材 +1）',icon:'i_twig'},pebble:{mat:'stone',txt:'撿到小石頭（石頭 +1）',icon:'i_pebble'},flower:{mat:'flower',txt:'摘到一束野花',icon:'i_flower'},scrap:{mat:'scrap',txt:'撿到廢鐵片',icon:'i_scrap'},mushroom:{mat:'mushroom',txt:'採到一朵看起來很好吃的野生菇',icon:'i_mushroom'}};
/* ================= 對話框 ================= */
let dlgResolve=null;
function finish(v){$('dialog').hidden=true;const r=dlgResolve;dlgResolve=null;r&&r(v);}
function say(o){return new Promise(res=>{
  dlgResolve=res;const f=$('dFace');const p=o.p&&PEOPLE[o.p];
  const faceKey=o.p==='hero'?'hero_face':(p?p.face:null);
  if(faceKey){f.style.backgroundImage=`url(${A[faceKey]})`;f.textContent='';}else{f.style.backgroundImage='none';f.textContent=o.icon||'';}
  const nm=o.who||(o.p==='hero'?'你':(p?p.name:''));
  $('dWho').innerHTML=`<span>${nm}</span>`+(p&&o.p in S.hearts?`<span class="hearts" aria-label="好感度 ${S.hearts[o.p]}">${hearts(o.p)}</span>`:'');
  const wUrl=o.wound&&WOUNDS[o.wound]?`assets/w_${o.wound}.webp`:'';
  if(wUrl)S.wounds[o.wound]=true;
  $('dText').innerHTML=(wUrl?`<figure style="margin:0 0 8px;text-align:center"><img alt="${WOUNDS[o.wound]}" src="${wUrl}" style="max-width:100%;max-height:min(230px,34vh);border-radius:12px;border:3px solid #F4E7CC;background:#fff">${o.hideCap?'':`<figcaption class="small">傷口圖：${WOUNDS[o.wound]}</figcaption>`}</figure>`:'')+(o.html||'');
  const bs=$('dBtns');bs.innerHTML='';bs.classList.toggle('many',(o.buttons||[1]).length>3);
  (o.buttons||[{label:'繼續',primary:true}]).forEach((b,i)=>{const el=document.createElement('button');el.type='button';
    el.className='btn'+(b.primary?' primary':'')+(b.danger?' danger':'');el.textContent=b.label;if(b.disabled)el.disabled=true;el.onclick=()=>finish(i);bs.appendChild(el);});
  $('dialog').hidden=false;if(o.onRender)o.onRender($('dText'),finish);
  const fb=bs.querySelector('button:not([disabled])');fb&&fb.focus({preventScroll:true});
});}

/* ================= 場景繪製 ================= */
const plane=$('plane');
let heroEl,heroImg,ringEl,npcEls={},treeEls={},plotEls=[],rockEls=[],machineEl=null,benchEl=null,binEl=null,harvEl=null,sprEls=[],forageEls=[];
function sc(){return SCENES[S.scene];}
function sprite(cls,src,x,y,h,wRatio){const e=document.createElement('div');e.className='ent spr '+cls;
  e.style.setProperty('--x',x);e.style.setProperty('--y',y);e.style.setProperty('--h',h);e.style.setProperty('--w',Math.round(h*wRatio));
  e.style.zIndex=Math.round(y);e.innerHTML=`<img alt="" src="${src||''}">`;plane.appendChild(e);return e;}
function setSprite(e,key,h){e.style.setProperty('--h',h);e.style.setProperty('--w',Math.round(h*RATIO[key]));e.querySelector('img').src=A[key];}
function buildScene(){
  const s=sc();plane.innerHTML='';plane.style.backgroundImage=`url(${A[s.bg]})`;npcEls={};treeEls={};plotEls=[];rockEls=[];machineEl=null;benchEl=null;binEl=null;harvEl=null;sprEls=[];forageEls=[];
  ringEl=document.createElement('div');ringEl.className='ent ring';plane.appendChild(ringEl);
  const H=s.heroH;
  (s.npcs||[]).forEach(n=>{const P=PEOPLE[n.id];const e=sprite('npc shadow',A[P.img],n.x,n.y,Math.round(H*P.hk),RATIO[P.img]);
    if(n.flip)e.querySelector('img').classList.add('flip');
    const tg=document.createElement('div');tg.className='tag';e.appendChild(tg);npcEls[n.id]=e;});
  (s.trees||[]).forEach(t=>{treeEls[t.id]=sprite('tree shadow','',t.x,t.y+6,Math.round(H*1.9),RATIO.tree);});
  if(S.scene==='home'){const b=sprite('','',270,700,290,RATIO.bed);b.querySelector('img').src=A.bed;b.style.zIndex=600;
    const st=sprite('shadow','',1290,700,90,1);st.innerHTML='<span class="badge lg" style="--c:#2F7D4F;--tc:#fff;--s:84px">包</span>';}
  if(s.plots)PLOTS.forEach((p,i)=>{const e=sprite('plot','',p[0],p[1]+95,190,1);e.style.zIndex=Math.round(p[1]);e.hidden=true;plotEls.push(e);});
  if(s.plots){machineEl=sprite('','',300,560,Math.round(H*1.9),RATIO.machine);machineEl.querySelector('img').src=A.machine;}
  if(s.rocks)rocksOf(s).forEach(r=>rockEls.push(sprite('tree','',r[0],r[1]+20,Math.round(H*.95),RATIO.rock)));
  if(s.plots){benchEl=sprite('','',600,300,Math.round(H*1.05),RATIO.bench);benchEl.querySelector('img').src=A.bench;
    binEl=sprite('','',1450,390,Math.round(H*.95),RATIO.bin);binEl.querySelector('img').src=A.bin;
    harvEl=sprite('','',1480,580,Math.round(H*1.25),RATIO.harvester);harvEl.querySelector('img').src=A.harvester;
    sprEls=SPRINKLER_SLOTS.map(p=>{const e=sprite('','',p.x,p.y,Math.round(H*.9),RATIO.sprinkler);e.querySelector('img').src=A.sprinkler;return e;});}
  if(S.forageDay!==S.day)genForage();
  (S.forage[S.scene]||[]).forEach(f=>{const e=sprite('','',f.x,f.y+14,Math.round(H*.34),1);e.querySelector('img').src=A[PICK[f.t].icon];e.querySelector('img').style.filter='drop-shadow(0 0 6px rgba(255,240,170,.95))';forageEls.push(e);});
  {const h=hookOf(S.scene);if(h&&h.build)h.build(S.scene,H,{sprite,npcEls});}
  (SIGNS[S.scene]||[]).forEach(g=>{const e=document.createElement('div');e.className='ent signpost';e.style.transform=`translate(${g.x}px,${g.y}px) translate(-50%,-50%)`;e.textContent=g.t();plane.appendChild(e);});
  snapFree();
  heroEl=sprite('shadow','',S.pos.x,S.pos.y,H,RATIO.hero);heroEl.id='hero';heroImg=heroEl.querySelector('img');heroImg.src=A.hero;
  refresh();fit();
  if(window.FAMusic)FAMusic.scene(S.scene,S);
}
function treeState(t){const st=S.trees[t.id]||{hp:3,regrow:0};if(st.hp<=0&&st.regrow&&S.day>=st.regrow){st.hp=3;st.regrow=0;}S.trees[t.id]=st;return st;}
/* 礦石：序章只有 mine_in（鍵是純數字，維持舊存檔）；章節場景可自帶 rocks 座標與 ore（礦石種類），鍵為 場景_編號 */
const rocksOf=s=>Array.isArray(s.rocks)?s.rocks:ROCKS;const rk=i=>S.scene==='mine_in'?i:S.scene+'_'+i;
function rockState(i){let r=S.rocks[rk(i)];const ore=sc().ore;if(!r||(r.hp<=0&&S.day>=r.regrow)){r={hp:S.tools.pick2?2:3,gold:!ore&&Math.random()<.34,regrow:0};if(ore)r.ore=true;S.rocks[rk(i)]=r;}return r;}
function plotState(i){return S.plots[i]||{st:'wild'};}
function plotKey(p){ /* 對應圖片 */
  if(p.st==='wild')return null;
  if(p.st==='tilled')return p.wet?'soil_wet':'soil_dry';
  if(p.g>=GROW_DAYS)return 'ripe';if(p.g>=2)return 'tall';if(p.g>=1)return 'sprout';return p.wet?'soil_wet':'soil_dry';}
function refresh(){
  const s=sc(),H=s.heroH;
  (s.trees||[]).forEach(t=>{const st=treeState(t),e=treeEls[t.id];const alive=st.hp>0;setSprite(e,alive?'tree':'stump',alive?Math.round(H*1.9):Math.round(H*.62));});
  plotEls.forEach((e,i)=>{const p=plotState(i),k=plotKey(p);e.hidden=!k;if(!k)return;
    const w=270;e.style.setProperty('--w',w);e.style.setProperty('--h',Math.round(w/RATIO[k]));e.querySelector('img').src=A[k];
    let extra='';if(p.st==='planted'&&p.g<GROW_DAYS&&p.wet)extra+='<span class="drop" aria-hidden="true">水</span>';
    if(p.st==='planted'&&p.g===0)extra+='<span class="seeds">已播種</span>';
    e.querySelectorAll('.drop,.seeds').forEach(x=>x.remove());e.insertAdjacentHTML('beforeend',extra);});
  if(machineEl)machineEl.classList.toggle('ghost',!S.machine);
  if(benchEl)benchEl.classList.toggle('ghost',!S.bench);
  if(binEl)binEl.hidden=!S.harvester;if(harvEl)harvEl.hidden=!S.harvester;
  sprEls.forEach((e,i)=>e.hidden=!S.spr.includes(i));
  rockEls.forEach((e,i)=>{const r=rockState(i),o=sc().ore;setSprite(e,r.hp>0?(r.ore&&o?o.img:r.gold?'rock_gold':'rock'):(r.ore&&o?o.rubble:'rubble'),r.hp>0?Math.round(H*.95):Math.round(H*.55));});
  Object.entries(npcEls).forEach(([id,e])=>{e.querySelector('.tag').innerHTML=PEOPLE[id].name+(npcHasNews(id)?'<span class="bang">!</span>':'');});
  $('place').textContent=s.name;$('coins').textContent=S.coins;$('coins').style.color=S.coins<0?'var(--bad)':'';$('day').textContent=S.day;
  $('sta').textContent=S.sta;const sb=$('staBar');sb.style.width=(S.sta/STA_MAX*100)+'%';sb.classList.toggle('low',S.sta<20);
  $('bagInfo').textContent=`${S.kit.length}/${S.kitCap}`;$('cardInfo').textContent=Object.keys(S.cards).length;
  $('joy').hidden=S.ctrl!=='joy';$('dpad').hidden=S.ctrl!=='pad';
  $('btnMap').hidden=!mapAvail();applyWx();
  $('goal').innerHTML='<b>目標</b>'+goalText();
}
function placeHero(){heroEl.style.setProperty('--x',S.pos.x);heroEl.style.setProperty('--y',S.pos.y);heroEl.style.zIndex=Math.round(S.pos.y);}
let scale=1;
function fit(){if($('game').hidden)return;const v=$('view');scale=Math.max(v.clientWidth/MW,v.clientHeight/MH);camera();}
function camera(){const v=$('view'),w=v.clientWidth,h=v.clientHeight;
  let tx=w/2-S.pos.x*scale,ty=h/2-(S.pos.y-sc().heroH*.4)*scale;
  tx=Math.min(0,Math.max(w-MW*scale,tx));ty=Math.min(0,Math.max(h-MH*scale,ty));
  plane.style.transform=`translate(${tx}px,${ty}px) scale(${scale})`;}
window.addEventListener('resize',fit);

/* ================= 劇情 ================= */
function goalText(){const rg=curRegion();if(rg!==BASE&&rg.goal)return mk(rg.goal)();
  {const h=hookOf(S.scene);if(h&&h.goal&&rg!==BASE)return h.goal();}
  if(rg===BASE){const g=chBase('goalBase');if(g)return g;}
  switch(S.step){
  case 5:return T('goal.5',{a:S.flagWoodDone?'✓':'□',b:S.flagKidDone?'✓':'□'});
  case 0:case 1:case 2:case 3:case 4:case 6:case 7:case 8:case 9:return T('goal.'+S.step);
  default:{if(S.coins<0)return T('goal.debt',{debt:-S.coins});
    if(S.f.p3&&!S.f.final){if(S.castleDone)return T('goal.castleDone');if(!S.f.tablet)return T('goal.tablet');if(!S.f.hunter)return T('goal.hunter');if(!S.f.guard)return T('goal.guard');return T('goal.prepare');}
    if(S.step>=10&&!S.f.p3)return T('goal.p3');
    if(!S.bench)return T('goal.bench');
    if(!S.spr.length||!S.harvester)return T('goal.auto');
    return T('goal.done');}}}
function npcHasNews(id){
  {const h=hookOf(S.scene);if(h&&h.news&&regionOf(S.scene)!==BASE)return h.news(id);}
  if(chBase('newsBase',id))return true;
  if(S.event&&S.event.day===S.day&&!S.event.done&&EVENTS.find(e=>e.id===S.event.id).who===id&&S.step>=7)return true;
  if(S.scene==='ruin'&&VICTIMS[id]&&!S.rescue[id])return true;
  if(id==='hunt')return !S.f.hunter;if(id==='guard')return S.scene==='gate'&&!S.f.guard;
  if(storyOf(id)&&S.hearts[id]>=3&&!S.story[id]&&S.step>=7)return true;
  if(id==='grandpa'&&((S.step>=10&&!S.f.p3)||(S.castleDone&&!S.f.final)))return true;
  if(id==='grandpa')return S.step===0||S.step===6||S.step===9&&kitCount('ration')>0;
  if(id==='wood')return S.step===1||(S.step===5&&!S.flagWoodDone);
  if(id==='kid')return S.step===5&&!S.flagKidDone;
  if(id==='shopkeeper')return S.step===2&&S.mat.wood>0;
  return false;}
async function introGrandpa(){
  await play('introGrandpa.welcome');
  await play('introGrandpa.bag',{kitCap:S.kitCap,matCap:S.matCap});
  await play('introGrandpa.go',{ctrlName:S.ctrl==='joy'?'搖桿':'方向鍵'});
  S.cards.legend=true;S.step=1;
}
async function accident(){
  busy=true;
  try{
    await play('accident.opening');
    const i=await play('accident.merchant');
    if(i===0){await play('accident.buy');}
    else{await play('accident.refuse');addHeart('wood',1);}
    await play('accident.after');
    S.cards.bleed=true;S.step=5;
    await play('accident.newContent');
  }finally{busy=false;save();refresh();}
}

/* ================= 互動 ================= */
function interactables(){const s=sc(),L=[];
  (s.npcs||[]).forEach(n=>{if(npcEls[n.id])L.push({kind:'npc',x:n.x,y:n.y,label:n.id==='merchant'?'看看商品':n.id==='shopkeeper'?'購物':'對話',id:n.id});});
  (s.things||[]).forEach(t=>L.push(Object.assign({},t,t.kind==='machine'?{label:S.machine?'使用乾糧製造機':'建造乾糧製造機'}:{})));
  (s.trees||[]).forEach(t=>{const st=treeState(t);if(st.hp>0)L.push({kind:'tree',x:t.x,y:t.y,label:S.axe?'砍樹':'需要斧頭',t});});
  if(s.plots)PLOTS.forEach((p,i)=>{const ps=plotState(i);let label;
    if(ps.st==='wild')label='翻土';else if(ps.st==='tilled')label=ps.wet?'播種':'澆水';
    else label=ps.g>=GROW_DAYS?'收成':(ps.wet?'今天澆過水了':'澆水');
    L.push({kind:'plot',x:p[0],y:p[1]+40,label,i});});
  if(s.rocks)rocksOf(s).forEach((r,i)=>{if(rockState(i).hp>0)L.push({kind:'rock',x:r[0],y:r[1],label:S.tools.pick||S.tools.pick2?'敲礦石':'需要十字鎬',i});});
  if(s.plots&&S.step>=10){L.push({kind:'bench',x:600,y:300,label:S.bench?'使用工作台':'建造工作台'});if(S.harvester)L.push({kind:'bin',x:1450,y:390,label:`收納箱（${S.bin}）`});}
  if(s.plots)(S.spr||[]).forEach(si=>L.push({kind:'spr',x:SPRINKLER_SLOTS[si].x,y:SPRINKLER_SLOTS[si].y,label:'移動灑水器',si}));
  if(S.scene==='river'&&wild())L.push({kind:'riverwater',x:560,y:505,label:'裝溪水'});
  {const h=hookOf(S.scene);if(h&&h.things)L.push(...h.things(S.scene));}
  (S.forage[S.scene]||[]).forEach((f,i)=>L.push({kind:'pick',x:f.x,y:f.y,label:'撿起來',i}));
  return L;}
let near=null;
function updateNear(){const H=sc().heroH;let best=null,bd=H*.95;
  for(const it of interactables()){const d=Math.hypot(it.x-S.pos.x,(it.y-S.pos.y)*1.3);if(d<bd){bd=d;best=it;}}
  near=best;const a=$('act');
  if(best){a.classList.add('ready');a.textContent=best.label;ringEl.classList.add('on');ringEl.style.setProperty('--x',best.x);ringEl.style.setProperty('--y',best.y);ringEl.style.setProperty('--r',Math.round(H*.45));ringEl.style.zIndex=Math.round(best.y)-1;}
  else{a.classList.remove('ready');a.textContent='動作';ringEl.classList.remove('on');}}
async function doAction(){
  if(busy||$('game').hidden||!near)return;
  const it=near;busy=true;stopInput();
  try{
    if(it.kind==='npc')await talk(it.id);
    else if(it.kind==='door')await go(it.to,it.at);
    else if(it.kind==='board')await board();
    else if(it.kind==='tree')await chop(it.t);
    else if(it.kind==='shelf')await shelf();
    else if(it.kind==='oldchest')await oldChest();
    else if(it.kind==='fchest')await forestChest();
    else if(it.kind==='bed')await bed();
    else if(it.kind==='stash')await stashMenu();
    else if(it.kind==='shed')await shed();
    else if(it.kind==='toolbox')await toolbox();
    else if(it.kind==='plot')await farmPlot(it.i);
    else if(it.kind==='rock')await mine(it.i);
    else if(it.kind==='machine')await machine();
    else if(it.kind==='bench')await bench();
    else if(it.kind==='bin')await takeBin();
    else if(it.kind==='pick')await pickUp(it.i);
    else if(it.kind==='tablet')await tablet();
    else if(it.kind==='spr')await moveSpr(it.si);
    else if(it.kind==='well')await well();
    else if(it.kind==='fire')await boil();
    else if(it.kind==='gatedoor')await gateDoor();
    else if(it.kind==='riverwater')await riverWater();
    else if(hookOf(S.scene)&&hookOf(S.scene).acts&&hookOf(S.scene).acts[it.kind])await hookOf(S.scene).acts[it.kind](it);
    if(S.pendingFaint){const r=S.pendingFaint;S.pendingFaint=null;await faint(r);}
  }catch(e){if(!e||!e.rescueAbort)throw e;}  /* 救援失敗：整段流程到此結束 */
  finally{busy=false;save();refresh();updateNear();}
}
async function go(to,at){
  if(typeof to==='function')to=to();
  if(!SCENES[to]){console.error('找不到場景：'+to);to='village';at=SCENES.village.spawn;}
  $('fade').classList.add('on');await sleep(RM?0:280);
  S.scene=to;S.pos={x:at[0],y:at[1]};buildScene();save();
  await sleep(RM?0:60);$('fade').classList.remove('on');
  if(to==='forest'&&S.step===3&&(S.earned>=60||S.matLv+S.kitLv>0))S.step=4;
  if(to==='forest'&&S.step===4){await sleep(RM?0:300);await accident();}
  await wxEnter();
  if(S.pendingFaint&&!go._f){const r=S.pendingFaint;S.pendingFaint=null;go._f=true;try{await faint(r);}finally{go._f=false;}}
}
function hit(e){e.classList.remove('hit');void e.offsetWidth;e.classList.add('hit');}
async function chop(t){
  if(!S.axe){await say({p:'hero',html:'<p>徒手沒辦法砍樹。先去找樵夫阿木借斧頭吧。</p>'});return;}
  if(matFree()<=0){await say({p:'hero',html:`<p class="warn">素材袋已經滿了（${S.matCap} 格）。</p><p>先把素材賣掉，或到雜貨店擴充素材袋。</p>`});return;}
  if(!await useSta(COST.chop))return;
  const st=treeState(t);hit(treeEls[t.id]);st.hp--;
  if(st.hp>0){toast(`砍！再 ${st.hp} 下`);await sleep(RM?0:160);return;}
  const got=Math.min(3,matFree());S.mat.wood+=got;st.regrow=S.day+1;
  toast(`獲得木材 ×${got}（素材袋 ${matUsed()}/${S.matCap}）`);
  if(S.step===2&&S.mat.wood>=3&&!S.warned.sellHint){S.warned.sellHint=true;await say({p:'hero',html:'<p>收集到木材了。拿去村子的雜貨店賣賣看吧。</p><p class="small">樹木砍倒後，隔天會重新長出來。</p>'});}
}
async function mine(i){
  if(!S.tools.pick&&!S.tools.pick2){await say({p:'hero',html:'<p>沒有十字鎬敲不動。礦坑入口的工具箱裡也許有。</p>'});return;}
  if(matFree()<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
  if(!await useSta(COST.mine))return;
  const r=rockState(i);hit(rockEls[i]);r.hp--;
  if(r.hp>0){toast(`敲！再 ${r.hp} 下`);await sleep(RM?0:160);return;}
  r.regrow=S.day+1;let msg='';
  const o=sc().ore;if(r.ore&&o&&matFree()>0){S.mat[o.mat]=(S.mat[o.mat]||0)+1;msg=o.txt;}
  if(r.gold&&matFree()>0){S.mat.gold++;msg='金礦 ×1';}
  const s=Math.min(2,matFree());if(s>0){S.mat.stone+=s;msg+=(msg?'、':'')+`石頭 ×${s}`;}
  toast(`獲得 ${msg||'（素材袋滿了）'}`);
}
async function farmPlot(i){
  if(!S.tools.hoe){await say({p:'hero',html:'<p>沒有農具。先到農田旁邊的工具棚看看。</p>'});return;}
  const p=Object.assign({st:'wild'},S.plots[i]);
  if(p.st==='wild'){if(!await useSta(COST.till))return;p.st='tilled';p.wet=false;toast('翻好土了');}
  else if(p.st==='tilled'&&!p.wet){if(!await useSta(COST.water))return;p.wet=true;toast('澆水完成');}
  else if(p.st==='tilled'&&p.wet){if(S.mat.seed<1){await say({p:'hero',html:'<p>沒有種子。到雜貨店買小麥種子吧。</p>'});return;}
    if(!await useSta(COST.plant))return;S.mat.seed--;p.st='planted';p.g=0;if(S.step===7)S.step=8;toast(`播種完成，再 ${GROW_DAYS} 天成熟（每天都要澆水）`);}
  else if(p.st==='planted'&&p.g>=GROW_DAYS){const n=Math.min(3,matFree());if(n<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
    S.mat.wheat+=n;p.st='tilled';p.wet=false;p.g=0;toast(`收成小麥 ×${n}`);}
  else if(p.st==='planted'&&!p.wet){if(!await useSta(COST.water))return;p.wet=true;toast('澆水完成');}
  else{toast('今天已經澆過水了');}
  S.plots[i]=p;autoWater();
}
async function shed(){
  if(S.tools.hoe){await say({p:'hero',html:'<p>工具棚裡整齊地掛著爺爺的舊農具。</p>'});return;}
  S.tools.hoe=true;S.tools.can=true;
  await say({p:'hero',html:'<p>工具棚裡有爺爺年輕時用的鋤頭和澆水壺。</p><p class="good">獲得：鋤頭、澆水壺</p><p class="small">種田的步驟：翻土 → 澆水 → 播種（種子在雜貨店買），之後每天澆水，3 天就能收成。</p>'});
}
async function toolbox(){
  if(S.tools.pick){await say({p:'hero',html:'<p>工具箱裡只剩一些生鏽的釘子。</p>'});return;}
  S.tools.pick=true;
  await say({p:'hero',html:'<p>工具箱裡有一把礦工留下的舊十字鎬，還能用。</p><p class="good">獲得：十字鎬</p><p class="small">礦坑裡的石頭敲三下就會碎，閃著金光的是金礦，可以賣到好價錢。</p>'});
}
async function machine(){
  if(!S.machine){
    const ok=S.mat.wood>=MACHINE_WOOD&&S.coins>=MACHINE_COIN;
    const i=await say({p:'hero',who:'乾糧製造機（建造）',html:`<p>爺爺說，把收成的小麥放進這台機器，就能做成免烹煮、耐保存的乾糧。</p><p>需要：木材 ×${MACHINE_WOOD}（有 ${S.mat.wood}）、金幣 ${MACHINE_COIN}（有 ${S.coins}）</p>`,
      buttons:[{label:ok?'建造':'材料不足',primary:true,disabled:!ok},{label:'離開'}]});
    if(i!==0)return;S.mat.wood-=MACHINE_WOOD;S.coins-=MACHINE_COIN;S.machine=true;if(S.step>=7&&S.step<9)S.step=9;
    await say({icon:'★',who:'建造完成',html:'<p>乾糧製造機完成了！</p><p class="small">放入 3 份小麥，就能做出 1 包乾糧。</p>'});return;}
  const ok=S.mat.wheat>=RATION_WHEAT,full=S.kit.length>=S.kitCap;
  const i=await say({p:'hero',who:'乾糧製造機',html:`<p>放入小麥 ×${RATION_WHEAT}，做出 1 包乾糧，會直接放進急救背包。</p><p>小麥：${S.mat.wheat}　急救背包：${S.kit.length}/${S.kitCap}</p><p class="small">乾糧做好後 ${RATION_LIFE} 天內有效。</p>`,
    buttons:[{label:!ok?'小麥不足':full?'急救背包已滿':'製作乾糧',primary:true,disabled:!ok||full},{label:'離開'}]});
  if(i!==0)return;S.mat.wheat-=RATION_WHEAT;S.kit.push('ration@'+(S.day+RATION_LIFE));
  toast(`做好乾糧！保存到第 ${S.day+RATION_LIFE} 天`);
}
async function bed(){
  const i=await say({p:'hero',who:'床',html:`<p>要睡覺進入下一天嗎？</p><p class="small">體力會恢復，作物會成長（前提是今天有澆水），委託板也會換新。</p>`,buttons:[{label:'睡覺',primary:true},{label:'還不想睡'}]});
  if(i!==0)return;
  $('fade').classList.add('on');await sleep(RM?0:500);
  const html=nextDay();S.sta=STA_MAX;refresh();$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>早安！體力恢復了。</p>'+html});
}
function nextDay(){
  S.day++;let grown=0,dry=0,wxMsg='';
  if(S.wxNext&&S.wxNext.day===S.day){S.wx=S.wxNext;S.wxNext=null;wxMsg+=`<p class="bad">今天${WX[S.wx.type].name}來襲！</p>`;S.wxHit={};}
  if(S.wxNext&&S.wxNext.day===S.day+1)wxMsg+=`<p class="warn">天氣預報：${WX[S.wxNext.type].fore}</p>`;
  Object.values(S.plots).forEach(p=>{if(p.st==='planted'&&p.g<GROW_DAYS){if(p.wet){p.g++;grown++;}else dry++;}p.wet=false;});
  S.req=S.req.map(()=>nextReq());
  let auto=0,harv=0;
  if(S.harvester)Object.values(S.plots).forEach(p=>{if(p.st==='planted'&&p.g>=GROW_DAYS){S.bin+=3;harv+=3;p.st='tilled';p.g=0;}});
  auto=autoWater();
  genForage();
  let evMsg='';
  if(S.event&&!S.event.done&&S.event.day===S.day-1){const ev=EVENTS.find(e=>e.id===S.event.id);evMsg=`<p class="small">昨天${PEOPLE[ev.who].name}的傷，後來自己去看了醫生。</p>`;}
  S.event=null;
  if(S.step>=7&&Math.random()<.6){const pool=EVENTS.filter(e=>!e.after||S.cards[e.after]);const ev=pool[Math.floor(Math.random()*pool.length)];S.event={id:ev.id,day:S.day};evMsg+=`<p class="warn">聽說${PEOPLE[ev.who].name}好像出了點小意外……</p>`;}
  if(S.quake&&S.castleDone){S.quake=false;evMsg+='<p class="small">落石之城修復完成了。</p>';}
  const exp=S.kit.filter(k=>base(k)==='ration'&&expiry(k)===S.day-1).length,expS=S.stash.filter(k=>base(k)==='ration'&&expiry(k)===S.day-1).length;
  return `${wxMsg}${grown?`<p>有 ${grown} 塊田的小麥長大了。</p>`:''}${dry?`<p class="warn">有 ${dry} 塊田昨天沒澆水，所以沒有長大。</p>`:''}${exp?`<p class="bad">背包裡有 ${exp} 包乾糧過期了，已經不能吃。</p>`:''}${expS?`<p class="bad">家裡的防災包有 ${expS} 包乾糧過期了，已經不能吃。</p>`:''}${auto?`<p>自動灑水器幫 ${auto} 塊田澆好水了。</p>`:''}${harv?`<p>自動收割機收了小麥 ×${harv}，放在收納箱裡。</p>`:''}${evMsg}<p class="small">委託板有新的工作，路邊也出現了新的東西可以撿。</p>`;
}
async function pickUp(i){
  const f=S.forage[S.scene][i],P=PICK[f.t];
  if(matFree()<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
  S.mat[P.mat]++;S.forage[S.scene].splice(i,1);buildScene();toast(P.txt);
  if(f.t==='mushroom'&&!S.warned.mush){S.warned.mush=true;await say({p:'hero',html:'<p>這朵菇顏色好漂亮，聞起來也很香……</p><p class="small">放進素材袋了。要怎麼處理呢？</p>'});}
}
async function bench(){
  if(!S.bench){const ok=S.mat.wood>=BENCH_WOOD;
    const i=await say({p:'hero',who:'工作台（建造）',html:`<p>有了工作台，就能用材料製作自動化機器。</p><p>需要：木材 ×${BENCH_WOOD}（有 ${S.mat.wood}）</p>`,buttons:[{label:ok?'建造':'木材不足',primary:true,disabled:!ok},{label:'離開'}]});
    if(i!==0)return;S.mat.wood-=BENCH_WOOD;S.bench=true;toast('工作台完成！');return;}
  for(;;){let pick=null;
    const html=Object.entries(RECIPES).map(([k,r])=>{const have=k==='sprinkler'?S.spr.length:(S.harvester?1:0);const done=have>=r.max;
      const ok=!done&&Object.entries(r.need).every(([m,n])=>S.mat[m]>=n);
      const need=Object.entries(r.need).map(([m,n])=>`${matIcon(m,24)}${MATS[m].name} ${S.mat[m]}/${n}`).join('　');
      return `<div class="row"><img alt="" src="${A[k]}" style="width:64px;height:48px;object-fit:contain"><div class="info"><b>${r.name}（已有 ${have}/${r.max}）</b><span>${r.desc}</span><span>${need}</span></div><button type="button" data-k="${k}" ${ok?'':'disabled'}>${done?'已達上限':'製作'}</button></div>`;}).join('');
    const r=await say({p:'hero',who:'工作台',html:html+'<p class="small">銅管、齒輪可以在雜貨店買；廢鐵片可以在路邊撿到。</p>',buttons:[{label:'離開',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-k]').forEach(b=>b.onclick=()=>{pick=b.dataset.k;fin('pick');})});
    if(r!=='pick')break;
    Object.entries(RECIPES[pick].need).forEach(([m,n])=>S.mat[m]-=n);
    if(pick==='sprinkler'){const si=await pickSlot('要把新的灑水器裝在哪裡？');S.spr.push(si);S.sprinklers=S.spr.length;const n=autoWater();refresh();await say({p:'hero',who:'自動灑水器',html:`<p>自動灑水器裝好了，負責<b>${SPRINKLER_AREA[si]}</b>。</p><p>範圍內翻好土或種了小麥的田，會一直保持濕潤${n?`（剛剛已經幫 ${n} 塊田澆好水）`:''}。</p><p class="small">還沒翻土的田不會澆。</p>`});}else S.harvester=true;
    refresh();toast(`${RECIPES[pick].name}完成！`);}
}
async function takeBin(){
  if(!S.bin){await say({p:'hero',html:'<p>收納箱是空的。自動收割機每天早上會把成熟的小麥收進來。</p>'});return;}
  const n=Math.min(S.bin,matFree());if(n<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
  S.bin-=n;S.mat.wheat+=n;toast(`從收納箱拿出小麥 ×${n}${S.bin?`（還剩 ${S.bin}）`:''}`);
}
async function eatMushroom(){
  if(Math.random()<.5){S.mat.mushroom--;S.pendingFaint=null;await faint('mushroom');return;}
  S.mat.mushroom--;S.sta=0;refresh();
  await play('eatMushroom');
  S.cards.mushroom=true;
}
async function gift(id){
  if(S.gifted[id]===S.day){await say({p:id,html:'<p>今天已經收過你的禮物了，明天再來聊吧！</p>'});return;}
  const opts=GIFTABLE.filter(k=>S.mat[k]>0);
  if(!opts.length){await say({p:'hero',html:'<p>素材袋裡沒有可以送的東西。野花、小麥、木材、石頭、金礦都可以當禮物。</p>'});return;}
  let pick=null;
  const html=opts.map(k=>`<div class="row">${matIcon(k)}<div class="info"><b>${MATS[k].name}</b><span>有 ${S.mat[k]} 份</span></div><button type="button" data-k="${k}">送這個</button></div>`).join('');
  const r=await say({p:id,who:`送禮給${PEOPLE[id].name}`,html,buttons:[{label:'算了',primary:true}],onRender:(root,fin)=>root.querySelectorAll('button[data-k]').forEach(b=>b.onclick=()=>{pick=b.dataset.k;fin('pick');})});
  if(r!=='pick')return;
  const L=LIKES[id]||{};
  if(pick==='mushroom'){
    await say({p:id,html:`<p>野生菇？這可不能亂吃，也不能亂送人啊！</p><p>${CARDS.mushroom.text}</p><p class="good">獲得知識卡：${CARDS.mushroom.title}</p>`});
    S.cards.mushroom=true;S.mat.mushroom--;return;}
  S.mat[pick]--;S.gifted[id]=S.day;
  if(pick===L.love){addHeart(id,2);await say({p:id,html:`<p>${L.loveTxt}</p><p class="good">好感度大幅提升！</p>`});}
  else if(pick===L.hate){await say({p:id,html:`<p>${L.hateTxt}</p><p class="small">好像不太喜歡……</p>`});}
  else{addHeart(id,1);await say({p:id,html:`<p>${L.normTxt||'謝謝你！'}</p>`});}
}
async function chatMenu(id,text){
  const st=storyOf(id);
  if(st&&S.hearts[id]>=3&&!S.story[id]&&S.step>=7){
    for(const t of st.text)await say({p:id,html:`<p>${t}</p>`});
    const c=CARDS[st.card];S.cards[st.card]=true;S.story[id]=true;
    await say({p:id,html:`<div class="card"><b>${c.title}</b><p>${c.text}</p></div><p class="good">獲得知識卡：${c.title}</p>`});return;}
  const canGift=S.step>=7;
  const i=await say({p:id,html:`<p>${text}</p>`,buttons:canGift?[{label:'送禮',primary:true},{label:'再見'}]:[{label:'再見',primary:true}]});
  if(canGift&&i===0)await gift(id);
}
async function pickSlot(title,exclude){
  const free=SPRINKLER_SLOTS.map((_,i)=>i).filter(i=>!S.spr.includes(i)&&i!==exclude);
  if(free.length<=1)return free[0];
  let pick=null;
  await say({p:'hero',who:'選擇位置',html:`<p>${title}</p>`+free.map(i=>`<div class="row"><div class="info"><b>${SPRINKLER_AREA[i]}</b></div><button type="button" data-s="${i}">裝在這裡</button></div>`).join(''),buttons:[],
    onRender:(root,fin)=>root.querySelectorAll('button[data-s]').forEach(b=>b.onclick=()=>{pick=+b.dataset.s;fin('p');})});
  return pick;}
async function moveSpr(si){
  const free=SPRINKLER_SLOTS.map((_,i)=>i).filter(i=>!S.spr.includes(i));
  if(!free.length){await say({p:'hero',who:'自動灑水器',html:`<p>這台灑水器負責<b>${SPRINKLER_AREA[si]}</b>。</p><p class="small">三個位置都已經裝了灑水器，沒有空位可以移動。</p>`});return;}
  let pick=null;
  const r=await say({p:'hero',who:'移動灑水器',html:`<p>這台灑水器目前負責<b>${SPRINKLER_AREA[si]}</b>。要移到哪裡？</p>`+free.map(i=>`<div class="row"><div class="info"><b>${SPRINKLER_AREA[i]}</b></div><button type="button" data-s="${i}">移到這裡</button></div>`).join(''),buttons:[{label:'不移動',primary:true}],
    onRender:(root,fin)=>root.querySelectorAll('button[data-s]').forEach(b=>b.onclick=()=>{pick=+b.dataset.s;fin('p');})});
  if(r!=='p')return;
  S.spr=S.spr.map(x=>x===si?pick:x);const n=autoWater();refresh();toast(`灑水器移到${SPRINKLER_AREA[pick]}${n?`，澆了 ${n} 塊田`:''}`);
}
async function well(){
  const first=!S.cards.water;
  const i=await say({p:'hero',who:'水井',html:`<p>清涼的井水，看起來很清澈。</p><p class="small">素材袋 ${matUsed()}/${S.matCap}　井水 ${S.mat.rawwater||0} 份</p>`,
    buttons:[{label:'打一桶井水（體力 2）',primary:true,disabled:matFree()<=0},{label:'直接喝一口'},{label:'離開'}]});
  if(i===0){if(!await useSta(2))return;S.mat.rawwater=(S.mat.rawwater||0)+1;toast('打了一桶井水');
    if(first){S.cards.water=true;await play('well.first');}}
  else if(i===1){
    if(Math.random()<.5){S.sta=Math.max(0,S.sta-15);refresh();await play('well.sick');if(S.sta<=0)S.pendingFaint='work';}
    else await play('well.ok');
    S.cards.water=true;await play('well.scold');}
}
async function boil(){
  const raw=S.mat.rawwater||0,space=S.kitCap-S.kit.length;
  if(!raw){await say({p:'hero',who:'爐火',html:'<p>暖暖的爐火。可以把打回來的井水煮沸，變成乾淨的開水。</p><p class="small">水井在村子廣場和農田。</p>'});return;}
  const n=Math.min(raw,space);
  const i=await say({p:'hero',who:'用爐火煮水',html:`<p>把井水煮沸、放涼，就是可以喝、也可以沖洗傷口的開水，會放進急救背包。</p><p>井水 ${raw} 份　急救背包空位 ${space} 格</p>`,
    buttons:[{label:n?`煮 ${n} 份`:'急救背包已滿',primary:true,disabled:!n},{label:'離開'}]});
  if(i!==0)return;S.mat.rawwater-=n;for(let k=0;k<n;k++)S.kit.push('water');S.cards.water=true;toast(`煮好開水 ×${n}`);
}
async function tablet(){
  const c=CARDS.fracture,isNew=!S.cards.fracture;S.cards.fracture=true;S.f.tablet=true;
  await play('tablet',{newTag:isNew?`<p class="good">獲得知識卡：${c.title}</p>`:''});
}
async function hunter(){
  if(!S.f.hunter){
    const needs={ice:1,elastic:1};
    await play('hunter.hello');
    const miss=needCheck(needs);
    if(miss.length){await play('hunter.missing',{need:needTxt(needs),missing:missTxt(miss)});return;}
    await quizOf('hunt');
    takeKit(needs);S.f.hunter=true;S.coins+=30;S.earned+=30;addHeart('hunt',2);S.cards.sprain=true;
    await play('hunter.thanks');return;}
  return chatMenu('hunt',T('chat.hunt'));
}
async function guardTalk(){
  if(S.scene==='gate'&&!S.f.guard){
    await play('guard.warn');
    S.f.guard=true;return;}
  return chatMenu('guard',T('chat.guard'));
}
function quakeFx(){if(RM)return;$('game').classList.add('quake');setTimeout(()=>$('game').classList.remove('quake'),900);}
async function gateDoor(){
  if(!S.f.guard){await play('guard.wait');return;}
  const valid=S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length;
  const first=!S.castleDone;
  const i=await say({p:'hero',who:first?'落石之城':'再次挑戰落石之城',html:`<p>${T(first?'gate.first':'gate.again')}</p>
    <p>急救背包：${S.kit.length}/${S.kitCap}　有效乾糧：${valid} 包　開水：${kitCount('water')} 瓶</p><p>家中防災包：有效乾糧 ${stashCount('ration')} 包　開水 ${stashCount('water')} 瓶</p><p class="small">${T('stash.gateHint')}</p><p class="small">背包裡的東西在救援中用掉就沒了，確定準備好了嗎？</p>`,buttons:[{label:'進入城堡',primary:true},{label:'再準備一下'}]});
  if(i!==0)return;
  quakeFx();await play('quake.rumble');
  await play('quake.after');
  S.quake=true;S.rescue={};S.rescueMiss={};S.fakesAtStart=[...new Set(S.kit.filter(k=>ITEMS[base(k)].fake).map(base))];S.expiredAtStart=S.kit.filter(expired).length;
  await go('ruin',[838,880]);quakeFx();
}
async function victim(id){
  const v=VICTIMS[id];
  if(S.rescue[id]){await say({p:id,html:`<p>${S.rescue[id]==='ok'?v.ok:'……謝謝你，你已經盡力了。'}</p>`});return;}
  const miss=needCheck(v.needs);
  if(miss.length){
    await say({p:id,wound:v.wound,html:`<p>${v.situ}</p><p>處理這個傷需要：${needTxt(v.needs)}</p><p class="bad">背包裡缺少：${miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k))).join('、')}</p><p>你沒辦法好好處理這個傷……</p>`});
    S.rescue[id]='missing';S.rescueMiss[id]=miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k)));}
  else{
    await say({p:id,wound:v.wound,html:`<p>${v.situ}</p><p class="small">使用：${needTxt(v.needs)}</p>`,buttons:[{label:'拿出用品處理',primary:true}]});
    takeKit(v.needs);
    const i=await say({p:id,html:`<p class="q">${v.q}</p>`,buttons:v.opts.map(o=>({label:o}))});
    const ok=i===v.ans;
    await say({p:id,html:`<p class="${ok?'good':'bad'}">${ok?'處置正確！':'這個做法不對。'}</p><p>${v.explain}</p>`});
    S.rescue[id]=ok?'ok':'wrong';if(ok)addHeart(id,2);}
  refresh();
  if(Object.keys(VICTIMS).every(k=>S.rescue[k]))await rationPhase();
}
async function rationPhase(){
  await play('rations.intro');
  const valid=S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length;
  let ok=false;
  if(valid>=RATION_NEED){for(let n=0;n<RATION_NEED;n++)S.kit.splice(S.kit.findIndex(k=>base(k)==='ration'&&!expired(k)),1);ok=true;
    await play('rations.ok');}
  else await play('rations.short',{valid,expiredNote:S.expiredAtStart?`（另外有 ${S.expiredAtStart} 包已經過期）`:''});
  if(!ok&&stashCount('ration')>0)await say({p:'hero',html:`<p>${T('stash.left')}</p>`});
  S.rescue.rations=ok?'ok':'missing';
  await play('water.intro');
  const w=kitCount('water');
  if(w>=WATER_NEED){for(let n=0;n<WATER_NEED;n++)S.kit.splice(S.kit.findIndex(k=>base(k)==='water'),1);S.rescue.water='ok';
    await play('water.ok');}
  else{S.rescue.water='missing';await play('water.short',{w});if(stashCount('water')>0)await say({p:'hero',html:`<p>${T('stash.left')}</p>`});}
  const stars=['guard','cook','soldier','rations','water'].filter(k=>S.rescue[k]==='ok').length;
  S.castleDone=true;S.castleBest=Math.max(S.castleBest||0,stars);refresh();
  await castleReport(stars);
}
async function castleReport(stars){
  if(window.FAMusic){FAMusic.jingle();FAMusic.scene(S.scene,S);}
  const name={guard:'城堡守衛（頭皮出血）',cook:'廚娘（疑似前臂骨折）',soldier:'見習小兵（腳踝扭傷）'};
  const col=r=>r==='ok'?'var(--ok)':r==='wrong'?'var(--warn)':'var(--bad)';
  const rows=Object.keys(name).map(k=>{const r=S.rescue[k];return `<div class="row"><div class="info"><b>${name[k]}</b><span style="color:${col(r)}">${r==='ok'?'救援成功':r==='wrong'?'有用品，但處置方式有誤':'缺少 '+(S.rescueMiss[k]||[]).join('、')}</span></div></div>`;}).join('')+
    `<div class="row"><div class="info"><b>三天份的乾糧</b><span style="color:${col(S.rescue.rations)}">${S.rescue.rations==='ok'?'準備充足':'不足'}</span></div></div><div class="row"><div class="info"><b>三天份的飲用水</b><span style="color:${col(S.rescue.water)}">${S.rescue.water==='ok'?'準備充足':'不足'}</span></div></div>`;
  const fk=S.fakesAtStart||[];
  const fakeHtml=fk.length?`<h4>你帶進城的偏方</h4>${fk.map(k=>`<div class="card"><b>${ITEMS[k].name}</b><p>${ITEMS[k].truth}</p></div>`).join('')}`:'<p class="good">你沒有把任何偏方帶進城。</p>';
  await say({p:'hero',who:'救援報告',html:`<div style="font-size:40px;color:var(--gold);letter-spacing:.1em">${'★'.repeat(stars)}${'☆'.repeat(5-stars)}</div>${rows}${fakeHtml}${S.expiredAtStart?`<p class="warn">背包裡有 ${S.expiredAtStart} 包過期的乾糧，要記得定期檢查。</p>`:''}<p class="small">最佳紀錄：${S.castleBest} 顆星。睡一覺之後城堡會修好，可以再挑戰一次。</p>`,buttons:[{label:'完成',primary:true}]});
}
async function doEvent(ev){
  await say({p:ev.who,wound:ev.wound,html:`<p>${ev.intro}</p>`});
  const miss=needCheck(ev.needs);
  if(miss.length){
    // 受傷的是雜貨店老闆娘時，賣急救用品的就是她：缺用品要能直接買，否則找她說話永遠進事件、打不開商店
    const shop=ev.who==='shopkeeper';
    const i=await say({p:ev.who,html:`<p>需要：${needTxt(ev.needs)}</p><p class="warn">你的背包還缺：${miss.map(([k,n])=>ITEMS[k].name+' ×'+(n-kitCount(k))).join('、')}</p><p class="small">今天之內帶用品回來還來得及。急救背包要隨時備著喔。</p>`,
      buttons:shop?[{label:'到櫃檯買急救用品',primary:true},{label:'離開'}]:undefined});
    if(shop&&i===0)await shopMenu();
    return;}
  for(const q of ev.qs)await quiz(ev.who,q.q,q.opts,q.ans,q.explain,q.wound);
  takeKit(ev.needs);S.event.done=true;S.coins+=20;S.earned+=20;addHeart(ev.who,1);
  const isNew=!S.cards[ev.id];S.cards[ev.id]=true;
  await say({p:ev.who,html:`<p>${ev.thanks}</p><p class="good">獲得 20 金幣${isNew?`、知識卡：${CARDS[ev.id].title}`:''}</p>`});
}
async function forestChest(){
  if(S.chests.f1){await say({p:'hero',html:'<p>寶箱已經空了。</p>'});return;}
  S.chests.f1=true;S.coins+=30;S.earned+=30;
  await say({icon:'◆',who:'打開寶箱',html:'<p>寶箱裡有一個舊錢袋。</p><p class="good">獲得 30 金幣</p>'});
}
async function oldChest(){
  if(S.chests.home){await say({p:'hero',html:'<p>爺爺的舊箱子，裡面放著褪色的騎士團制服。</p>'});return;}
  S.chests.home=true;S.coins+=20;S.earned+=20;
  await say({p:'grandpa',html:'<p>那是爺爺的舊箱子。裡面的零錢你拿去用吧。</p><p class="good">獲得 20 金幣</p>'});
}
async function shelf(){
  const books=[['legend',true],['bleed',S.step>=5],['scrape',S.step>=5],['food',S.step>=10]];
  const html=books.map(([k,ok])=>ok?`<div class="card"><b>${CARDS[k].title}</b><p>${CARDS[k].text}</p></div>`:'').join('');
  books.forEach(([k,ok])=>{if(ok)S.cards[k]=true;});
  await say({icon:'書',who:'爺爺的書架',html:html+(S.step<10?'<p class="small">其他書的字跡太模糊了，也許之後爺爺會幫你翻出來。</p>':''),buttons:[{label:'闔上書',primary:true}]});
}

/* 委託板 */
function nextReq(){const pool=REQUESTS.map((r,i)=>i).filter(i=>!REQUESTS[i].p2||S.step>=7);
  let r;do{r=pool[S.reqNext%pool.length];S.reqNext++;}while(S.req.includes(r)&&pool.length>3);return r;}
async function board(){
  for(;;){
    let pick=-1;
    const rows=S.req.map((ri,i)=>{const r=REQUESTS[ri];const ok=S.mat[r.item]>=r.n;
      return `<div class="row"><div class="info"><b>${r.who}：${r.text}</b><span>交付${MATS[r.item].name} ×${r.n}　報酬 ${r.pay} 金幣＋好感度</span></div><button type="button" data-i="${i}" ${ok?'':'disabled'}>${ok?'交付':'數量不足'}</button></div>`;}).join('');
    const r=await say({icon:'板',who:'委託板',html:`${rows}<p class="small">素材袋：${matList()}</p>`,buttons:[{label:'離開',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-i]').forEach(b=>b.onclick=()=>{pick=+b.dataset.i;fin('pick');})});
    if(r!=='pick')break;
    const q=REQUESTS[S.req[pick]];S.mat[q.item]-=q.n;S.coins+=q.pay;S.earned+=q.pay;addHeart(q.from,1);
    S.req[pick]=nextReq();toast(`完成委託！獲得 ${q.pay} 金幣`);refresh();
  }
}

/* 商店 */
async function shopMenu(){
  let msg='',keepScroll=0;
  if(S.step===2&&!S.warned.firstSell){S.warned.firstSell=true;
    await play('shop.firstSell',{__p:shopP()});
    if(!S.mat.wood)return;}
  for(;;){
    let pick=null;
    const matNext=MAT_UP[S.matLv],kitNext=KIT_UP[S.kitLv];
    const full0=S.kit.length>=S.kitCap;
    const debt=S.coins<0?`<p class="bad">你還欠醫療費 ${-S.coins} 金幣。急救用品可以先賒帳（欠款最多到 ${DEBT_LIMIT} 金幣），其他東西還清之前不能買，但可以賣素材。</p>`:'';
    let html=(msg?`<p class="good" style="position:sticky;top:-18px;z-index:2;background:#1d3a2a;border:1.5px solid var(--ok);border-radius:10px;padding:8px 12px;margin-top:0">${msg}</p>`:'')+`<p class="small">金幣 <b style="color:var(--gold)">${S.coins}</b>　急救背包 <b style="color:${full0?'var(--bad)':'var(--gold)'}">${S.kit.length}/${S.kitCap}</b>${full0?'（已滿，可以擴充背包，或打開背包丟掉用不到的東西）':''}　素材袋 ${matUsed()}/${S.matCap}</p>`+debt+'<h4>賣出素材</h4>'+['wood','stone','gold','wheat','flower','scrap'].filter(k=>k==='wood'||S.step>=7).map(k=>`<div class="row"><div class="info"><b>${MATS[k].name}</b><span>一份 ${MATS[k].sell} 金幣，素材袋裡有 ${S.mat[k]} 份</span></div><button type="button" data-a="sell:${k}" ${S.mat[k]?'':'disabled'}>全部賣出</button></div>`).join('');
    if(S.step>=7)html+=`<h4>種子</h4><div class="row"><div class="info"><b>小麥種子</b><span>${MATS.seed.buy} 金幣一包，放進素材袋；一包種一塊田</span></div><button type="button" data-a="seed" ${S.coins>=MATS.seed.buy&&matFree()>0?'':'disabled'}>購買</button></div>`;
    {const good=S.kit.filter(k=>base(k)==='ration'&&!expired(k)).length,bad=S.kit.filter(expired).length;
     if(S.step>=7&&(good||bad))html+=`<div class="row">${badge('ration')}<div class="info"><b>乾糧</b><span>一包 ${RATION_SELL} 金幣，急救背包裡有 ${good} 包${bad?`（另有 ${bad} 包過期，不能賣）`:''}。會先賣最快過期的</span></div><button type="button" data-a="ration" ${good?'':'disabled'}>賣 1 包</button></div>`;}
    if(S.step>=7&&S.mat.mushroom)html+=`<div class="row">${matIcon('mushroom')}<div class="info"><b>野生菇</b><span>素材袋裡有 ${S.mat.mushroom} 朵</span></div><button type="button" data-a="mush">賣賣看</button></div>`;
    if(S.step>=10)html+=`<h4>機器零件</h4>`+['pipe','gear'].map(k=>`<div class="row">${matIcon(k)}<div class="info"><b>${MATS[k].name}</b><span>${MATS[k].buy} 金幣，放進素材袋</span></div><button type="button" data-a="part:${k}" ${S.coins>=MATS[k].buy&&matFree()>0?'':'disabled'}>購買</button></div>`).join('');
    html+=`<h4>擴充包包</h4>`;
    html+=`<div class="row"><div class="info"><b>素材袋 ${S.matCap} → ${matNext?matNext.cap:'已達上限'} 格</b><span>${matNext?matNext.cost+' 金幣':''}</span></div>${matNext?`<button type="button" data-a="mat" ${S.coins>=matNext.cost?'':'disabled'}>擴充</button>`:''}</div>`;
    html+=`<div class="row"><div class="info"><b>急救背包 ${S.kitCap} → ${kitNext?kitNext.cap:'已達上限'} 格</b><span>${kitNext?kitNext.cost+' 金幣。格數變多，但裝太重會走得比較慢':'背包已經是最大尺寸'}</span></div>${kitNext?`<button type="button" data-a="kit" ${S.coins>=kitNext.cost?'':'disabled'}>擴充</button>`:''}</div>`;
    if(S.step>=5){html+=`<h4>急救用品</h4>`+SHOP_MED.concat(mapAvail()?SHOP_EXTRA:[]).map(k=>{const it=ITEMS[k];const full=S.kit.length>=S.kitCap;
      return `<div class="row">${badge(k)}<div class="info"><b>${it.name}　<span style="color:var(--gold)">背包裡有 ${kitCount(k)} 個</span></b><span>${it.price} 金幣　重量 ${it.w}　${it.desc}</span></div><button type="button" data-a="buy:${k}" ${S.coins-it.price>=-DEBT_LIMIT&&!full?'':'disabled'}>${full?'背包已滿':S.coins-it.price<-DEBT_LIMIT?'超過賒帳上限':S.coins<it.price?'賒帳買 1 個':'買 1 個'}</button></div>`;}).join('');}
    else html+=`<p class="small">急救用品目前缺貨中。</p>`;
    const r=await say({p:shopP(),html,buttons:[{label:'離開',primary:true}],onRender:(root,fin)=>{const box=root.closest('.box');box.scrollTop=keepScroll;root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{keepScroll=box.scrollTop;pick=b.dataset.a;fin('pick');});}});
    if(r!=='pick')break;
    msg='';
    if(pick.startsWith('sell:')){const k=pick.slice(5),g=S.mat[k]*MATS[k].sell;S.coins+=g;S.earned+=g;msg=`✓ 賣出${MATS[k].name} ×${S.mat[k]}，獲得 ${g} 金幣`;S.mat[k]=0;if(S.step===2&&k==='wood')S.step=3;}
    else if(pick==='ration'){const list=S.kit.map((k,i)=>[k,i]).filter(([k])=>base(k)==='ration'&&!expired(k)).sort((a,b)=>expiry(a[0])-expiry(b[0]));const [k,i]=list[0];S.kit.splice(i,1);S.coins+=RATION_SELL;S.earned+=RATION_SELL;msg=`✓ 賣出乾糧 ×1（保存到第 ${expiry(k)} 天），獲得 ${RATION_SELL} 金幣`;}
    else if(pick==='mush'){await play('shop.noMushroom',{__p:shopP()});}
    else if(pick.startsWith('part:')){const k=pick.slice(5);S.coins-=MATS[k].buy;S.mat[k]++;msg=`✓ 已購買：${MATS[k].name} ×1`;}
    else if(pick==='seed'){S.coins-=MATS.seed.buy;S.mat.seed++;msg=`✓ 已購買：小麥種子 ×1（共 ${S.mat.seed} 包）`;}
    else if(pick==='mat'){S.coins-=matNext.cost;S.matCap=matNext.cap;S.matLv++;addHeart('shopkeeper',1);msg=`✓ 素材袋擴充為 ${S.matCap} 格`;}
    else if(pick==='kit'){S.coins-=kitNext.cost;S.kitCap=kitNext.cap;S.kitLv++;addHeart('shopkeeper',1);msg=`✓ 急救背包擴充為 ${S.kitCap} 格`;}
    else if(pick.startsWith('buy:')){const k=pick.slice(4);S.coins-=ITEMS[k].price;S.kit.push(k);msg=`✓ 已購買：${ITEMS[k].name} ×1（急救背包 ${S.kit.length}/${S.kitCap}）`;}
    refresh();
  }
}
async function merchantMenu(){
  if(S.step<5){await play('merchant.early');return;}
  let mmsg='';
  for(;;){let pick=null;
    const html=(mmsg?`<p class="warn">${mmsg}</p>`:'')+`<p class="small">急救背包 ${S.kit.length}/${S.kitCap}</p>`+(S.step>=7?'<p>對了，森林裡長的野生菇，烤一烤可香了，我自己天天吃呢，呵呵。</p>':'')+'<p>便宜又有效的祖傳祕方，別人都不知道喔。</p>'+MERCHANT_GOODS.map(k=>{const it=ITEMS[k];const full=S.kit.length>=S.kitCap;
      return `<div class="row">${badge(k)}<div class="info"><b>${it.name}</b><span>${it.price} 金幣　重量 ${it.w}　${it.desc}</span></div><button type="button" data-a="${k}" ${S.coins>=it.price&&!full?'':'disabled'}>${full?'背包已滿':'購買'}</button></div>`;}).join('');
    const r=await say({p:'merchant',html,buttons:[{label:'離開',primary:true}],onRender:(root,fin)=>root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{pick=b.dataset.a;fin('pick');})});
    if(r!=='pick')break;S.coins-=ITEMS[pick].price;S.kit.push(pick);mmsg=`已買下：${ITEMS[pick].name} ×1（急救背包 ${S.kit.length}/${S.kitCap}）`;refresh();}
}

/* 問答 */
/* 問答。fatal={scenario,bad:[選項編號]}：選到嚴重錯誤的選項 → 救援失敗（顯示正確知識卡、回到早上），並用 RESCUE_ABORT 中止呼叫端整段流程 */
/* 依序點選步驟（燒燙傷、滅火器、救溺…共用） */
async function orderQuiz(p,title,steps,explain){
  for(;;){const order=steps.map((x,i)=>i).sort(()=>Math.random()-.5);let got=[],ok=true;
    const r=await say({p,who:title,html:`<p class="q">請依照正確順序點選：</p><div id="oq">${order.map(i=>`<button type="button" class="btn" data-o="${i}" style="margin:4px 0;width:100%">${steps[i]}</button>`).join('')}</div><p id="oqs" class="small"></p>`,buttons:[],
      onRender:(root,fin)=>root.querySelectorAll('button[data-o]').forEach(b=>b.onclick=()=>{const i=+b.dataset.o;if(i!==got.length){ok=false;fin('wrong');return;}got.push(i);b.disabled=true;b.textContent=`${got.length}. ${steps[i]}`;root.querySelector('#oqs').textContent='正確，繼續！';if(got.length===steps.length)setTimeout(()=>fin('ok'),400);})});
    if(r==='ok'){await say({p,html:`<p class="good">順序完全正確！</p><p>${explain}</p>`});return true;}
    await say({p,html:`<p class="bad">順序不對喔。</p><p>${explain}</p>`,buttons:[{label:'再試一次',primary:true}]});}}
const RESCUE_ABORT={rescueAbort:true};
window.addEventListener('unhandledrejection',e=>{if(e.reason&&e.reason.rescueAbort)e.preventDefault();});  /* 救援失敗的中止訊號沒人接時（例如除錯直接呼叫）不要當成錯誤 */
async function quiz(p,q,opts,ans,explain,w,fatal){
  for(;;){const i=await say({p,wound:w,hideCap:true,html:`<p class="q">${q}</p>`,buttons:opts.map(o=>({label:o}))});
    if(fatal&&i!==ans&&fatal.bad.includes(i)){const sc=SCENARIOS[fatal.scenario];await rescueFail({scenario:fatal.scenario,choice:opts[i],intro:sc.intro,cardKey:sc.card});throw RESCUE_ABORT;}
    const ok=i===ans;await say({p,html:`<p class="${ok?'good':'bad'}">${ok?'處置正確！':'這個做法不對。'}</p><p>${explain}</p>`,buttons:[{label:ok?'繼續':'再選一次',primary:true}]});
    if(ok)return;}}
const ALT={saline:['water']};
const haveN=k=>kitCount(k)+(ALT[k]||[]).reduce((a,b)=>a+kitCount(b),0);
function needCheck(needs){return Object.entries(needs).filter(([k,n])=>haveN(k)<n).map(([k,n])=>[k,n-haveN(k)+kitCount(k)]);}
function takeKit(needs){for(const [k,n] of Object.entries(needs))for(let i=0;i<n;i++){let j=S.kit.findIndex(x=>base(x)===k&&!expired(x));if(j<0)for(const a of (ALT[k]||[])){j=S.kit.findIndex(x=>base(x)===a);if(j>=0)break;}if(j>=0)S.kit.splice(j,1);}}
const needTxt=needs=>Object.entries(needs).map(([k,n])=>`${ITEMS[k].name} ×${n}${ALT[k]?'（或開水）':''}`).join('、');

async function talk(id){
  {const h=hookOf(S.scene);if(h&&h.talk){const r=h.talk(id);if(r!==undefined)return r;}}
  if(S.scene==='ruin'&&VICTIMS[id])return victim(id);
  if(S.event&&S.event.day===S.day&&!S.event.done&&S.step>=7){const ev=EVENTS.find(e=>e.id===S.event.id);if(ev.who===id)return doEvent(ev);}
  if(id==='hunt')return hunter();
  if(id==='guard')return guardTalk();
  if(id==='shopkeeper'){if(S.step>=7){const i=await play('shop.welcome');if(i===0)return shopMenu();if(i===1)return gift('shopkeeper');return;}return shopMenu();}
  if(id==='merchant')return merchantMenu();
  if(id==='grandpa'){
    if(S.step===0)return introGrandpa();
    const fakes=[...new Set(S.kit.filter(k=>ITEMS[base(k)].fake))];
    if(fakes.length){const k=fakes[0];
      const i=await play('grandpa.fake',{name:ITEMS[k].name,truth:ITEMS[k].truth});
      if(i===0){S.kit=S.kit.filter(x=>x!==k);addHeart('grandpa',1);toast(`丟掉了 ${ITEMS[k].name}`);}return;}
    const old=S.kit.filter(expired);
    if(old.length){const i=await play('grandpa.expired',{n:old.length});
      if(i===0){S.kit=S.kit.filter(k=>!expired(k));addHeart('grandpa',1);}return;}
    const oldS=S.stash.filter(expired);
    if(oldS.length){const i=await play('grandpa.expiredStash',{n:oldS.length});
      if(i===0){S.stash=S.stash.filter(k=>!expired(k));addHeart('grandpa',1);}return;}
    if(S.castleDone&&!S.f.final){
      const st=S.castleBest||0;
      await play('grandpa.castleBack',{stars:st});
      S.f.final=true;return;}
    {const r=chBase('grandpaFinal');if(r)return r;}
    if(S.step>=10&&!S.f.p3){
      await play('grandpa.p3');
      S.f.p3=true;return;}
    if(S.step===6){
      await play('grandpa.step6');
      S.step=7;return;}
    if(S.step===9&&kitCount('ration')>0){
      await play('grandpa.step9a');
      S.step=10;S.cards.food=true;
      await play('grandpa.step9b');return;}
    const tip=T(S.step>=10?(S.bench?'tip.autoDone':'tip.bench'):S.step===7?'tip.7':S.step===8?'tip.8':S.step===9?'tip.9':S.step===5?'tip.5':'tip.default');
    return chatMenu('grandpa',tip);
  }
  if(id==='wood'){
    if(S.step===1){await play('wood.axe');S.axe=true;S.step=2;addHeart('wood',1);return;}
    if(S.step===5&&!S.flagWoodDone){
      const needs={glove:1,gauze:1,elastic:1};const miss=needCheck(needs);
      if(miss.length){await play('wood.missing',{need:needTxt(needs),missing:missTxt(miss)});return;}
      await play('wood.bring');
      await quizOf('wood');
      takeKit(needs);S.flagWoodDone=true;S.coins+=40;S.earned+=40;addHeart('wood',2);
      await play('wood.thanks');
      if(S.flagKidDone){S.step=6;await prologueDone();}
      return;}
    return chatMenu('wood',T(S.step>=7?'chat.wood7':'chat.wood'));
  }
  if(id==='kid'){
    if(S.step===5&&!S.flagKidDone){
      const needs={saline:1,bandaid:1};const miss=needCheck(needs);
      await play('kid.hurt');
      if(miss.length){await play('kid.missing',{need:needTxt(needs),missing:missTxt(miss)});return;}
      await quizOf('kid');
      takeKit(needs);S.flagKidDone=true;S.coins+=20;S.earned+=20;addHeart('kid',2);
      await play('kid.thanks');
      if(S.flagWoodDone){S.step=6;await prologueDone();}
      return;}
    return chatMenu('kid',T(S.step>=6?'chat.kid6':'chat.kid'));
  }
}
async function prologueDone(){
  await play('prologueDone');
}

/* 防災包（爺爺家門口）：產出仍先進急救背包，玩家自己帶回家放入；防災包內的東西不計負重 */
/* 防災包是「一個物件」：stashAt 記錄它在哪（base＝爺爺家、地區 id＝該地區住處、carry＝帶在身上旅行）。
   只有人在放著它的住處才能開；帶在身上時，可在住處放下。 */
async function stashMenu(){
  const here=curRegion().id;
  if(S.stashAt==='carry'){
    const i=await say({p:'hero',who:'防災包',html:`<p>防災包還帶在身上。要放在這裡（${curRegion().name}）嗎？</p><p class="small">放下後才能整理裡面的東西；之後出遠門前要記得再帶上。</p>`,buttons:[{label:'放在這裡',primary:true},{label:'繼續帶著'}]});
    if(i===0){S.stashAt=here;save();return stashBox();}
    return;}
  if(S.stashAt!==here){await say({p:'hero',who:'防災包',html:`<p>防災包不在這裡，它放在${regionName(S.stashAt)}。</p><p class="small">平時放在住處門口，緊急時才方便一手帶走。</p>`});return;}
  return stashBox();}
/* 離開某地區前（例如搭船）呼叫：防災包若放在這個地區，問玩家要不要帶上；回傳是否帶上 */
async function stashDepart(){
  const here=curRegion().id;if(S.stashAt!==here)return S.stashAt==='carry';
  const i=await say({p:'hero',who:'防災包',html:'<p>要帶上防災包嗎？</p><p class="small">不帶的話，它會留在原地；旅途中就用不到裡面的東西。</p>',buttons:[{label:'帶上防災包',primary:true},{label:'留在這裡'}]});
  if(i===0){S.stashAt='carry';save();return true;}return false;}
async function stashBox(){
  for(;;){
    let act=null;
    const note=k=>base(k)==='ration'?(expired(k)?'<span style="color:var(--bad)">已過期</span>':`保存到第 ${expiry(k)} 天`):'';
    const goodR=S.stash.filter(k=>base(k)==='ration'&&!expired(k)),water=stashCount('water');
    const fast=goodR.length?Math.min(...goodR.map(expiry)):null;
    const inRows=S.stash.length?S.stash.map((k,i)=>`<div class="row">${badge(k)}<div class="info"><b>${ITEMS[base(k)].name}</b><span>${note(k)}</span></div><button type="button" data-o="${i}">取出</button></div>`).join(''):'<p class="small">防災包是空的。</p>';
    const kitRows=S.kit.map((k,i)=>[k,i]).filter(([k])=>['ration','water'].includes(base(k))).map(([k,i])=>`<div class="row">${badge(k)}<div class="info"><b>${ITEMS[base(k)].name}</b><span>${note(k)}</span></div><button type="button" data-p="${i}">放入</button></div>`).join('')||'<p class="small">急救背包裡沒有乾糧或開水。</p>';
    await say({p:'hero',who:'防災包',html:`<h4>家中防災包 ${S.stash.length}/${STASH_CAP}</h4>
      <p>乾糧 ${goodR.length} 包${fast!=null?`（最快保存到第 ${fast} 天）`:''}　開水 ${water} 瓶</p>
      <p class="small">家中儲備目標（一週）：乾糧 ${goodR.length}/7　開水 ${water}/7</p>${inRows}
      <h4>急救背包 ${S.kit.length}/${S.kitCap}</h4>${kitRows}`,buttons:[{label:'關閉',primary:true}],
      onRender:(root,fin)=>{root.querySelectorAll('button[data-o]').forEach(b=>b.onclick=()=>{act=['o',+b.dataset.o];fin('act');});root.querySelectorAll('button[data-p]').forEach(b=>b.onclick=()=>{act=['p',+b.dataset.p];fin('act');});}}).then(r=>{if(r!=='act')act=null;});
    if(!act)return;
    if(act[0]==='o'){if(S.kit.length>=S.kitCap){toast('急救背包已滿');continue;}S.kit.push(S.stash.splice(act[1],1)[0]);}
    else{if(S.stash.length>=STASH_CAP){toast('防災包已滿');continue;}S.stash.push(S.kit.splice(act[1],1)[0]);}
    refresh();save();
  }
}

/* 世界地圖：只顯示各地區位置與開放狀態；點目前所在的地區回到中心地點，其他地區顯示怎麼過去（由章節 region.travelHint 說明，例如搭船） */
async function worldMap(){
  if(busy)return;busy=true;stopInput();let pick=null;const regs=regionList();
  try{
    const pins=regs.map((r,i)=>{const open=regionOpen(r),here=r===curRegion();
      return `<button type="button" data-r="${i}" ${open?'':'disabled'} style="position:absolute;left:${r.pin[0]}%;top:${r.pin[1]}%;transform:translate(-50%,-50%);border:3px solid #FFF3D6;border-radius:999px;padding:4px 12px;font-weight:900;cursor:${open?'pointer':'default'};background:${open?(here?'#86E0A4':'#E3B95B'):'rgba(16,24,33,.8)'};color:${open?'#2A1D08':'#B8C2C9'}">${open?r.name+(here?'（目前）':''):'🔒'}</button>`;}).join('');
    const r=await say({icon:'圖',who:'世界地圖',html:`<div style="position:relative;border-radius:12px;overflow:hidden"><img alt="" src="${A.world}" style="width:100%;display:block">${pins}</div><p class="small">點選所在地區可以快速回到中心地點；到其他地區要依指示前往。其他地區會隨課程單元開放。</p>`,buttons:[{label:'關閉',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-r]').forEach(b=>b.onclick=()=>{pick=+b.dataset.r;fin('go');})});
    if(r==='go'){const g=regs[pick];
      if(g===curRegion()){const c=g.center||BASE.center;busy=false;await go(c.scene,c.at);busy=true;}
      else await say({p:'hero',html:`<p>${g.travelHint||'要依指示才能前往這個地區。'}</p>`});}
  }finally{busy=false;save();refresh();}}

/* 背包 */
async function bag(){if(busy)return;busy=true;stopInput();
  try{for(;;){let pick=-1;const l=load_();const pct=Math.min(100,l/LOAD_HEAVY*100);
    const slots=S.kit.length?S.kit.map((k,i)=>{const b=base(k);const note=b==='ration'?(expired(k)?'<span style="color:var(--bad)">已過期</span>':`保存到第 ${expiry(k)} 天`):'';
      return `<div class="row">${badge(k)}<div class="info"><b>${ITEMS[b].name}</b><span>重量 ${ITEMS[b].w}　${note}</span></div>${b==='water'?`<button type="button" data-d="${i}">喝</button> `:b==='sugar'?`<button type="button" data-g="${i}">吃</button> `:b==='ration'&&!expired(k)?`<button type="button" data-r="${i}">吃</button> `:''}<button type="button" data-i="${i}">丟掉</button></div>`;}).join(''):'<p class="small">急救背包是空的。</p>';
    const tools=[S.axe&&'斧頭',S.tools.hoe&&'鋤頭',S.tools.can&&'澆水壺',S.tools.pick&&'十字鎬'].filter(Boolean).join('、')||'沒有';
    const r=await say({p:'hero',who:'我的包包',html:`<h4>急救背包 ${S.kit.length}/${S.kitCap}</h4><div class="meter"><i class="${l>LOAD_HEAVY?'over':l>LOAD_OK?'heavy':''}" style="width:${pct}%"></i></div>
      <p class="small">負重 ${l}　${l>LOAD_HEAVY?'太重了，走得很慢':l>LOAD_OK?'有點重，走路變慢':'輕鬆好走'}</p>${slots}
      <h4>素材袋 ${matUsed()}/${S.matCap}</h4>${Object.entries(S.mat).filter(([k,n])=>n>0).map(([k,n])=>`<div class="row">${matIcon(k)}<div class="info"><b>${MATS[k].name} ×${n}</b></div>${k==='mushroom'?'<button type="button" data-m="eat">吃掉</button> <button type="button" data-m="toss">丟掉</button>':''}</div>`).join('')||'<p class="small">空的</p>'}<h4>工具</h4><p>${tools}</p>`,buttons:[{label:'關閉',primary:true}],
      onRender:(root,fin)=>{root.querySelectorAll('button[data-i]').forEach(b=>b.onclick=()=>{pick=+b.dataset.i;fin('pick');});root.querySelectorAll('button[data-m]').forEach(b=>b.onclick=()=>fin(b.dataset.m));root.querySelectorAll('button[data-d]').forEach(b=>b.onclick=()=>{pick=+b.dataset.d;fin('drink');});root.querySelectorAll('button[data-g]').forEach(b=>b.onclick=()=>{pick=+b.dataset.g;fin('sugar');});root.querySelectorAll('button[data-r]').forEach(b=>b.onclick=()=>{pick=+b.dataset.r;fin('ration');});}});
    if(r==='drink'){if(S.drinkDay!==S.day){S.drinkDay=S.day;S.drinks=0;}S.kit.splice(pick,1);if(S.drinks<3){S.drinks++;S.sta=Math.min(STA_MAX,S.sta+10);toast('喝了開水，體力 +10');}else toast('喝了開水，已經不渴了');refresh();continue;}
    if(r==='sugar'){await eatSugar(pick);continue;}
    if(r==='ration'){eatRation(pick);refresh();continue;}
    if(r==='eat'){await eatMushroom();continue;}if(r==='toss'){S.mat.mushroom--;toast('丟掉了野生菇');continue;}
    if(r!=='pick')break;S.kit.splice(pick,1);refresh();}}
  finally{busy=false;save();refresh();}}
/* 傷口圖鑑：看過的傷口才顯示圖；還沒看過任何一張時整段不顯示（序章沒有傷口圖時畫面與以前相同） */
function woundGallery(){const ws=Object.keys(WOUNDS),seen=S.wounds||{},n=ws.filter(w=>seen[w]).length;if(!n)return '';
  return `<h4>傷口圖鑑 ${n}/${ws.length}</h4><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px">`+ws.map(w=>seen[w]?`<figure style="margin:0;text-align:center"><img alt="" src="assets/w_${w}.webp" style="width:100%;border-radius:8px;border:2px solid #F4E7CC;background:#fff"><figcaption class="small">${WOUNDS[w]}</figcaption></figure>`:`<figure style="margin:0;text-align:center;opacity:.5"><div style="aspect-ratio:1;border-radius:8px;border:2px dashed #B8C2C9;display:grid;place-items:center">？</div><figcaption class="small">？</figcaption></figure>`).join('')+'</div>';}
async function cards(){if(busy)return;busy=true;stopInput();
  try{const ks=Object.keys(S.cards);await say({p:'hero',who:'知識卡',html:woundGallery()+(ks.length?ks.map(k=>`<div class="card"><b>${CARDS[k].title}</b><p>${CARDS[k].text}</p></div>`).join(''):'<p class="small">還沒有知識卡。</p>'),buttons:[{label:'關閉',primary:true}]});}
  finally{busy=false;}}
async function settings(){if(busy)return;busy=true;stopInput();let reset=false;const hasOut=!!(window.FACloud&&FACloud.email());
  try{const i=await say({p:'hero',who:'設定',html:`<p>移動方式：<b>${S.ctrl==='joy'?'虛擬搖桿':'方向鍵'}</b></p><p class="small">用電腦玩時，可以用鍵盤方向鍵走路、空白鍵互動。</p><p class="small">${cloudLine()}</p>${window.FAMusic?`<p>背景音樂：<b>${FAMusic.isOn()?'開':'關'}</b>　音量 <input type="range" id="musVol" min="0" max="100" value="${Math.round(FAMusic.vol()*100)}" style="vertical-align:middle"></p><p class="small">配樂：AI 輔助原創作曲與合成音色製作</p>`:''}`,buttons:[{label:S.ctrl==='joy'?'改用方向鍵':'改用虛擬搖桿',primary:true},{label:'卡住了？回到這個場景的入口'},{label:'全部重新開始',danger:true},...(hasOut?[{label:'登出'}]:[]),...(window.FAMusic?[{label:FAMusic.isOn()?'關閉背景音樂':'開啟背景音樂'}]:[]),{label:'關閉'}],
      onRender:root=>{const v=root.querySelector('#musVol');if(v)v.oninput=()=>FAMusic.setVol(v.value/100);}});
    if(i===0)S.ctrl=S.ctrl==='joy'?'pad':'joy';
    else if(i===1){const sp=sc().spawn;S.pos={x:sp[0],y:sp[1]};placeHero();camera();toast('已回到入口');}
    else if(i===2){const j=await say({p:'hero',who:'重新開始',html:'<p>所有進度都會清除。</p>',buttons:[{label:'重新開始',danger:true},{label:'取消',primary:true}]});if(j===0){const c=S.ctrl;S=newState();S.ctrl=c;S.started=true;reset=true;if(window.FACloud)FACloud.clearCheckpoints();}}
    else if(i===3&&hasOut){await doSignOut();return;}
    else if(window.FAMusic&&i===(hasOut?4:3))FAMusic.setOn(!FAMusic.isOn());}
  finally{busy=false;save();if(reset){buildScene();startScene();}else refresh();}}

/* ================= 移動 ================= */
function walkable(x,y){const rows=WALKS[S.scene];const j=Math.floor(y/CELL),i=Math.floor(x/CELL);return j>=0&&j<rows.length&&i>=0&&i<rows[0].length&&rows[j].charCodeAt(i)===49;}
function blockers(){const s=sc(),H=s.heroH,B=[];
  (s.trees||[]).forEach(t=>{const st=treeState(t);B.push([t.x,t.y,H*(st.hp>0?.32:.22)]);});
  if(s.rocks)rocksOf(s).forEach((r,i)=>{if(rockState(i).hp>0)B.push([r[0],r[1],H*.34]);});
  if(s.plots){B.push([300,540,H*.45]);if(S.bench)B.push([600,290,H*.5]);if(S.harvester){B.push([1450,380,H*.4]);B.push([1480,565,H*.6]);}}
  return B;}
function free(x,y){const H=sc().heroH,r=H*.12;
  if(!(walkable(x,y)&&walkable(x-r,y)&&walkable(x+r,y)&&walkable(x,y-r*.5)&&walkable(x,y+r*.5)))return false;
  for(const [bx,by,rx] of blockers()){if(((x-bx)/rx)**2+((y-by)/(rx*.5))**2<1)return false;}
  return true;}
/* 目前位置不可走時，螺旋搜尋最近的可走位置；找不到就回場景入口（避免穿牆） */
function snapFree(){if(free(S.pos.x,S.pos.y))return;for(let r=8;r<600;r+=8)for(let k=0;k<16;k++){const a=k/16*Math.PI*2,x=S.pos.x+Math.cos(a)*r,y=S.pos.y+Math.sin(a)*r;if(x>10&&y>10&&x<MW-10&&y<MH-10&&free(x,y)){S.pos={x,y};return;}}const sp=sc().spawn;if(sp)S.pos={x:sp[0],y:sp[1]};}
const input={jx:0,jy:0,keys:{},pad:{}};
function stopInput(){input.jx=input.jy=0;input.pad={};input.keys={};resetKnob();if(walking){walking=false;heroEl&&heroEl.classList.remove('walking');}}
function inputVec(){let x=input.jx,y=input.jy;const k=input.keys,p=input.pad;
  if(k.ArrowLeft||k.a||p.left)x-=1;if(k.ArrowRight||k.d||p.right)x+=1;if(k.ArrowUp||k.w||p.up)y-=1;if(k.ArrowDown||k.s||p.down)y+=1;
  const m=Math.hypot(x,y);if(m>1){x/=m;y/=m;}return [x,y];}
let last=0,walking=false,saveT=0,exiting=false;const trail=[];
function loop(t){const dt=Math.min(.05,(t-last)/1000||0);last=t;
  if(!$('game').hidden&&!busy&&heroEl){
    const [vx,vy]=inputVec();
    if(Math.hypot(vx,vy)>.12){const sp=sc().heroH*1.8*speedMul();
      const nx=S.pos.x+vx*sp*dt,ny=S.pos.y+vy*sp*dt;
      if(!free(S.pos.x,S.pos.y)){snapFree();}
      else{const dx=nx-S.pos.x,dy=ny-S.pos.y;
        if(free(nx,S.pos.y))S.pos.x=nx;
        else if(Math.abs(dx)>Math.abs(dy)*.3){for(const m of [1,2,3,-1,-2,-3]){const sy=m*Math.abs(dx);if(free(nx,S.pos.y+sy)){S.pos.x=nx;S.pos.y+=sy;break;}}}
        if(free(S.pos.x,ny))S.pos.y=ny;
        else if(Math.abs(dy)>Math.abs(dx)*.3){for(const m of [1,2,3,-1,-2,-3]){const sx=m*Math.abs(dy);if(free(S.pos.x+sx,ny)){S.pos.y=ny;S.pos.x+=sx;break;}}}}
      trail.push([S.pos.x,S.pos.y]);if(trail.length>60)trail.shift();
      if(Math.abs(vx)>.2)heroImg.classList.toggle('flip',vx<0);
      if(!walking){walking=true;heroEl.classList.add('walking');}
      placeHero();camera();checkExit();saveT+=dt;if(saveT>2){saveT=0;save();}
    }else if(walking){walking=false;heroEl.classList.remove('walking');save();}
    updateNear();}
  requestAnimationFrame(loop);}
async function checkExit(){if(exiting)return;
  for(const ex of (sc().exits||[])){if(ex.test(S.pos.x,S.pos.y)){
    exiting=true;busy=true;const px=S.pos.x,py=S.pos.y;stopInput();
    try{if(ex.block&&(!ex.need||!ex.need())){await say({p:'hero',html:`<p>${ex.block}</p>`});
        let back=null;for(let k=trail.length-1;k>=0;k--){const [tx,ty]=trail[k];if(!ex.test(tx,ty)&&free(tx,ty)&&Math.hypot(tx-px,ty-py)>30){back=[tx,ty];break;}}
        if(!back)back=sc().spawn;S.pos={x:back[0],y:back[1]};trail.length=0;placeHero();camera();}
      else await go(ex.to,ex.at);}
    catch(e){if(!e||!e.rescueAbort)throw e;}
    finally{busy=false;exiting=false;save();refresh();}
    return;}}}

/* ================= 操控 ================= */
const joy=$('joy'),knob=joy.querySelector('.knob');let joyId=null;
function resetKnob(){knob.style.setProperty('--kx','0px');knob.style.setProperty('--ky','0px');input.jx=input.jy=0;joyId=null;}
function joyMove(e){const r=joy.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,max=r.width/2-30;
  let dx=e.clientX-cx,dy=e.clientY-cy;const d=Math.hypot(dx,dy);if(d>max){dx*=max/d;dy*=max/d;}
  knob.style.setProperty('--kx',dx+'px');knob.style.setProperty('--ky',dy+'px');input.jx=dx/max;input.jy=dy/max;}
joy.addEventListener('pointerdown',e=>{joyId=e.pointerId;joy.setPointerCapture(e.pointerId);joyMove(e);e.preventDefault();});
joy.addEventListener('pointermove',e=>{if(e.pointerId===joyId)joyMove(e);});
['pointerup','pointercancel','lostpointercapture'].forEach(ev=>joy.addEventListener(ev,e=>{if(e.pointerId===joyId)resetKnob();}));
$('dpad').querySelectorAll('button').forEach(b=>{const d=b.dataset.d;
  const on=e=>{input.pad[d]=true;b.classList.add('on');try{b.setPointerCapture(e.pointerId);}catch(_){}e.preventDefault();};
  const off=()=>{input.pad[d]=false;b.classList.remove('on');};
  b.addEventListener('pointerdown',on);['pointerup','pointercancel','lostpointercapture'].forEach(ev=>b.addEventListener(ev,off));});
window.addEventListener('keydown',e=>{if(!$('dialog').hidden)return;const k=e.key.length===1?e.key.toLowerCase():e.key;
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','w','a','s','d'].includes(k)){input.keys[k]=true;e.preventDefault();}
  if((k===' '||k==='Enter')&&!$('game').hidden){doAction();e.preventDefault();}});
window.addEventListener('keyup',e=>{const k=e.key.length===1?e.key.toLowerCase():e.key;input.keys[k]=false;});
window.addEventListener('blur',stopInput);
$('act').addEventListener('click',doAction);
$('btnMap').onclick=worldMap;$('btnBag').onclick=bag;$('btnCards').onclick=cards;$('btnSettings').onclick=settings;

/* ================= 雲端存檔與存檔點 ================= */
const checkpoint=()=>{if(window.FACloud)try{FACloud.checkpoint(S);}catch(e){}};
const CLOUD_TXT={ok:'已同步到雲端',loading:'同步中…',offline:'目前連不上雲端，進度先存在這台裝置，之後會自動補傳',conflict:'另一台裝置也在使用這個帳號，雲端同步已暫停（重新整理頁面可選擇要用哪一份進度）',off:'未登入，進度只存在這台裝置',nolib:'目前無法連線雲端，進度只存在這台裝置'};
function cloudLine(){if(!window.FACloud)return '進度只存在這台裝置。';const m=FACloud.email();return (m?`已登入：${m}<br>`:'')+'雲端：'+(CLOUD_TXT[FACloud.status()]||'');}
async function doSignOut(){window.__loggingOut=true;try{if(window.FACloud)await FACloud.signOut();}catch(e){}try{localStorage.removeItem(KEY);}catch(e){}location.reload();}
function summary(o){return `第 ${o.day||1} 天，序章進度 ${o.step||0}，金幣 ${o.coins||0}`;}
async function askConflict({local,cloud}){
  const i=await say({p:'hero',who:'進度不一致',html:`<p>雲端的進度和這台裝置的進度不一樣，要用哪一個？</p><p>雲端：${summary(cloud)}</p><p>這台裝置：${summary(local)}</p><p class="small">沒選的那一份會被覆蓋。</p>`,
    buttons:[{label:'用雲端的進度',primary:true},{label:'用這台裝置的進度'}]});
  return i===0;}
function renderAuth(){
  const box=$('authBox');if(!box)return;
  const st=window.FACloud?FACloud.status():'nolib',mail=window.FACloud?FACloud.email():null;
  if(!window.FACloud||st==='nolib'){box.innerHTML='<span class="small">目前無法連線雲端，進度只會存在這台裝置。</span>';return;}
  if(!mail){box.innerHTML='<button type="button" id="btnLogin">用 Google 登入（進度存雲端）</button><div class="small">也可以不登入直接玩，進度只會存在這台裝置。</div>';
    $('btnLogin').onclick=()=>FACloud.signIn();return;}
  box.innerHTML=`<span>已登入：${mail}</span> <span class="small">${CLOUD_TXT[st]||''}</span> <button type="button" id="btnLogout">登出（換帳號）</button>`;
  $('btnLogout').onclick=()=>{const ok=FACloud.status()==='ok';
    if(confirm(ok?'登出後，這台裝置上的遊戲進度會清除，雲端的進度會保留，下次登入就能接續。確定要登出嗎？':'目前進度還沒同步到雲端，登出後這台裝置上的進度會遺失。確定要登出嗎？'))doSignOut();};}
async function initCloud(){
  if(!window.FACloud)return;
  FACloud.onStatus(s=>{if(s==='conflict')toast('另一台裝置也在使用這個帳號，雲端同步已暫停');if(!$('title').hidden)renderAuth();});
  const mail=await FACloud.init();renderAuth();
  if(!mail)return;
  const btn=$('btnStart');btn.disabled=true;btn.textContent='同步中…';
  let raw=null;try{raw=JSON.parse(localStorage.getItem(KEY));}catch(e){}
  const r=await FACloud.sync(raw&&(raw.v===1||raw.v===2)?raw:null,askConflict);
  if(r.action==='use-cloud'){const c=S.ctrl;S=migrate(r.state);if(c)S.ctrl=c;try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}}
  btn.disabled=false;btn.textContent=S.started?'繼續冒險':startLabel;renderAuth();}
/* 救援失敗：顯示正確知識卡 → 回到當天早上的存檔點 → 扣救援費 → 記錄失敗。呼叫端在 await 之後要 return，不要繼續原本的流程。 */
async function rescueFail({scenario,choice,intro,cardKey}){
  stopInput();
  await play('rescueFail.intro',{intro});
  if(cardKey&&CARDS[cardKey]){const c=CARDS[cardKey];S.cards[cardKey]=true;await play('rescueFail.card',{cardTitle:c.title,cardText:c.text});}
  const snap=window.FACloud?await FACloud.restore(S.day):null;
  if(window.FACloud)FACloud.failure(scenario,choice);
  if(snap){const cards=Object.assign({},snap.cards,S.cards),c=S.ctrl;S=migrate(snap);S.cards=cards;S.ctrl=c;S.started=true;}
  S.coins-=RESCUE_FEE;S.pendingFaint=null;
  $('fade').classList.add('on');await sleep(RM?0:500);buildScene();refresh();$('fade').classList.remove('on');
  await play(snap?'rescueFail.back':'rescueFail.backNoCheckpoint');
  save();if(window.FACloud)FACloud.flush();
}

/* ================= 天災與野外事件（D4）：天災由老師發布（D5）或除錯入口排定；野外項目（溺水、裝溪水）在 WILD 開啟前不出現 ================= */
async function retreatIndoor(){const h=curRegion().home||BASE.home;await go(h.scene,curRegion()===BASE?SCENES.home.spawn:h.at);}
async function wxEnter(){
  const t=wxToday();S.wxHit=S.wxHit||{};
  if(t==='typhoon'&&isOutdoor(S.scene)&&!S.wxHit[S.scene]){S.wxHit[S.scene]=true;
    const i=await say({p:'hero',html:'<p class="bad">狂風暴雨！樹枝被吹得劈啪作響，招牌在搖晃……</p>',buttons:[{label:'馬上回到室內避難',primary:true},{label:'趁現在趕快把事情做完'}]});
    if(i===0){await retreatIndoor();return;}
    await quiz('hero','被困在戶外，暫時回不了家，要躲在哪裡？',['大樹下面，可以擋雨','廣告招牌旁邊','就近進入堅固的建築物；遠離大樹、招牌、電線和河邊'],2,CARDS.typhoon.text,undefined,{scenario:'typhoon',bad:[0,1]});S.cards.typhoon=true;
    if(kitCount('raincoat')<1){S.sta=Math.max(0,S.sta-20);refresh();
      await say({p:'hero',html:'<p>沒有雨衣，全身都濕透了，開始不停發抖……</p><p class="small">體力 -20</p>'});
      await quiz('hero','全身濕透、一直發抖，該怎麼辦？',['繼續工作，動一動就不冷了','到避風處換下濕衣服、擦乾、保暖，喝點溫熱的飲料','喝一點酒暖暖身子'],1,CARDS.hypothermia.text,undefined,{scenario:'hypothermia',bad:[0,2]});S.cards.hypothermia=true;
      if(S.sta<=0)S.pendingFaint='exhaust';}
    else await say({p:'hero',html:'<p>還好有穿雨衣，身體保持乾燥。</p>'});}
  if(t==='flood'&&S.scene==='river'&&!S.wxHit.river){S.wxHit.river=true;
    await say({p:'hero',html:'<p class="bad">溪水變得又混濁又急，水面漂著樹枝，上游傳來低沉的轟隆聲……</p>'});
    await quiz('hero','看到這些徵兆，該怎麼做？',['走到橋上看清楚一點','沿著溪谷往下游跑','立刻往溪流兩側的高處撤離'],2,CARDS.flood.text,undefined,{scenario:'flood',bad:[0,1]});S.cards.flood=true;
    await say({p:'hero',html:'<p>你爬上河谷旁的高地。不久，一道混著泥沙的洪水轟隆沖過河谷……</p><p class="small">今天河谷太危險，先回村子吧。</p>'});
    await go('village',[1540,380]);}
  if(t==='fog'&&S.scene==='forest'&&!S.wxHit.forest){S.wxHit.forest=true;
    await say({p:'hero',html:'<p>濃霧越來越厚，四周的樹看起來都一樣……回村子的路在哪裡？</p>'});
    await quiz('hero','在濃霧中迷路了，第一步該怎麼做？',['憑感覺一直往前走，總會走出去','停下來、保持冷靜，留在原地，發出求救訊號','往看起來比較亮的地方跑'],1,CARDS.lost.text);S.cards.lost=true;
    const has=kitCount('whistle')>0;
    const i=await say({p:'hero',html:has?'<p>背包裡有哨子。</p>':'<p class="small">如果有哨子就好了……</p>',buttons:has?[{label:'吹哨子，三短聲一組',primary:true},{label:'大聲喊救命'}]:[{label:'大聲喊救命',primary:true}]});
    if(has&&i===0){await say({p:'wood',html:'<p>我聽到哨子聲了！你在那裡別動，我過去找你！</p>'});}
    else{S.sta=Math.max(0,S.sta-15);refresh();await say({p:'wood',html:'<p>……喊了好久，喉嚨都啞了，我才聽到你的聲音。下次記得帶哨子！</p><p class="small">體力 -15</p>'});if(S.sta<=0)S.pendingFaint='exhaust';}
    S.cards.signal=true;await say({p:'hero',html:`<div class="card"><b>${CARDS.signal.title}</b><p>${CARDS.signal.text}</p></div>`});
    await go('village',[890,860]);}
  if(!t&&S.scene==='river'&&S.f.p3&&!S.f.drown&&wild()&&Math.random()<DROWN_CHANCE){S.f.drown=true;try{
    await say({p:'kid',html:'<p class="bad">救命啊！小芽在溪邊玩水，腳一滑被沖進溪裡了！</p>'});
    const i=await say({p:'hero',html:'<p class="q">你不太會游泳，要怎麼救她？</p>',buttons:[{label:'立刻跳下水去救'},{label:'大聲呼救、叫人打 119，找樹枝伸給她、拋出能漂浮的東西'}]});
    if(i===0){await rescueFail({scenario:'drowning',choice:'立刻跳下水去救',intro:SCENARIOS.drowning.intro,cardKey:SCENARIOS.drowning.card});throw RESCUE_ABORT;}
    await say({p:'hero',html:'<p class="good">你把一根長樹枝伸過去，小芽抓住後被拉上了岸！</p>'});
    await orderQuiz('hero','救溺五步驟',['叫：大聲呼救','叫：打 119','伸：用竹竿、樹枝伸給他','拋：拋出能漂浮的東西','划：利用船具划過去'],CARDS.cross.text);
    S.cards.cross=true;addHeart('kid',1);
  }catch(e){if(e&&e.rescueAbort)S.f.drown=false;throw e;}}  /* 救援失敗後這件事要能重來 */
}
function wxTick(){if(busy||$('game').hidden)return;const t=wxToday();
  if(t==='typhoon'&&['home','shop','ch2_inn2','ch2_smithy'].includes(S.scene)&&!S.wxEye&&S.wx.day===S.day){S.wxEye=S.day;busy=true;stopInput();
    (async()=>{try{await say({p:'hero',html:'<p>咦？外面的風雨突然停了，天空好像還露出了一點藍色……颱風走了嗎？</p>',buttons:[{label:'太好了，出門看看！'},{label:'再等等，先聽聽收音機的消息'}]}).then(async i=>{
      await say({p:curRegion()===BASE?'grandpa':(curRegion().shopkeeper||'grandpa'),html:`<p class="${i===1?'good':'bad'}">${i===1?'做得對！':'等一下！'}</p><p>這是颱風眼經過，風雨暫停只是暫時的，另一半的暴風很快就會來！</p>`});S.cards.typhoon=true;});}finally{busy=false;save();refresh();}})();}}
setInterval(wxTick,15000);
async function riverWater(){
  if(matFree()<=0){await say({p:'hero',html:'<p class="warn">素材袋已經滿了。</p>'});return;}
  if(wxToday()==='flood'){await say({p:'hero',html:'<p class="bad">溪水暴漲，太危險了！</p>'});return;}
  if(!await useSta(2))return;S.mat.rawwater=(S.mat.rawwater||0)+1;toast('裝了一桶溪水（要煮沸才能喝）');
  if(!S.cards.riverwater){S.cards.riverwater=true;await say({p:'hero',html:`<div class="card"><b>${CARDS.riverwater.title}</b><p>${CARDS.riverwater.text}</p></div><p class="good">獲得知識卡</p>`});}}
/* ================= 啟動 ================= */
async function startScene(){busy=false;if(S.step===0&&S.day===1)checkpoint();if(S.step===0){busy=true;await sleep(RM?0:400);try{await introGrandpa();}finally{busy=false;save();refresh();}}}
S=load()||newState();
if(S.started)$('btnStart').textContent='繼續冒險';
$('btnFull').onclick=()=>{const d=document.documentElement;try{if(document.fullscreenElement)document.exitFullscreen();else if(d.requestFullscreen)d.requestFullscreen().then(()=>{try{screen.orientation&&screen.orientation.lock&&screen.orientation.lock('landscape').catch(()=>{});}catch(e){}}).catch(()=>toast('這台裝置不支援全螢幕'));else toast('這台裝置不支援全螢幕');}catch(e){toast('這台裝置不支援全螢幕');}};
$('btnStart').onclick=()=>{if($('btnStart').disabled)return;S.started=true;document.body.classList.add('playing');$('title').hidden=true;$('game').hidden=false;buildScene();save();startScene();};
requestAnimationFrame(loop);
initCloud();
async function lines(p,arr){for(const x of arr)await say({p,html:`<p>${x}</p>`});}  /* 連續幾句同一個人說的話（章節程式用） */
/* ================= 章節程式用的核心功能（FA）：章節程式只能透過它存取遊戲，不直接碰核心變數 ================= */
let FA=null;
try{FA={get S(){return S;},ITEMS,MATS,CARDS,A,RATIO,RM,STA_MAX,RATION_NEED,WATER_NEED,$,
  say,quiz,play,T,lines,chatMenu,gift,shopMenu,merchantMenu,go,toast,refresh,buildScene,nextDay,sleep,
  kitCount,takeKit,addHeart,needCheck,sprite,quakeFx,base,expired,stashDepart,stormy,wxToday,rescueFail,RESCUE_ABORT,orderQuiz,curRegion,regionOf,hearts,
  setBusy:v=>{busy=v;},stopInput,save};
Object.entries(CH_MODS).forEach(([id,f])=>{try{CHH[id]=f(FA);}catch(err){console.error('章節程式初始化失敗，已略過：',id,err);}});
}catch(err){console.error('章節介面初始化失敗，章節停用：',err);}
if(location.hash==='#debug'&&localStorage.getItem('fa-debug')==='1')window.__fa={wxEnter,riverWater,retreatIndoor,quiz,rescueFail,scheduleWx,wxToday,stormy,nextDay,refresh,say,cards,SCENES,CHAPTERS,REGIONS,regionOf,curRegion,mapAvail,stashDepart,worldMap,woundGallery,T,rationPhase,stashMenu,eatSugar,rescueFail,checkpoint,save,moveSpr,well,boil,bag,needCheck,takeKit,faint,hypoWarn,doEvent,EVENTS,victim,gateDoor,tablet,hunter,guardTalk,gift,bench,takeBin,pickUp,eatMushroom,get S(){return S},go,talk,doAction,bed,machine,farmPlot,mine,shopMenu,refresh,buildScene};
})();
