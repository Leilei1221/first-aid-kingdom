/* 第三章「藍堡的日常」E2：釣魚、魚尺（留下或放回）、保育類要放回、魚攤買賣。
 * 全部是草稿：跟 E1 一樣，只有老師預覽或本機 #debug 加 ?e1=1 才會出現。
 * 狀態記在既有的 S.c.ch3_fish（不新增頂層欄位）：{rod:有沒有釣竿, bag:{魚種:隻數}, rel:放回幾次, n:釣起幾次}。
 * 魚尺、價格、機率都是遊戲參數，不是真實的法規或公分數字。 */
export const FISH={rodPrice:60,castSta:4,bagMax:8,sizeLine:40,smallChance:.35,protectedChance:.08,eatSta:12,relPerRep:3,
  biteZone:26,biteSpeed:75,  /* 咬鉤條：綠色範圍寬度、游標每秒移動的格數（0～100） */
  spots:{pier:{x:720,y:600,label:'釣魚（碼頭）'},lh:{x:820,y:800,label:'釣魚（燈塔岩邊）'}},stallAt:{x:1150,y:520},
  /* 燈塔岩邊（老師 2026-10-09 要求；港口信譽 3 以上開放）：魚比碼頭大、比較容易遇到保育類（要放回）。沒有新增魚種，只是機率不同；都是遊戲參數 */
  lh:{protectedChance:.15,smallChance:.2,w:{mackerel:5,horse:10,snapper:35,grouper:50}}};
export const SPECIES=[
  {id:'mackerel',name:'鯖魚',price:20,w:40},{id:'horse',name:'竹筴魚',price:25,w:30},
  {id:'snapper',name:'鯛魚',price:40,w:20},{id:'grouper',name:'石斑魚',price:70,w:10}];
export const PROTECTED=[{id:'turtle',name:'綠蠵龜（海龜）'},{id:'ray',name:'鬼蝠魟（蝠鱝）'}];
export const pickSpecies=(r,w)=>{const L=SPECIES.map(s=>({s,w:w&&w[s.id]!=null?w[s.id]:s.w})),tot=L.reduce((a,b)=>a+b.w,0);let x=r*tot;for(const o of L){if((x-=o.w)<0)return o.s;}return L[L.length-1].s;};
export default function(FA,{on,debug,addRep,preview,lhOpen}){
const {say,quiz,toast,refresh,CARDS,staMax,A,RATIO}=FA;
const img=(k,h)=>`<img src="${A[k]}" alt="" style="display:block;margin:6px auto;max-height:${h}px;max-width:100%">`;
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
const st=()=>{S.c=S.c||{};const f=S.c.ch3_fish||(S.c.ch3_fish={rod:false,bag:{},rel:0,n:0});if(preview)f.rod=true;return f;};
const bagN=()=>Object.values(st().bag).reduce((a,b)=>a+b,0);
const bagMax=()=>FISH.bagMax+(st().plus||0);  /* 日本商人的加大魚簍 */
const nameOf=id=>SPECIES.find(s=>s.id===id).name;
const card=async k=>{if(S.cards[k])return;S.cards[k]=true;await say({p:'hero',html:`<div class="card"><b>${CARDS[k].title}</b><p>${CARDS[k].text}</p></div><p class="good">獲得知識卡</p>`});};
const F=()=>debug&&window.__ch3FishForce||null;  /* 只有 #debug：測試用的指定結果 */
async function biteGame(){
  const f=F();if(f&&f.hit!=null){await say({p:'hero',html:'<p>浮標沉下去了……</p>'});return f.hit;}
  const zone=Math.floor(Math.random()*(100-FISH.biteZone));
  return say({p:'hero',who:'釣魚',html:`<p class="small" id="fm">浮標一動也不動……</p>
    <div style="height:22px;background:#E4DCCB;border-radius:11px;position:relative;overflow:hidden;margin:8px 0"><div style="position:absolute;left:${zone}%;width:${FISH.biteZone}%;top:0;bottom:0;background:rgba(91,163,100,.55)"></div><div id="fk" style="position:absolute;top:0;bottom:0;width:6px;background:#2A1D08;left:0;visibility:hidden"></div></div>
    <button id="fp" type="button" class="btn primary" style="width:100%;touch-action:manipulation" disabled>拉竿！</button>`,buttons:[],
    onRender:(root,fin)=>{
      const q=id=>root.querySelector('#'+id);let t0=null,tick=null,over=false;
      const end=v=>{if(over)return;over=true;clearInterval(tick);clearTimeout(w);document.removeEventListener('keydown',kd);fin(v);};
      const w=setTimeout(()=>{q('fm').innerHTML='<b>上鉤了！趕快在綠色範圍內拉竿！</b>（也可以按空白鍵）';q('fp').disabled=false;q('fk').style.visibility='visible';t0=performance.now();
        tick=setInterval(()=>{const p=((performance.now()-t0)/1000*FISH.biteSpeed)%200;q('fk').style.left=(p<=100?p:200-p)+'%';
          if(performance.now()-t0>6000)end(false);},30);},RM_WAIT());
      const pull=()=>{if(t0==null||over)return;const p=((performance.now()-t0)/1000*FISH.biteSpeed)%200,x=p<=100?p:200-p;end(x>=zone&&x<=zone+FISH.biteZone);};
      const kd=e=>{if(e.code==='Space'){e.preventDefault();pull();}};document.addEventListener('keydown',kd);q('fp').onclick=pull;}});
}
const RM_WAIT=()=>600+Math.floor(Math.random()*900);
const ruler=size=>`<div style="position:relative;height:22px;background:#E4DCCB;border-radius:11px;overflow:hidden;margin:8px 0"><div style="width:${size}%;height:100%;background:#5BA3C9"></div><div style="position:absolute;left:${FISH.sizeLine}%;top:0;bottom:0;width:3px;background:#B3402A"></div></div><p class="small">紅線＝要留下的最小尺寸（遊戲設定）</p>`;
async function protectedCatch(sp){
  await say({p:'hero',html:`${img('ch3_p_'+sp.id,150)}<p>釣線另一端傳來很重的力量……不是魚，是一隻<b>${sp.name}</b>！</p>`});
  await quiz('hero',`釣到了${sp.name}，你要怎麼做？`,['把牠拉上岸，拍照給大家看','把牠留下來，拿去賣','小心地剪斷魚線，把牠放回海裡'],2,'海龜、鯨豚、鯨鯊、鬼蝠魟等是保育類野生動物，不能騷擾、獵捕、買賣或持有。意外釣到要小心放回海裡，不要拖上岸。');
  st().rel++;addRep(1);
  await say({p:'hero',html:'<p class="good">牠慢慢游走了。港口信譽 +1</p>'});
  await card('ch3_c_protected');
}
async function fishOutcome(sp,size){
  const f=st(),small=size<FISH.sizeLine;
  const i=await say({p:'hero',who:'釣到了！',html:`${img('ch3_f_'+sp.id,90)}<p><b>${sp.name}</b>　大小 ${size}</p>${ruler(size)}`,buttons:[{label:'留下',primary:!small},{label:'放回海裡',primary:small}]});
  if(small){
    if(i===0)await say({p:'ch3_fishwife',html:'<p>這麼小的魚我們不收。讓牠回去長大，以後才有魚可以釣。</p>'});
    f.rel++;if(f.rel%FISH.relPerRep===0){addRep(1);toast('放回小魚：港口信譽 +1');}
    await say({p:'hero',html:'<p class="good">小魚游回海裡了。</p>'});await card('ch3_c_size');return;}
  if(i===1){f.rel++;await say({p:'hero',html:'<p>牠游回海裡了。</p>'});return;}
  if(bagN()>=bagMax()){await say({p:'hero',html:`<p class="bad">魚簍滿了（${bagMax()} 隻），裝不下。到魚攤賣一些吧。</p>`});return;}
  f.bag[sp.id]=(f.bag[sp.id]||0)+1;
  await say({p:'hero',html:`<p class="good">留下了一隻${sp.name}。</p><p class="small">魚簍 ${bagN()}/${bagMax()}。可以拿去魚攤賣，或請老闆娘烤來吃。</p>`});}
async function fishSpot(spot){
  const P=spot==='lh'?FISH.lh:FISH,f=st();
  if(!f.rod){await say({p:'hero',html:'<p>這裡可以釣魚，不過我沒有釣竿。魚攤有賣。</p>'});return;}
  if(S.sta<FISH.castSta){await say({p:'hero',html:'<p>太累了，先休息一下再釣吧。</p>'});return;}
  S.sta-=FISH.castSta;refresh();f.n++;
  const hit=await biteGame();
  if(!hit){await say({p:'hero',html:'<p>魚跑掉了……再試一次吧。</p>'});return;}
  const fo=F(),r=fo&&fo.roll!=null?fo.roll:Math.random();
  if(r<P.protectedChance){const sp=PROTECTED[fo&&fo.pi!=null?fo.pi:Math.floor(Math.random()*PROTECTED.length)];return protectedCatch(sp);}
  const sp=fo&&fo.sp?SPECIES.find(s=>s.id===fo.sp):pickSpecies(Math.random(),spot==='lh'?FISH.lh.w:null);
  const size=fo&&fo.size!=null?fo.size:(Math.random()<P.smallChance?10+Math.floor(Math.random()*(FISH.sizeLine-10)):FISH.sizeLine+Math.floor(Math.random()*(100-FISH.sizeLine+1)));
  return fishOutcome(sp,size);}
async function stall(){
  for(;;){
    const f=st(),n=bagN();
    const bagTxt=n?Object.entries(f.bag).filter(([,c])=>c>0).map(([k,c])=>`${nameOf(k)} ×${c}`).join('、'):'空的';
    const labels=[];const act=[];
    labels.push(f.rod?'釣竿：已經有了':`買釣竿（${FISH.rodPrice} 金幣）`);act.push('rod');
    labels.push('賣出漁獲');act.push('sell');labels.push('請老闆娘烤一條魚（體力 +'+FISH.eatSta+'）');act.push('eat');
    labels.push('看看大網');act.push('net');labels.push('離開');act.push('bye');
    const i=await say({p:'ch3_fishwife',html:`${f.rod?img('ch3_rod',50):''}<p>要買賣什麼嗎？</p><p class="small">魚簍：${bagTxt}　金幣 ${S.coins}</p>`,
      buttons:labels.map((l,k)=>({label:l,primary:k===1,disabled:(act[k]==='rod'&&(f.rod||S.coins<FISH.rodPrice))||(act[k]==='sell'&&!n)||(act[k]==='eat'&&!n)}))});
    const a=act[i];
    if(a==='bye')return;
    if(a==='rod'){S.coins-=FISH.rodPrice;f.rod=true;refresh();toast('買到釣竿了！');}
    else if(a==='sell'){let t=0;for(const [k,c] of Object.entries(f.bag))t+=c*SPECIES.find(s=>s.id===k).price;f.bag={};S.coins+=t;S.earned=(S.earned||0)+t;refresh();
      await say({p:'ch3_fishwife',html:`<p>都是大小合適的好魚！</p><p class="good">賣了 ${t} 金幣</p>`});}
    else if(a==='eat'){const k=Object.keys(f.bag).find(x=>f.bag[x]>0);f.bag[k]--;S.sta=Math.min(staMax(),S.sta+FISH.eatSta);refresh();
      await say({p:'ch3_fishwife',html:`<p>烤得熱騰騰的，要吃熟的才安全。</p><p class="good">吃了${nameOf(k)}，體力 +${FISH.eatSta}</p>`});await card('ch3_c_cook');}
    else if(a==='net'){
      await say({p:'ch3_fishwife',html:'<p>有個商人推銷一張很大的流刺網，說一次可以撈上好幾簍魚。</p>'});
      await quiz('hero','要不要買這張大網？',['買！撈得越多賺得越多','不買。大網會把大小魚、保育類動物一起纏住，不適用','買來，只撈大魚就好'],1,'流刺網不分大小，也不分保育類，會把魚、海龜、鯨豚、海鳥一起纏住。台灣不少地方已經限制或禁止。用釣竿一次一隻，才能選擇要留下還是放回。');
      await card('ch3_c_gear');}
  }}
const things=id=>{
  if(!on())return [];
  if(id==='ch3_harbor')return [{kind:'ch3_fishspot',x:FISH.spots.pier.x,y:FISH.spots.pier.y,label:FISH.spots.pier.label}];
  if(id==='ch3_lighthouse')return lhOpen&&lhOpen()?[{kind:'ch3_fishspot_lh',x:FISH.spots.lh.x,y:FISH.spots.lh.y,label:FISH.spots.lh.label}]:[];
  if(id==='ch3_market')return [{kind:'ch3_stall',x:FISH.stallAt.x,y:FISH.stallAt.y,label:'魚攤'}];
  return [];};
const build=(id,H,{sprite})=>{
  if(!on())return;
  const put=(x,y,k,h)=>{const e=sprite('shadow','',x,y,Math.round(H*h),RATIO[k]);e.querySelector('img').src=A[k];};
  if(id==='ch3_harbor')put(FISH.spots.pier.x,FISH.spots.pier.y,'ch3_fish_spot',2.1);
  if(id==='ch3_market')put(FISH.stallAt.x,FISH.stallAt.y,'ch3_fish_stall',2.0);};
return {things,build,acts:{ch3_fishspot:()=>fishSpot('pier'),ch3_fishspot_lh:()=>fishSpot('lh'),ch3_stall:stall},st};
}
