/* 第三章「藍堡的日常」E3：冬季裝備（防寒外套＋保暖毛帽，5 種顏色）。老師 2026-10-10 改成「整張全身圖」：每套裝扮（預設、水手、登山、救生員、守護者）各有穿上外套與毛帽的圖，
 * 檔名 assets/outfit_<套>_<色>.webp（tools/outfit_winter_import.py 匯入），不再用疊圖與逐像素換色。
 * 要同時買了外套與毛帽才能穿；整套裝扮由核心的「背包 → 裝扮」換，這裡只管「穿不穿冬季裝備」與顏色。
 * 狀態記在 S.c.ch3_e3.wear＝{on,c}（舊存檔的 wear.jacket／wear.hat 會自動轉過來）。 */
export const COLORS=[['紅','red'],['藍','blue'],['綠','green'],['黃','yellow'],['灰','gray']];
const baseId=base=>{const m=/outfit_(\w+?)\.webp/.exec(String(base||''));return m?m[1]:'default';};
export const winterSrc=(base,c)=>`assets/outfit_${baseId(base)}_${(COLORS[c]||COLORS[0])[1]}.webp`;
export const norm=e=>{const w=e.wear=e.wear||{};
  if(w.on===undefined&&(w.jacket||w.hat)){w.on=!!((w.jacket&&w.jacket.on)||(w.hat&&w.hat.on));w.c=0;}
  delete w.jacket;delete w.hat;if(!(w.c>=0&&w.c<COLORS.length))w.c=0;return w;};
export default function(FA,{on}){
const {say}=FA;
const st=()=>{FA.S.c=FA.S.c||{};const e=FA.S.c.ch3_e3||(FA.S.c.ch3_e3={frag:{},own:{},cnt:{},seen:{},wear:{}});norm(e);return e;};
const has=e=>!!(e.own&&e.own.jacket&&e.own.hat);
const look=()=>{if(!on())return null;const e=st();return e.wear.on&&has(e)?winterSrc(FA.outfitBase(),e.wear.c):null;};
const update=()=>{FA.refreshHero();};
FA.setHeroLook(look,()=>{});
async function wardrobe(){
  const e=st();
  for(;;){
    const w=e.wear,src=winterSrc(FA.outfitBase(),w.c);
    const r=await say({p:'hero',who:'換裝',html:`<div style="display:flex;gap:12px;align-items:flex-start"><div style="flex:0 0 150px;text-align:center"><img id="wv" alt="" src="${w.on&&has(e)?src:FA.outfitBase()}" style="width:150px;border-radius:10px;background:rgba(255,255,255,.06)"></div><div style="flex:1;min-width:0">
      <p class="small">冬季裝備：防寒外套＋保暖毛帽，穿在目前的裝扮上（整套裝扮到背包的「裝扮」換）</p>
      ${has(e)?`<div style="margin-bottom:6px"><button type="button" class="btn${w.on?' primary':''}" data-t="1">冬季裝備：${w.on?'穿著':'沒穿'}</button><div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">${COLORS.map(([n],ci)=>`<button type="button" class="btn${w.c===ci?' primary':''}" data-c="${ci}" style="padding:2px 8px;min-width:0">${n}</button>`).join('')}</div></div>`:'<p class="small" style="margin-top:10px">防寒外套和保暖毛帽都買了，就可以穿上冬季裝備、換顏色。</p>'}
      </div></div>`,buttons:[{label:'完成',primary:true}],
      onRender:(root,fin)=>{
        root.querySelectorAll('button[data-t]').forEach(b=>b.onclick=()=>{w.on=!w.on;fin('again');});
        root.querySelectorAll('button[data-c]').forEach(b=>b.onclick=()=>{w.on=true;w.c=+b.dataset.c;fin('again');});}});
    if(r!=='again')break;}
  update();}
return {update,wardrobe,look,st,has};
}
