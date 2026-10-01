/* 背景音樂：5 首 m4a（assets/music/），用 Web Audio 解碼後循環，場景切換時交叉淡入淡出。
 * 預設關閉（教室多台同時播放），在「設定」開啟；開關與音量存在 localStorage（fa-music、fa-music-vol），不進遊戲存檔。
 * 音檔載入失敗或瀏覽器不支援時安靜略過，不影響遊戲。 */
(function(){
'use strict';
const TRACKS={village:'assets/music/village.m4a',indoor:'assets/music/indoor.m4a',forest_mine:'assets/music/forest_mine.m4a',rescue:'assets/music/rescue.m4a',clear:'assets/music/clear.m4a'};
const FADE=1.2;
let ctx=null,master=null,cur=null,want=null,token=0;const cache={};
const ls=(k,v)=>{try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){}return null;};
const isOn=()=>ls('fa-music')==='1';
const vol=()=>{const v=parseFloat(ls('fa-music-vol'));return isNaN(v)?.5:Math.min(1,Math.max(0,v));};
const gainOf=v=>v*2;   // 音檔響度約 −23 LUFS，偏小，所以放大

/* 場景 → 曲目 */
function trackFor(scene,S){
  if(scene==='home'||scene==='shop')return 'indoor';
  if(scene==='forest'||scene==='mine_out'||scene==='mine_in')return 'forest_mine';
  if(scene==='ruin'&&S&&S.quake&&!(S.rescue&&S.rescue.rations))return 'rescue';   // 救援進行中
  return 'village';
}
function init(){
  if(ctx)return true;
  const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return false;
  ctx=new AC();master=ctx.createGain();master.gain.value=gainOf(vol());master.connect(ctx.destination);return true;
}
function load(name){
  if(!cache[name])cache[name]=fetch(TRACKS[name]).then(r=>{if(!r.ok)throw new Error(r.status);return r.arrayBuffer();})
    .then(b=>new Promise((res,rej)=>ctx.decodeAudioData(b,res,rej))).catch(e=>{delete cache[name];throw e;});
  return cache[name];
}
function fadeOut(h,t){if(!h)return;h.g.gain.cancelScheduledValues(ctx.currentTime);h.g.gain.setValueAtTime(h.g.gain.value,ctx.currentTime);
  h.g.gain.linearRampToValueAtTime(0,ctx.currentTime+t);try{h.src.stop(ctx.currentTime+t+.05);}catch(e){}}
async function play(name){
  want=name;
  if(!isOn()||!init())return;
  if(ctx.state==='suspended')ctx.resume();
  if(cur&&cur.name===name)return;
  const my=++token;
  let buf;try{buf=await load(name);}catch(e){return;}
  if(my!==token||!isOn())return;
  const src=ctx.createBufferSource(),g=ctx.createGain();src.buffer=buf;src.loop=true;
  g.gain.setValueAtTime(0,ctx.currentTime);g.gain.linearRampToValueAtTime(1,ctx.currentTime+FADE);
  src.connect(g);g.connect(master);src.start();
  fadeOut(cur,FADE);cur={name,src,g};
}
function stop(){token++;fadeOut(cur,.4);cur=null;}
function scene(id,S){play(trackFor(id,S));}
/* 短音效（任務完成）：播放時把背景音樂壓低，結束後恢復 */
async function jingle(){
  if(!isOn()||!init())return;
  if(ctx.state==='suspended')ctx.resume();
  let buf;try{buf=await load('clear');}catch(e){return;}
  const src=ctx.createBufferSource(),g=ctx.createGain();src.buffer=buf;g.gain.value=1;src.connect(g);g.connect(master);
  const t=ctx.currentTime,d=buf.duration;
  if(cur){const bg=cur.g.gain;bg.cancelScheduledValues(t);bg.setValueAtTime(bg.value,t);bg.linearRampToValueAtTime(.2,t+.3);bg.setValueAtTime(.2,t+d-.5);bg.linearRampToValueAtTime(1,t+d+1);}
  src.start(t);
}
function setOn(on){ls('fa-music',on?'1':'0');if(on){if(want)play(want);}else stop();}
function setVol(v){ls('fa-music-vol',String(v));if(master)master.gain.setTargetAtTime(gainOf(v),ctx.currentTime,.05);}
document.addEventListener('visibilitychange',()=>{if(!ctx)return;if(document.hidden)ctx.suspend();else if(isOn())ctx.resume();});
window.FAMusic={scene,jingle,isOn,setOn,vol,setVol,trackFor};
})();
