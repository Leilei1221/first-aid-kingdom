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

## 本機分支進度（2026-10-02，**尚未推送、未合併 main**；以本節為準）
- `main` = `origin/main`（已含 music-ready 的設定視窗修正）。
- `chief`：村長圖與角色資料、`docs/chief-dialogue-draft.md`（對話待老師審）。基於舊 main，可獨立合併。
- `integrate`：main ＋ `stash` 防災包（已解衝突，專項測試全過；與上線版比對只差有意改的進城確認與新欄位 `stash`）。
- `d1`（基於 integrate）：D1 章節框架（`chapters/index.json`、`tools/chapter_test.py`、假章節在 `tools/fixtures/chapters/`），與 integrate 比對 0 差異；另有 `docs/chapter-pack-format.md`、`docs/stage-d1-summary.md`、`docs/stage-d2-summary.md`。
- `d1` 另含 D2（地區／世界地圖、`S.c`／`S.stashAt`、傷口圖鑑、哨子手電筒雨衣）；51 情境比對相對 integrate 只多傷口圖（24 個對話框）與新欄位。營火與打火石移到 D4。過敏題 V3 文字差異待老師決定（見 `docs/stage-d2-summary.md`）。
- `d1` 另含 D3（第二章＋渡海，**預設關閉**）：`chapters/ch2/`（chapter.js、scenes、cards 等）；本機測試加 `?open=ch2`（需 `#debug`）；測試 `tools/ch2_test.py`、`CHAPTER=ch2 python3 tools/walk_test.py`。51 情境比對相對 integrate 仍只多傷口圖與新欄位。D3 未做：老師端「救援失敗次數」（要 Supabase 政策，留 D4）、停航（D4 天氣）。第二章要對學生開放需 D5（老師端開關）或把 `chapters/index.json` 的 `open` 改 true（全班一起開）。
- **D4 在分支 `d4`（本機，未推送、未併 main）**：天氣引擎（老師發布，無隨機）、救援失敗接線、天災與野外事件、營火、村長救災物資、老師端「全班最常犯的錯」。**開關預設全關**：`content/weather.json` 的 `WILD_ON`、`RELIEF_ON`，天災由 D5 老師端發布；待審文字見 `docs/d4-review-checklist.md`。測試：`weather`、`rescue`、`wild`、`camp`、`relief`、`ch2`（含觸電嚴重錯誤）。觸電嚴重錯誤會影響已上線的第二章。救援費目前 200（摘要曾寫 100，待老師定）。
- **D5 在分支 `d5`（本機，未推送、未併 main；含 D4）**：老師端「班級控制」（章節與功能開關、發布天災）；遊戲讀取 `fa_my_class_control()`；章節開放改為執行時判斷。**要用必須先由老師在 Supabase 執行 `supabase/drafts/002_fa_class_control.sql`**（Claude 不套用）；沒執行前遊戲用預設、老師端顯示說明。測試：`control_test.py`、`teacher_test.py`（28 項）。救援費以 200 為準（老師 10/2 確認）。
- **第三章 D1 在分支 `ch3`（本機，未推送）**：`chapters/ch3/`（8 場景＋遮罩＋角色＋物件圖＋航行 chapter.js，預設關閉、老師端 `ch3` 開關）；礦坑入口南邊石階（序章 `mine_out`）通往南岸漁港，完成第二章才能過。**沒有任何教學內容**；待審項見 `chapters/ch3/REVIEW.md`；版面預覽 `docs/ch3-layout/`；測試 `ch3_test.py`、`layout_test.py ch3`、`CHAPTER=ch3 walk_test.py`。**部署 ch3 前要先把 `002_fa_class_control.sql` 的 flag 檢查式含 `ch3`（草稿已改）再執行。**
- 老師 10/2 已確認 D1 與「防災包先合併再做 D1」的順序；**D2 摘要待老師確認**。防災包文字（`docs/stash-text-review.md`）仍待審；要部署（推送）須老師說「推」。
- 第三章素材包在 OneDrive：`健康與護理作業/115/多元選修/急救王國/第三章交付包/`（設計草案、題目與知識卡草稿、場景／角色／物件 PNG，含村長）；轉檔等 D3／D1 之後處理。

## 最新狀態（2026-10-01 晚，交接用；與下方舊敘述衝突時以本節為準）

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
