/* 章節小店（第二章熔岩鍛造鎮用；2026-10-10 老師同意第二章加玩法）：一個通用的買東西選單，沿用現有物品，沒有新寫任何醫療文字。
 * 價格規則：乾糧、開水和船上賣的一樣（SHIP_RATION、SHIP_WATER），體力補給同雜貨店的 STAMINA_SHOP，急救用品與防災小物同雜貨店價格；
 * 沒有好感度折扣、不賒帳。收購不在這裡（商人才收，而且價格受經濟規則限制，見 tools/economy_test.py）。 */
import {SHIP_RATION,SHIP_WATER} from './voyage.js';
export function openStore(FA,S,{who,intro}){
  const {say,refresh,staMax,kitCount}=FA;
  return async function(){
    let msg='';
    for(;;){
      let pick=null;const full=S.kit.length>=S.kitCap;
      const rows=[]
        .concat(FA.SHOP_MED.map(k=>({id:k,name:FA.ITEMS[k].name,price:FA.ITEMS[k].price,desc:FA.ITEMS[k].desc,kit:true,have:kitCount(k)})))
        .concat([{id:'ration',name:'乾糧',price:SHIP_RATION,desc:`免烹煮、耐保存，保存 ${FA.RATION_LIFE} 天。`,kit:true},{id:'water',name:'開水',price:SHIP_WATER,desc:'煮沸過的乾淨開水。',kit:true}])
        .concat(FA.STAMINA_SHOP.food.map(f=>({id:'sta:'+f.id,name:f.name,price:f.cost,desc:`${f.desc}（現在吃下，目前體力 ${S.sta}/${staMax()}）`,eat:f})))
        .concat(FA.SHOP_EXTRA.map(k=>({id:k,name:FA.ITEMS[k].name,price:FA.ITEMS[k].price,desc:FA.ITEMS[k].desc,kit:true,have:kitCount(k)})));
      const html=(msg?`<p class="good">${msg}</p>`:'')+`<p>${intro}</p><p class="small">金幣 ${S.coins}　急救背包 ${S.kit.length}/${S.kitCap}</p>`+rows.map(r=>{
        const dis=S.coins<r.price||(r.kit&&full)||(r.eat&&S.sta>=staMax());
        return `<div class="row"><div class="info"><b>${r.name}${r.have!=null?`　<span style="color:var(--gold)">背包裡有 ${r.have} 個</span>`:''}</b><span>${r.price} 金幣　${r.desc}</span></div><button type="button" data-a="${r.id}" ${dis?'disabled':''}>${r.kit&&full?'背包已滿':r.eat&&S.sta>=staMax()?'體力已滿':'買 1 個'}</button></div>`;}).join('');
      const r=await say({p:'hero',who,html,buttons:[{label:'離開',primary:true}],
        onRender:(root,fin)=>root.querySelectorAll('button[data-a]').forEach(b=>b.onclick=()=>{pick=b.dataset.a;fin('pick');})});
      if(r!=='pick')return;
      const it=rows.find(x=>x.id===pick);if(!it||S.coins<it.price)continue;
      if(it.kit){if(S.kit.length>=S.kitCap)continue;S.coins-=it.price;S.kit.push(it.id==='ration'?'ration@'+(S.day+FA.RATION_LIFE):it.id);msg=`已買下：${it.name} ×1（急救背包 ${S.kit.length}/${S.kitCap}）`;}
      else{if(S.sta>=staMax())continue;S.coins-=it.price;const b4=S.sta;S.sta=Math.min(staMax(),S.sta+it.eat.restore);msg=`吃了${it.name}，體力 +${S.sta-b4}`;}
      refresh();}};}
