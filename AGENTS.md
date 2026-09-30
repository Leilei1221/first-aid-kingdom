# 給接手的 AI 助手（Codex／Claude Code 通用）

專案：急救王國（花蓮高中基礎急救教學遊戲）。負責老師：黃雅蕾（蕾蕾）。線上版：https://leilei1221.github.io/first-aid-kingdom/ ；repo：Leilei1221/first-aid-kingdom（公開）。

## 先讀
1. `HANDOFF.md`（V3 版，是需求規格；第 0 節工作守則最重要）
2. `README.md`（結構與本機開啟方式）
3. 本檔

## 工作守則（摘自 HANDOFF 第 0 節）
- 每個階段動工前：用繁體中文列出摘要，等老師確認。
- 醫療內容（`content/knowledge_cards.json`、`content/quests_and_events.json`、`content/dialogues.json` 裡的題目與解說）不可自行改寫；疑似錯誤列出來請老師確認。
- 全程繁體中文。
- 行為不變優先：每個改動都要能證明玩起來和之前一樣。
- 精簡、低維護，不引入不必要的框架；沒有建置步驟。
- 對外發布動作（建 repo、推送、開啟服務、寫入資料庫）先問老師。不要把金鑰、service_role key 放進 repo。

## 目前進度（2026-09-30）
- 階段 A 完成並已上線：圖片外部化（assets/*.webp）、內容改讀 content/*.json、對話抽到 content/dialogues.json、`js/game.js` 為遊戲邏輯。
- 新舊版行為比對：51 個情境、513 個對話框逐字一致（`tools/compare_run.py`）。
- 已用 V3 圖片覆蓋 hero、grandpa、grandpa_face、home（綠底白十字），並加入 V3 新素材 39 張（第二章、傷口圖 w_*）。`w_cut_arm.webp` 依 V3 文件不使用，未加入。
- `assets/manifest.json` 仍是舊的 55 張清單（啟動時預載用）。新功能合併、實際用到新圖時，再跑 `python3 tools/gen_manifest.py`，不要預載沒用到的圖。
- `reference/` 已從 repo 移除（含舊紅十字圖）。舊圖仍留在 git 歷史；如需徹底清除要改寫歷史，這要先問老師。
- V3.1 已處理：穿牆修正（`snapFree()`，`tools/wall_test.py` 驗證：舊版 33 個測試點穿牆 24 個，新版 0 個）、cap.webp 更新（RATIO cap=0.414）。V3.1 第 3～5 節（旅館二樓遮罩、設備檢查點、砂輪機任務）屬第二章內容，隨階段 D 合併；對照用原型在 `~/Projects/first-aid-kingdom-v3-spec/v3.1/`。
- 階段 B 資料表 SQL 草稿在 `supabase/drafts/001_fa_tables.sql`。**尚未套用到 Supabase**：老師已同意內容，但套用指令被權限分類器擋下，需老師自行授權或在 Supabase SQL 編輯器貼上執行。套用前不要寫依賴這些表的程式邏輯以外的上線動作。
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
