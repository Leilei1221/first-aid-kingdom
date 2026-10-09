# 雪嶺（E4）F2 生圖提示詞 v0.1：營地 1

整理日期：2026 年 10 月 9 日　對應 `docs/ch4-plan.md` 第 2 節「營地 1：濕了要換、手腳頭保暖、夜間保暖、不喝酒取暖」。
圖片請交到 `圖檔/ch4_assets/原始圖檔/`（和 F1 同一個資料夾，檔名用下面建議的名字）。共用規則、風格參考同 `docs/ch4-image-prompts-f1.md`：場景附 `ch4_village.webp` 當風格參考，人物附 `ch4_guide.webp`。**不要紅十字、圖上不要有可讀文字、不要真實地標與宗教人物。**

## 0. F2 要幾張圖
| # | 內容 | 用途 | 尺寸 | 必要性 |
|---|---|---|---|---|
| 1 | 營地 1（白天） | 主場景：夜間保暖、失溫程度分辨的地點 | 1672×941 | 必要 |
| 2 | 營地 1（夜晚版，同構圖） | 夜間保暖選擇（暖暖包、毛襪、保暖毯、頭燈）的場景 | 1672×941 | 建議（沒有的話我用程式把白天圖調暗，效果差一些） |
| 3 | 同行登山客（站立，全身＋頭像） | 營地 1 的同伴，穿得不夠暖的示範角色 | 全身 1024×1536 左右、頭像 1254×1254 | 必要 |
| 4 | 同行登山客（受寒版，全身） | 失溫程度分辨題的情境圖（發抖、縮著） | 同上 | 建議 |

山腳村「補買裝備」的攤位已經在 F1 的場景圖裡，不用新圖；暖暖包、保暖毯、頭燈、毛襪的圖示第三章已經有。

## 1. 營地 1 場景（#1、#2）
中文說明：半山腰一塊平坦的雪地營地，視野開闊可以看到遠處山谷；比山腳村更冷、雪更多。
- **上方左側**：兩頂帳篷（一藍一赭色），旁邊堆著背包與繩索。
- **上方中央偏右**：石頭圍成的營火圈，有一小堆營火在燒（互動點）。
- **右上**：一條往上的岩石小徑，通往營地 2（現在先不通，路口有一道繩索欄）。
- **左下**：往下回山腳村的石階小路，路口立著木製路標（箭頭與圖案，不要字）。
- **右側**：幾個木箱、一個木樁座椅，後方遠處有一頭犛牛站在不能走的雪坡邊（只當風景）。
- **中央與下半部**：一大片平坦、略有踩踏痕跡的雪地與碎石地，**完全空曠**（我要做可走遮罩）。

**共用段（#1、#2 都先貼）**
```
Match the art style of the attached reference image: hand-painted fantasy RPG game environment, wide cinematic 16:9 composition, isometric 2.5D feel viewed from about 45 degrees above, rich painterly texture, saturated but not harsh colors. A large open flat walkable ground area in the center and lower part of the image with no obstacles on it; tents, props, rocks and cliffs are placed along the top edge and the sides only. No characters standing in the walkable area. No text, no letters, no numbers, no logos, no watermark. No red cross anywhere.
```

**#1 白天**
```
[共用段]
A Himalayan-inspired mid-mountain camp on a wide snowy ledge, bright cold morning light, scattered snow and gravel, distant valley and snow peaks behind. Upper left: two expedition tents (one blue, one ochre) with backpacks and coiled ropes beside them. Upper center-right: a stone-ringed campfire pit with a small campfire burning and a log seat beside it. Upper right: a rocky path leading further uphill, blocked at its start by a simple rope fence. Lower left: a stone stair path leading down to the valley village, with a wooden signpost using arrows and pictograms only. Right side: a few wooden supply crates and a wooden stump seat; far behind them on a non-walkable snow slope stands a yak. The center and lower part is a wide, completely clear flat area of packed snow and gravel.
```

**#2 夜晚版**（把 #1 生好的圖附上當參考）
```
Use the attached image as the exact reference: keep the same composition, the same layout and the same objects in the same places. Change only the time of day to night: deep blue starry sky, cold blue moonlight and snow, warm orange glow from the campfire and from small hanging lanterns near the tents, soft long shadows. The center and lower walkable area remains completely clear. No text, no letters, no watermark.
```

## 2. 同行登山客（#3、#4）
中文說明：一位二十歲出頭的年輕登山客，第一次上山，**穿得不夠暖**（棉質連帽上衣、牛仔褲、一般運動鞋、沒有帽子手套），背著小背包，帶著不好意思的笑容。這個角色是營地 1 的「反面示範」：玩家會看到他發抖，並幫他保暖。性別不用特別指定，造型中性。
- 全身圖檔名建議 `ch4_hiker.png`、頭像 `ch4_hiker_face.png`；受寒版 `ch4_hiker_cold.png`。

**全身共用段（沿用 F1，附上 `ch4_guide.webp` 當風格參考）**
```
Match the art style of the attached reference image: full-body fantasy RPG character, detailed painterly anime-influenced illustration, standing relaxed front-facing three-quarter pose, whole body visible from head to shoes, plain light-gray background for easy cutout, soft warm lighting. No text, no letters, no logos, no watermark.
```

**#3 站立**
```
[全身共用段]
A young hiker in their early twenties on their first mountain trip, underdressed for the cold: a cotton hooded sweatshirt, jeans, ordinary canvas sneakers, no hat and no gloves, a small daypack, a bit sheepish and cheerful, slightly damp hair.
```

**頭像**（附上剛生好的全身圖）
```
Head-and-shoulders portrait of the same character as in the attached full-body image, same art style and same outfit, sheepish friendly smile, square 1:1 composition, plain light-gray background for easy cutout. No text, no watermark.
```

**#4 受寒版**（附上 #3 當參考）
```
The same character as in the attached image, same outfit and same art style, now clearly cold: sitting hunched on a log with arms wrapped around the knees, shoulders pulled up, shivering (a few small motion lines), pale cheeks, slightly blue-tinged lips, damp sleeves and jeans, looking miserable but conscious and awake. Full body, plain light-gray background for easy cutout. Not gory, not dramatic. No text, no letters, no watermark.
```

## 3. 交付後我會做的事
- 營地 1 場景：轉 WebP、做可行走遮罩、設定營火、路標、往營地 2 的繩索欄（F3 才通）與回山腳村的出入口；夜晚版在睡前的「夜間保暖」使用。
- 登山客：去背、頭像裁 160×160；受寒版用在失溫程度分辨題的畫面。
- 山腳村的出發檢查、營地 1 的題目與保暖等級會另外出**草稿**給你審（醫療內容照規劃文件第 4 節，附依據）。

## 4. 還沒有、但之後的階段會需要
營地 2、雪線、山屋場景；高山症與凍傷、雪盲的傷口圖；章末紀念物；公告板。到各階段再出提示詞。
