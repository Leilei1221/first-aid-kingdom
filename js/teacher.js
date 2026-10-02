/* 老師端進度頁（只讀）。資料來源：教室系統的班級與名單（hc_classes、hc_students）＋ 遊戲存檔（fa_saves）。
 * 權限由資料庫的 RLS 決定：老師只能讀到自己班上學生的存檔；本頁另外只列 teacher_id 等於自己的班級。
 * 測試時可用 window.__faTeacherApi 取代真實的 Supabase 存取。 */
(function(){
const CFG=window.FA_CONFIG||{};
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

/* ---------- 進度計算（純函式） ---------- */
const STEP_LABEL=['開場','向阿木借斧頭','賣木材','接委託、擴充包包','阿木受傷事件','買急救用品、幫村民包紮','回報爺爺','農田與礦坑','建造乾糧製造機','做出第一包乾糧','第二階段完成'];
function milestones(s){
  const f=s.f||{},m=[];
  for(let i=1;i<=10;i++)m.push((s.step||0)>=i);
  m.push(!!f.p3,!!f.tablet,!!f.hunter,!!f.guard,!!s.castleDone,!!f.final);
  return m;}
function stageLabel(s){
  const f=s.f||{},st=s.step||0;
  if(f.final)return '序章完成';
  if(s.castleDone)return '城堡已通關（待回報爺爺）';
  if(f.p3)return '東邊區域（石碑、阿鹿、城堡）';
  return STEP_LABEL[Math.min(st,10)];}
/* 第二章（S.c）：沒有收到信、沒進過鍛造鎮就當作「未開始」；進度百分比只算序章，第二章另外顯示 */
function ch2Of(s){const c=s.c||{};
  if(c.done)return {label:'已完成',stars:c.stars||0,done:true};
  if(c.intro||c.smith||c.fire)return {label:'進行中',stars:c.stars||0,done:false};
  if(c.letter)return {label:'已收到信',stars:0,done:false};
  return {label:'',stars:0,done:false};}
function summarize(state,cardTotal){
  const s=state||{},m=milestones(s),done=m.filter(Boolean).length;
  return {day:s.day||1,stage:stageLabel(s),pct:Math.round(done/m.length*100),stars:s.castleBest||0,castleDone:!!s.castleDone,
    cards:Object.keys(s.cards||{}).length,cardTotal:cardTotal||0,coins:s.coins||0,hearts:s.hearts||{},ch2:ch2Of(s)};}
const pad=n=>String(n).padStart(2,'0');
function fmtTime(iso){if(!iso)return '';const d=new Date(iso);if(isNaN(d))return '';return `${d.getMonth()+1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;}
function ago(iso){if(!iso)return '';const m=Math.round((Date.now()-new Date(iso))/60000);if(m<1)return '剛剛';if(m<60)return m+' 分鐘前';if(m<1440)return Math.round(m/60)+' 小時前';return Math.round(m/1440)+' 天前';}
function csv(rows){return '﻿'+rows.map(r=>r.map(v=>{v=v==null?'':String(v);return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}).join(',')).join('\r\n');}

/* ---------- 真實的 Supabase 存取 ---------- */
function loadLib(){return new Promise((res,rej)=>{
  if(window.supabase&&window.supabase.createClient)return res();
  const s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js';
  const t=setTimeout(()=>rej(new Error('逾時')),10000);
  s.onload=()=>{clearTimeout(t);res();};s.onerror=()=>{clearTimeout(t);rej(new Error('載入失敗'));};document.head.appendChild(s);});}
async function makeApi(){
  await loadLib();
  const c=window.supabase.createClient(CFG.url,CFG.anonKey,{auth:{flowType:'pkce',persistSession:true,detectSessionInUrl:true,autoRefreshToken:true}});
  const must=r=>{if(r.error)throw r.error;return r.data;};
  return {
    async user(){const {data}=await c.auth.getSession();return data.session?data.session.user:null;},
    signIn(){return c.auth.signInWithOAuth({provider:'google',options:{redirectTo:location.origin+location.pathname}});},
    async signOut(){await c.auth.signOut();},
    async isTeacher(){return must(await c.rpc('hc_is_allowed_teacher'))===true;},
    async classes(uid){return must(await c.from('hc_classes').select('id,name,grade,academic_year,semester').eq('teacher_id',uid).eq('is_active',true).order('grade').order('name'));},
    async students(cid){return must(await c.from('hc_students').select('id,student_no,seat_no,name,email,login_email').eq('class_id',cid).eq('is_active',true).order('seat_no'));},
    /* 班級控制（supabase/drafts/002_fa_class_control.sql）：老師只能碰自己班，權限靠 RLS */
    async flags(cid){return must(await c.from('fa_class_flags').select('flag,enabled').eq('class_id',cid));},
    async setFlag(cid,flag,enabled){must(await c.from('fa_class_flags').upsert({class_id:cid,flag,enabled},{onConflict:'class_id,flag'}));},
    async weather(cid){return must(await c.from('fa_class_weather').select('id,type,published_at,cancelled').eq('class_id',cid).order('id',{ascending:false}).limit(5));},
    async publishWeather(cid,type){must(await c.from('fa_class_weather').insert({class_id:cid,type}));},
    async cancelWeather(id){must(await c.from('fa_class_weather').update({cancelled:true}).eq('id',id));},
    async failures(emails){if(!emails.length)return [];return must(await c.from('fa_failures').select('email,scenario,choice,created_at').in('email',emails));},
    async saves(emails){if(!emails.length)return [];return must(await c.from('fa_saves').select('email,state,updated_at').in('email',emails));}
  };
}

/* ---------- 畫面 ---------- */
let api=null,user=null,classes=[],rows=[],fails=[],cardTotal=0,names={},scenarioNames={};
let ctrl={flags:{},weather:null,error:null},defaults={ch2:true,ch3:false,wild:false,relief:false},wxNames={};
const FLAGS=[['ch2','第二章（熔岩鍛造鎮）','完成序章並收到爺爺的信後，學生才會看到'],['ch3','第三章（港口藍堡）','完成第二章後，從礦坑入口往南的漁港搭船前往'],['wild','野外項目','營火露營、溺水救援、河谷裝溪水、阿鹿的高山症支線'],['relief','村長救災物資','地震、山洪災後當天與隔天，領乾糧與開水']];
const say=(t,bad)=>{const e=$('status');e.hidden=false;e.textContent=t;e.style.borderColor=bad?'var(--bad)':'';};

async function loadStatic(){
  try{const ix=await (await fetch('chapters/index.json')).json();ix.forEach(c=>{defaults[c.id]=!!c.open;});}catch(e){}
  try{const w=await (await fetch('content/weather.json')).json();defaults.wild=!!w.WILD_ON;defaults.relief=!!w.RELIEF_ON;Object.entries(w.WX||{}).forEach(([k,v])=>wxNames[k]=v.name);}catch(e){}
  try{const c=await (await fetch('content/knowledge_cards.json')).json();cardTotal=Object.keys(c.CARDS||{}).length;}catch(e){}
  try{const r=await (await fetch('content/rescue.json')).json();Object.entries(r.SCENARIOS||{}).forEach(([k,v])=>scenarioNames[k]=v.name);}catch(e){}
  for(const u of ['content/characters.json','chapters/ch2/characters.json']){try{const c=await (await fetch(u)).json();Object.entries(c.PEOPLE||{}).forEach(([k,v])=>names[k]=v.name);}catch(e){}}
}

async function loadControl(cid){
  ctrl={flags:{},weather:null,error:null};
  if(!api.flags){ctrl.error='這個版本沒有班級控制。';return;}
  try{
    (await api.flags(cid)).forEach(r=>ctrl.flags[r.flag]=!!r.enabled);
    ctrl.weather=((await api.weather(cid))||[]).find(w=>!w.cancelled)||null;
  }catch(e){ctrl.error='讀不到班級控制資料表。請先在 Supabase 執行 supabase/drafts/002_fa_class_control.sql。';}
}
function renderControl(){
  const el=$('ctrl');if(!el)return;
  if(ctrl.error){el.innerHTML=`<h3>班級控制</h3><p class="small">${esc(ctrl.error)}</p>`;return;}
  const eff=k=>k in ctrl.flags?ctrl.flags[k]:defaults[k];
  const w=ctrl.weather;
  el.innerHTML=`<h3>班級控制</h3>
    ${FLAGS.map(([k,n,note])=>`<div class="fl"><b>${esc(n)}</b><span>${eff(k)?'開啟':'關閉'}${k in ctrl.flags?'':'（預設）'}</span><button type="button" data-flag="${k}" data-on="${eff(k)?0:1}">${eff(k)?'關閉':'開啟'}</button><small>${esc(note)}</small></div>`).join('')}
    <div class="fl"><b>發布天災</b><span>${w?`目前公告：${esc(wxNames[w.type]||w.type)}（${esc(fmtTime(w.published_at))} 發布）`:'沒有進行中的公告'}</span>
      <span class="wxbtns">${['typhoon','flood','fog'].map(k=>`<button type="button" data-wx="${k}">發布${esc(wxNames[k]||k)}</button>`).join('')}${w?`<button type="button" data-cancel="${esc(w.id)}">取消目前公告</button>`:''}</span>
      <small>學生遊戲會把它排成「自己遊戲的明天」天災，每則公告每位學生只套用一次；只套用近兩天內發布的。</small></div>`;
}
async function onControlClick(e){
  const b=e.target.closest('button');if(!b)return;const cid=$('cls').value;
  try{
    if(b.dataset.flag){await api.setFlag(cid,b.dataset.flag,b.dataset.on==='1');}
    else if(b.dataset.wx){if(!confirm(`要對這個班發布「${wxNames[b.dataset.wx]||b.dataset.wx}」嗎？學生遊戲會在下一次讀取設定時收到預報。`))return;await api.publishWeather(cid,b.dataset.wx);}
    else if(b.dataset.cancel){await api.cancelWeather(b.dataset.cancel);}
    else return;
    await loadControl(cid);renderControl();
  }catch(err){say('儲存失敗：'+(err&&err.message||err),true);}
}
async function loadClass(cid){
  say('讀取中…');
  const sts=await api.students(cid);
  const mail=s=>String(s.login_email||s.email||'').trim().toLowerCase();
  const emails=sts.map(mail).filter(Boolean);
  const saves=await api.saves(emails);
  try{fails=api.failures?await api.failures(emails):[];}catch(e){fails=[];}  /* 失敗記錄讀不到不影響進度頁 */
  const by={};saves.forEach(r=>by[String(r.email).toLowerCase()]=r);
  rows=sts.map(s=>{const r=by[mail(s)];return {seat:s.seat_no,no:s.student_no,name:s.name,email:mail(s),updated:r?r.updated_at:null,sum:r?summarize(r.state,cardTotal):null};});
  await loadControl(cid);renderControl();render();$('status').hidden=true;
}

/* 全班最常犯的錯：每個情境有幾位學生、共幾次，以及最常選的那個答案 */
function failSummary(list){const by={};
  list.forEach(f=>{const s=by[f.scenario]||(by[f.scenario]={scenario:f.scenario,n:0,who:new Set(),choices:{}});s.n++;s.who.add(String(f.email).toLowerCase());s.choices[f.choice]=(s.choices[f.choice]||0)+1;});
  return Object.values(by).map(s=>({scenario:s.scenario,times:s.n,students:s.who.size,top:Object.entries(s.choices).sort((a,b)=>b[1]-a[1])[0][0]})).sort((a,b)=>b.students-a.students||b.times-a.times);}
function render(){
  const started=rows.filter(r=>r.sum);
  const fs=failSummary(fails);
  $('fails').innerHTML=fs.length?`<h3>全班最常犯的錯（救援失敗）</h3>`+fs.map(f=>`<div class="fl"><b>${esc(scenarioNames[f.scenario]||f.scenario)}</b><span>${f.students} 人、${f.times} 次</span><small>最常選：${esc(f.top)}</small></div>`).join(''):'';
  $('sum').innerHTML=[
    [`${started.length} / ${rows.length}`,'已開始遊戲的人數'],
    [started.length?Math.round(started.reduce((a,r)=>a+r.sum.pct,0)/started.length)+'%':'—','已開始者的平均進度'],
    [started.filter(r=>r.sum.castleDone).length,'通關落石之城'],
    ...(started.some(r=>r.sum.ch2.label)?[[started.filter(r=>r.sum.ch2.done).length,'完成第二章']]:[]),
    [started.filter(r=>r.sum.coins<0).length,'目前有欠款']].map(([b,t])=>`<div><b>${esc(b)}</b><span>${esc(t)}</span></div>`).join('');
  $('list').innerHTML=rows.map(r=>{
    if(!r.sum)return `<details class="st none"><summary><span class="seat">${esc(r.seat)}</span><span class="nm">${esc(r.name)}<small>${esc(r.no)}</small></span><span class="chips">尚未開始</span></summary></details>`;
    const x=r.sum,hearts=Object.entries(x.hearts).map(([k,n])=>`<span>${esc(names[k]||k)} ${'♥'.repeat(Math.min(5,n))}${'♡'.repeat(5-Math.min(5,n))}</span>`).join('');
    return `<details class="st"><summary><span class="seat">${esc(r.seat)}</span><span class="nm">${esc(r.name)}<small>${esc(r.no)}</small></span>
      <span class="prog"><i><em style="width:${x.pct}%"></em></i>${x.pct}%　${esc(x.stage)}</span>
      <span class="chips"><span>第 <b>${x.day}</b> 天</span><span>城堡 <b>${x.stars}</b>★</span>${x.ch2.label?`<span>第二章 <b>${esc(x.ch2.label)}</b>${x.ch2.done?` ${x.ch2.stars}★`:''}</span>`:''}<span>知識卡 <b>${x.cards}</b>/${x.cardTotal}</span><span class="${x.coins<0?'debt':''}">金幣 <b>${x.coins}</b>${x.coins<0?'（欠款）':''}</span></span></summary>
      <div class="body">最後遊玩：<b>${esc(fmtTime(r.updated))}</b>（${esc(ago(r.updated))}）　<span class="small">${esc(r.email)}</span><div class="hearts">${hearts}</div></div></details>`;}).join('')||'<p class="small">這個班級沒有學生名單。</p>';
}

function exportCsv(){
  const cls=classes.find(c=>c.id===$('cls').value)||{};
  const head=['班級','座號','學號','姓名','email','最後遊玩','天數','主線進度%','主線階段','城堡最佳星數','知識卡','知識卡總數','金幣','第二章','第二章星數'];
  const body=rows.map(r=>{const x=r.sum;return [cls.name,r.seat,r.no,r.name,r.email,x?fmtTime(r.updated):'尚未開始',x?x.day:'',x?x.pct:'',x?x.stage:'',x?x.stars:'',x?x.cards:'',x?x.cardTotal:'',x?x.coins:'',x?x.ch2.label:'',x&&x.ch2.done?x.ch2.stars:''];});
  const blob=new Blob([csv([head,...body])],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`急救王國進度_${cls.name||'班級'}.csv`;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},500);
}

async function main(){
  try{api=window.__faTeacherApi||await makeApi();}catch(e){say('無法載入登入元件，請檢查網路後重新整理。',true);return;}
  await loadStatic();
  try{user=await api.user();}catch(e){}
  if(!user){
    $('status').innerHTML='請先登入老師帳號。<br><br><button type="button" id="btnIn" class="primary">用 Google 登入</button>';
    $('btnIn').onclick=()=>api.signIn();return;}
  $('btnOut').hidden=false;$('btnOut').onclick=async e=>{e.preventDefault();await api.signOut();location.reload();};
  $('who').textContent=user.email||'';
  let ok=false;try{ok=await api.isTeacher();}catch(e){}
  if(!ok){say('這個帳號沒有老師端權限。學生帳號請回到遊戲。',true);return;}
  try{classes=await api.classes(user.id);}catch(e){say('讀取班級失敗：'+(e&&e.message||e),true);return;}
  if(!classes.length){say('目前沒有屬於您的班級。');return;}
  $('cls').innerHTML=classes.map(c=>`<option value="${esc(c.id)}">${esc(c.name)}</option>`).join('');
  $('app').hidden=false;
  const go=async()=>{try{await loadClass($('cls').value);}catch(e){say('讀取失敗：'+(e&&e.message||e),true);}};
  $('ctrl').addEventListener('click',onControlClick);
  $('cls').onchange=go;$('btnRefresh').onclick=go;$('btnCsv').onclick=exportCsv;
  await go();
}
window.FATeacher={failSummary,summarize,stageLabel,milestones,csv};
main();
})();
