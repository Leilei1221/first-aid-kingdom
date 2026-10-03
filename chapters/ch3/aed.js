/* 第三章第 3 節：AED 練習的步驟與判定（純資料與純函式；畫面在 chapter.js，測試見 tools/ch3_lesson3_test.py）。
 * 語音句子只有 analyze 那一句取自草稿（Q3-6 題幹：「正在分析心律，請勿碰觸傷者」）；
 * 其餘語音句子（standby、pads、shock、after）是我擬的最小集合，待老師審。
 * 每一步一個正確做法、一個錯誤示範；錯誤示範的說明文字取自草稿 K3-2 與 Q3-6、Q3-7 的解析。
 * code 是草稿的嚴重錯誤代碼（E2 不用 AED、E5 分析或電擊時碰傷者、E4 中斷過久），本階段只記錄、不觸發救援失敗。 */
export const STEPS=[
  {id:'on',voice:'（AED 還沒開機）',
   right:'按下電源，打開 AED',wrong:{label:'不開機，先壓傷者的胸口',msg:'開機後，AED 會用語音一步一步指示，要依語音指示操作。',code:null}},
  {id:'pads',voice:'請依圖示貼上貼片',
   right:'依貼片上的圖示，把貼片貼在傷者胸口',wrong:{label:'不貼，繼續壓胸就好',msg:'AED 會用語音一步一步指示，不要因害怕而不取、不用。不使用 AED 會延誤急救。',code:'E2'}},
  {id:'analyze',voice:'正在分析心律，請勿碰觸傷者',
   right:'大家都不碰傷者，等語音指示',wrong:{label:'繼續壓胸',msg:'分析時碰觸會干擾判讀。',code:'E5'}},
  {id:'shock',voice:'建議電擊，請大家離開',
   right:'大聲說「大家離開」，確認沒人碰到傷者，再按電擊',wrong:{label:'不確認，直接按電擊',msg:'需要電擊時，大聲說「大家離開」，確認沒人碰到傷者再電擊。',code:'E5'}},
  {id:'after',voice:'電擊完成，請立刻開始 CPR',
   right:'立刻繼續 CPR 約 2 分鐘，再依 AED 指示',wrong:{label:'先觀察一陣子，等救護人員到才動作',msg:'電擊後立刻續做 CPR 約 2 分鐘，直到救護人員接手或傷者開始動。',code:'E4'}}
];
/* 選第 i 步的某個做法（right=true 為正確）→ {ok, msg, code}；ok 才能進下一步 */
export function choose(i,right){const s=STEPS[i];return right?{ok:true,msg:'',code:null}:{ok:false,msg:s.wrong.msg,code:s.wrong.code};}
