# 急救王國（First Aid Kingdom）

花蓮高中多元選修「基礎急救」教學遊戲。純 HTML/JS，沒有框架、沒有建置步驟：檔案本身就是要發布的內容。

## 結構
```
index.html            介面與樣式
js/game.js            遊戲邏輯
preview.html          老師預覽入口（不放連結）：點場景直接進去看，不存進度、不連雲端；網址 index.html?preview=場景id
content/*.json        所有內容資料（知識卡、事件、對話、數值、場景…），審核與修改都在這裡
  dialogues.json      劇情與教學對話（say）、小測驗（quizzes）、目標與提示文字（text）
data/walks.json       各場景可行走遮罩
assets/*.webp         圖片；assets/manifest.json 為圖片清單
reference/            原單檔版本（行為基準）
tools/                測試與輔助工具
```

## 本機開啟
內容用 `fetch` 讀取，不能直接雙擊 index.html。在專案資料夾執行：
```
python3 -m http.server 8765
```
再開 http://localhost:8765/index.html 。

## 老師端
`teacher.html`：老師用學校 Google 帳號登入後，查看自己班學生的遊戲進度（只讀），可匯出 CSV。學生端沒有連結。

## 測試
- `#debug`：網址加 `#debug`，且在瀏覽器 Console 先執行 `localStorage.setItem('fa-debug','1')`，才會出現 `window.__fa`（學生沒設旗標就看不到）。
- 行為比對：`tools/compare_run.py`（新舊版逐字比對對話與狀態）；`tools/walk_test.py`（鍵盤走路測出口）。
- `tools/cloud_test.py`（雲端同步）、`tools/teacher_test.py`（老師端）：用模擬資料測試。
- 新增或刪除圖片後：`python3 tools/gen_manifest.py`。

## 修改內容的注意事項
- 醫療內容以老師審核為準，見 HANDOFF.md 第 0、8 節。
- `content/scenes.json` 的出口條件、`content/signs.json` 的路標條件是函式原始碼字串，載入時編譯。
