/* 四關星數合計與獎狀等級（老師 2026-10-14 決定）。遊戲與老師端共用，沒有任何相依。
   四關各取「最高星數」（每關上限 5）：落石之城（序章）、第二章、第三章、第四章。
   18～19 顆＝結業獎狀，20 顆＝優等獎狀。獎狀只是學習紀錄，不等同 BLS 證照。 */
(function(){
const MAX=5,GRAD=18,HONOR=20;
const NAMES={castle:'落石之城（序章）',ch2:'第二章 熔岩鍛造鎮',ch3:'第三章 港口藍堡',ch4:'第四章 雪嶺'};
function parts(s){const c=(s&&s.c)||{},n=v=>Math.max(0,Math.min(MAX,Math.floor(+v||0)));
  return {castle:n(s&&s.castleBest),ch2:n(c.stars),ch3:n(c.ch3_stars),ch4:n(c.ch4&&c.ch4.stars)};}
function total(s){const p=parts(s);return p.castle+p.ch2+p.ch3+p.ch4;}
function tier(n){return n>=HONOR?'honor':n>=GRAD?'grad':null;}
window.FAStars={parts,total,tier,GRAD,HONOR,MAX,NAMES};
})();
