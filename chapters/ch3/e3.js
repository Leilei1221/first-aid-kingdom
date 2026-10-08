/* 第三章「藍堡的日常」E3：各國商人（日本、澳洲、尼泊爾）、中英雙語、海圖碎片、登山裝備與登山包、換裝入口。
 * 草稿：只有老師預覽或 #debug ?e1=1 看得到。狀態記在 S.c.ch3_e3（見 wear.js）與 S.c.ch3_pack（登山包等級，核心用來提高負重門檻）。
 * 商船每 3 天輪流靠岸一艘、停 2 天；價格、收購價都是遊戲參數，在 e3.json。 */
import wearInit from './wear.js';
import {SPECIES,FISH} from './fish.js';
export const CYCLE={days:3,stay:2,order:['jp','au','np']};
export const merchantOn=day=>day%CYCLE.days<CYCLE.stay?CYCLE.order[Math.floor(day/CYCLE.days)%CYCLE.order.length]:null;
export const nextArrival=day=>{for(let d=day;d<day+CYCLE.days*2;d++)if(merchantOn(d)&&d>day)return d;return null;};
export default function(FA,{on,preview,previewM,rep,fishSt}){
const {say,lines,toast,refresh,A,RATIO,ITEMS,staMax,base,expired,sprite,$}=FA;
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
const W=wearInit(FA,{on});
let D=null;const data=async()=>D||(D=await (await fetch(new URL('e3.json',import.meta.url))).json());
const st=()=>{const e=W.st();e.seen=e.seen||{};e.frag=e.frag||{};e.own=e.own||{};e.cnt=e.cnt||{};
  if(on()&&!e.init){e.init=true;e.own.o_knight=true;}  /* 披風騎士：第一次開啟時就送 */
  if(preview&&!e.own.jacket){['jacket','hat','pants','gloves','boots','goggles','o_sailor','o_climber','o_lifeguard'].forEach(k=>e.own[k]=true);}  /* 預覽：全部都有，方便試穿 */
  return e;};
const today=()=>preview&&previewM?previewM:merchantOn(S.day);
const img=(k,h)=>k&&A[k]?`<img src="${A[k]}" alt="" style="display:block;margin:6px auto;max-height:${h}px;max-width:100%">`:'';
const showBtn=()=>{const b=$('btnWear');if(!b)return;const n=on()?Object.keys(st().own).length:0;b.hidden=!(on()&&(preview||n>1));};
async function fragment(k,M){
  const e=st();if(e.frag[k])return;e.frag[k]=1;const n=Object.keys(e.frag).length;
  await say({icon:'🧭',who:'獲得：海圖碎片',html:`${img('ch3_map_frag',120)}<p>${M.name.split(' ')[0]}給了你一片舊海圖的碎片。（${n}/3）</p>`+(n>=3?'<p class="good">三片碎片拼在一起了，上面畫著遠方的海岸和山。以後也許會用到。</p>':'')});}
function rowHtml(r){return `<div class="row" style="align-items:center">${r.icon?`<img src="${A[r.icon]}" alt="" style="width:46px;height:46px;object-fit:contain;margin-right:8px">`:''}<div class="info"><b>${r.name}</b><span>${r.desc||''}</span></div><button type="button" data-a="${r.id}" ${r.disabled?'disabled':''}>${r.label}</button></div>`;}
async function pickFrom(M,rowsFn,title){
  let msg='';
  for(;;){
    const rows=rowsFn();
    const r=await say({p:M.id,html:`${msg?`<p class="good">${msg}</p>`:''}<p class="small">${title}　金幣 ${S.coins}　急救背包 ${S.kit.length}/${S.kitCap}</p>${rows.map(rowHtml).join('')||'<p>目前沒有可以交易的東西。</p>'}`,buttons:[{label:'回上一頁',primary:true}],
      onRender:(root,fin)=>root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{rows.find(x=>x.id===b.dataset.a).run();msg=rows.find(x=>x.id===b.dataset.a).done||'';fin('pick');})});
    if(r!=='pick')return;}}
function buyRows(k,D){
  const e=st(),cur=S.c.ch3_pack|0;
  return D.GOODS[k].map(g=>{
    if(g.type==='kit'){const it=ITEMS[g.k],full=S.kit.length>=S.kitCap;return {id:g.k,icon:null,name:it.name,desc:'急救用品',label:`買（${it.price}）`,disabled:S.coins<it.price||full,done:`買了 ${it.name}`,run(){S.coins-=it.price;S.kit.push(g.k);refresh();}};}
    const own=g.type==='gear'?!!e.own[g.k]:g.type==='pack'?cur>=g.lv:g.type==='outfit'?!!e.own[g.k]:g.type==='bag'?!!(fishSt().plus):false;
    const need=g.type==='pack'&&g.lv>cur+1;
    return {id:g.k,icon:D.ICONS[g.k],name:g.name,desc:g.desc+(g.type==='count'?`（現有 ${e.cnt[g.k]||0}）`:''),label:own?'已擁有':need?'先買小的':`買（${g.price}）`,disabled:own||need||S.coins<g.price,done:`買了 ${g.name.split(' ')[0]}`,
      run(){S.coins-=g.price;
        if(g.type==='gear'||g.type==='outfit')e.own[g.k]=1;
        else if(g.type==='count')e.cnt[g.k]=(e.cnt[g.k]||0)+1;
        else if(g.type==='pack'){const P=FA.PACKS[g.lv-1];S.kitCap=P.cap;S.c.ch3_pack=g.lv;}
        else if(g.type==='bag')fishSt().plus=4;
        else if(g.type==='food')S.sta=Math.min(staMax(),S.sta+15);
        refresh();showBtn();}};});}
function sellRows(k,D){
  const sp=D.SELL[k];
  if(sp.kind==='fish'){const f=fishSt();return Object.entries(f.bag||{}).filter(([,c])=>c>0).map(([id,c])=>{const s=SPECIES.find(x=>x.id===id),pay=Math.round(s.price*sp.mul);return {id,icon:'ch3_f_'+id,name:`${s.name} ×${c}`,desc:'比市集多三成',label:`賣 1（${pay}）`,done:`賣了 1 隻${s.name}，${pay} 金幣`,run(){f.bag[id]--;S.coins+=pay;S.earned=(S.earned||0)+pay;refresh();}};});}
  const items=sp.kind==='kit'?[sp.item]:sp.items;
  return items.map(it=>{const n=S.kit.filter(x=>base(x)===it&&!expired(x)).length;return {id:it,icon:null,name:`${ITEMS[it].name} ×${n}`,desc:'',label:`賣 1（${sp.pay}）`,disabled:!n,done:`賣了 1 個${ITEMS[it].name}，${sp.pay} 金幣`,
    run(){const i=S.kit.findIndex(x=>base(x)===it&&!expired(x));if(i>=0){S.kit.splice(i,1);S.coins+=sp.pay;S.earned=(S.earned||0)+sp.pay;refresh();}}};});}
async function merchant(){
  const k=today();if(!k)return;const D=await data(),M=D.MERCHANTS[k],e=st();
  if(!e.seen[k]){e.seen[k]=true;await say({p:M.id,html:`${img(M.ship,110)}<p>${M.hello[0]}</p>`});await say({p:M.id,html:`<p>${M.hello[1]}</p>`});await fragment(k,M);}
  for(;;){
    const i=await say({p:M.id,html:`${img(M.ship,90)}<p>${M.name.split('（')[0]}：要買點什麼嗎？ What would you like?</p>`,buttons:[{label:'買東西 Buy',primary:true},{label:'賣東西 Sell'},{label:'聊聊（學英文）'},{label:'離開 Bye'}]});
    if(i===0)await pickFrom(M,()=>buyRows(k,D),'買東西');
    else if(i===1){await say({p:M.id,html:`<p>${M.sellNote}</p>`});await pickFrom(M,()=>sellRows(k,D),'賣東西');}
    else if(i===2){await lines(M.id,M.talk);}
    else return;}}
const things=id=>{if(id!=='ch3_harbor'||!on()||!today())return [];const M=D&&D.MERCHANTS[today()];return [{kind:'ch3_merchant',x:900,y:540,label:M?M.name.split('（')[0]:'商人'}];};
const build=(id,H,{sprite})=>{
  showBtn();W.update();
  if(id!=='ch3_harbor'||!on()||!today())return;
  const k=today(),key='ch3_m_'+k,s=sprite('shadow','',900,540,Math.round(H*1.05),RATIO[key]);s.querySelector('img').src=A[key];};
/* 外面的 NPC 賣整套造型：水手服（老船長）、救生員裝（信譽夠了，向救生員領） */
const sailorOffer=()=>on()&&!st().own.o_sailor;
const lifegOffer=()=>on()&&!st().own.o_lifeguard&&rep()>=8;
async function buySailor(){const e=st();if(S.coins<200){await say({p:'ch3_captain',html:'<p>水手服要 200 金幣。存夠了再來吧。</p>'});return;}S.coins-=200;e.own.o_sailor=1;refresh();showBtn();await say({p:'ch3_captain',html:'<p>哈哈，穿上這身，你也是半個水手了！</p><p class="good">獲得整套造型：水手（到上方「換裝」穿上）</p>'});}
async function giveLifeg(){const e=st();e.own.o_lifeguard=1;showBtn();await say({p:'ch3_lifeg',html:'<p>你幫了港口這麼多忙，這套救生員的裝備送給你。</p><p class="good">獲得整套造型：救生員（到上方「換裝」穿上）</p>'});}
const boardExtra=()=>{if(!on())return '';const k=today(),Dd=D;const nm=x=>Dd?Dd.MERCHANTS[x].from:x;
  if(k)return `<p>今天靠岸的商船：<b>${nm(k)}</b>（走到港口廣場找商人）</p>`;
  const nx=nextArrival(S.day);return nx?`<p>今天沒有商船靠岸。下一艘：第 ${nx} 天（${nm(merchantOn(nx))}）</p>`:'';};
return {things,build,acts:{ch3_merchant:merchant},wardrobe:W.wardrobe,wear:W.wardrobe,sailorOffer,lifegOffer,buySailor,giveLifeg,boardExtra,load:data,st};
}
