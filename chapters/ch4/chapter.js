/* 第四章「雪嶺」章節程式（F1：章節骨架——山腳村、旅店、帕桑出發、回藍堡；營地與醫療內容之後的階段才加）。
 * 草稿：沒登入的人預設也「開放」章節，所以進入條件在這裡自己擋：只有老師預覽（preview.html）或 #debug 的 ?open=ch4 才進得去。
 * 對白全部是擬稿（沒有醫療內容），見 chapters/ch4/REVIEW.md。狀態記在 S.c.ch4，不新增頂層欄位。 */
export default function(FA){
const S=new Proxy({},{get:(_,k)=>FA.S[k],set:(_,k,v)=>{FA.S[k]=v;return true;}});
const {$,say,lines,go,toast,refresh,nextDay,sleep,checkpoint,stashDepart,RM}=FA;
const QS=new URLSearchParams(location.search),PREV=!!QS.get('preview');
const DEBUG=location.hash==='#debug'&&localStorage.getItem('fa-debug')==='1';
const DRAFT_OK=PREV||(DEBUG&&(QS.get('open')||'').split(',').includes('ch4'));
const INN_COST=20;  /* 住一晚的價錢（遊戲參數，和鍛造鎮旅館一樣） */
const HARBOR={scene:'ch3_harbor',at:[820,640]},VILLAGE={scene:'ch4_village',at:[880,620]};
const st=()=>{const c=S.c;c.ch4=c.ch4||{};return c.ch4;};
if(PREV&&String(QS.get('preview')).startsWith('ch4_'))st().arrived=true;  /* 預覽直接站在雪嶺：當作已經到過 */
/* 開放條件：完成第三章章末、見過帕桑、集滿 3 片海圖碎片（第三章 E3 的 S.c.ch3_e3）；預覽不需要 */
const ready=()=>{if(!DRAFT_OK)return false;if(PREV)return true;const e=(S.c&&S.c.ch3_e3)||{};return !!(S.c&&S.c.ch3_done&&e.seen&&e.seen.np&&Object.keys(e.frag||{}).length>=3);};
async function trip(to,msg){
  $('fade').classList.add('on');await sleep(RM?0:500);
  FA.setBusy(false);await go(to.scene,to.at);FA.setBusy(true);
  $('fade').classList.remove('on');
  if(msg)await say(msg);}
/* 在藍堡港口跟帕桑出發（由第三章 e3.js 的帕桑選單呼叫）；回傳有沒有出發 */
async function depart(){
  if(!ready())return false;
  const first=!st().arrived;
  if(first){
    await lines('ch3_m_np',['三片海圖碎片拼在一起了，你看，這就是我的家鄉——雪嶺。','山上很冷，也很美。我是嚮導，我帶你上去；不過你也要學會照顧自己和同伴。']);}
  const i=await say({p:'ch3_m_np',html:`<p>${first?'要不要跟我回去看看？':'要回雪嶺嗎？'}</p>`,buttons:[{label:'出發去雪嶺',primary:true},{label:'再準備一下'}]});
  if(i!==0)return false;
  await stashDepart();
  st().arrived=true;
  await trip(VILLAGE,{icon:'🛶',who:'前往雪嶺',html:'<p>帕桑的朋友把船開進河口，你們換上小船，沿著河一路往上游划。傍晚，山腳村的炊煙出現在眼前。</p>'});
  if(first)await lines('ch4_guide',['歡迎來到雪嶺山腳村！這裡是上山前的最後一個村子。','上山的路我還在檢查，等路況確認好，我們就出發。你先逛逛村子，跟旅店老闆娘打個招呼吧。']);
  return true;}
async function boat(){
  const i=await say({p:'hero',who:'小船',html:'<p>要搭小船回藍堡嗎？</p>',buttons:[{label:'回藍堡',primary:true},{label:'不用了'}]});
  if(i!==0)return;
  await stashDepart();
  await trip(HARBOR);}
async function trail(){
  await say({p:'hero',html:'<p>石階一路往上，通往山上的營地。路口的木牌畫著箭頭和山的圖案。</p>'});
  await say({p:'ch4_guide',html:'<p>前面的營地還沒準備好，現在還不能上去。再等一等，我們很快就出發。</p>'});}
async function room(){
  const i=await say({p:'ch4_innk',who:'山腳旅店',html:`<p>要住一晚嗎？一晚 ${INN_COST} 金幣，體力會完全恢復，進入下一天。</p><p class="small">金幣 ${S.coins}</p>`,buttons:[{label:'住一晚',primary:true,disabled:S.coins<INN_COST},{label:'不用了'}]});
  if(i!==0)return;
  S.coins-=INN_COST;$('fade').classList.add('on');await sleep(RM?0:500);
  const html=nextDay();S.sta=FA.staMax();refresh();$('fade').classList.remove('on');checkpoint();
  await say({icon:'☀',who:`第 ${S.day} 天`,html:'<p>在暖暖的爐火旁睡了一覺，體力完全恢復了。</p>'+html});}
async function guideTalk(){
  const e=st();
  for(;;){
    const i=await say({p:'ch4_guide',html:`<p>${e.met?'有什麼事嗎？':'你好，我們又見面了。'}</p>`,buttons:[{label:'聊聊雪嶺'},{label:'什麼時候上山？'},{label:'先離開',primary:true}]});
    e.met=true;
    if(i===0)await lines('ch4_guide',['雪嶺的村子在山谷裡，冬天雪封了路，大家就待在屋子裡織毛線、煮熱茶。','Warm clothes 是保暖衣物。上山前，衣服要一層一層穿，濕了就要換。']);
    else if(i===1)await lines('ch4_guide',['山上的營地我還在整理，再給我一點時間。','等路準備好了，我會告訴你。']);
    else return;}}
async function innkTalk(){
  const e=st();
  if(!e.innk){e.innk=true;await lines('ch4_innk',['歡迎！你是帕桑帶來的客人吧？','旅店有熱茶，也有乾淨的床。累了就在床上好好睡一覺。']);return;}
  await lines('ch4_innk',['山上的天氣說變就變，趕路的人最需要一個暖暖的地方休息。','想睡覺就走到床邊，住一晚 '+INN_COST+' 金幣。']);}
return {
  acts:{ch4_boat:boat,ch4_trail:trail,ch4_room:room},
  talk(id){if(id==='ch4_guide')return guideTalk();if(id==='ch4_innk')return innkTalk();},
  goal(){return '和帕桑聊聊，看看雪嶺山腳村。（山上的營地之後才開放）';},
  news(id){return id==='ch4_guide'&&!st().met;},
  ready,depart};
}
