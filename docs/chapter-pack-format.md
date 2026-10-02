# 章節資料包格式說明（D1 已實作，2026-10-02）

給：老師、Claude Chat／Co-work（編寫第三章等後續章節時使用）。
**狀態：D1 載入器已實作並通過測試（`tools/chapter_test.py`），本檔即為實際格式。** 第二章、第三章尚未放入；放入時各章仍需老師開放。

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

## 3. 各檔欄位（與載入器一致）

資料包放在 `chapters/<章id>/`，並在 `chapters/index.json` 登記：

```json
[{"id":"ch3","name":"港口藍堡","open":false}]
```

`open` 預設 `false`。關閉的章節不會載入內容，但**通往它的出口**（`to` 以 `ch3_` 開頭）會被擋下，玩家看到「這一章還沒開放」並被退回出口外。D5 之後 `open` 由老師端（資料庫）決定。

`chapters/ch3/chapter.json`：

```json
{"id":"ch3","name":"港口藍堡","files":{"scenes":"scenes.json","characters":"characters.json",
 "dialogues":"dialogues.json","cards":"cards.json","events":"events.json","items":"items.json",
 "ratios":"ratios.json","signs":"signs.json","walks":"walks.json"},
 "assets":["ch3_harbor","ch3_lifeg","ch3_lifeg_face"]}
```

- `files`：有哪些檔就列哪些（不是每章都需要全部）。
- `assets`：圖片檔名（不含 `.webp`），放在 `chapters/ch3/assets/`，只在章節開放時預載；**圖片的 key 也要有 `ch3_` 前綴**。
- 載入器會檢查：場景、角色、知識卡、對話 key、事件、物品、遮罩的 id 都必須以 `ch3_` 開頭，**有一個不符就整章略過**，並在 console 顯示是哪些 id（不會影響序章）。

| 檔 | 內容（欄位與序章 `content/` 相同） |
|---|---|
| `scenes.json` | `{場景id:{name,bg,spawn,heroH,npcs,things,exits}}`。`exits[].test`、`need` 為函式原始碼字串，如 `(x,y)=>x<30` |
| `walks.json` | `{場景id:[可行走網格]}`（格式同 `data/walks.json`；沒有就由 Claude Code 建） |
| `characters.json` | `{"PEOPLE":{角色id:{name,img,face,hk}}}` |
| `ratios.json` | `{"RATIO":{圖key:寬高比}}` |
| `dialogues.json` | `{say:{},quizzes:{},text:{}}`，key 以 `ch3_` 開頭，如 `ch3_cpr.intro` |
| `cards.json` | `{"CARDS":{ch3_xxx:{title,text}}}` |
| `events.json` | `{"EVENTS":[{id:"ch3_x",...}],"VICTIMS":{}}` |
| `items.json` | `{"ITEMS":{ch3_xxx:{...}}}` |
| `signs.json` | `{場景id:[路標]}` |

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
| 章節存檔欄位 | 預設不新增；若章節需要自己的狀態再加（會與 D2 一併設計），並要有 `migrate()` 預設值。玩家存檔所在的場景若屬於未開放或不存在的章節，讀檔時自動回到村莊 |
| 章節開放 | 預設**關閉**，由老師端（D5）開放；開放狀態讀資料庫，不寫在資料包 |
| 大小限制 | 第三章若做獨立 Artifact 試玩有 16MB 上限；正式版放 GitHub Pages，無此限制 |
