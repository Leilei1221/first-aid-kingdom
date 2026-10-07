# 給接手的 AI 助手（Codex／Claude Code 通用）

專案：急救王國（花蓮高中基礎急救教學遊戲）。負責老師：黃雅蕾（蕾蕾）。線上版：https://leilei1221.github.io/first-aid-kingdom/ ；repo：Leilei1221/first-aid-kingdom（公開）。

## 先讀
1. `HANDOFF.md`（V3.1 版，是需求規格；第 0 節工作守則最重要）
   `docs/HANDOFF-v3.2-world-logic-and-stash.md`（補充：世界邏輯原則與「防災包搬家」，老師已確認；**其行號來自舊版程式，以現有程式為準**）
2. `README.md`（結構與本機開啟方式）
3. 本檔

## 工作守則（摘自 HANDOFF 第 0 節）
- 每個階段動工前：用繁體中文列出摘要，等老師確認。
- 醫療內容（`content/knowledge_cards.json`、`content/quests_and_events.json`、`content/dialogues.json` 裡的題目與解說）不可自行改寫；疑似錯誤列出來請老師確認。
- 全程繁體中文。
- 行為不變優先：每個改動都要能證明玩起來和之前一樣。
- 精簡、低維護，不引入不必要的框架；沒有建置步驟。
- 對外發布動作（建 repo、推送、開啟服務、寫入資料庫）先問老師。不要把金鑰、service_role key 放進 repo。

## ★ 目前狀態（2026-10-04 交班；與下方所有舊敘述衝突時，以本節為準）

**一切都已推到 `origin/main`（`b4e1a05`），本機沒有未推送的工作。** 舊分支（stash、chief、integrate、d1、d4、d5、ch3 等）都已併入 main，可忽略。

### 已上線（GitHub Pages）
序章；防災包搬家；第二章（熔岩鍛造鎮）＋渡海（**預設開放**）；章節框架（`chapters/`）；世界地圖、傷口圖鑑；救援失敗（嚴重錯誤→正確知識卡→回早上存檔點，救援費 **200 金幣**）；天氣引擎；天災與野外事件；營火；村長救災物資；**老師端「班級控制」**（2026-10-04 老師已在 Supabase 執行 `002_fa_class_control.sql`，老師端看得到開關；**尚未實測按下開關對學生端的效果**）；**老師預覽**（`preview.html`，見下）。
- **第三章（港口藍堡）內容已做完，老師已於 2026-10-07 審核通過（全部照現有文字）**：第 1～4 節＋章末整合演練；`draft` 標記已拿掉，改記 `reviewed:"2026-10-07"`。誰看得到見下方「誰會看到第三章」。狀態、參數、審核前的備註都寫在 **`chapters/ch3/REVIEW.md`（先讀它；裡面的「draft／待審」是審核前的歷史紀錄）**。
- 觸電題（第二章阿焰）選「直接抓手／潑水」會變成救援失敗（已上線）。

### 第三章現況（`chapters/ch3/`）
| 節 | 位置 | 內容 |
|---|---|---|
| 第 1 節 | 港口市集，倒地的漁夫 | 判斷（安全、反應、呼吸）、求救；Q1-1～Q1-7、K1-1～3、指派路人 |
| 第 2 節 | 救生站，CPR 假人 | 按壓位置與深度速率；Q2-1～Q2-8、K2-1～3；按壓節拍遊戲（疲勞、換手），只記錄「最長中斷」「按壓時間占比」 |
| 第 3 節 | 救生站，面罩與牆邊 AED | 30:2 與 AED；Q3-1～Q3-8、K3-1～3；吹氣小遊戲、5 步 AED 練習 |
| 第 4 節 | 港口，救生員 | 專線、居家儲備、技能要回實體練習；Q4-1、2、3、5、6、D-1～3、K4-1、2、4（海嘯警報 K4-3、Q4-4 沒做） |
| 章末 | 市集倒地者（第 1～4 節都做完才出現選項） | 判斷→分工→壓 30＋吹氣 2→再壓 30→AED→續壓換手→救護人員接手；五面向各 1 星；第一次完成取得「心跳之匣」 |
- 資料：`cards.json`、`dialogues.json`（題目 `ch3_q*`、`ch3_d*`，每題／每張卡有 `reviewed`、`note`、`severe`／`severeOpts`；`note`、`status`、`pending`、`omitted` 是審核前的備註，留作歷史）；程式：`chapter.js`；計算：`rhythm.js`（節拍、吹氣、章末合併與星數）、`aed.js`（AED 步驟）。
- **遊戲參數不是醫學數字**，都在 `rhythm.js` 最上方：節拍燈 110 下／分、疲勞條 30 秒、停 1.5 秒算中斷、吹氣條綠色範圍 40～70、每輪壓 30 下、換手後再壓 12 下。`FINALE.pauseLimitMs`＝10 秒是**老師的課堂規則**（只用在章末「壓胸品質」那顆星）。
- 完成狀態記在既有 `S.c`：`ch3_done`、`ch3_stars`、`ch3_box`；**沒有新增頂層存檔欄位**。
- **嚴重錯誤（E1–E7）只記錄、不觸發救援失敗**（記在 `window.__ch3Finale`，只有 #debug）：救援失敗說明草稿沒有，**不能自己寫**，要老師提供。
- 畫面上方「目標」依進度指路。**NPC 對話（2026-10-07 老師同意擬稿）**：港口救生員（選單：請教第 4 節／聊聊，聊聊依章末星數說不同的話）、救生站救生員、港口水手、南岸水手（選單：去藍堡怎麼走／看浪況／天氣與颱風季／救生衣與落水，水域安全的句子是擬稿、沒有任何數字）都有了；老船長是航行對話。**還沒有對白**的：漁婦、漁夫、紅／藍／綠衣路人，按「對話」只顯示「……（這位角色的對話之後才會加入。）」。程式在 `chapters/ch3/chapter.js`（`lifegHarbor`、`sailorPort` 等），測試 `tools/ch3_npc_test.py`。

### 誰會看到第三章（2026-10-07 老師決定）
- **訪客、沒登入、老師帳號**（不屬於任何班）：完成第二章後，第三章就開放。**任何學生只要不登入就玩（或讀不到後台設定，例如校網擋住），也屬於這一類，班級後台管不到他們。老師已說明明天（2026-10-08）起會全面要求學生登入。**
- **學生（有班級）**：照班級後台，後台沒設定第三章就是關閉。
- **野外項目（wild）也一樣**：不屬於任何班的人預設開；有班級的學生預設關，由班級後台決定。
- 村長救災物資、天災：**不在這條規則內**，維持預設關閉與班級後台控管（老師要試用預覽頁）；天災只由班級公告觸發，沒有任何隨機天災。
- 第三章內容現在對所有沒登入的人開放（已審核通過）。若要讓學生一定要登入才受管控，需另外設計（例如不登入不能進第三章）。

### 後續遊戲設計（2026-10-07 老師提出，分階段做）
- **① 星級獎勵（已做）**：大關卡 3、4、5 顆星報酬不同，**每個新達成的星級只領一次**（重打拿更高星才補差額，跳級就一次補齊）。落石之城（序章，要先完成第三章 `S.c.ch3_done` 才開啟，之前結算畫面與以前完全一樣）與第三章章末演練都適用；第二章不動。數字在 `content/balance.json` 的 `STAR_REWARD`（目前 castle：60／120／240、ch3：80／160／320，都是遊戲平衡參數，可調）；已領等級記在 `S.c.starPaid`（不新增頂層欄位）；核心函式 `starReward(kind,stars)`（`js/game.js`），章節程式用 `FA.starReward`。測試 `tools/star_reward_test.py`、`tools/ch3_finale_test.py`。
- **② 商店特殊道具（未做）**：補體力、提升體力上限的道具，價格偏高；完成第三章之後開啟。
- **③ NPC 聊天話題（未做；取代原本的「刷題賺金幣」，老師明確不要刷題）**：NPC 對話多一個「聊聊」，話題對應**現有知識卡**（文字不改），第一次只給知識卡、之後重複聊有機會掉小額金幣（建議每次 25%、5～10 金幣、同話題每天一次、每天上限 30，皆為參數）；話題可隨好感度解鎖；NPC 開場一兩句由我擬稿給老師審。分配建議：阿鹿（高山症、蛇咬、迷路、求救訊號、失溫、過溪）、阿木（外出血、小傷口、骨折、頭頸部受傷）、小芽（擦傷、蜜蜂、流鼻血、過敏、噎住）、廚娘（燒燙傷、乾淨的水、防災包食物、低血糖）、守衛與小兵（颱風、山洪、昏倒、突然倒下）。完成第三章後開啟。
- **④ 交通工具（未做）**：熱氣球、竹蜻蜓、復古滑翔機、無人機，島與島之間穿梭，要花很多錢（暫擬 1500／3000／6000／10000）；建議買了可往返兩島、省下航行兩夜與食水，颱風豪雨天仍不能用；圖由老師提供，買的地方暫定選單（旅行商人或船長）。完成第三章之後開啟。

### 老師預覽（不放連結、知道網址的人都能開）
`/first-aid-kingdom/preview.html`：點場景直接進去，**全部章節視為開放、不存進度、不連雲端、用獨立存檔 key（`fa-kingdom-preview`）、不碰一般存檔**。程式：`js/game.js` 的 `PREVIEW`（`?preview=場景id`）；章末演練捷徑 `?preview=ch3_market&lessons=1`（標記第 1～4 節已做完，由 `chapters/ch3/chapter.js` 處理）。測試：`tools/preview_test.py`。

### 開關（預設都關，除第二章）
| 開關 | 位置 | 控制 |
|---|---|---|
| 章節 | `chapters/index.json` 的 `open`；老師端 `ch2`／`ch3` | **不屬於任何班的人（老師、訪客、沒登入）：章節預設開放**（`js/game.js` 的 `flagOn`；第三章仍要先完成第二章才走得進去）。**有班級的學生**：預設 ch2 開、ch3 關，老師端按班級開關覆蓋（明確設定一律優先） |
| `WILD_ON` | `content/weather.json`；老師端 `wild` | 打火石與營火、溺水救援、河谷裝溪水、阿鹿高山症支線。**不屬於任何班的人（老師、訪客、沒登入）預設開**（2026-10-07 老師決定）；有班級的學生預設關，老師端按班級覆蓋 |
| `RELIEF_ON` | 同上；老師端 `relief` | 村長救災物資 |
| 天災 | 老師端發布（颱風／豪雨／濃霧）；本機 `__fa.scheduleWx('typhoon')` | 無隨機，只由老師發布 |
本機測試網址參數（需 `#debug`＋`localStorage fa-debug=1`）：`?open=ch2,ch3`、`?wild=1`、`?relief=1`。

### 老師（蕾蕾）要做的事（我不能代做）
1. **試老師端的開關**：先對一個測試班按一個無害的開關（例如「野外項目」開再關），確認沒有錯誤、狀態有變。真實的函式與 RLS 我沒在真的資料庫測過（測試用模擬雲端）。
2. 審文字：第三章（`chapters/ch3/REVIEW.md`）**已審核通過**；**還沒審**：`docs/d4-review-checklist.md`（D4）、`docs/stash-text-review.md`（防災包 A1–A4、B1、C）。這兩份審過前，對應開關保持關閉。
3. **「一週份 vs 三天份」仍是矛盾**：第三章 K4-2、Q4-2（已審核通過）教一週、每日 3 公升，但線上遊戲現行 `water`／`food` 文字寫「至少三天份」。老師審第三章時照現狀通過；要消除矛盾得審 `docs/stash-text-review.md`，再同步改防災包文字（K4-2 最後一行迷思也提到「遊戲舊設定為三天份」，要一起改寫）。
4. **核對 AHA 原文**（我讀不到 cpr.heart.org／ahajournals.org，403）：吹氣「每次約 1 秒」、AED 貼片「前外側或前後位置」、按壓時間占比（搜尋摘要只有「至少 60%」，未核對，不採用）。
5. 決定：嚴重錯誤要不要觸發救援失敗（要的話提供每項說明與正確知識卡）；海嘯警報支線要不要做；老師端要不要顯示第三章星數。
6. 試玩預覽，告訴我哪裡要調（星數規則、節奏參數、倒地者與假人位置、「練習 AED」互動點離牆上箱子有點遠）。

### 下一步（等老師回覆後）
- 第三章已審核通過、`draft` 已拿掉；學生那邊的實際效果（班級後台開關）還沒用學生帳號實測。
- 嚴重錯誤的救援失敗（需老師提供說明）；其餘 NPC（漁婦、漁夫、三位路人）的對白（老師要提供，或我擬稿請老師審）；老師端顯示第三章星數（要改 `js/teacher.js` 與 `tools/teacher_test.py`）。
- 防災包文字定稿；D4 待審文字定稿後把 `draft` 標記拿掉、開對應開關（這兩份尚未審）。
- 可選清理：第二章與第三章的航行程式（`chapters/ch2/chapter.js`、`chapters/ch3/chapter.js`）重複，之後可整理成共用。

### 資料與工具位置
- 第三章素材包與草稿：`~/Library/CloudStorage/OneDrive-個人/健康與護理作業/115/多元選修/急救王國/第三章交付包/`；V3 原型：`~/Projects/first-aid-kingdom-v3-spec/`。
- 各階段摘要與結果：`docs/stage-d1..d5-summary.md`、`docs/ch3-d1-summary.md`；章節資料包格式：`docs/chapter-pack-format.md`（含 `chapter.js` 掛接點與 `region` 說明）。
- 第三章遮罩可重跑：`tools/ch3_masks.py`；版面檢查：`python3 tools/layout_test.py ch3`。

### 測試（全部在 `tools/`，先 `python3 -m http.server 8765`；用 `python3 -u` 才看得到即時輸出）
`stash`、`ration`、`sugar`、`credit`、`shop_event`、`chapter`（含假章節）、`ch2`、`ch3`、`ch3_goal`、`ch3_lesson1`～`ch3_lesson4`、`ch3_finale`（第三章各節與章末演練）、`preview`、`weather`、`rescue`、`wild`、`camp`、`relief`、`control`（班級控制與章節執行時開關）、`cloud`（18 項）、`wall`、`teacher`（用 `teacher.html` 網址，28 項）、`walk_test.py`（章節用 `CHAPTER=ch2|ch3`）、`compare_run.py`（51 情境比對）。
- **推送前一定跑 51 情境比對**（用 `git worktree` 放 scratchpad、獨立埠，測完 `git worktree remove`），報告差異，**等老師說「推」才推**。
- 測試寫法陷阱：`page.evaluate` 會等 Promise，遊戲對話要等人點才結束，所以呼叫 `__fa.talk/say/go` 要用 `() => { ...; }` 不回傳；`drive()` 判斷對話結束要再等 450ms 避開場景切換。
- `walk_test` 在「家、森林南出口、農田南出口、草原北出口、草原通往漁港」會卡住，是測試工具的路徑規劃限制，不是程式錯誤。
- 已知：macOS 沒有 `timeout`；背景比對要等真正結束（用完成標記檔 `until [ -f ... ]` 迴圈；背景啟動指令結束只代表「開始跑了」）。
- 已知：整套測試跑時 `cloud` 測試偶爾因載入逾時失敗（疑為網路字型），單獨重跑會過；同一檔案在比對進行中不要修改。
- 瀏覽器分頁測試本機改過的 JS 時，舊檔可能被快取：用 `fetch(url,{cache:'reload'})` 再重新整理。

### 工作守則（務必遵守）
- 每個階段動工前先出摘要（列「要老師決定」並給建議），等確認；老師說「按你的建議做」就做完整個階段，每步獨立提交附測試。
- 醫療與知識卡文字：照原文搬、標 draft，**不得自行改寫**；V3 與現行有出入時列出請老師決定（例如過敏題的「疹子」，至今沒掛 `hives` 圖）。
- 全程繁體中文；不引入框架；沒有建置步驟。
- 外部動作（推送、Supabase、Google Cloud）先問；不要把金鑰放進 repo；Supabase SQL 由老師執行。
- 序章玩起來不可變：改動後 51 情境比對與已上線版 0 差異（有意的差異要逐項說明）。

## （舊）2026-10-01 晚的狀態——已過時，僅供參考；以上方「★ 目前狀態」為準

### 已上線（main = origin/main，GitHub Pages）
- 序章 + 階段 B（Google 登入、雲端存檔、每日存檔點、PWA、手機版面）+ 老師端進度頁。
- 今天新增並已推送：
  - **背景音樂**：5 首 m4a（`assets/music/`），`js/music.js`；預設**關閉**，設定選單開關與音量，偏好存 localStorage（`fa-music`、`fa-music-vol`），不進存檔。來源與授權：`docs/music-license-and-notes.md`（AI 輔助作曲，可用於學校公開網站；設定選單有標示文字）。給作曲者的委託說明：`docs/music-brief.md`。
  - **隱私權政策** `privacy.html`（通用版，涵蓋急救王國、健護課教室管理系統、寵物照護）。
  - **修正**：老闆娘受傷事件缺用品時打不開商店（`tools/shop_event_test.py`）；背包方糖可吃（體力 < `HYPO_AT` 才能吃，`tools/sugar_test.py`）；標題畫面「登出（換帳號）」鈕、登入加 `prompt=select_account`；欠款賒帳（急救用品，`DEBT_LIMIT=300`，`tools/credit_test.py`）；乾糧可吃（體力 +`RATION_EAT`=20，過期不能吃，劇情第 9 步唯一一包要留給爺爺，`tools/ration_test.py`）。
- 這些改動都用 51 情境比對驗證（與上線版 0 差異，除了有意改的對話按鈕）。

### 尚未上線
- **防災包搬家（第一階段）**：分支 `stash`（提交 `3c1de68`，基於舊 main，合併時 `game.js` 會有小衝突，處理時保留 main 的新功能）。程式與 `tools/stash_test.py` 17 項已過；**等老師審核文字**後才定稿：`docs/stash-text-review.md`（A1–A4 為補充文件 3.5 節四處更新，尚未寫入；B1 是食物知識卡 `food` 也寫「至少三天份」，老師要提供新寫法或請先擬稿；C 為暫用新增文字）。**審核前不要動醫療與知識卡文字。** 合併後也要把防災包顯示的乾糧「吃」等新行為一起測。
- **災後救災物資發放**（老師已同意設計，等村長圖）：山洪、地震災後，**村長**指揮發放乾糧、開水、打火石（颱風、火災先不提供）；受背包格數與負重限制；**救災物資不能賣**（防止乾糧賣 15 金幣刷錢）；只開放災後當天與隔天，過後收回、不累積；已領走的視為自己的物品。時間點是**災後**（不是進城前，避免破壞地震章末「事前準備」的評分）。山洪屬 V3 天災系統，隨**階段 D4**；只有地震的部分可先做。村長形象說明：`docs/village-chief-brief.md`（未提交；老師已用 Claude Chat 生成一張全身＋頭像，灰底，**尚未存成檔案給我**，下一步請老師給圖檔路徑，再去背、轉 `chief.webp` / `chief_face.webp`、補角色資料與對話草稿給老師審）。
- **`origin/music-ready` 分支**：有人（老師的帳號，12:36）提交了一個小修正「設定視窗手機橫向時 4 個以上按鈕改兩欄」，**尚未併入 main**；目前設定選單最多 6 個按鈕，這個修正應該要併入，請先看過再併。該分支還有一個獨立工作樹 `~/Projects/first-aid-kingdom-musicwt`（不是我開的，不要動它的檔案）。
- 階段 D（D1 框架 → D2 V3 共用系統 → D3 第二章＋渡海 → D4 天災與救援失敗 → D5 老師控制）尚未開始，仍須先出摘要給老師確認。

### Google 登入（已完成，不要改回去）
- 登入實際使用的 OAuth 用戶端在 Google Cloud 專案 **health-classroom（專案編號 1089473790781）**，用戶端 `health-classroom`；使用者類型已改為**外部**、發布狀態**實際運作中**，只要 email、基本資料，無額外範圍，不需 Google 審查。**這個專案不要改回「內部」**，否則校外 Gmail 又會 403 `org_internal`。
- 這個專案同時給健護課教室管理系統、寵物照護使用；Supabase 專案 `fcstpyiggvhduaztwlrf` 共用。資料庫以名單判斷權限（老師 `hc_teacher_allowlist`、學生 `hc_students`、急救王國 `fa_guests`），校外 Gmail 登入看不到任何學生資料、也進不了教師端。
- 之前誤改過另一個專案 `organic-justice-439513-q8`（只有 MCP Drive Client），已還原為內部。**改 Google Cloud 設定時務必看網址列的 `project=` 與用戶端 ID 開頭數字**，專案名稱有兩個都叫 My First Project。
- 朋友與老師訪客：由老師在 Supabase SQL Editor 執行 `insert into public.fa_guests(email, note) values ('小寫email','備註');`（工具套用會被權限擋下，不要繞過）。老師的測試帳號：`phyllis1982.tw@gmail.com`。

### 老師的決定與偏好（今天）
- 欠款：不做利息；做限額賒帳（已做）。
- 老師用 Claude Chat、ChatGPT 生圖與作曲，再交檔案給我；我只負責轉檔與接入。
- 推送前我都先給比對結果並等老師說「推」（老師說「比對沒問題就推」「A 推」等視為同意）。
- 測試：`tools/` 下的 `stash_test.py`、`shop_event_test.py`、`sugar_test.py`、`credit_test.py`、`ration_test.py`、`cloud_test.py`（18 項）、`teacher_test.py`（用 `teacher.html` 網址）、`compare_run.py`、`walk_test.py`、`wall_test.py`。`compare_run.py` 網址不要自己加 `#debug`（腳本會加）。macOS 沒有 `timeout` 指令；背景執行的比對要等「真正結束」才看結果。
- 開新分支測試時用 `git worktree` 放在 scratchpad，測完要移除；`main` 若被工作樹佔用，專案資料夾不能 checkout main。

## 歷史進度（2026-09-30，部分已過時）
- 階段 A 完成並已上線：圖片外部化（assets/*.webp）、內容改讀 content/*.json、對話抽到 content/dialogues.json、`js/game.js` 為遊戲邏輯。
- 新舊版行為比對：51 個情境、513 個對話框逐字一致（`tools/compare_run.py`）。
- 已用 V3 圖片覆蓋 hero、grandpa、grandpa_face、home（綠底白十字），並加入 V3 新素材 39 張（第二章、傷口圖 w_*）。`w_cut_arm.webp` 依 V3 文件不使用，未加入。
- `assets/manifest.json` 仍是舊的 55 張清單（啟動時預載用）。新功能合併、實際用到新圖時，再跑 `python3 tools/gen_manifest.py`，不要預載沒用到的圖。
- `reference/` 已從 repo 移除（含舊紅十字圖）。舊圖仍留在 git 歷史；如需徹底清除要改寫歷史，這要先問老師。
- V3.1 已處理：穿牆修正（`snapFree()`，`tools/wall_test.py` 驗證：舊版 33 個測試點穿牆 24 個，新版 0 個）、cap.webp 更新（RATIO cap=0.414）。V3.1 第 3～5 節（旅館二樓遮罩、設備檢查點、砂輪機任務）屬第二章內容，隨階段 D 合併；對照用原型在 `~/Projects/first-aid-kingdom-v3-spec/v3.1/`。
- 老師端進度頁（只讀）：`teacher.html` + `js/teacher.js`（網址 `/first-aid-kingdom/teacher.html`，不放連結給學生）。只列登入老師自己的班級（`hc_classes.teacher_id = 自己`），讀 `hc_students` 名單與 `fa_saves`；權限靠 RLS（`hc_teaches_student_email`）。顯示已開始人數、主線進度%、天數、城堡星數、知識卡、金幣/欠款、好感度，可匯出 CSV。測試：`tools/teacher_test.py`（模擬資料，17 項）。老師決定：不做「全校/其他老師帳號」的進度。
- 階段 B 資料表 SQL 在 `supabase/drafts/001_fa_tables.sql`（已套用，檔名保留作紀錄）。朋友訪客用 `fa_guests`：`insert into public.fa_guests(email, note) values ('xxx@gmail.com','朋友');`（小寫 email，由老師在 SQL Editor 執行）。
- V3.2 已收到（本機 `~/Projects/first-aid-kingdom-v3-spec/v3.2/`：CHANGES-v3.2.md、ROADMAP.md、src、5 張新圖 capt/capt_face/deck/port/vport）：渡海航線（新場景 port/deck/vport、船長、船票與補給、停航）屬第二章，隨階段 D 合併，圖片也等那時再放進 assets 與 manifest。ROADMAP.md 是後續需求（新用品、檢傷分類、止血帶、結局與自由模式、2.5D、配樂），階段 D 規劃時納入；其中醫療內容需老師審核後才能製作。
- 階段 B 已併進 main（2026-10-01）：`js/cloud.js`（登入、同步、每日存檔點、失敗記錄）、`js/config.js`（Supabase URL 與可公開的 publishable key）、`game.js` 整合（存檔排程上傳、bed/faint 建存檔點、`rescueFail()` 救援失敗、設定選單登出）、標題畫面登入區。測試：`tools/cloud_test.py`（模擬雲端，16 項全過）。Supabase 資料表已由老師於 2026-10-01 執行 `supabase/drafts/001_fa_tables.sql` 建立；Google 登入已啟用，重新導向網址已加入。**真實 Google 登入尚待老師實測驗收**（我不能替老師登入）。
- 階段 B 已加入（同在 `stage-b`）：PWA（manifest.webmanifest、icons/、iOS meta）、手機橫向版面、直向提示、全螢幕鈕（取自 V3.1 head.html）。沒有 service worker（不需離線）。iPhone Safari 不支援網頁全螢幕，學生需「加入主畫面」。救援失敗的 5 個致命情境（山洪、颱風躲樹下、失溫、溺水、觸電）與 3 個一般錯誤扣 100 金幣，都屬於 V3 新功能，等階段 D 合併時再接 `rescueFail()`。
- **尚未合併 V3 新功能**：V3 原型在本機 `~/Projects/first-aid-kingdom-v3-spec/`（src、content、reference/prototype-latest-DO-NOT-COMMIT.html）。不要用它的 src 覆蓋現有程式，把它當規格逐項合併進目前結構。
- 下一步：階段 B（Google 登入＋雲端存檔），摘要待老師確認。

## 結構重點
- `js/game.js` 開頭載入 JSON 與圖片；場景出口與路標條件在 JSON 裡是函式原始碼字串，載入時用 `mk()` 編譯（`compileScenes`／`compileSigns`）。
- 對話用 `play('key',{vars})`／`T('key')`／`quizOf('key')` 讀取 `content/dialogues.json`；`{變數}` 會替換，`{CARDS.xxx.title}` 取知識卡。
- 存檔 key：`fa-kingdom-p1-v1`，`migrate()` 負責向下相容，改存檔結構時務必保留。
- `#debug`：網址加 `#debug` 且 localStorage 設 `fa-debug=1` 才會出現 `window.__fa`。

## 測試（每次改動後）
```
python3 -m http.server 8765        # 專案根目錄
python3 tools/compare_run.py new http://localhost:8765/index.html out_new.json
python3 tools/compare_run.py diff out_base.json out_new.json
python3 tools/walk_test.py http://localhost:8765/index.html
```
- 基準版：用 V3 的 `reference/prototype-latest-DO-NOT-COMMIT.html`（需加入 `#debug` 掛鉤；V3 的 `tools/build_inline.py` 可組出）錄製 out_base.json。V3 有新功能，比對時要用同一份基準錄製並限定序章情境。
- `walk_test.py` 的路徑規劃粗糙，家、森林南出口、農田南出口、草原北出口在舊版也會卡住，屬測試工具限制，不是程式錯誤；看的是新舊是否一致。
- 沒在 iPad／手機真機測過，請老師實測。

## 已知取捨與待辦
- 網址換了，claude.ai 上的舊 localStorage 進度不會自動帶過來（階段 B 用雲端存檔＋匯入處理）。
- V3 第 11.2、12.4 的「試玩」選項（試玩切換第二章、試玩發布天災）正式版必須移除，改讀資料庫（老師設定）。
- V3 第 13 節「救援失敗＋每日存檔點」：嚴重錯誤清單需老師確認後才實作。
- PWA（manifest.json、iOS 設定）需在正式網址上加。

## 接下來的順序與限制（2026-10-01 老師確認）
1. （已完成）10/1 下午序章已上線；之後的修正與功能見上方「最新狀態」。學生的雲端與本機存檔不可損壞，改存檔結構時務必保留 `migrate()` 相容。
2. **防災包搬家（第一階段）**：規格見 `docs/HANDOFF-v3.2-world-logic-and-stash.md`。一律在獨立分支做，通過該文件第 6 節 11 項驗收（含舊存檔、實際走路、雲端來回、所有出口）與序章 51 情境比對（有意改變的進城確認對話列為唯一差異）後，由老師決定何時部署。新增 `S.stash`、`STASH_CAP=20`（balance.json）、`migrate()` 補 `[]`。第 3.5 節的新文字（知識卡 water、守衛對話、目標提示、爺爺的話）**須老師逐字審核後才寫入**，先用現有文字完成程式。防災包圖 `escape_bag.webp` 之後由老師提供，先用 badge 暫代。
3. **階段 D（章節框架）**：順序 D1 框架 → D2 V3 共用系統 → D3 第二章＋渡海 → D4 天災與救援失敗情境 → D5 老師控制（章節開放、天災發布）。第三章（港口藍堡）由老師另用 Co-work 編寫，之後依章節資料包格式交付；D1 完成時請先寫「章節資料包格式說明」給老師轉交 Co-work（章節前綴 `ch3_`、場景/角色/對話/知識卡/事件/遮罩各自獨立成檔、特殊小遊戲另文字說明）。第二章預設**關閉**，待老師審核醫療內容並在老師端開放。
4. 防災包是「一個物件」，位置為爺爺家／旅館房間／隨身（旅行）；第二章、第三章的設計要依此規則（見補充文件第 1、5 節）。
5. 建議用**新對話**進行階段 D 與防災包（舊對話過長）。
6. 已知待處理：哽塞知識卡 `choke` 與 AHA 2025 的差異（補充文件第 7 節）——老師決定另開獨立章節，**審核前不要改**。補充文件寫「背包與爺爺披風仍是紅十字」已過時：這些圖已換成綠底白十字（含 hero、grandpa、home）。
