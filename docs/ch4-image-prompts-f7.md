# 雪嶺（E4）F7 生圖提示詞 v0.1：山屋的日常

整理日期：2026 年 10 月 9 日　對應 `docs/ch4-plan.md` 第 3 節「完成後的日常」。
圖片請交到 `圖檔/ch4_assets/原始圖檔/`（和 F1～F6 同一個資料夾）。共用規則同前：**不要紅十字（急救標誌用綠底白十字）、圖上不要有可讀文字、不要真實地標與宗教人物。**

## 0. F7 的日常構想（供你先確認，圖都是依這個畫的）
完成章末演練後，山屋每天都有事做（沿用藍堡 E1～E3 的做法），分五塊：
1. **公告板（每天一件登山求助）**：每天輪一件，共五種：失溫、高山症、凍傷、雪盲、迷路。處理好拿「嚮導信譽」。題目與知識卡**全部沿用第 2～5 節已出現的內容重新組合，不新增醫療內容**。
2. **天氣窗口**：每天預報「適合上山／風雪大不宜」。風雪天不接戶外求助，山屋裡只做補給與訓練（不另外做隨機天災；老師端的天災公告仍由核心處理）。
3. **補給與買賣**：山屋小店賣熱奶茶、乾糧等補給；帕桑收購藥品與繃帶（沿用第三章商人的做法）。
4. **嚮導訓練**：可重複的挑戰，從第 2～5 節的題庫隨機抽題，每天第一次完成有信譽。
5. **嚮導信譽與稱號**：見習嚮導 → 正式嚮導 → 嚮導隊長（門檻是遊戲參數，我暫擬 5／15 點）。
- 夜晚版山屋室外、暴風雪版山屋室外，你之前都已經生好了，這階段會用在「夜間求助」與「風雪天」，**不用重生**。
- 以上是規劃；你若想刪減（例如先不要買賣），告訴我就可以少生圖。

## 1. F7 要幾張圖
| # | 內容 | 用途 | 尺寸 | 必要性 |
|---|---|---|---|---|
| 1 | 嚮導徽章 3 個（見習、正式、隊長） | 信譽稱號圖示 | 各 256×256、淺灰底 | 必要 |
| 2 | 天氣窗口圖示 2 個（適合上山、風雪大不宜） | 公告板顯示每日預報 | 各 256×256、淺灰底 | 必要 |
| 3 | 小店商品圖示 3 個（熱奶茶、乾糧、保暖飲水壺） | 山屋小店 | 各 256×256、淺灰底 | 建議 |
| 4 | 過路登山客 2 位（全身＋頭像各一，共 4 張） | 每日求助的傷者（變化臉孔，不用每天都是小宇、老周、阿岩） | 全身 1024×1536、頭像 1254×1254 | 建議 |
| 5 | 訓練用雪地假人（單張物件圖） | 嚮導訓練的互動點 | 約 520 寬、淺灰底 | 選配 |
| 6 | 公告板放大圖（單張插圖） | 打開公告板時的畫面 | 1024×768 | 選配 |

沒有 #3～#6 也能做：小店用現有的暖暖包、毛襪、保暖毯、頭燈圖示；求助者用小宇、老周、阿岩輪流（頭像不同、題目不同）。

## 2. 嚮導徽章 3 個（#1）
附上第三章的物件圖（例如 `ch3_aed_cabinet.webp`）當風格參考。
```
Match the art style of the attached reference image: hand-painted fantasy RPG item icon, rich painterly texture, warm lighting, single object centered, plain flat light-gray background for easy cutout. No text, no letters, no numbers, no watermark. [BADGE]
```
- `ch4_b_trainee`（見習）：`A small round embroidered mountain-guide patch in plain brown wool: a stylized snow peak over a short coiled rope, thin stitched border, modest and simple.`
- `ch4_b_guide`（正式）：`A round embroidered mountain-guide badge in silver and deep blue: a stylized snow peak over a coiled rope with a small orange whistle, a laurel ring, thick stitched border.`
- `ch4_b_captain`（隊長）：`A round embroidered mountain-guide captain badge in rich gold and deep blue: a stylized snow peak with a small star above it, a coiled rope and a whistle, a double laurel ring, thick stitched border, slightly more ornate than a regular badge.`

## 3. 天氣窗口圖示 2 個（#2）
同上共用段，`[BADGE]` 換成：
- `ch4_w_clear`（適合上山）：`A round wooden weather token showing a bright sun over a snow peak and a clear blue sky, cheerful and calm, no text.`
- `ch4_w_storm`（風雪大不宜）：`A round wooden weather token showing a dark swirling snowstorm cloud with wind streaks over a snow peak and a small crossed-out footprint trail symbol (no letters), cautionary mood, no text.`

## 4. 小店商品圖示 3 個（#3）
同上共用段：
- `ch4_g_tea`：`A steaming ceramic cup of hot yak-butter-style milk tea with a wooden spoon, rising steam, warm cozy colors.`
- `ch4_g_dryfood`：`A small cloth bundle of dried yak cheese cubes and flatbread tied with a string, simple and rustic.`
- `ch4_g_flask`：`A dented metal insulated flask with a leather strap and a little steam wisp from the cap.`

## 5. 過路登山客 2 位（#4）
附上 `ch4_hiker.webp` 當風格參考。性別不用特別指定，造型各不相同，**穿戴都是正常的登山裝備**（日常求助的原因是各種意外，不是「穿太少」）。檔名建議：`ch4_walker1.png`、`ch4_walker1_face.png`、`ch4_walker2.png`、`ch4_walker2_face.png`。

**全身共用段**
```
Match the art style of the attached reference image: full-body fantasy RPG character, detailed painterly anime-influenced illustration, standing relaxed front-facing three-quarter pose, whole body visible from head to boots, plain light-gray background for easy cutout, soft warm lighting. No text, no letters, no logos, no watermark. [CHARACTER]
```
- walker1：`A young trekker in their twenties with a green insulated jacket, a gray wool hat, trekking poles, a medium backpack, a gentle tired smile.`
- walker2：`A sturdy middle-aged porter in a thick brown padded coat, a woven headband and a cloth wrap, carrying a large basket-frame load on the back with a strap across the forehead, a practical, kind expression.`

**頭像共用段（附上各自的全身圖）**
```
Head-and-shoulders portrait of the same character as in the attached full-body image, same art style and same outfit, friendly expression, square 1:1 composition, plain light-gray background for easy cutout. No text, no watermark.
```

## 6. 選配
- **訓練假人（#5）**：`Match the art style of the attached reference image: hand-painted fantasy RPG game prop, single object centered, plain flat light-gray background for easy cutout. A life-size cloth rescue training dummy dressed in a red jacket and wool hat, lying on its back in the snow with a small orange marker flag beside it. No text, no watermark.`
- **公告板放大圖（#6）**：`Match the art style of the attached reference image: hand-painted fantasy RPG illustration. A rustic wooden notice board close-up with five pinned parchment notes showing only tiny pictograms (a snowflake, a mountain, a hand, an eye, a footprint trail), a small lantern hanging beside it, warm lighting, no writing on any paper, no text, no letters, no watermark.`

## 7. 交付後我會做的事
- 公告板每天輪一件求助（五種，夜晚的用夜晚版山屋、風雪天用暴風雪版），完成加信譽；天氣窗口顯示在公告板；小店、訓練、信譽與稱號；每日任務「處理一次事件」也算。
- 題目與知識卡**全部沿用第 2～5 節**，不新增醫療內容；日常的對白與信譽數字是遊戲參數，我會另外出清單給你審。
- 狀態記在 `S.c.ch4`，不新增頂層欄位。
- 之後 F8 是老師端 `ch4` 開關（要新的 SQL）、老師端進度顯示、整體驗收與 51 情境比對。
