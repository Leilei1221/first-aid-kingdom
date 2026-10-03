/* 第三章按壓節拍的計算（純函式，不碰畫面；tools/ch3_lesson2_test.py 直接測這支）。
 * 速率範圍 100～120 下／分來自草稿 K2-2；GUIDE_BPM 取範圍中點只是節拍燈的示範速度。
 * 「停下多久算一次中斷」（PAUSE_GAP_MS）、疲勞多久滿（FATIGUE_SEC）、換手後再壓幾下（AFTER_SWAP）都是遊戲節奏用的參數，
 * 不是醫學數字，也不拿來判定 E4（中斷過久的規則等老師決定）；本階段只「記錄」。 */
export const RATE_MIN=100,RATE_MAX=120,GUIDE_BPM=110;
export const DEFAULTS={pauseGapMs:1500,fatigueSec:30,afterSwap:12};

/* 最近 n 下的速率（下／分）；不到 3 下回傳 null */
export function recentRate(taps,n=6){
  const t=taps.slice(-n);if(t.length<3)return null;
  return Math.round(60000*(t.length-1)/(t[t.length-1]-t[0]));}
export const rateBand=bpm=>bpm==null?null:bpm<RATE_MIN?'slow':bpm>RATE_MAX?'fast':'ok';

/* 全部按壓時間點（毫秒）→ 統計。間隔超過 pauseGapMs 的算一次「中斷」，其餘算按壓時間。
 * ratio＝按壓時間 ÷ 第一下到最後一下的總時間；longestPauseMs＝最長一次中斷。 */
export function stats(taps,{pauseGapMs=DEFAULTS.pauseGapMs}={}){
  const n=taps.length;
  if(n<2)return {n,totalMs:0,compMs:0,ratio:null,pauses:[],longestPauseMs:0,avgRate:null};
  let comp=0;const pauses=[];
  for(let i=1;i<n;i++){const g=taps[i]-taps[i-1];if(g>pauseGapMs)pauses.push(g);else comp+=g;}
  const total=taps[n-1]-taps[0];
  const compTaps=n-1-pauses.length;
  return {n,totalMs:total,compMs:comp,ratio:total>0?comp/total:null,pauses,longestPauseMs:pauses.length?Math.max(...pauses):0,
    avgRate:comp>0?Math.round(60000*compTaps/comp):null};}

/* ---------- 吹氣（第 3 節）：按住「吹氣」讓胸部起伏條上升，放開時依高度判定 ----------
 * 草稿只說「吹到胸部明顯起伏即可，避免吹太少或吹太多」，沒有數字；「每次約 1 秒」待老師核對原文，所以這裡不用秒數判定。
 * 目標區與上升速度只是遊戲手感的參數，老師試玩後再調。 */
export const BREATH={low:40,high:70,perSec:50};
export const breathLevel=(heldMs,perSec=BREATH.perSec)=>Math.min(100,Math.max(0,heldMs/1000*perSec));
export const breathBand=(level,{low,high}=BREATH)=>level<low?'low':level>high?'high':'ok';
