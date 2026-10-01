# 章節資料包格式說明（草案，D1 確認後定稿）

給：老師、Claude Chat／Co-work（編寫第三章等後續章節時使用）。
**狀態：草案。** 這是依現有 `content/` 結構推導的建議格式，階段 D1 實作並經老師確認後才定稿；交付前請以定稿版為準。

## 1. 原則

- 一章 = 一個資料夾 `chapters/chN/`，所有檔名與 id 一律加前綴 `chN_`（例如 `ch3_harbor`、`ch3_lifeg`、`ch3_cpr`），避免與序章與其他章撞名。
- 內容與程式分開：章節資料包**只放資料**（JSON、圖片）。特殊小遊戲（如 CPR 節拍、AED 操作）需要程式，另以文字說明玩法，由 Claude Code 實作。
- 醫療內容（題目、解說、知識卡）每一項標示審核狀態：`final`（老師已審）或 `draft`（待審）。**`draft` 的內容不會對學生開放。**
- 圖片：場景 1672×941，角色全身透明背景、頭像 160×160 以上，物件透明背景；來稿 PNG 即可，由 Claude Code 轉 WebP。急救標誌一律綠底白十字，圖上不要有可讀文字。

## 2. 資料夾結構

```
chapters/ch3/
  chapter.json          章節資訊：id、名稱、順序、入口場景、開放條件、相依
  scenes.json           場景（背景圖、出生點、NPC、可互動物件、出口）
  signs.json            路標（選用）
  characters.json       角色（名稱、全身圖、頭像、高度係數 hk）
  dialogues.json        對話、題目、文字（含 key 命名規則）
  cards.json            知識卡
  events.json           事件與題目（含每題的嚴重錯誤標記）
  items.json            新增物品與商店品項（選用）
  masks/                場景可行走遮罩（選用，沒有就由 Claude Code 建）
  assets/               圖片（ch3_ 前綴）
  minigames.md          特殊小遊戲的玩法文字說明
  REVIEW.md             待審項目清單（每項對應一個 id）
```

## 3. 各檔欄位（對照現有格式）

| 檔 | 對照現有 | 說明 |
|---|---|---|
| `scenes.json` | `content/scenes.json` | 每個場景：`name`、`bg`、`spawn:[x,y]`、`heroH`、`npcs:[{id,x,y,flip}]`、`things:[{kind,x,y,label}]`、`exits:[{to,at,block,test,need}]`。`test` 與 `need` 為函式原始碼字串（如 `(x,y)=>y>845`），載入時編譯 |
| `characters.json` | `PEOPLE` | `{id:{name,img,face,hk}}`；寬高比由程式從圖片量出（`RATIO`） |
| `dialogues.json` | `content/dialogues.json` | 分 `say`、`quizzes`、`text`；`{變數}` 會替換，`{CARDS.xxx.title}` 取知識卡標題 |
| `cards.json` | `CARDS` | `{id:{title,text,status}}` |
| `events.json` | `EVENTS`／`VICTIMS` | 題目含 `qs:[{q,opts,ans,explain}]`；嚴重錯誤用 `fatal:true` 標記（救援失敗用，**清單需老師確認**） |
| `chapter.json` | （新） | `{id:"ch3",name,order,entry:"ch3_fishport",requires:["ch2"],status:"draft"}` |

## 4. 交付檢查清單（Co-work 自查）

- [ ] 所有 id 都有 `ch3_` 前綴，沒有與序章重複。
- [ ] 每個出口的目的場景存在；每個 NPC、物件的 id 都有定義。
- [ ] 每個題目有 `ans`、`explain`，並標示 `draft` 或 `final`。
- [ ] 沒有死亡畫面用語；失敗用「救援失敗」語氣。
- [ ] 沒有編造數字（秒數、公分等）；來源未核對者標【待審】。
- [ ] 圖片沒有紅十字、沒有可讀文字。

## 5. 還沒決定的事（會影響格式）

| 項目 | 狀況 |
|---|---|
| 章節存檔欄位 | 預設不新增；若章節需要自己的狀態，放在 `S.ch.<章id>` 底下，並要有 `migrate()` 預設值 |
| 章節開放 | 預設**關閉**，由老師端（D5）開放；開放狀態讀資料庫，不寫在資料包 |
| 大小限制 | 第三章若做獨立 Artifact 試玩有 16MB 上限；正式版放 GitHub Pages，無此限制 |
