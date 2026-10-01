/* 雲端存檔（Supabase）。
 * 沒登入、沒網路、或 CDN 被學校網路擋住時，遊戲照常使用本機存檔，不會壞掉。
 * 本機 meta（fa-kingdom-p1-v1-meta）記錄：這份本機存檔屬於誰、上次同步到雲端的版本、是否有尚未上傳的變更。
 * 遊戲存檔本身（S）完全不加欄位，所以不影響原有的存檔格式與 migrate()。 */
(function(){
const CFG=window.FA_CONFIG||{};
const META='fa-kingdom-p1-v1-meta',CPKEY='fa-kingdom-cp-v1';
const LS={get(k){try{return JSON.parse(localStorage.getItem(k));}catch(e){return null;}},
  set(k,v){try{localStorage.setItem(k,JSON.stringify(v));}catch(e){}},del(k){try{localStorage.removeItem(k);}catch(e){}}};
const clone=o=>JSON.parse(JSON.stringify(o));
let remote=null,email=null,status='off',pending=null,pushing=false,conflict=false,timer=null,retry=null;
const listeners=[];
const setStatus=s=>{if(status===s)return;status=s;listeners.forEach(f=>{try{f(s);}catch(e){}});};

/* ---------- 真實的 Supabase 存取（測試時可用 window.__faRemote 取代） ---------- */
function makeRemote(client){return {
  async user(){const {data}=await client.auth.getSession();return data.session?data.session.user:null;},
  signIn(){return client.auth.signInWithOAuth({provider:'google',options:{redirectTo:location.origin+location.pathname,queryParams:{prompt:'select_account'}}});},
  async signOut(){await client.auth.signOut();},
  async load(e){const {data,error}=await client.from('fa_saves').select('state,updated_at').eq('email',e).maybeSingle();if(error)throw error;return data;},
  async insert(e,state){const {data,error}=await client.from('fa_saves').insert({email:e,state}).select('updated_at').single();if(error)throw error;return data.updated_at;},
  async update(e,state,expected){const {data,error}=await client.from('fa_saves').update({state}).eq('email',e).eq('updated_at',expected).select('updated_at');
    if(error)throw error;return data&&data[0]?data[0].updated_at:null;},
  async checkpoint(e,day,state){const {error}=await client.from('fa_checkpoints').upsert({email:e,day,state},{onConflict:'email,day'});if(error)throw error;},
  async loadCheckpoint(e,day){const {data,error}=await client.from('fa_checkpoints').select('state').eq('email',e).lte('day',day).order('day',{ascending:false}).limit(1);
    if(error)throw error;return data&&data[0]?data[0].state:null;},
  async clearCheckpoints(e){const {error}=await client.from('fa_checkpoints').delete().eq('email',e);if(error)throw error;},
  async failure(e,scenario,choice){const {error}=await client.from('fa_failures').insert({email:e,scenario,choice});if(error)throw error;}
};}

function loadLib(){return new Promise((res,rej)=>{
  if(window.supabase&&window.supabase.createClient)return res();
  const s=document.createElement('script');s.src='https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js';
  const t=setTimeout(()=>rej(new Error('逾時')),8000);
  s.onload=()=>{clearTimeout(t);res();};s.onerror=()=>{clearTimeout(t);rej(new Error('載入失敗'));};document.head.appendChild(s);});}

async function init(){
  if(window.__faRemote)remote=window.__faRemote;
  else{
    if(!CFG.url||!CFG.anonKey){setStatus('nolib');return null;}
    try{await loadLib();}catch(e){setStatus('nolib');return null;}
    const client=window.supabase.createClient(CFG.url,CFG.anonKey,{auth:{flowType:'pkce',persistSession:true,detectSessionInUrl:true,autoRefreshToken:true}});
    remote=makeRemote(client);
  }
  let u=null;try{u=await remote.user();}catch(e){}
  email=u&&u.email?u.email.toLowerCase():null;
  setStatus(email?'ok':'off');
  return email;
}

/* ---------- 同步決策（純函式，方便測試） ----------
 * local：本機存檔或 null；meta：本機 meta；cloud：{state,updated_at} 或 null；mail：目前登入的 email
 * 回傳：'use-cloud'（採用雲端）、'push-local'（上傳本機）、'keep'（一致，不動）、'new'（雲端沒有、本機也沒進度）、'ask'（兩邊都有變動，問使用者） */
function decide(local,meta,cloud,mail){
  meta=meta||{};
  const pristine=s=>!s||((s.day||1)===1&&(s.step||0)===0&&!s.started);
  const mine=!!local&&meta.email===mail;
  const anon=!!local&&!meta.email;
  if(!cloud)return (mine||(anon&&!pristine(local)))?'push-local':'new';
  if(!local||(!mine&&!anon)||(anon&&pristine(local)))return 'use-cloud';
  if(mine){
    if(meta.synced===cloud.updated_at)return meta.dirty?'push-local':'keep';
    return meta.dirty?'ask':'use-cloud';
  }
  return 'ask';
}

/* 登入後同步。askFn({local,cloud}) 回傳 true＝採用雲端，false＝採用這台裝置。 */
async function sync(local,askFn){
  if(!email)return {action:'none'};
  setStatus('loading');
  let cloud;
  try{cloud=await remote.load(email);}catch(e){setStatus('offline');return {action:'offline'};}
  const meta=LS.get(META)||{};
  let act=decide(local,meta,cloud,email);
  if(act==='ask')act=(await askFn({local,cloud:cloud.state}))?'use-cloud':'push-local';
  if(act==='use-cloud'){LS.set(META,{email,synced:cloud.updated_at,dirty:false});conflict=false;setStatus('ok');return {action:act,state:clone(cloud.state)};}
  if(act==='keep'){conflict=false;setStatus('ok');return {action:act};}
  if(act==='new'){LS.set(META,{email,synced:null,dirty:false});conflict=false;setStatus('ok');return {action:act};}
  // push-local：以雲端目前版本為基準上傳（雲端沒有就新增）
  LS.set(META,{email,synced:cloud?cloud.updated_at:null,dirty:true});conflict=false;
  pending=clone(local);await push();
  return {action:'push-local'};
}

/* ---------- 上傳（節流；有變動才傳） ---------- */
function queueSave(state){
  if(!email||conflict||status==='nolib')return;
  pending=JSON.stringify(state);
  const m=LS.get(META)||{};
  if(m.email!==email||!m.dirty)LS.set(META,{email,synced:m.email===email?m.synced:null,dirty:true});
  if(!timer)timer=setTimeout(()=>{timer=null;push();},8000);
}
async function push(){
  if(pushing||pending==null||!email||conflict)return;
  pushing=true;const st=typeof pending==='string'?JSON.parse(pending):pending;pending=null;
  try{
    const m=LS.get(META)||{};let ts;
    if(!m.synced)ts=await remote.insert(email,st);
    else{ts=await remote.update(email,st,m.synced);if(ts===null){conflict=true;setStatus('conflict');pushing=false;return;}}
    LS.set(META,{email,synced:ts,dirty:pending!=null});setStatus('ok');
  }catch(e){
    if(e&&e.code==='23505'){conflict=true;setStatus('conflict');}
    else{if(pending==null)pending=st;setStatus('offline');clearTimeout(retry);retry=setTimeout(()=>{retry=null;push();},30000);}
  }
  pushing=false;
  if(pending!=null&&!conflict&&!timer)timer=setTimeout(()=>{timer=null;push();},8000);
}
async function flush(){if(timer){clearTimeout(timer);timer=null;}await push();}
document.addEventListener('visibilitychange',()=>{if(document.hidden)flush();});
window.addEventListener('pagehide',()=>{flush();});

/* ---------- 每日存檔點 ---------- */
function checkpoint(state){
  const snap=clone(state),day=snap.day||1;
  let c=LS.get(CPKEY);if(!c||c.email!==(email||null))c={email:email||null,list:[]};
  c.list=c.list.filter(x=>x.day!==day);c.list.push({day,state:snap});c.list.sort((a,b)=>a.day-b.day);c.list=c.list.slice(-8);
  LS.set(CPKEY,c);
  if(email&&remote&&!conflict)Promise.resolve(remote.checkpoint(email,day,snap)).catch(()=>{});
}
async function restore(day){
  const c=LS.get(CPKEY);
  if(c&&c.email===(email||null)){const hit=c.list.filter(x=>x.day<=day).pop();if(hit)return clone(hit.state);}
  if(email&&remote){try{const s=await remote.loadCheckpoint(email,day);if(s)return clone(s);}catch(e){}}
  return null;
}
async function clearCheckpoints(){LS.del(CPKEY);if(email&&remote){try{await remote.clearCheckpoints(email);}catch(e){}}}
async function failure(scenario,choice){if(email&&remote){try{await remote.failure(email,scenario,choice);}catch(e){}}}

/* ---------- 登入／登出 ---------- */
async function signIn(){if(remote)await remote.signIn();}
async function signOut(){await flush();try{await remote.signOut();}catch(e){}LS.del(META);LS.del(CPKEY);email=null;pending=null;conflict=false;setStatus('off');}

window.FACloud={init,sync,decide,queueSave,flush,checkpoint,restore,clearCheckpoints,failure,signIn,signOut,
  email:()=>email,status:()=>status,onStatus:f=>listeners.push(f)};
})();
