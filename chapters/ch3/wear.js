/* 第三章「藍堡的日常」E3：換裝的疊件（外套、毛帽，可換 10 種顏色），疊在目前穿的整套裝扮上。整套裝扮由核心的「背包 → 裝扮」換（老師另一個決定的功能），這裡只管疊件。
 * 草稿：只有老師預覽或 #debug ?e1=1 看得到。狀態記在 S.c.ch3_e3（wear）。
 * 換色用逐像素的色相旋轉（不用 canvas filter，因為 iPad Safari 不支援）。疊件的位置是遊戲參數，可調。 */
export const COLORS=[['紅',0],['橙',28],['黃',52],['綠',120],['青',170],['藍',215],['紫',275],['粉',325],['灰',-1],['黑',-2]];
export const LAYERS={  /* 疊件在 330×520 主角畫布上的位置（x、y、寬），高度依圖片比例 */
  jacket:{name:'外套',img:'ch3_g_jacket',x:62,y:96,w:190},
  hat:{name:'毛帽',img:'ch3_g_hat',x:92,y:-58,w:92}};
function recolor(ctx,x,y,w,h,mode){
  if(mode===0)return;
  const d=ctx.getImageData(x,y,w,h),a=d.data;
  for(let i=0;i<a.length;i+=4){if(!a[i+3])continue;
    let r=a[i]/255,g=a[i+1]/255,b=a[i+2]/255;const mx=Math.max(r,g,b),mn=Math.min(r,g,b),l=(mx+mn)/2,dl=mx-mn;
    let hh=0,s=0;if(dl>0){s=dl/(1-Math.abs(2*l-1));hh=mx===r?((g-b)/dl)%6:mx===g?(b-r)/dl+2:(r-g)/dl+4;hh*=60;if(hh<0)hh+=360;}
    let nl=l;
    if(mode===-1){s*=.08;}else if(mode===-2){s*=.08;nl=l*.5;}else hh=(hh+mode)%360;
    const c=(1-Math.abs(2*nl-1))*s,x2=c*(1-Math.abs((hh/60)%2-1)),m=nl-c/2;
    let R,G,B;const k=Math.floor(hh/60);[R,G,B]=[[c,x2,0],[x2,c,0],[0,c,x2],[0,x2,c],[x2,0,c],[c,0,x2]][k%6];
    a[i]=Math.round((R+m)*255);a[i+1]=Math.round((G+m)*255);a[i+2]=Math.round((B+m)*255);}
  ctx.putImageData(d,x,y);}
const loadImg=src=>new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=rej;i.src=src;});
export default function(FA,{on}){
const {say,A,RATIO}=FA;
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
const st=()=>{S.c=S.c||{};return S.c.ch3_e3||(S.c.ch3_e3={frag:{},own:{},cnt:{},seen:{},wear:{}});};
let url=null,key='';
const wornKey=()=>{const e=st();return JSON.stringify([FA.outfitBase(),e.wear]);};
async function compose(e){
  const cv=document.createElement('canvas');cv.width=330;cv.height=520;const ctx=cv.getContext('2d');
  ctx.drawImage(await loadImg(FA.outfitBase()),0,0,330,520);
  for(const [k,L] of Object.entries(LAYERS)){const w=e.wear[k];if(!w||!w.on||!e.own[k])continue;
    const im=await loadImg(A[L.img]),h=Math.round(L.w/(im.width/im.height));
    const t=document.createElement('canvas');t.width=L.w;t.height=h;const tc=t.getContext('2d');tc.drawImage(im,0,0,L.w,h);recolor(tc,0,0,L.w,h,COLORS[w.c||0][1]);
    ctx.drawImage(t,L.x,L.y);}
  return cv;}
async function update(){
  const e=st();key=wornKey();
  if(!on()||!Object.values(e.wear).some(w=>w&&w.on)){url=null;FA.refreshHero();return;}
  try{url=(await compose(e)).toDataURL('image/png');}catch(_){url=null;}FA.refreshHero();}
const look=()=>on()&&url&&key===wornKey()?url:null;
FA.setHeroLook(look,()=>{update();});  /* 換整套裝扮時，核心會通知這裡重新合成 */
async function wardrobe(){
  const e=st();
  for(;;){
    const ownL=Object.entries(LAYERS).filter(([k])=>e.own[k]);
    let cv=null;try{cv=await compose(e);}catch(_){}
    const r=await say({p:'hero',who:'換裝',html:`<div style="display:flex;gap:12px;align-items:flex-start"><div style="flex:0 0 150px;text-align:center"><canvas id="wv" width="330" height="520" style="width:150px;border-radius:10px;background:rgba(255,255,255,.06)"></canvas></div><div style="flex:1;min-width:0">
      <p class="small">疊件：穿在目前的裝扮外面（整套裝扮到背包的「裝扮」換）</p>
      ${ownL.length?ownL.map(([k,L])=>{const w=e.wear[k]||{};return `<div style="margin-bottom:6px"><button type="button" class="btn${w.on?' primary':''}" data-t="${k}">${L.name}：${w.on?'穿著':'沒穿'}</button><div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">${COLORS.map(([n],ci)=>`<button type="button" class="btn${(w.c||0)===ci?' primary':''}" data-c="${k}:${ci}" style="padding:2px 8px;min-width:0">${n}</button>`).join('')}</div></div>`;}).join(''):'<p class="small" style="margin-top:10px">買了外套或毛帽，這裡就可以疊在身上、換顏色。</p>'}
      </div></div>`,buttons:[{label:'完成',primary:true}],
      onRender:(root,fin)=>{
        const paint=c=>{const v=root.querySelector('#wv');if(v&&c)v.getContext('2d').drawImage(c,0,0);};paint(cv);
        root.querySelectorAll('button[data-t]').forEach(b=>b.onclick=()=>{const k=b.dataset.t;e.wear[k]=Object.assign({c:0},e.wear[k],{on:!(e.wear[k]&&e.wear[k].on)});fin('again');});
        root.querySelectorAll('button[data-c]').forEach(b=>b.onclick=()=>{const [k,c]=b.dataset.c.split(':');e.wear[k]=Object.assign({},e.wear[k],{on:true,c:+c});fin('again');});}});
    if(r!=='again')break;}
  await update();}
return {update,wardrobe,look,st};
}
